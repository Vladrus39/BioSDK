from __future__ import annotations

import csv
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Any

import numpy as np

from biogpu.runtime.contracts import BioGPUJob, BioGPUObjective, BioGPUResult, BioGPUTrace, build_biogpu_claim_ladder


@dataclass(frozen=True)
class ReplayPulseMetadata:
    row_index: int
    recording_path: str
    culture: str
    date: str
    condition: str
    target_type: str
    target_id: int | None
    pulse_index: int
    start_s: float
    end_s: float
    duration_s: float


@dataclass(frozen=True)
class ReplayPulseFeatureMatrix:
    X: np.ndarray
    metadata: list[ReplayPulseMetadata]
    electrodes: list[int]
    feature_names: list[str]
    response_window_ms: float


def _load_replay_matrix_from_v15_outputs(v15_out_dir: str | Path) -> ReplayPulseFeatureMatrix:
    """Lightweight loader for v1.5 pulse matrix.

    This intentionally avoids importing v16/v17 analysis modules so v1.8 runtime
    can start quickly even in constrained environments.
    """
    base = Path(v15_out_dir)
    npz_path = base / "pulse_feature_matrix.npz"
    meta_path = base / "pulse_feature_metadata.csv"
    if not npz_path.exists():
        raise FileNotFoundError(f"Missing {npz_path}")
    if not meta_path.exists():
        raise FileNotFoundError(f"Missing {meta_path}")
    data = np.load(npz_path, allow_pickle=True)
    X = np.asarray(data["X"], dtype=np.float32)
    electrodes = [int(v) for v in np.asarray(data["electrodes"]).tolist()]
    feature_names = [str(v) for v in np.asarray(data["feature_names"], dtype=object).tolist()]
    response_window_ms = float(np.asarray(data["response_window_ms"]).ravel()[0]) if "response_window_ms" in data else 100.0
    metadata: list[ReplayPulseMetadata] = []
    with meta_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            target_raw = row.get("target_id", "")
            target_id = None if target_raw in ("", "None", None) else int(float(str(target_raw)))
            metadata.append(
                ReplayPulseMetadata(
                    row_index=int(float(row.get("row_index", len(metadata)))),
                    recording_path=str(row.get("recording_path", "")),
                    culture=str(row.get("culture", "")),
                    date=str(row.get("date", "")),
                    condition=str(row.get("condition", "")),
                    target_type=str(row.get("target_type", "")),
                    target_id=target_id,
                    pulse_index=int(float(row.get("pulse_index", 0))),
                    start_s=float(row.get("start_s", 0.0)),
                    end_s=float(row.get("end_s", 0.0)),
                    duration_s=float(row.get("duration_s", 0.0)),
                )
            )
    if len(metadata) != X.shape[0]:
        raise ValueError(f"Metadata row count {len(metadata)} does not match X rows {X.shape[0]}")
    return ReplayPulseFeatureMatrix(X=X, metadata=metadata, electrodes=electrodes, feature_names=feature_names, response_window_ms=response_window_ms)


def _safe_json(obj: Any) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False)


