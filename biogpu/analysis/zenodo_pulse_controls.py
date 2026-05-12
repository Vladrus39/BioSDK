from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np

from biogpu.analysis.zenodo_pulse_level import (
    _count_ranges,
    _load_spike_seconds_by_electrode,
    _percentile_rank,
    _safe_rate,
    electrode_distance,
)
from biogpu.data_ingest.zenodo_mea2100_preprocessed import discover_recording_dirs, read_metadata, read_sample_num_csv
from biogpu.data_ingest.zenodo_protocol_windows import read_protocol_windows_for_recording


@dataclass
class ElectrodePulseResponse:
    recording_path: str
    culture: str
    date: str
    condition: str
    target_id: int | None
    electrode_id: int
    is_target: bool
    distance_to_target: float | None
    pulse_count: int
    response_window_ms: float
    response_delta_rate_hz: float
    response_percentile: float


@dataclass
class RecordingControlResult:
    recording_path: str
    culture: str
    date: str
    condition: str
    target_id: int | None
    pulse_count: int
    electrodes_analyzed: int
    target_electrode_present: bool
    target_response_delta_rate_hz: float | None
    target_response_percentile: float | None
    random_electrode_delta_mean_hz: float | None
    random_electrode_delta_median_hz: float | None
    random_electrode_percentile_mean: float | None
    random_electrode_percentile_median: float | None
    near_mean_delta_hz: float | None
    far_mean_delta_hz: float | None
    near_minus_far_delta_hz: float | None


def _window_arrays(windows: list[Any], duration_s: float, response_window_s: float) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    starts = np.asarray([float(w.start_s) for w in windows], dtype=float)
    ends = np.asarray([float(w.end_s) for w in windows], dtype=float)
    durations = np.maximum(ends - starts, 0.0)
    valid = durations > 0
    starts = starts[valid]
    ends = ends[valid]
    durations = durations[valid]

    response_starts = ends
    response_ends = np.minimum(duration_s, ends + response_window_s) if duration_s > 0 else ends + response_window_s
    response_durations = np.maximum(response_ends - response_starts, 0.0)
    response_pre_starts = np.maximum(0.0, starts - response_durations)
    response_pre_ends = starts
    response_pre_durations = np.maximum(response_pre_ends - response_pre_starts, 0.0)
    return response_starts, response_ends, response_pre_starts, response_pre_ends, response_durations, response_pre_durations


def _response_delta_for_times(
    times: np.ndarray,
    response_starts: np.ndarray,
    response_ends: np.ndarray,
    response_pre_starts: np.ndarray,
    response_pre_ends: np.ndarray,
    response_durations: np.ndarray,
    response_pre_durations: np.ndarray | None = None,
) -> float:
    resp_pre = _count_ranges(times, response_pre_starts, response_pre_ends)
    resp = _count_ranges(times, response_starts, response_ends)
    if response_pre_durations is None:
        response_pre_durations = response_durations
    return _safe_rate(resp, response_durations) - _safe_rate(resp_pre, response_pre_durations)


def compute_electrode_pulse_responses(
    recording_dir: str | Path,
    root_path: str | Path,
    response_window_ms: float = 100.0,
) -> list[ElectrodePulseResponse]:
    """Compute pulse-aligned post-stimulus response delta for every electrode in one recording.

    The delta is: rate([stim_end, stim_end + response_window]) minus rate([stim_start - response_window, stim_start]).
    The percentile is within-recording rank of the electrode delta. A true target response should beat
    same-recording non-target electrodes if the protocol target is biologically meaningful.
    """
    rec = Path(recording_dir)
    root = Path(root_path)
    windows = read_protocol_windows_for_recording(rec, root)
    if not windows:
        return []
    spikes_by_electrode, _hz, duration_s = _load_spike_seconds_by_electrode(rec)
    if not spikes_by_electrode:
        return []

    response_window_s = float(response_window_ms) / 1000.0
    rs, re, ps, pe, rd, pd = _window_arrays(windows, duration_s, response_window_s)
    if len(rs) == 0:
        return []

    deltas: dict[int, float] = {}
    for eid, times in spikes_by_electrode.items():
        deltas[int(eid)] = _response_delta_for_times(times, rs, re, ps, pe, rd, pd)

    vals = np.asarray(list(deltas.values()), dtype=float)
    target = windows[0].target_id
    out: list[ElectrodePulseResponse] = []
    for eid, delta in sorted(deltas.items()):
        is_target = bool(target is not None and int(eid) == int(target))
        dist = float(electrode_distance(int(target), int(eid))) if target is not None else None
        out.append(
            ElectrodePulseResponse(
                recording_path=str(rec.relative_to(root)),
                culture=windows[0].culture,
                date=windows[0].date,
                condition=windows[0].condition,
                target_id=target,
                electrode_id=int(eid),
                is_target=is_target,
                distance_to_target=dist,
                pulse_count=len(rs),
                response_window_ms=float(response_window_ms),
                response_delta_rate_hz=float(delta),
                response_percentile=float(_percentile_rank(vals, float(delta))),
            )
        )
    return out


