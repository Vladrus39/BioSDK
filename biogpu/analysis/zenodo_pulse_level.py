from __future__ import annotations

import csv
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np

from biogpu.data_ingest.zenodo_mea2100_preprocessed import (
    discover_recording_dirs,
    parse_electrode_number,
    read_metadata,
    read_sample_num_csv,
)
from biogpu.data_ingest.zenodo_protocol_windows import (
    ProtocolStimulusWindow,
    discover_protocol_windows,
    read_protocol_windows_for_recording,
    summarize_protocol_windows,
    write_protocol_windows_csv,
)
from biogpu.data_ingest.zenodo_stimulus_reconstruction import normalize_condition


def electrode_xy(e: int) -> tuple[int, int]:
    return int(e) // 10, int(e) % 10


def electrode_distance(a: int, b: int, metric: str = "manhattan") -> float:
    ar, ac = electrode_xy(a)
    br, bc = electrode_xy(b)
    if metric == "euclidean":
        return float(math.sqrt((ar - br) ** 2 + (ac - bc) ** 2))
    return float(abs(ar - br) + abs(ac - bc))


@dataclass
class RecordingPulseResponse:
    recording_path: str
    culture: str
    date: str
    condition: str
    target_id: int | None
    target_type: str
    pulse_count: int
    stimulus_duration_ms_mean: float
    response_window_ms: float
    electrodes_analyzed: int
    target_electrode_present: bool
    target_exact_delta_rate_hz: float | None
    target_response_delta_rate_hz: float | None
    target_response_percentile: float | None
    best_response_electrode: int | None
    best_response_delta_rate_hz: float | None
    mean_response_delta_rate_hz: float
    median_response_delta_rate_hz: float
    near_mean_response_delta_rate_hz: float | None
    far_mean_response_delta_rate_hz: float | None
    target_pulse_fraction_response_gt_pre: float | None
    target_pulse_mean_response_count_delta: float | None
    exact_window_note: str


def _load_spike_seconds_by_electrode(recording_dir: str | Path) -> tuple[dict[int, np.ndarray], float, float]:
    rec = Path(recording_dir)
    meta = read_metadata(rec)
    hz = float(meta.get("sampling_fr_hz") or 20000.0)
    duration_s = float(meta.get("recording_duration_sec") or 0.0)
    spikes: dict[int, np.ndarray] = {}
    for f in sorted(rec.glob("electrode*.csv")):
        eid = parse_electrode_number(f)
        samples = read_sample_num_csv(f)
        arr = np.asarray(samples, dtype=float) / hz if samples else np.asarray([], dtype=float)
        spikes[eid] = np.sort(arr)
    return spikes, hz, duration_s


def _count_ranges(times: np.ndarray, starts: np.ndarray, ends: np.ndarray) -> np.ndarray:
    left = np.searchsorted(times, starts, side="left")
    right = np.searchsorted(times, ends, side="left")
    return right - left


def _safe_rate(counts: np.ndarray, durations: np.ndarray) -> float:
    total_t = float(np.sum(durations))
    if total_t <= 0:
        return 0.0
    return float(np.sum(counts) / total_t)


def _percentile_rank(values: np.ndarray, value: float) -> float:
    if len(values) == 0 or np.isnan(value):
        return float("nan")
    return float(np.sum(values <= value) / len(values) * 100.0)


