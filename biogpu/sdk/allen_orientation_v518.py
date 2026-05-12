"""BioSDK Allen visual-coding orientation sample gate, v5.18."""
from __future__ import annotations

import csv
import importlib.util
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from biogpu.data_ingest.dandi_nwb import inspect_nwb_units
from biogpu.data_ingest.nwb_stimulus_discovery import candidates_as_dict, discover_stimulus_tables, inspect_nwb_structure


DEFAULT_OUT = Path("outputs/v518_allen_orientation_gate")
ALLEN_NWB_PATTERNS = ("data/external/allen/**/*.nwb",)
ALLEN_MANIFEST_PATTERNS = (
    "data/external/allen/**/*manifest*.json",
    "data/external/allen/**/*manifest*.csv",
    "data/external/allen/**/*session*.json",
    "data/external/allen/**/*session*.csv",
)
ORIENTATION_TERMS = (
    "orientation",
    "orientation_deg",
    "ori",
    "drifting_gratings",
    "static_gratings",
    "gabor",
    "stimulus_name",
    "stimulus_condition_id",
)


@dataclass(frozen=True)
class AllenOrientationSampleReportV518:
    path: str
    gate_status: str
    file_size_bytes: int
    has_units: bool
    unit_count: int
    spike_times_count: int
    has_intervals: bool
    has_trials: bool
    has_stimulus: bool
    stimulus_candidate_count: int
    orientation_candidate_count: int
    selected_orientation_signal: str | None
    blockers: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _files(root: Path, patterns: tuple[str, ...]) -> list[Path]:
    paths: list[Path] = []
    for pattern in patterns:
        paths.extend(path for path in root.glob(pattern) if path.is_file())
    return sorted(set(paths))


def find_allen_nwb_samples_v518(root: str | Path = ".") -> list[Path]:
    return _files(Path(root).resolve(), ALLEN_NWB_PATTERNS)


def find_allen_manifest_assets_v518(root: str | Path = ".") -> list[Path]:
    return _files(Path(root).resolve(), ALLEN_MANIFEST_PATTERNS)


def _relative_paths(paths: list[Path], root: Path) -> list[str]:
    return [str(path.relative_to(root)).replace("\\", "/") for path in paths[:20]]


def _package_available(package_name: str) -> bool:
    return importlib.util.find_spec(package_name) is not None


def orientation_candidate_signals_v518(candidates: list[dict[str, Any]]) -> list[str]:
    signals: list[str] = []
    for candidate in candidates:
        haystack = [str(candidate.get("path", "")), str(candidate.get("kind", ""))]
        haystack.extend(str(key) for key in candidate.get("keys", []) or [])
        joined = " ".join(haystack).lower()
        if any(term in joined for term in ORIENTATION_TERMS):
            label = str(candidate.get("path") or candidate.get("kind") or "orientation_candidate")
            if label not in signals:
                signals.append(label)
    return signals


def validate_allen_orientation_nwb_v518(nwb_path: str | Path) -> dict[str, Any]:
    path = Path(nwb_path)
    blockers: list[str] = []
    units: dict[str, Any] = {}
    structure: dict[str, Any] = {}
    candidates: list[dict[str, Any]] = []
    if not path.exists():
        blockers.append("Allen NWB file missing")
    else:
        try:
            units = inspect_nwb_units(path)
        except Exception as exc:
            blockers.append(f"failed to inspect units: {exc}")
            units = {"exists": True, "has_units": False}
        try:
            structure = inspect_nwb_structure(path, max_depth=4, max_items=900)
        except Exception as exc:
            blockers.append(f"failed to inspect structure: {exc}")
            structure = {}
        try:
            candidates = candidates_as_dict(discover_stimulus_tables(path))
        except Exception as exc:
            blockers.append(f"failed to discover stimulus tables: {exc}")
            candidates = []
    orientation_signals = orientation_candidate_signals_v518(candidates)
    if not units.get("has_units"):
        blockers.append("/units spike_times table missing")
    if not structure.get("has_stimulus"):
        blockers.append("/stimulus group missing")
    if not orientation_signals:
        blockers.append("orientation stimulus metadata not identified")
    gate_status = "allen_orientation_sample_validated" if not blockers else "allen_orientation_sample_incomplete"
    report = AllenOrientationSampleReportV518(
        path=str(path),
        gate_status=gate_status,
        file_size_bytes=path.stat().st_size if path.exists() else 0,
        has_units=bool(units.get("has_units")),
        unit_count=int(units.get("unit_count_from_index") or 0),
        spike_times_count=int(units.get("spike_times_count") or 0),
        has_intervals=bool(structure.get("has_intervals")),
        has_trials=bool(structure.get("has_trials")),
        has_stimulus=bool(structure.get("has_stimulus")),
        stimulus_candidate_count=len(candidates),
        orientation_candidate_count=len(orientation_signals),
        selected_orientation_signal=orientation_signals[0] if orientation_signals else None,
        blockers=tuple(blockers),
    )
    return {"report": report.to_dict(), "units": units, "structure": structure, "stimulus_table_candidates": candidates, "orientation_signals": orientation_signals}


