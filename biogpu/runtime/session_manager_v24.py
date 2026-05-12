
from __future__ import annotations

import csv
import hashlib
import json
import platform
import time
import zipfile
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

try:
    from biogpu.benchmarks.registry_v23 import build_biogpu_v23_benchmark_registry
except Exception:  # pragma: no cover - keeps the module importable in partial installs
    build_biogpu_v23_benchmark_registry = None

RunMode = Literal["replay", "dry_run", "power_pc", "live_lab"]
SessionStatus = Literal["created", "validated", "running", "completed", "failed"]
SafetyClass = Literal["offline_replay_only", "dry_run_only", "live_lab_only"]


@dataclass(frozen=True)
class BioGPUArtifactRef:
    """Reference to a generated input/output artifact.

    The artifact manager stores relative paths and SHA256 digests so that a
    future power-PC or lab run can be audited without relying on a chat log.
    """

    path: str
    kind: str
    sha256: str
    size_bytes: int
    required: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BioGPURunManifest:
    """A versioned, hardware-neutral BioGPU run manifest.

    This is the object that should be created before every replay, dry-run,
    power-PC, or future live-lab run.
    """

    version: str
    session_id: str
    run_mode: RunMode
    benchmark_ids: list[str]
    safety_class: SafetyClass
    created_utc: str
    project_goal: str
    dataset_refs: list[str] = field(default_factory=list)
    hardware_profile: str = "software_only"
    operator_note: str = ""
    config: dict[str, Any] = field(default_factory=dict)
    expected_outputs: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BioGPUAuditEvent:
    index: int
    timestamp_utc: str
    event: str
    status: str
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BioGPUSessionSummary:
    session_id: str
    run_mode: RunMode
    status: SessionStatus
    validation_errors: list[str]
    audit_events: int
    artifacts: list[BioGPUArtifactRef]
    result_bundle: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["artifacts"] = [artifact.to_dict() for artifact in self.artifacts]
        return data


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def stable_session_id(prefix: str, run_mode: RunMode, benchmark_ids: list[str]) -> str:
    raw = f"{prefix}|{run_mode}|{'/'.join(sorted(benchmark_ids))}|{int(time.time())}"
    digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:10]
    return f"{prefix}-{run_mode}-{digest}"


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    p = Path(path)
    with p.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def artifact_ref(path: str | Path, base_dir: str | Path, kind: str, required: bool = False) -> BioGPUArtifactRef:
    p = Path(path)
    base = Path(base_dir)
    rel = p.relative_to(base).as_posix() if p.is_relative_to(base) else p.as_posix()
    return BioGPUArtifactRef(
        path=rel,
        kind=kind,
        sha256=sha256_file(p),
        size_bytes=p.stat().st_size,
        required=required,
    )


def build_v24_manifest(
    run_mode: RunMode = "dry_run",
    benchmark_ids: list[str] | None = None,
    hardware_profile: str = "software_only",
    operator_note: str = "",
) -> BioGPURunManifest:
    if benchmark_ids is None:
        benchmark_ids = [
            "B0_target_vs_random_electrode",
            "B1_spot_localization",
            "B2_temporal_pattern_classification",
            "B4_adaptive_closed_loop",
            "B5_energy_latency_comparison",
        ]

    safety_class: SafetyClass
    if run_mode == "live_lab":
        safety_class = "live_lab_only"
    elif run_mode == "dry_run":
        safety_class = "dry_run_only"
    else:
        safety_class = "offline_replay_only"

    return BioGPURunManifest(
        version="v2.4",
        session_id=stable_session_id("biogpu", run_mode, benchmark_ids),
        run_mode=run_mode,
        benchmark_ids=benchmark_ids,
        safety_class=safety_class,
        created_utc=utc_now(),
        project_goal=(
            "Design and implement a real working BioGPU: encoder -> living/neural substrate "
            "or replay substrate -> readout -> benchmark -> energy/task comparison."
        ),
        dataset_refs=[
            "Zenodo 14363732 pulse-window feature matrix for replay mode",
            "Future DANDI/Allen/NWB task-aligned datasets for power-PC mode",
            "Future MEA/HD-MEA live stream for licensed-lab mode",
        ],
        hardware_profile=hardware_profile,
        operator_note=operator_note,
        config={
            "mode_contract": {
                "replay": "uses public spike-response features and never emits live stimulation settings",
                "dry_run": "validates manifests, benchmark selection, and artifact bundling without hardware",
                "power_pc": "runs heavy statistics/shuffles/bootstrap on local compute",
                "live_lab": "requires vendor SDK, approved SOP, qualified lab, and live backend",
            },
            "default_output_dir": "outputs/realdata_zenodo_14363732_v24_session_manager",
            "forbidden_in_repo": [
                "live wet-lab culturing protocol",
                "exact live stimulation safety limits",
                "vendor-specific physical wiring procedure",
            ],
        },
        expected_outputs=[
            "run_manifest.json",
            "audit_log.jsonl",
            "session_summary.json",
            "result_bundle.zip",
        ],
    )