def analyze_all_electrode_responses(
    root_path: str | Path,
    response_window_ms: float = 100.0,
) -> list[ElectrodePulseResponse]:
    root = Path(root_path)
    out: list[ElectrodePulseResponse] = []
    for rec in discover_recording_dirs(root):
        out.extend(compute_electrode_pulse_responses(rec, root, response_window_ms=response_window_ms))
    return out


def summarize_recording_controls(rows: list[ElectrodePulseResponse]) -> list[RecordingControlResult]:
    by_rec: dict[str, list[ElectrodePulseResponse]] = {}
    for r in rows:
        by_rec.setdefault(r.recording_path, []).append(r)

    out: list[RecordingControlResult] = []
    for rec_path, sub in sorted(by_rec.items()):
        target_rows = [r for r in sub if r.is_target]
        target = target_rows[0] if target_rows else None
        non_target = [r for r in sub if not r.is_target]
        near = [r.response_delta_rate_hz for r in sub if r.distance_to_target is not None and r.distance_to_target <= 1]
        far = [r.response_delta_rate_hz for r in sub if r.distance_to_target is not None and r.distance_to_target >= 3]
        near_mean = float(np.mean(near)) if near else None
        far_mean = float(np.mean(far)) if far else None
        out.append(
            RecordingControlResult(
                recording_path=rec_path,
                culture=sub[0].culture,
                date=sub[0].date,
                condition=sub[0].condition,
                target_id=sub[0].target_id,
                pulse_count=sub[0].pulse_count,
                electrodes_analyzed=len(sub),
                target_electrode_present=bool(target),
                target_response_delta_rate_hz=float(target.response_delta_rate_hz) if target else None,
                target_response_percentile=float(target.response_percentile) if target else None,
                random_electrode_delta_mean_hz=float(np.mean([r.response_delta_rate_hz for r in non_target])) if non_target else None,
                random_electrode_delta_median_hz=float(np.median([r.response_delta_rate_hz for r in non_target])) if non_target else None,
                random_electrode_percentile_mean=float(np.mean([r.response_percentile for r in non_target])) if non_target else None,
                random_electrode_percentile_median=float(np.median([r.response_percentile for r in non_target])) if non_target else None,
                near_mean_delta_hz=near_mean,
                far_mean_delta_hz=far_mean,
                near_minus_far_delta_hz=(near_mean - far_mean) if near_mean is not None and far_mean is not None else None,
            )
        )
    return out


def _one_sided_high_p_value(observed: float, null_values: list[float]) -> float | None:
    clean = [float(v) for v in null_values if np.isfinite(v)]
    if not clean or not np.isfinite(observed):
        return None
    return float((1 + sum(v >= observed for v in clean)) / (len(clean) + 1))


def _two_sided_centered_p_value(observed: float, null_values: list[float], center: float | None = None) -> float | None:
    clean = [float(v) for v in null_values if np.isfinite(v)]
    if not clean or not np.isfinite(observed):
        return None
    c = float(np.median(clean) if center is None else center)
    obs_dev = abs(float(observed) - c)
    return float((1 + sum(abs(v - c) >= obs_dev for v in clean)) / (len(clean) + 1))