def build_allen_orientation_gate_v518(root: str | Path = ".") -> dict[str, Any]:
    project_root = Path(root).resolve()
    nwb_paths = find_allen_nwb_samples_v518(project_root)
    manifest_paths = find_allen_manifest_assets_v518(project_root)
    sample_reports = [validate_allen_orientation_nwb_v518(path) for path in nwb_paths]
    reports = [item["report"] for item in sample_reports]
    valid_reports = [report for report in reports if report["gate_status"] == "allen_orientation_sample_validated"]
    if valid_reports:
        overall_status = "allen_orientation_sample_validated"
    elif nwb_paths:
        overall_status = "allen_nwb_present_needs_orientation_validation"
    elif manifest_paths:
        overall_status = "allen_manifest_present_needs_nwb_download"
    else:
        overall_status = "allen_orientation_sample_missing_download_required"
    return {
        "version": "v5.18",
        "phase": "allen_visual_coding_orientation_gate",
        "overall_status": overall_status,
        "active_phase": "biosdk_public_core",
        "bic_os_phase_locked": True,
        "nwb_sample_count": len(nwb_paths),
        "manifest_asset_count": len(manifest_paths),
        "validated_sample_count": len(valid_reports),
        "allensdk_available": _package_available("allensdk"),
        "pynwb_available": _package_available("pynwb"),
        "local_nwb_paths_sample": _relative_paths(nwb_paths, project_root),
        "local_manifest_paths_sample": _relative_paths(manifest_paths, project_root),
        "sample_reports": reports,
        "download_plan": {
            "target_directory": "data/external/allen/",
            "preferred_asset": "one small Allen Brain Observatory / visual-coding NWB or AllenSDK cache slice with drifting/static grating orientation metadata",
            "avoid": "full Allen cache download by default",
            "validation_command": "powershell -ExecutionPolicy Bypass -File scripts/run_biogpu_v518_allen_orientation_gate.ps1",
        },
        "required_next_steps": [
            "select one small Allen visual-coding session with orientation stimulus metadata",
            "place the NWB or cache manifest under data/external/allen/",
            "run the v5.18 gate to inspect units, stimulus tables and orientation labels",
            "do not claim multi-dataset BioSDK proof until at least one Allen sample validates",
        ],
        "claim_boundary": "v5.18 validates local Allen orientation sample readiness only. Without a real Allen NWB/cache slice, it is a download/intake gate, not external neurophysiology proof.",
    }


def write_allen_orientation_outputs_v518(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, str]:
    project_root = Path(root).resolve()
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    gate = build_allen_orientation_gate_v518(project_root)
    detailed = [validate_allen_orientation_nwb_v518(path) for path in find_allen_nwb_samples_v518(project_root)]
    paths = {
        "summary_json": out / "V518_ALLEN_ORIENTATION_GATE_SUMMARY.json",
        "sample_reports_json": out / "V518_ALLEN_ORIENTATION_SAMPLE_REPORTS.json",
        "asset_manifest_csv": out / "V518_ALLEN_ORIENTATION_ASSET_MANIFEST.csv",
        "download_plan_json": out / "V518_ALLEN_ORIENTATION_DOWNLOAD_PLAN.json",
        "markdown_report": out / "BIOGPU_V518_ALLEN_ORIENTATION_GATE_REPORT.md",
    }
    paths["summary_json"].write_text(json.dumps(gate, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["sample_reports_json"].write_text(json.dumps({"samples": detailed}, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["download_plan_json"].write_text(json.dumps(gate["download_plan"], indent=2, ensure_ascii=False), encoding="utf-8")
    _write_asset_manifest_csv(paths["asset_manifest_csv"], project_root)
    paths["markdown_report"].write_text(_markdown_report(gate), encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}


def _write_asset_manifest_csv(path: Path, root: Path) -> None:
    fields = ["asset_kind", "path", "size_bytes"]
    assets = [("nwb", item) for item in find_allen_nwb_samples_v518(root)] + [("manifest", item) for item in find_allen_manifest_assets_v518(root)]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for kind, asset_path in assets:
            writer.writerow({"asset_kind": kind, "path": str(asset_path.relative_to(root)).replace("\\", "/"), "size_bytes": asset_path.stat().st_size})


def _markdown_report(gate: dict[str, Any]) -> str:
    lines = [
        "# BioGPU-Core v5.18 Allen Orientation Gate",
        "",
        f"- Overall status: `{gate['overall_status']}`",
        f"- NWB samples: `{gate['nwb_sample_count']}`",
        f"- Manifest assets: `{gate['manifest_asset_count']}`",
        f"- Validated samples: `{gate['validated_sample_count']}`",
        f"- AllenSDK available: `{gate['allensdk_available']}`",
        f"- BiC OS locked: `{gate['bic_os_phase_locked']}`",
        "",
        "## Required Next Steps",
        "",
    ]
    for step in gate["required_next_steps"]:
        lines.append(f"- {step}")
    lines.extend(["", "## Boundary", "", gate["claim_boundary"], ""])
    return "\n".join(lines)
