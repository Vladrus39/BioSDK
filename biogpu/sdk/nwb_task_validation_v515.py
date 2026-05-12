"""BioSDK DANDI/NWB task sample validation, v5.15."""
from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from biogpu.data_ingest.dandi_nwb import inspect_nwb_units
from biogpu.data_ingest.nwb_stimulus_discovery import (
    build_windows_from_simple_intervals,
    candidates_as_dict,
    discover_stimulus_tables,
    inspect_nwb_structure,
)


DEFAULT_OUT = Path("outputs/v515_dandi_nwb_task_validation")
DEFAULT_NWB_PATTERNS = ("data/external/nwb/**/*.nwb", "data/external/dandi/**/*.nwb")


@dataclass(frozen=True)
class NWBTaskValidationV515:
    nwb_path: str
    gate_status: str
    has_units: bool
    unit_count: int
    spike_times_count: int
    has_intervals: bool
    has_trials: bool
    has_stimulus: bool
    stimulus_candidate_count: int
    selected_interval_path: str | None
    selected_label_column: str | None
    exported_window_count: int
    blockers: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def find_local_nwb_samples_v515(root: str | Path = ".") -> list[Path]:
    project_root = Path(root).resolve()
    paths: list[Path] = []
    for pattern in DEFAULT_NWB_PATTERNS:
        paths.extend(path for path in project_root.glob(pattern) if path.is_file())
    return sorted(set(paths))


def _choose_interval_and_label(candidates: list[dict[str, Any]]) -> tuple[str | None, str | None]:
    interval_candidates = [item for item in candidates if item.get("kind") == "interval_table" and item.get("row_count")]
    if not interval_candidates:
        return None, None
    selected = sorted(interval_candidates, key=lambda item: int(item.get("row_count") or 0), reverse=True)[0]
    keys = list(selected.get("keys") or [])
    preferred_labels = (
        "loads",
        "response_accuracy",
        "probe_in_out",
        "loadsProbe_PicIDs",
        "loadsEnc1_PicIDs",
        "loadsEnc2_PicIDs",
        "loadsEnc3_PicIDs",
    )
    label = next((name for name in preferred_labels if name in keys), None)
    if label is None:
        label = next((name for name in keys if "label" in name.lower() or "stim" in name.lower() or "condition" in name.lower()), None)
    return str(selected.get("path")), label


def validate_nwb_task_sample_v515(nwb_path: str | Path) -> dict[str, Any]:
    path = Path(nwb_path)
    units = inspect_nwb_units(path)
    structure = inspect_nwb_structure(path, max_depth=4, max_items=800)
    candidates = candidates_as_dict(discover_stimulus_tables(path))
    interval_path, label_column = _choose_interval_and_label(candidates)
    windows: list[dict[str, Any]] = []
    blockers: list[str] = []

    if not units.get("exists"):
        blockers.append("NWB file missing")
    if not units.get("has_units"):
        blockers.append("/units spike_times table missing")
    if not structure.get("has_intervals"):
        blockers.append("/intervals group missing")
    if not structure.get("has_trials"):
        blockers.append("/intervals/trials table missing")
    if not structure.get("has_stimulus"):
        blockers.append("/stimulus group missing")
    if interval_path is None:
        blockers.append("no interval table with row_count found")

    if interval_path is not None:
        try:
            windows = build_windows_from_simple_intervals(path, interval_path, label_column=label_column)
        except Exception as exc:
            blockers.append(f"failed to export simple interval windows: {exc}")

    unit_count = int(units.get("unit_count_from_index") or 0)
    spike_times_count = int(units.get("spike_times_count") or 0)
    exported_window_count = len(windows)
    if exported_window_count == 0:
        blockers.append("no task windows exported")

    gate_status = "dandi_nwb_task_sample_validated" if not blockers and unit_count > 0 and spike_times_count > 0 else "dandi_nwb_task_sample_incomplete"
    validation = NWBTaskValidationV515(
        nwb_path=str(path),
        gate_status=gate_status,
        has_units=bool(units.get("has_units")),
        unit_count=unit_count,
        spike_times_count=spike_times_count,
        has_intervals=bool(structure.get("has_intervals")),
        has_trials=bool(structure.get("has_trials")),
        has_stimulus=bool(structure.get("has_stimulus")),
        stimulus_candidate_count=len(candidates),
        selected_interval_path=interval_path,
        selected_label_column=label_column,
        exported_window_count=exported_window_count,
        blockers=tuple(blockers),
    )
    return {
        "validation": validation.to_dict(),
        "units": units,
        "structure": structure,
        "stimulus_table_candidates": candidates,
        "windows": windows,
    }