def validate_manifest(manifest: BioGPURunManifest) -> list[str]:
    errors: list[str] = []
    allowed_modes = {"replay", "dry_run", "power_pc", "live_lab"}
    if manifest.run_mode not in allowed_modes:
        errors.append(f"invalid run_mode: {manifest.run_mode}")
    if not manifest.benchmark_ids:
        errors.append("benchmark_ids must not be empty")
    if manifest.run_mode == "live_lab" and manifest.safety_class != "live_lab_only":
        errors.append("live_lab mode must use live_lab_only safety class")
    if manifest.run_mode != "live_lab" and manifest.safety_class == "live_lab_only":
        errors.append("live_lab_only safety class cannot be used outside live_lab mode")
    if manifest.run_mode in {"replay", "dry_run", "power_pc"}:
        forbidden = ["stimulation_amplitude", "pulse_voltage", "culturing_recipe"]
        text = json.dumps(manifest.to_dict()).lower()
        for term in forbidden:
            if term in text:
                errors.append(f"unsafe live-lab term found in non-live manifest: {term}")

    if build_biogpu_v23_benchmark_registry is not None:
        try:
            registry = build_biogpu_v23_benchmark_registry()
            known = {task.task_id for task in registry.tasks}
            for benchmark_id in manifest.benchmark_ids:
                if benchmark_id not in known:
                    errors.append(f"unknown benchmark_id: {benchmark_id}")
        except Exception as exc:  # pragma: no cover
            errors.append(f"benchmark registry unavailable: {exc}")
    return errors


class BioGPUAuditLog:
    def __init__(self) -> None:
        self.events: list[BioGPUAuditEvent] = []

    def add(self, event: str, status: str, **details: Any) -> BioGPUAuditEvent:
        item = BioGPUAuditEvent(
            index=len(self.events),
            timestamp_utc=utc_now(),
            event=event,
            status=status,
            details=details,
        )
        self.events.append(item)
        return item

    def to_jsonl(self) -> str:
        return "\n".join(json.dumps(e.to_dict(), ensure_ascii=False) for e in self.events) + ("\n" if self.events else "")

    def write_jsonl(self, path: str | Path) -> None:
        Path(path).write_text(self.to_jsonl(), encoding="utf-8")