def random_electrode_null_distribution(
    recording_controls: list[RecordingControlResult],
    electrode_rows: list[ElectrodePulseResponse],
    n_permutations: int = 1000,
    seed: int = 13,
) -> list[dict[str, float]]:
    """Draw one same-recording non-target electrode per recording and aggregate null medians.

    This is stricter than pooling all electrodes because each permutation keeps the number of recordings
    fixed and avoids letting high-electrode-count recordings dominate the null distribution.
    """
    rng = np.random.default_rng(seed)
    by_rec: dict[str, list[ElectrodePulseResponse]] = {}
    for r in electrode_rows:
        if not r.is_target:
            by_rec.setdefault(r.recording_path, []).append(r)

    usable = [r for r in recording_controls if r.target_electrode_present and by_rec.get(r.recording_path)]
    out: list[dict[str, float]] = []
    for i in range(int(n_permutations)):
        ds: list[float] = []
        ps: list[float] = []
        for rec in usable:
            choice = rng.choice(by_rec[rec.recording_path])
            ds.append(float(choice.response_delta_rate_hz))
            ps.append(float(choice.response_percentile))
        if ds and ps:
            out.append(
                {
                    "permutation": float(i),
                    "median_random_electrode_delta_rate_hz": float(np.median(ds)),
                    "mean_random_electrode_delta_rate_hz": float(np.mean(ds)),
                    "median_random_electrode_percentile": float(np.median(ps)),
                    "mean_random_electrode_percentile": float(np.mean(ps)),
                }
            )
    return out


def _load_target_spike_seconds(recording_dir: str | Path, target_id: int) -> tuple[np.ndarray, float]:
    """Load only the target electrode spike train for fast random-time controls."""
    rec = Path(recording_dir)
    meta = read_metadata(rec)
    hz = float(meta.get("sampling_fr_hz") or 20000.0)
    duration_s = float(meta.get("recording_duration_sec") or 0.0)
    candidates = [rec / f"electrode{int(target_id):03d}.csv", rec / f"electrode{int(target_id)}.csv"]
    f = next((p for p in candidates if p.exists()), None)
    if f is None:
        return np.asarray([], dtype=float), duration_s
    samples = read_sample_num_csv(f)
    arr = np.asarray(samples, dtype=float) / hz if samples else np.asarray([], dtype=float)
    return np.sort(arr), duration_s


def _prepare_random_time_target_cache(
    root_path: str | Path,
    recording_controls: list[RecordingControlResult],
    response_window_ms: float,
) -> list[dict[str, Any]]:
    """Load target spike trains and protocol durations once for fast random-time controls."""
    root = Path(root_path)
    rec_by_rel = {str(p.relative_to(root)): p for p in discover_recording_dirs(root)}
    response_window_s = float(response_window_ms) / 1000.0
    cache: list[dict[str, Any]] = []
    for rec_ctrl in recording_controls:
        if not rec_ctrl.target_electrode_present or rec_ctrl.recording_path not in rec_by_rel:
            continue
        rec = rec_by_rel[rec_ctrl.recording_path]
        windows = read_protocol_windows_for_recording(rec, root)
        if not windows or windows[0].target_id is None:
            continue
        target = int(windows[0].target_id)
        target_times, duration_s = _load_target_spike_seconds(rec, target)
        if len(target_times) == 0 or duration_s <= 0:
            continue
        durations = np.asarray([max(0.0, float(w.end_s) - float(w.start_s)) for w in windows], dtype=float)
        durations = durations[durations > 0]
        if len(durations) == 0:
            continue
        max_start = duration_s - response_window_s - durations
        valid = max_start > response_window_s
        durations = durations[valid]
        max_start = max_start[valid]
        if len(durations) == 0:
            continue
        cache.append(
            {
                "recording_path": rec_ctrl.recording_path,
                "target_times": target_times,
                "durations": durations,
                "max_start": max_start,
                "response_window_s": response_window_s,
            }
        )
    return cache