def build_dandi_nwb_task_validation_gate_v515(root: str | Path = ".") -> dict[str, Any]:
    project_root = Path(root).resolve()
    samples = find_local_nwb_samples_v515(project_root)
    validations = [validate_nwb_task_sample_v515(path) for path in samples]
    valid = [item for item in validations if item["validation"].get("gate_status") == "dandi_nwb_task_sample_validated"]
    total_windows = sum(int(item["validation"].get("exported_window_count") or 0) for item in validations)
    total_units = sum(int(item["validation"].get("unit_count") or 0) for item in validations)
    total_spikes = sum(int(item["validation"].get("spike_times_count") or 0) for item in validations)
    if valid:
        overall_status = "dandi_nwb_task_sample_validated"
    elif samples:
        overall_status = "dandi_nwb_samples_present_but_incomplete"
    else:
        overall_status = "dandi_nwb_sample_missing"
    return {
        "version": "v5.15",
        "phase": "dandi_nwb_task_sample_validation",
        "overall_status": overall_status,
        "active_phase": "biosdk_public_core",
        "bic_os_phase_locked": True,
        "nwb_sample_count": len(samples),
        "validated_sample_count": len(valid),
        "total_unit_count": total_units,
        "total_spike_times_count": total_spikes,
        "total_exported_window_count": total_windows,
        "validations": [item["validation"] for item in validations],
        "claim_boundary": "v5.15 validates DANDI/NWB parser portability and task-window export for local samples only; it does not prove full multi-dataset BioSDK or BiC OS readiness.",
    }


def write_dandi_nwb_task_outputs_v515(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, str]:
    project_root = Path(root).resolve()
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    samples = find_local_nwb_samples_v515(project_root)
    detailed = [validate_nwb_task_sample_v515(path) for path in samples]
    gate = build_dandi_nwb_task_validation_gate_v515(project_root)
    paths = {
        "summary_json": out / "V515_DANDI_NWB_TASK_VALIDATION_SUMMARY.json",
        "sample_reports_json": out / "V515_DANDI_NWB_SAMPLE_REPORTS.json",
        "task_windows_csv": out / "V515_DANDI_NWB_TASK_WINDOWS.csv",
        "markdown_report": out / "BIOGPU_V515_DANDI_NWB_TASK_VALIDATION_REPORT.md",
    }
    paths["summary_json"].write_text(json.dumps(gate, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["sample_reports_json"].write_text(json.dumps({"samples": detailed}, indent=2, ensure_ascii=False), encoding="utf-8")
    _write_windows_csv(paths["task_windows_csv"], detailed)
    paths["markdown_report"].write_text(_markdown_report(gate), encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}


def _write_windows_csv(path: Path, reports: list[dict[str, Any]]) -> None:
    fields = ["nwb_path", "stimulus_id", "start_s", "end_s", "label", "split", "source_interval_path"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for report in reports:
            nwb_path = report["validation"]["nwb_path"]
            for window in report.get("windows", []):
                row = {field: window.get(field) for field in fields}
                row["nwb_path"] = nwb_path
                writer.writerow(row)


def _markdown_report(gate: dict[str, Any]) -> str:
    lines = [
        "# BioGPU-Core v5.15 DANDI/NWB Task Validation",
        "",
        f"- Overall status: `{gate['overall_status']}`",
        f"- Samples: `{gate['validated_sample_count']}/{gate['nwb_sample_count']}` validated",
        f"- Units: `{gate['total_unit_count']}`",
        f"- Spike times: `{gate['total_spike_times_count']}`",
        f"- Exported task windows: `{gate['total_exported_window_count']}`",
        f"- BiC OS locked: `{gate['bic_os_phase_locked']}`",
        "",
        "## Samples",
        "",
    ]
    for item in gate["validations"]:
        lines.append(
            f"- `{item['nwb_path']}`: `{item['gate_status']}`, units `{item['unit_count']}`, windows `{item['exported_window_count']}`"
        )
    lines.extend(["", "## Boundary", "", gate["claim_boundary"], ""])
    return "\n".join(lines)