class BioGPUResultBundler:
    def __init__(self, output_dir: str | Path) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def build_bundle(self, bundle_name: str = "biogpu_v24_result_bundle.zip") -> Path:
        bundle_path = self.output_dir / bundle_name
        include_suffixes = {".json", ".jsonl", ".md", ".csv"}
        with zipfile.ZipFile(bundle_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
            for p in sorted(self.output_dir.rglob("*")):
                if p == bundle_path or not p.is_file():
                    continue
                if p.suffix in include_suffixes:
                    z.write(p, p.relative_to(self.output_dir).as_posix())
        return bundle_path


def render_manifest_markdown(manifest: BioGPURunManifest, validation_errors: list[str]) -> str:
    lines = [
        "# BioGPU v2.4 Run Manifest",
        "",
        f"- Session ID: `{manifest.session_id}`",
        f"- Mode: `{manifest.run_mode}`",
        f"- Safety class: `{manifest.safety_class}`",
        f"- Hardware profile: `{manifest.hardware_profile}`",
        f"- Created UTC: `{manifest.created_utc}`",
        "",
        "## Project goal",
        "",
        manifest.project_goal,
        "",
        "## Benchmarks",
        "",
    ]
    lines.extend(f"- `{bid}`" for bid in manifest.benchmark_ids)
    lines.extend([
        "",
        "## Dataset references",
        "",
    ])
    lines.extend(f"- {ref}" for ref in manifest.dataset_refs)
    lines.extend([
        "",
        "## Validation",
        "",
    ])
    if validation_errors:
        lines.extend(f"- ERROR: {err}" for err in validation_errors)
    else:
        lines.append("- OK: manifest validates cleanly")
    lines.extend([
        "",
        "## Boundary",
        "",
        "This manifest is a software/runtime artifact. It does not contain live wet-lab recipes, exact live stimulation limits, or vendor-specific physical wiring instructions.",
    ])
    return "\n".join(lines) + "\n"


def write_v24_session_outputs(
    output_dir: str | Path,
    run_mode: RunMode = "dry_run",
    benchmark_ids: list[str] | None = None,
    hardware_profile: str = "software_only",
    operator_note: str = "",
) -> dict[str, Any]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    manifest = build_v24_manifest(run_mode, benchmark_ids, hardware_profile, operator_note)
    audit = BioGPUAuditLog()
    audit.add("manifest_created", "ok", session_id=manifest.session_id, run_mode=manifest.run_mode)

    errors = validate_manifest(manifest)
    audit.add("manifest_validated", "ok" if not errors else "error", validation_errors=errors)

    (out / "run_manifest.json").write_text(json.dumps(manifest.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    (out / "BIOGPU_V24_RUN_MANIFEST.md").write_text(render_manifest_markdown(manifest, errors), encoding="utf-8")
    audit.write_jsonl(out / "audit_log.jsonl")

    system_info = {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "created_utc": utc_now(),
    }
    (out / "system_info.json").write_text(json.dumps(system_info, indent=2, ensure_ascii=False), encoding="utf-8")

    # A dry-run placeholder that future real results should replace, but which
    # makes the bundle contract testable today.
    dry_result = {
        "session_id": manifest.session_id,
        "run_mode": manifest.run_mode,
        "status": "dry_run_complete" if manifest.run_mode == "dry_run" else "manifest_only",
        "benchmarks_selected": manifest.benchmark_ids,
        "note": "v2.4 validates runtime packaging and audit contracts; it does not execute heavy readout sweeps.",
    }
    (out / "dry_run_result.json").write_text(json.dumps(dry_result, indent=2, ensure_ascii=False), encoding="utf-8")

    # CSV overview for quick inspection.
    with (out / "selected_benchmarks.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["session_id", "run_mode", "benchmark_id"])
        writer.writeheader()
        for bid in manifest.benchmark_ids:
            writer.writerow({"session_id": manifest.session_id, "run_mode": manifest.run_mode, "benchmark_id": bid})

    # Bundle after all primary artifacts are written.
    bundler = BioGPUResultBundler(out)
    bundle_path = bundler.build_bundle()

    artifacts = [
        artifact_ref(out / "run_manifest.json", out, "manifest", required=True),
        artifact_ref(out / "BIOGPU_V24_RUN_MANIFEST.md", out, "report", required=True),
        artifact_ref(out / "audit_log.jsonl", out, "audit", required=True),
        artifact_ref(out / "system_info.json", out, "environment", required=False),
        artifact_ref(out / "dry_run_result.json", out, "result", required=False),
        artifact_ref(out / "selected_benchmarks.csv", out, "index", required=True),
        artifact_ref(bundle_path, out, "bundle", required=True),
    ]

    summary = BioGPUSessionSummary(
        session_id=manifest.session_id,
        run_mode=manifest.run_mode,
        status="validated" if manifest.run_mode != "dry_run" else "completed",
        validation_errors=errors,
        audit_events=len(audit.events),
        artifacts=artifacts,
        result_bundle=bundle_path.name,
    )
    (out / "session_summary.json").write_text(json.dumps(summary.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")

    # Rebuild bundle including session_summary.
    bundle_path = bundler.build_bundle()
    final_summary = summary.to_dict()
    final_summary["result_bundle_sha256"] = sha256_file(bundle_path)
    final_summary["result_bundle_size_bytes"] = bundle_path.stat().st_size
    (out / "session_summary.json").write_text(json.dumps(final_summary, indent=2, ensure_ascii=False), encoding="utf-8")
    bundler.build_bundle()

    return final_summary