def _random_time_window_delta_from_cache(item: dict[str, Any], rng: np.random.Generator) -> float | None:
    durations = item["durations"]
    max_start = item["max_start"]
    response_window_s = float(item["response_window_s"])
    if len(durations) == 0:
        return None
    starts = rng.uniform(response_window_s, max_start)
    ends = starts + durations
    response_starts = ends
    response_ends = ends + response_window_s
    response_pre_starts = starts - response_window_s
    response_pre_ends = starts
    response_durations = np.full(len(starts), response_window_s, dtype=float)
    return _response_delta_for_times(
        item["target_times"],
        response_starts,
        response_ends,
        response_pre_starts,
        response_pre_ends,
        response_durations,
    )

def random_time_window_null_distribution(
    root_path: str | Path,
    recording_controls: list[RecordingControlResult],
    response_window_ms: float = 100.0,
    n_permutations: int = 300,
    seed: int = 17,
) -> list[dict[str, float]]:
    """Randomize stimulus timing while preserving pulse count and duration per recording.

    For each permutation, every recording keeps its true target electrode, but the stimulation windows are
    replaced by random same-duration windows. If the real effect is stimulus-aligned, the real target delta
    should exceed this time-window null.
    """
    rng = np.random.default_rng(seed)
    cache = _prepare_random_time_target_cache(root_path, recording_controls, response_window_ms)
    out: list[dict[str, float]] = []
    for i in range(int(n_permutations)):
        ds: list[float] = []
        for item in cache:
            d = _random_time_window_delta_from_cache(item, rng)
            if d is not None and np.isfinite(d):
                ds.append(float(d))
        if ds:
            out.append(
                {
                    "permutation": float(i),
                    "recordings": float(len(ds)),
                    "median_random_time_target_delta_rate_hz": float(np.median(ds)),
                    "mean_random_time_target_delta_rate_hz": float(np.mean(ds)),
                }
            )
    return out

def _summary_stats(values: list[float]) -> dict[str, float | None]:
    clean = np.asarray([float(v) for v in values if np.isfinite(v)], dtype=float)
    if len(clean) == 0:
        return {"n": 0, "mean": None, "median": None, "std": None, "q05": None, "q95": None}
    return {
        "n": int(len(clean)),
        "mean": float(np.mean(clean)),
        "median": float(np.median(clean)),
        "std": float(np.std(clean, ddof=1)) if len(clean) > 1 else 0.0,
        "q05": float(np.quantile(clean, 0.05)),
        "q95": float(np.quantile(clean, 0.95)),
    }