def _summarize_recording(
    rec: Path,
    root: Path,
    response_window_s: float = 0.100,
) -> RecordingPulseResponse | None:
    windows = read_protocol_windows_for_recording(rec, root)
    if not windows:
        return None
    spikes_by_electrode, _hz, duration_s = _load_spike_seconds_by_electrode(rec)
    if not spikes_by_electrode:
        return None

    starts = np.asarray([w.start_s for w in windows], dtype=float)
    ends = np.asarray([w.end_s for w in windows], dtype=float)
    stim_durations = np.maximum(ends - starts, 0.0)
    valid_exact = stim_durations > 0
    starts = starts[valid_exact]
    ends = ends[valid_exact]
    stim_durations = stim_durations[valid_exact]
    if len(starts) == 0:
        return None

    # Exact stimulus window: compare [start, end] with immediately preceding same-duration window.
    exact_pre_starts = np.maximum(0.0, starts - stim_durations)
    exact_pre_ends = starts
    exact_pre_durations = np.maximum(exact_pre_ends - exact_pre_starts, 0.0)

    # Biological response window: compare [end, end + response_window] with equally long pre-onset window.
    response_starts = ends
    response_ends = np.minimum(duration_s, ends + response_window_s) if duration_s > 0 else ends + response_window_s
    response_durations = np.maximum(response_ends - response_starts, 0.0)
    response_pre_starts = np.maximum(0.0, starts - response_durations)
    response_pre_ends = starts
    response_pre_durations = np.maximum(response_pre_ends - response_pre_starts, 0.0)

    exact_deltas: dict[int, float] = {}
    response_deltas: dict[int, float] = {}
    response_count_delta_by_electrode: dict[int, np.ndarray] = {}
    for eid, times in spikes_by_electrode.items():
        exact_pre = _count_ranges(times, exact_pre_starts, exact_pre_ends)
        exact_stim = _count_ranges(times, starts, ends)
        exact_deltas[eid] = _safe_rate(exact_stim, stim_durations) - _safe_rate(exact_pre, exact_pre_durations)

        resp_pre = _count_ranges(times, response_pre_starts, response_pre_ends)
        resp = _count_ranges(times, response_starts, response_ends)
        response_deltas[eid] = _safe_rate(resp, response_durations) - _safe_rate(resp_pre, response_pre_durations)
        response_count_delta_by_electrode[eid] = resp - resp_pre

    target = windows[0].target_id
    target_type = windows[0].target_type
    response_vals = np.asarray(list(response_deltas.values()), dtype=float)
    exact_vals = np.asarray(list(exact_deltas.values()), dtype=float)
    best_eid = None
    best_delta = None
    if response_deltas:
        best_eid = max(response_deltas, key=response_deltas.get)
        best_delta = float(response_deltas[best_eid])

    target_present = target in response_deltas if target is not None else False
    target_exact_delta = float(exact_deltas[target]) if target_present else None
    target_response_delta = float(response_deltas[target]) if target_present else None
    target_percentile = _percentile_rank(response_vals, target_response_delta) if target_present else None

    near_mean = None
    far_mean = None
    if target is not None:
        near = [v for e, v in response_deltas.items() if electrode_distance(int(target), int(e)) <= 1]
        far = [v for e, v in response_deltas.items() if electrode_distance(int(target), int(e)) >= 3]
        near_mean = float(np.mean(near)) if near else None
        far_mean = float(np.mean(far)) if far else None

    frac_gt = None
    mean_count_delta = None
    if target_present:
        deltas = response_count_delta_by_electrode[int(target)]
        frac_gt = float(np.mean(deltas > 0)) if len(deltas) else None
        mean_count_delta = float(np.mean(deltas)) if len(deltas) else None

    return RecordingPulseResponse(
        recording_path=str(rec.relative_to(root)),
        culture=windows[0].culture,
        date=windows[0].date,
        condition=windows[0].condition,
        target_id=target,
        target_type=target_type,
        pulse_count=len(starts),
        stimulus_duration_ms_mean=float(np.mean(stim_durations) * 1000.0),
        response_window_ms=float(response_window_s * 1000.0),
        electrodes_analyzed=len(spikes_by_electrode),
        target_electrode_present=bool(target_present),
        target_exact_delta_rate_hz=target_exact_delta,
        target_response_delta_rate_hz=target_response_delta,
        target_response_percentile=target_percentile,
        best_response_electrode=best_eid,
        best_response_delta_rate_hz=best_delta,
        mean_response_delta_rate_hz=float(np.mean(response_vals)) if len(response_vals) else 0.0,
        median_response_delta_rate_hz=float(np.median(response_vals)) if len(response_vals) else 0.0,
        near_mean_response_delta_rate_hz=near_mean,
        far_mean_response_delta_rate_hz=far_mean,
        target_pulse_fraction_response_gt_pre=frac_gt,
        target_pulse_mean_response_count_delta=mean_count_delta,
        exact_window_note=(
            "exact_delta uses protocol [start,end] vs same-length pre-window; "
            "response_delta uses [end,end+response_window] vs same-length pre-onset window"
        ),
    )