class RealDataReplayBioGPUSubstrate:
    """Offline BioGPU substrate backed by public real MEA response traces.

    This is not a simulator in the old sense: every returned response vector comes
    from a real pulse window in the saved v1.5 feature matrix. It is still not a
    live device; it is a public-data replay implementation of the BioGPU runtime
    contract. Its purpose is to build the software architecture before lab
    hardware is available.
    """

    def __init__(self, v15_out_dir: str | Path, seed: int = 18):
        self.v15_out_dir = Path(v15_out_dir)
        self.matrix = _load_replay_matrix_from_v15_outputs(self.v15_out_dir)
        self.rng = np.random.default_rng(int(seed))
        self.feature_names = list(self.matrix.feature_names)
        self._by_target: dict[int, np.ndarray] = {}
        self._by_culture: dict[str, np.ndarray] = {}
        self._index()

    def _index(self) -> None:
        targets: dict[int, list[int]] = {}
        cultures: dict[str, list[int]] = {}
        for i, meta in enumerate(self.matrix.metadata):
            if meta.target_id is not None:
                targets.setdefault(int(meta.target_id), []).append(i)
            cultures.setdefault(str(meta.culture), []).append(i)
        self._by_target = {k: np.asarray(v, dtype=int) for k, v in targets.items()}
        self._by_culture = {k: np.asarray(v, dtype=int) for k, v in cultures.items()}

    def health_check(self) -> dict[str, Any]:
        return {
            "type": "RealDataReplayBioGPUSubstrate",
            "mode": "offline_public_data_replay",
            "live_hardware": False,
            "pulse_windows": int(self.matrix.X.shape[0]),
            "feature_count": int(self.matrix.X.shape[1]),
            "electrode_count": int(len(self.matrix.electrodes)),
            "culture_count": int(len(self._by_culture)),
            "target_class_count": int(len(self._by_target)),
            "v15_out_dir": str(self.v15_out_dir),
        }

    def available_targets(self) -> list[int]:
        return sorted(int(k) for k in self._by_target.keys())

    def available_cultures(self) -> list[str]:
        return sorted(self._by_culture.keys())

    def _choose_index(self, target_electrode: int | None = None, culture: str | None = None) -> int:
        if target_electrode is not None and int(target_electrode) not in self._by_target:
            raise KeyError(f"No replay pulse windows found for target electrode {target_electrode}")
        if culture is not None and str(culture) not in self._by_culture:
            raise KeyError(f"No replay pulse windows found for culture {culture}")
        candidates: np.ndarray | None = None
        if target_electrode is not None:
            candidates = self._by_target[int(target_electrode)]
        if culture is not None:
            cidx = self._by_culture[str(culture)]
            candidates = cidx if candidates is None else np.intersect1d(candidates, cidx, assume_unique=False)
        if candidates is None:
            candidates = np.arange(self.matrix.X.shape[0], dtype=int)
        if candidates.size == 0:
            raise KeyError(f"No replay pulse windows match target={target_electrode}, culture={culture}")
        return int(self.rng.choice(candidates))

    def run_job(self, job: BioGPUJob) -> BioGPUResult:
        payload = dict(job.input_payload or {})
        target = payload.get("target_electrode")
        culture = payload.get("culture")
        idx = self._choose_index(target_electrode=None if target is None else int(target), culture=None if culture is None else str(culture))
        meta = self.matrix.metadata[idx]
        features = np.asarray(self.matrix.X[idx], dtype=float)
        trace = BioGPUTrace(
            job_id=job.job_id,
            source="Zenodo public preprocessed MEA replay from v1.5 pulse_feature_matrix.npz",
            culture=str(meta.culture),
            recording=str(Path(meta.recording_path).name or meta.recording_path),
            target_electrode=None if meta.target_id is None else int(meta.target_id),
            response_features=features.tolist(),
            feature_names=self.feature_names,
            metadata={
                "pulse_index": idx,
                "condition": str(meta.condition),
                "start_s": float(meta.start_s),
                "end_s": float(meta.end_s),
                "requested_target_electrode": target,
                "requested_culture": culture,
                "runtime_mode": "offline_public_data_replay",
            },
        )
        return BioGPUResult(
            job_id=job.job_id,
            prediction=trace.target_electrode,
            confidence=None,
            metrics={"feature_l2_norm": float(np.linalg.norm(features)), "feature_nonzero_fraction": float(np.mean(features != 0))},
            trace=trace,
            metadata={"note": "Prediction is replay metadata, not a trained decoder output in this demo."},
        )


def build_v18_architecture_manifest(v15_out_dir: str | Path) -> dict[str, Any]:
    substrate = RealDataReplayBioGPUSubstrate(v15_out_dir)
    return {
        "version": "v1.8",
        "objective": BioGPUObjective().to_dict(),
        "claim_ladder": [s.to_dict() for s in build_biogpu_claim_ladder()],
        "runtime_contract": {
            "job": "BioGPUJob: task/input/encoding/substrate/readout/safety metadata",
            "trace": "BioGPUTrace: source/culture/recording/target/response feature vector",
            "result": "BioGPUResult: decoded output + metrics + trace",
        },
        "substrates": {
            "available_now": [
                "SimulatedMEA for synthetic development",
                "RealDataReplayBioGPUSubstrate for public real MEA pulse responses",
                "RealMEAVendorNeutralAdapter dry-run contract for future lab hardware",
            ],
            "future_lab": [
                "MEA2100/MaxOne/HD-MEA vendor driver",
                "closed-loop stimulation/readout control",
                "raw stream + TTL synchronization",
            ],
        },
        "current_replay_substrate_health": substrate.health_check(),
        "why_public_data_is_enough_for_now": [
            "It is enough to design BioGPU software contracts and prove real response separability.",
            "It is enough to build a replay substrate so algorithms see real biological response vectors.",
            "It is not enough to prove live closed-loop speed/energy advantage; that needs hardware.",
        ],
    }


