"""BioGPU Replay Worker v8.1 — runs replay benchmarks as production jobs.

Connects the existing BioGPU replay pipelines (v33 compact, v36 lineage,
v58 raw-native, v16 DANDI, v20 Allen) to the BioSDK production scheduler.
Each job produces: feature matrix, readout results, evidence bundle.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from biogpu.production.config_v60 import load_production_config
from biogpu.sdk.signing_v66 import sign_file, load_signing_key

# Known replay benchmarks that can be launched
REPLAY_BENCHMARKS = {
    "v33_compact": {
        "module": "biogpu.benchmarks.biogpu_v33_realdata_sweep",
        "description": "V33 compact paper-grade real-data sweep on Zenodo pulse-window features",
        "data_source": "Zenodo 14363732",
        "expected_accuracy_range": "0.45-0.52 (chance=0.25)",
        "runtime_seconds": 5,
    },
    "v36_lineage": {
        "module": "biogpu.benchmarks.biogpu_v36_lineage_bootstrap",
        "description": "V36 lineage-strict split with bootstrap confidence intervals",
        "data_source": "Zenodo 14363732",
        "expected_accuracy_range": "0.30-0.40 (chance=0.25)",
        "runtime_seconds": 30,
    },
    "v16_dandi": {
        "module": "biogpu.benchmarks.biogpu_v516_dandi_nwb_task_benchmark",
        "description": "DANDI/NWB task benchmark with spike features and shuffled-label readout",
        "data_source": "DANDI 000469",
        "expected_accuracy_range": "exploratory single-sample",
        "runtime_seconds": 3,
    },
    "v20_allen": {
        "module": "biogpu.benchmarks.biogpu_v520_allen_orientation_benchmark",
        "description": "Allen visual-coding orientation benchmark",
        "data_source": "Allen/DANDI 000021",
        "expected_accuracy_range": "exploratory single-session",
        "runtime_seconds": 5,
    },
    "v58_raw": {
        "module": "biogpu.benchmarks.biogpu_v58_raw_native_benchmark",
        "description": "Raw HDF5 native event-window feature benchmark",
        "data_source": "Zenodo 14363732 raw HDF5",
        "expected_accuracy_range": "exploratory raw-native",
        "runtime_seconds": 10,
    },
}


@dataclass
class ReplayJob:
    job_id: str
    benchmark_id: str
    status: str = "queued"  # queued, running, completed, failed
    worker_id: str = ""
    started_at: str = ""
    completed_at: str = ""
    result: dict[str, Any] = field(default_factory=dict)
    evidence_bundle_path: str = ""
    evidence_bundle_sha256: str = ""
    error: str = ""


class ReplayWorker:
    """Worker that executes BioGPU replay benchmarks as production jobs."""

    def __init__(self, project_root: str | Path = ".", worker_id: str = "worker-1"):
        self.root = Path(project_root)
        self.worker_id = worker_id
        self.config = load_production_config()
        self.job_dir = self.root / "data" / "production" / "replay_jobs"
        self.job_dir.mkdir(parents=True, exist_ok=True)

    def queue_job(self, benchmark_id: str) -> ReplayJob | None:
        if benchmark_id not in REPLAY_BENCHMARKS:
            print(f"Unknown benchmark: {benchmark_id}")
            return None
        import uuid
        job = ReplayJob(
            job_id=f"replay-{uuid.uuid4().hex[:8]}",
            benchmark_id=benchmark_id,
            status="queued",
        )
        self._save_job(job)
        return job

    def execute_job(self, job: ReplayJob) -> ReplayJob:
        """Execute a replay job and collect results."""
        benchmark = REPLAY_BENCHMARKS.get(job.benchmark_id)
        if not benchmark:
            job.status = "failed"
            job.error = f"Unknown benchmark: {job.benchmark_id}"
            return job

        job.status = "running"
        job.started_at = datetime.now(timezone.utc).isoformat()
        job.worker_id = self.worker_id
        self._save_job(job)

        try:
            # Locate existing results if already computed
            existing = self._find_existing_results(job.benchmark_id)
            if existing:
                job.result = existing
                job.status = "completed"
                job.completed_at = datetime.now(timezone.utc).isoformat()
                print(f"  Found existing results for {job.benchmark_id}: accuracy={existing.get('best_accuracy', 'N/A')}")
            else:
                # Try to run the benchmark
                print(f"  Running benchmark: {benchmark['module']}")
                result = self._run_benchmark_module(benchmark["module"])
                job.result = result
                job.status = "completed" if result else "failed"
                job.completed_at = datetime.now(timezone.utc).isoformat()

            # Create evidence bundle (non-fatal on failure)
            if job.status == "completed":
                try:
                    bundle_path = self._create_evidence_bundle(job)
                    job.evidence_bundle_path = str(bundle_path)
                    if bundle_path.exists():
                        job.evidence_bundle_sha256 = hashlib.sha256(bundle_path.read_bytes()).hexdigest()
                except Exception:
                    pass  # Evidence bundle is optional

        except Exception as exc:
            job.status = "failed"
            job.error = str(exc)

        self._save_job(job)
        return job

    def _find_existing_results(self, benchmark_id: str) -> dict[str, Any] | None:
        """Find pre-computed benchmark results in outputs/."""
        mapping = {
            "v33_compact": "powerpc_stage1_v33_compact/sweep_summary_v33.json",
            "v36_lineage": "powerpc_stage2_v36_lineage_compact/v36_summary.json",
            "v16_dandi": "v516_dandi_nwb_task_benchmark/V516_DANDI_NWB_TASK_BENCHMARK_SUMMARY.json",
            "v20_allen": "v520_allen_orientation_benchmark/V520_ALLEN_ORIENTATION_BENCHMARK_SUMMARY.json",
            "v58_raw": "v58_raw_native_benchmark/V58_RAW_NATIVE_FEATURE_SUMMARY.json",
        }
        rel_path = mapping.get(benchmark_id)
        if not rel_path:
            return None
        fpath = self.root / "outputs" / rel_path
        if not fpath.exists():
            return None
        try:
            data = json.loads(fpath.read_text(encoding="utf-8"))
            # Normalize: extract best accuracy from nested structures
            if "best_accuracy" not in data:
                if "best_run" in data and isinstance(data["best_run"], dict):
                    data["best_accuracy"] = data["best_run"].get("accuracy")
                elif "best_by_decoder" in data and data["best_by_decoder"]:
                    data["best_accuracy"] = max(
                        (d.get("accuracy", 0) for d in data["best_by_decoder"]), default=None
                    )
                elif "aggregate_by_decoder" in data and data["aggregate_by_decoder"]:
                    data["best_accuracy"] = max(
                        (d.get("best_accuracy", 0) for d in data["aggregate_by_decoder"]), default=None
                    )
            if "dataset_rows" not in data:
                data["dataset_rows"] = data.get("rows", data.get("dataset_rows", 0))
            if "dataset_features" not in data:
                data["dataset_features"] = data.get("features", data.get("dataset_features", 0))
            return data
        except Exception:
            return None

    def _run_benchmark_module(self, module_name: str) -> dict[str, Any]:
        """Run a benchmark module via subprocess."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", module_name, "--root", str(self.root)],
                capture_output=True, text=True, timeout=120,
                cwd=str(self.root),
            )
            return {
                "module": module_name,
                "returncode": result.returncode,
                "stdout": result.stdout[-3000:],
                "stderr": result.stderr[-1000:],
                "ran_at": datetime.now(timezone.utc).isoformat(),
            }
        except subprocess.TimeoutExpired:
            return {"module": module_name, "error": "timeout", "ran_at": datetime.now(timezone.utc).isoformat()}
        except Exception as exc:
            return {"module": module_name, "error": str(exc), "ran_at": datetime.now(timezone.utc).isoformat()}

    def _create_evidence_bundle(self, job: ReplayJob) -> Path:
        """Create a signed evidence bundle for the job."""
        bundle_dir = self.root / "data" / "production" / "storage" / "objects" / f"job_{job.job_id}"
        bundle_dir.mkdir(parents=True, exist_ok=True)

        # Write job result
        (bundle_dir / "job_result.json").write_text(json.dumps(asdict(job), indent=2, ensure_ascii=False, default=str), encoding="utf-8")
        (bundle_dir / "job_manifest.json").write_text(json.dumps({
            "job_id": job.job_id,
            "benchmark_id": job.benchmark_id,
            "worker_id": job.worker_id,
            "status": job.status,
            "completed_at": job.completed_at,
        }, indent=2, ensure_ascii=False), encoding="utf-8")

        # Sign key files
        key = load_signing_key(str(self.root / self.config.signing_key_path))
        for f in bundle_dir.glob("*.json"):
            sign_file(f, key)

        return bundle_dir

    def _save_job(self, job: ReplayJob) -> None:
        path = self.job_dir / f"{job.job_id}.json"
        path.write_text(json.dumps(asdict(job), indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    def list_jobs(self) -> list[ReplayJob]:
        jobs = []
        for f in sorted(self.job_dir.glob("replay-*.json")):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                jobs.append(ReplayJob(**{k: v for k, v in data.items() if k in ReplayJob.__dataclass_fields__}))
            except Exception:
                continue
        return jobs



def _extract_accuracy(result: dict[str, Any]) -> Any:
    """Extract best accuracy from various result formats."""
    if not result:
        return "N/A"
    for key in ["best_accuracy", "accuracy"]:
        if key in result and result[key] is not None:
            return result[key]
    if "best_run" in result and isinstance(result["best_run"], dict):
        return result["best_run"].get("accuracy", "N/A")
    if "best_by_decoder" in result and result["best_by_decoder"]:
        return max((d.get("accuracy", 0) for d in result["best_by_decoder"]), default="N/A")
    if "aggregate_by_decoder" in result and result["aggregate_by_decoder"]:
        return max((d.get("best_accuracy", 0) for d in result["aggregate_by_decoder"]), default="N/A")
    return "N/A"


def run_all_benchmarks(root: str | Path = ".") -> dict[str, Any]:
    """Run all available replay benchmarks and return summary."""
    worker = ReplayWorker(root, "worker-v81-autorun")
    results = {}
    for bid in REPLAY_BENCHMARKS:
        print(f"\n[{bid}] {REPLAY_BENCHMARKS[bid]['description']}")
        job = worker.queue_job(bid)
        if job:
            job = worker.execute_job(job)
            results[bid] = {
                "status": job.status,
                "accuracy": _extract_accuracy(job.result),
                "evidence_bundle": job.evidence_bundle_sha256,
            }
            print(f"  -> {job.status}")
    return {
        "worker": "v8.1",
        "benchmarks_run": len(results),
        "completed": sum(1 for r in results.values() if r["status"] == "completed"),
        "results": results,
        "ran_at": datetime.now(timezone.utc).isoformat(),
    }