def analyze_pulse_responses(
    root_path: str | Path,
    response_window_ms: float = 100.0,
) -> list[RecordingPulseResponse]:
    root = Path(root_path)
    response_window_s = float(response_window_ms) / 1000.0
    rows: list[RecordingPulseResponse] = []
    for rec in discover_recording_dirs(root):
        summary = _summarize_recording(rec, root, response_window_s=response_window_s)
        if summary is not None:
            rows.append(summary)
    return rows


def pulse_response_summary(rows: list[RecordingPulseResponse]) -> dict[str, Any]:
    by_condition: dict[str, int] = {}
    pulses_by_condition: dict[str, int] = {}
    for r in rows:
        by_condition[r.condition] = by_condition.get(r.condition, 0) + 1
        pulses_by_condition[r.condition] = pulses_by_condition.get(r.condition, 0) + int(r.pulse_count)

    valid = [r for r in rows if r.target_electrode_present and r.target_response_delta_rate_hz is not None]
    light = [r for r in valid if r.condition == "lightstim"]
    elec = [r for r in valid if r.condition == "elecstim"]

    def _stats(sub: list[RecordingPulseResponse]) -> dict[str, Any]:
        deltas = [float(r.target_response_delta_rate_hz) for r in sub if r.target_response_delta_rate_hz is not None]
        percentiles = [float(r.target_response_percentile) for r in sub if r.target_response_percentile is not None]
        frac = [float(r.target_pulse_fraction_response_gt_pre) for r in sub if r.target_pulse_fraction_response_gt_pre is not None]
        exact = [float(r.target_exact_delta_rate_hz) for r in sub if r.target_exact_delta_rate_hz is not None]
        return {
            "recordings": len(sub),
            "mean_target_response_delta_rate_hz": float(np.mean(deltas)) if deltas else None,
            "median_target_response_delta_rate_hz": float(np.median(deltas)) if deltas else None,
            "median_target_response_percentile": float(np.median(percentiles)) if percentiles else None,
            "mean_target_pulse_fraction_response_gt_pre": float(np.mean(frac)) if frac else None,
            "median_target_exact_delta_rate_hz": float(np.median(exact)) if exact else None,
        }

    return {
        "task": "pulse_aligned_stimulus_response_analysis",
        "recordings_with_protocols": len(rows),
        "by_condition_recordings": by_condition,
        "by_condition_pulses": pulses_by_condition,
        "target_electrode_present_count": len(valid),
        "lightstim": _stats(light),
        "elecstim": _stats(elec),
        "honesty_note": "Uses exact stimulation_protocols CSV windows from the preprocessed archive. This is a real pulse-aligned analysis, not synthetic labeling. Raw HDF5/TTL should still be inspected as independent verification before publication-grade claims.",
    }