def build_control_summary(
    recording_controls: list[RecordingControlResult],
    random_electrode_null: list[dict[str, float]],
    random_time_null: list[dict[str, float]],
) -> dict[str, Any]:
    valid = [r for r in recording_controls if r.target_electrode_present and r.target_response_delta_rate_hz is not None]
    light = [r for r in valid if r.condition == "lightstim"]
    elec = [r for r in valid if r.condition == "elecstim"]

    def condition_stats(sub: list[RecordingControlResult]) -> dict[str, Any]:
        return {
            "recordings": len(sub),
            "target_delta_rate_hz": _summary_stats([float(r.target_response_delta_rate_hz) for r in sub if r.target_response_delta_rate_hz is not None]),
            "target_percentile": _summary_stats([float(r.target_response_percentile) for r in sub if r.target_response_percentile is not None]),
            "same_recording_random_electrode_delta_rate_hz": _summary_stats([float(r.random_electrode_delta_median_hz) for r in sub if r.random_electrode_delta_median_hz is not None]),
            "same_recording_random_electrode_percentile": _summary_stats([float(r.random_electrode_percentile_median) for r in sub if r.random_electrode_percentile_median is not None]),
            "near_minus_far_delta_hz": _summary_stats([float(r.near_minus_far_delta_hz) for r in sub if r.near_minus_far_delta_hz is not None]),
        }

    observed_median_target_percentile = float(np.median([r.target_response_percentile for r in valid if r.target_response_percentile is not None])) if valid else float("nan")
    observed_median_target_delta = float(np.median([r.target_response_delta_rate_hz for r in valid if r.target_response_delta_rate_hz is not None])) if valid else float("nan")
    observed_mean_target_delta = float(np.mean([r.target_response_delta_rate_hz for r in valid if r.target_response_delta_rate_hz is not None])) if valid else float("nan")

    re_median_percentiles = [d["median_random_electrode_percentile"] for d in random_electrode_null]
    re_median_deltas = [d["median_random_electrode_delta_rate_hz"] for d in random_electrode_null]
    rt_median_deltas = [d["median_random_time_target_delta_rate_hz"] for d in random_time_null]
    rt_mean_deltas = [d["mean_random_time_target_delta_rate_hz"] for d in random_time_null]

    return {
        "task": "pulse_level_controls_v1_4",
        "recordings_with_target": len(valid),
        "lightstim": condition_stats(light),
        "elecstim": condition_stats(elec),
        "all_conditions": condition_stats(valid),
        "observed": {
            "median_target_response_percentile": observed_median_target_percentile,
            "median_target_response_delta_rate_hz": observed_median_target_delta,
            "mean_target_response_delta_rate_hz": observed_mean_target_delta,
        },
        "random_electrode_null": {
            "permutations": len(random_electrode_null),
            "median_random_electrode_percentile": _summary_stats(re_median_percentiles),
            "median_random_electrode_delta_rate_hz": _summary_stats(re_median_deltas),
            "p_value_target_percentile_gt_random_electrode": _one_sided_high_p_value(observed_median_target_percentile, re_median_percentiles),
            "p_value_target_delta_gt_random_electrode": _one_sided_high_p_value(observed_median_target_delta, re_median_deltas),
        },
        "random_time_window_null": {
            "permutations": len(random_time_null),
            "median_random_time_target_delta_rate_hz": _summary_stats(rt_median_deltas),
            "mean_random_time_target_delta_rate_hz": _summary_stats(rt_mean_deltas),
            "p_value_target_delta_gt_random_time_windows": _one_sided_high_p_value(observed_median_target_delta, rt_median_deltas),
            "p_value_mean_target_delta_gt_random_time_windows": _one_sided_high_p_value(observed_mean_target_delta, rt_mean_deltas),
        },
        "interpretation_rule": (
            "A strong result requires the true target electrode to exceed same-recording random electrodes "
            "and the true protocol timing to exceed randomized same-duration windows. This control layer is "
            "still a response benchmark, not a claim that BioGPU outperforms silicon GPUs."
        ),
    }


