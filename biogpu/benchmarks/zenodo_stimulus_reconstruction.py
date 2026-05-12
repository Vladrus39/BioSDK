from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from biogpu.data_ingest.zenodo_stimulus_reconstruction import (
    assess_pulse_window_availability,
    reconstruct_recording_level_windows,
    summarize_reconstructed_windows,
    write_windows_csv,
)


def run_zenodo_stimulus_reconstruction(root_path: str, output_dir: str | None = None) -> dict[str, Any]:
    windows = reconstruct_recording_level_windows(root_path)
    summary = summarize_reconstructed_windows(windows)
    pulse_assessment = assess_pulse_window_availability(root_path)
    result = {
        "benchmark": "zenodo_14363732_stimulus_window_reconstruction",
        "root_path": root_path,
        "summary": summary,
        "pulse_assessment": pulse_assessment,
    }
    if output_dir:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        write_windows_csv(windows, out / "recording_level_stimulus_windows.csv")
        (out / "stimulus_window_reconstruction.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        report = [
            "# Zenodo 14363732 stimulus-window reconstruction",
            "",
            "## Summary",
            "",
            f"- Recording-level windows: {summary['window_count']}",
            f"- Conditions: {summary['by_condition']}",
            f"- Window quality: {summary['by_quality']}",
            f"- Light spots: {summary['light_spots']}",
            f"- Stimulation electrodes: {summary['stimulation_electrodes']}",
            "",
            "## Honesty conclusion",
            "",
            pulse_assessment["conclusion"],
            "",
            "The uploaded `Pre_processed_MEA_data.zip` allows exact reconstruction of full-recording condition windows, because each recording has duration and stimulation condition metadata. It does not expose pulse-level TTL/onset/offset timing, so exact per-pulse windows require raw HDF5 trigger channels or the original stimulation protocol.",
        ]
        (out / "STIMULUS_WINDOW_RECONSTRUCTION_REPORT.md").write_text("\n".join(report), encoding="utf-8")
    return result