def write_v18_biogpu_core_outputs(v15_out_dir: str | Path, out_dir: str | Path, demo_jobs: int = 8, seed: int = 18) -> dict[str, Any]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    substrate = RealDataReplayBioGPUSubstrate(v15_out_dir, seed=seed)
    manifest = build_v18_architecture_manifest(v15_out_dir)
    targets = substrate.available_targets()
    cultures = substrate.available_cultures()
    rng = np.random.default_rng(int(seed))
    results: list[dict[str, Any]] = []
    for i in range(int(demo_jobs)):
        target = int(rng.choice(targets)) if targets else None
        job = BioGPUJob(
            job_id=f"v18_replay_job_{i:03d}",
            task="replay_biological_response_for_targeted_stimulus",
            input_payload={"target_electrode": target},
            encoding="recorded_zenodo_protocol_target_replay",
            substrate="RealDataReplayBioGPUSubstrate",
            readout="metadata_replay_demo_only",
            safety_class="offline_public_data_replay_only",
            metadata={"demo": True, "available_cultures": len(cultures)},
        )
        results.append(substrate.run_job(job).to_dict())

    summary = {
        "version": "v1.8",
        "title": "BioGPU-Core runtime direction: public-real-data replay substrate + hardware-neutral contracts",
        "main_goal": BioGPUObjective().mission,
        "health": substrate.health_check(),
        "demo_jobs": int(demo_jobs),
        "demo_result_count": int(len(results)),
        "available_targets_sample": targets[:20],
        "available_cultures_sample": cultures[:10],
        "next_step_on_this_environment": [
            "Keep adding software contracts, docs, smoke tests, and adapters that do not require heavy compute.",
            "Use v1.5 matrix as the fast path for local readout and replay development.",
        ],
        "next_step_on_power_pc": [
            "Run v1.7/v1.8 full paper-grade readouts with 100-1000 shuffles and many negative seeds.",
            "Download/parse DANDI NWB and Allen data for task-aligned BioGPU benchmarks.",
        ],
        "next_step_in_lab": [
            "Implement a vendor-approved live MEA/HD-MEA adapter behind the same BioGPUJob/Trace/Result contract.",
            "Measure latency, repeatability, biological stability, and energy/task metrics.",
        ],
    }
    (out / "v18_biogpu_architecture_manifest.json").write_text(_safe_json(manifest), encoding="utf-8")
    (out / "v18_biogpu_runtime_summary.json").write_text(_safe_json(summary), encoding="utf-8")
    (out / "v18_replay_demo_results.json").write_text(_safe_json(results), encoding="utf-8")
    with (out / "v18_replay_demo_results.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["job_id", "requested_target", "replayed_target", "culture", "recording", "feature_l2_norm", "feature_nonzero_fraction"])
        writer.writeheader()
        for row in results:
            tr = row.get("trace") or {}
            writer.writerow({
                "job_id": row.get("job_id"),
                "requested_target": (tr.get("metadata") or {}).get("requested_target_electrode"),
                "replayed_target": tr.get("target_electrode"),
                "culture": tr.get("culture"),
                "recording": tr.get("recording"),
                "feature_l2_norm": (row.get("metrics") or {}).get("feature_l2_norm"),
                "feature_nonzero_fraction": (row.get("metrics") or {}).get("feature_nonzero_fraction"),
            })
    (out / "BIOGPU_V18_RUNTIME_REPORT.md").write_text(render_v18_report(summary, manifest), encoding="utf-8")
    return summary


def render_v18_report(summary: dict[str, Any], manifest: dict[str, Any]) -> str:
    ladder_lines = []
    for stage in manifest.get("claim_ladder", []):
        ladder_lines.append(f"- **{stage['stage']}** — {stage['status']}: {stage['claim']}")
    return f"""# BioGPU-Core v1.8 — from analysis to runtime architecture

## Main goal

{summary['main_goal']}

## What v1.8 changes

v1.8 keeps the Zenodo result, but prevents the project from becoming only a MEA analysis project. It adds a hardware-neutral BioGPU runtime contract:

```text
BioGPUJob -> encoder/substrate -> BioGPUTrace -> readout -> BioGPUResult
```

The current substrate is `RealDataReplayBioGPUSubstrate`: it returns real recorded pulse-level response vectors from the public Zenodo-derived v1.5 matrix. A future live MEA/HD-MEA adapter must satisfy the same contract.

## Replay substrate health

```json
{_safe_json(summary['health'])}
```

## Claim ladder

{chr(10).join(ladder_lines)}

## What public data is enough for

- Designing the BioGPU software runtime.
- Building encoders/readouts against real biological response vectors.
- Proving pulse-level biological separability above shuffled baselines.
- Preparing the exact contract that real hardware must implement later.

## What public data is not enough for

- Proving live closed-loop BioGPU operation.
- Proving energy advantage over GPUs.
- Proving hardware latency, stability, and repeatability.

## Demo

This v1.8 archive includes `{summary['demo_result_count']}` replay jobs written to:

```text
outputs/realdata_zenodo_14363732_v18_biogpu_core/v18_replay_demo_results.json
outputs/realdata_zenodo_14363732_v18_biogpu_core/v18_replay_demo_results.csv
```

Each result is a BioGPU-style job/result object backed by a real public MEA response vector.
"""