def _write_dict_csv(rows: list[dict[str, Any]], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if fieldnames:
            writer.writeheader()
            writer.writerows(rows)


def _write_dataclass_csv(rows: list[Any], path: str | Path, fieldnames: list[str] | None = None) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fieldnames = list(asdict(rows[0]).keys()) if rows else []
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if fieldnames:
            writer.writeheader()
            for row in rows:
                writer.writerow(asdict(row))


def _write_control_plots(
    summary: dict[str, Any],
    recording_controls: list[RecordingControlResult],
    random_electrode_null: list[dict[str, float]],
    random_time_null: list[dict[str, float]],
    out_dir: Path,
) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return

    valid = [r for r in recording_controls if r.target_electrode_present]
    target_percentiles = [float(r.target_response_percentile) for r in valid if r.target_response_percentile is not None]
    random_percentiles = [d["median_random_electrode_percentile"] for d in random_electrode_null]
    if target_percentiles and random_percentiles:
        plt.figure(figsize=(7, 4))
        plt.hist(random_percentiles, bins=20, alpha=0.7, label="random-electrode null median")
        plt.axvline(float(np.median(target_percentiles)), linestyle="--", label="observed target median")
        plt.xlabel("Median response percentile")
        plt.ylabel("Permutation count")
        plt.title("Target response vs random-electrode null")
        plt.legend()
        plt.tight_layout()
        plt.savefig(out_dir / "control_random_electrode_percentile_null.png", dpi=150)
        plt.close()

    real_deltas = [float(r.target_response_delta_rate_hz) for r in valid if r.target_response_delta_rate_hz is not None]
    random_time_deltas = [d["median_random_time_target_delta_rate_hz"] for d in random_time_null]
    if real_deltas and random_time_deltas:
        plt.figure(figsize=(7, 4))
        plt.hist(random_time_deltas, bins=20, alpha=0.7, label="random-time null median")
        plt.axvline(float(np.median(real_deltas)), linestyle="--", label="observed target median")
        plt.xlabel("Median target delta rate, Hz")
        plt.ylabel("Permutation count")
        plt.title("True stimulus timing vs randomized windows")
        plt.legend()
        plt.tight_layout()
        plt.savefig(out_dir / "control_random_time_window_null.png", dpi=150)
        plt.close()

    near_far = [r.near_minus_far_delta_hz for r in valid if r.near_minus_far_delta_hz is not None]
    if near_far:
        plt.figure(figsize=(7, 4))
        plt.hist(near_far, bins=16)
        plt.axvline(0.0, linestyle="--")
        plt.xlabel("Near minus far delta rate, Hz")
        plt.ylabel("Recordings")
        plt.title("Spatial locality control")
        plt.tight_layout()
        plt.savefig(out_dir / "control_near_minus_far_delta_hist.png", dpi=150)
        plt.close()


def render_control_report(summary: dict[str, Any], response_window_ms: float, n_random_electrode: int, n_random_time: int) -> str:
    return f"""# Zenodo 14363732 — Pulse-level controls v1.4

## Purpose

v1.3 found a strong pulse-aligned target-electrode response. v1.4 tests whether that finding survives stricter controls.

The analysis now checks two null hypotheses:

1. **Random-electrode null** — if the target label is meaningless, a same-recording random electrode should look similar to the protocol target.
2. **Random-time-window null** — if the timing is meaningless, the real target electrode should look similar when stimulation windows are randomly moved to same-duration non-protocol times.

Response window after stimulus end: `{response_window_ms}` ms.
Random-electrode permutations requested: `{n_random_electrode}`.
Random-time permutations requested: `{n_random_time}`.

## Control summary

```json
{json.dumps(summary, indent=2, ensure_ascii=False)}
```

## Interpretation

- Passing the random-electrode control supports that the protocol target electrode is not just an arbitrary high-rate channel.
- Passing the random-time-window control supports that the response is aligned to the real stimulation protocol, not just general recording activity.
- This is still a biological response benchmark, not yet a full biological-computation advantage claim.
- Publication-grade claims still need raw HDF5/TTL verification and an actual train/test task benchmark.
"""


def write_control_outputs(
    root_path: str | Path,
    out_dir: str | Path,
    response_window_ms: float = 100.0,
    n_random_electrode_permutations: int = 1000,
    n_random_time_permutations: int = 300,
    seed: int = 13,
    make_plots: bool = False,
) -> dict[str, Any]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    electrode_rows = analyze_all_electrode_responses(root_path, response_window_ms=response_window_ms)
    recording_controls = summarize_recording_controls(electrode_rows)
    random_electrode_null = random_electrode_null_distribution(
        recording_controls,
        electrode_rows,
        n_permutations=n_random_electrode_permutations,
        seed=seed,
    )
    random_time_null = random_time_window_null_distribution(
        root_path,
        recording_controls,
        response_window_ms=response_window_ms,
        n_permutations=n_random_time_permutations,
        seed=seed + 1,
    )
    summary = build_control_summary(recording_controls, random_electrode_null, random_time_null)

    _write_dataclass_csv(electrode_rows, out / "pulse_electrode_response_by_recording.csv")
    _write_dataclass_csv(recording_controls, out / "pulse_recording_controls.csv")
    _write_dict_csv(random_electrode_null, out / "random_electrode_null_distribution.csv")
    _write_dict_csv(random_time_null, out / "random_time_window_null_distribution.csv")
    (out / "pulse_control_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    (out / "PULSE_LEVEL_CONTROLS_REPORT.md").write_text(
        render_control_report(summary, response_window_ms, n_random_electrode_permutations, n_random_time_permutations),
        encoding="utf-8",
    )
    if make_plots:
        _write_control_plots(summary, recording_controls, random_electrode_null, random_time_null, out)
    return summary