def write_recording_summary_csv(rows: list[RecordingPulseResponse], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(asdict(rows[0]).keys()) if rows else [f.name for f in RecordingPulseResponse.__dataclass_fields__.values()]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(asdict(r))


def _write_plots(rows: list[RecordingPulseResponse], out: Path) -> None:
    try:
        import matplotlib.pyplot as plt
    except Exception:
        return
    valid = [r for r in rows if r.target_electrode_present and r.target_response_delta_rate_hz is not None]
    if not valid:
        return

    percentiles = [float(r.target_response_percentile) for r in valid if r.target_response_percentile is not None]
    if percentiles:
        plt.figure(figsize=(7, 4))
        plt.hist(percentiles, bins=12)
        plt.xlabel("Target electrode response percentile")
        plt.ylabel("Recordings")
        plt.title("Pulse-aligned target response percentile")
        plt.tight_layout()
        plt.savefig(out / "pulse_target_response_percentile_hist.png", dpi=150)
        plt.close()

    xs = []
    ys = []
    for r in valid:
        if r.target_id is not None and r.target_response_delta_rate_hz is not None:
            xs.append(int(r.target_id))
            ys.append(float(r.target_response_delta_rate_hz))
    if xs:
        plt.figure(figsize=(8, 4))
        plt.scatter(xs, ys)
        plt.xlabel("Target / spot electrode")
        plt.ylabel("Target response delta rate, Hz")
        plt.title("Pulse-aligned target response delta by spot")
        plt.tight_layout()
        plt.savefig(out / "pulse_target_response_delta_by_spot.png", dpi=150)
        plt.close()

    near = [r.near_mean_response_delta_rate_hz for r in valid if r.near_mean_response_delta_rate_hz is not None]
    far = [r.far_mean_response_delta_rate_hz for r in valid if r.far_mean_response_delta_rate_hz is not None]
    if near and far:
        plt.figure(figsize=(6, 4))
        plt.boxplot([near, far], labels=["distance <= 1", "distance >= 3"])
        plt.ylabel("Mean response delta rate, Hz")
        plt.title("Pulse-aligned spatial response: near vs far")
        plt.tight_layout()
        plt.savefig(out / "pulse_near_vs_far_response_delta.png", dpi=150)
        plt.close()


def render_markdown_report(
    protocol_summary: dict[str, Any],
    response_summary: dict[str, Any],
    response_window_ms: float,
) -> str:
    return f"""# Zenodo 14363732 — Pulse-level stimulation-window analysis v1.3

## What changed from v1.2

v1.2 correctly moved the project to real spike data, but it was too conservative about the uploaded preprocessed archive.
After inspecting the actual archive, the `stimulation_protocols/*_stimulation_protocol.csv` files were found. They contain explicit `start`, `end`, and `target` columns.

Therefore, Zenodo 14363732 can now be used for a first honest pulse-level benchmark directly from the preprocessed archive.

## Protocol-window discovery

```json
{json.dumps(protocol_summary, indent=2, ensure_ascii=False)}
```

## Pulse-aligned response analysis

Response window used after stimulus end: `{response_window_ms}` ms.

```json
{json.dumps(response_summary, indent=2, ensure_ascii=False)}
```

## Interpretation

- `stimulus_windows.csv` is now pulse-level, not recording-level.
- `target_exact_delta_rate_hz` compares spikes inside the exact protocol `[start,end]` window with an immediately preceding same-duration pre-window.
- `target_response_delta_rate_hz` compares spikes in `[end,end+response_window]` with a same-duration pre-onset window.
- For LightStim this is more biologically useful than exact-window counts, because spikes may occur after the light pulse window.
- For ElecStim the exact window is very short, so the post-stimulus response window is the safer first-pass signal.

## Honesty note

This is real pulse-aligned evidence from the uploaded preprocessed dataset. It is still not a full BioGPU advantage claim. The next publication-grade step is independent raw HDF5/TTL verification plus a true task/readout benchmark with train/test splits across cultures/sessions.
"""


def write_outputs(
    root_path: str | Path,
    out_dir: str | Path,
    response_window_ms: float = 100.0,
) -> dict[str, Any]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    windows = discover_protocol_windows(root_path)
    write_protocol_windows_csv(windows, out / "stimulus_windows.csv")
    protocol_summary = summarize_protocol_windows(windows)

    rows = analyze_pulse_responses(root_path, response_window_ms=response_window_ms)
    write_recording_summary_csv(rows, out / "pulse_response_by_recording.csv")
    response_summary = pulse_response_summary(rows)
    with (out / "pulse_response_summary.json").open("w", encoding="utf-8") as f:
        json.dump(response_summary, f, indent=2, ensure_ascii=False)
    with (out / "protocol_windows_summary.json").open("w", encoding="utf-8") as f:
        json.dump(protocol_summary, f, indent=2, ensure_ascii=False)
    (out / "PULSE_LEVEL_ANALYSIS_REPORT.md").write_text(
        render_markdown_report(protocol_summary, response_summary, response_window_ms),
        encoding="utf-8",
    )
    _write_plots(rows, out)
    return {
        "protocol_summary": protocol_summary,
        "pulse_response_summary": response_summary,
    }
