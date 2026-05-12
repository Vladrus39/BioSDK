from __future__ import annotations

from pathlib import Path
from typing import Any
import json
import numpy as np

from biogpu.data_ingest.zenodo_mea2100 import parse_spike_txt
from biogpu.data_ingest.dandi_nwb import read_nwb_units_as_spiketrain
from biogpu.data_ingest.stimulus_windows import (
    read_stimulus_windows_csv,
    read_stimulus_windows_json,
    build_windowed_spiketrains,
    summarize_windows,
)
from biogpu.reading.feature_extractor import BasicSpikeFeatureExtractor
from biogpu.decoding.linear_readout import LinearReadout
from biogpu.data.versioning import make_run_metadata
from biogpu.data.energy import estimate_energy_proxy


def _load_windows(path: str | Path):
    p = Path(path)
    if p.suffix.lower() == ".json":
        return read_stimulus_windows_json(p)
    return read_stimulus_windows_csv(p)


def _train_test_indices(n: int, train_fraction: float = 0.7, seed: int = 1):
    rng = np.random.default_rng(seed)
    idx = np.arange(n)
    rng.shuffle(idx)
    cut = max(1, min(n - 1, int(round(n * train_fraction)))) if n > 1 else 1
    return idx[:cut], idx[cut:]


def _fit_score_linear(X: np.ndarray, y: np.ndarray, train_fraction: float, seed: int) -> dict[str, Any]:
    if len(y) < 2 or len(set(y.tolist())) < 2:
        return {"accuracy": None, "reason": "Need at least two classes and two labeled windows"}
    train_idx, test_idx = _train_test_indices(len(y), train_fraction, seed)
    # Ensure train has at least two classes; fall back to alternating split if needed.
    if len(set(y[train_idx].tolist())) < 2:
        train_idx = np.arange(0, len(y), 2)
        test_idx = np.arange(1, len(y), 2)
    if len(test_idx) == 0 or len(set(y[train_idx].tolist())) < 2:
        return {"accuracy": None, "reason": "Insufficient class diversity after split"}
    dec = LinearReadout().fit(X[train_idx], y[train_idx])
    pred = dec.predict(X[test_idx])
    acc = float(np.mean(pred == y[test_idx])) if len(test_idx) else None
    return {
        "accuracy": acc,
        "train_count": int(len(train_idx)),
        "test_count": int(len(test_idx)),
        "classes": sorted([str(x) for x in set(y.tolist())]),
    }


def run_task_aligned_spike_benchmark(
    spike_source: str,
    windows_path: str,
    source_type: str = "txt",
    time_unit: str = "s",
    num_units: int | None = None,
    train_fraction: float = 0.7,
    seed: int = 1,
    window_ms: float | None = None,
    readout_bins: int = 4,
) -> dict[str, Any]:
    """Run a first honest task-aligned real-spike benchmark.

    This benchmark requires externally supplied stimulus windows. It does not
    invent labels. It is appropriate for public datasets only when the user has
    mapped real stimulus/behavior metadata into a CSV/JSON window file.
    """
    if source_type.lower() in {"txt", "zenodo_txt", "spike_txt"}:
        spikes = parse_spike_txt(spike_source, time_unit=time_unit)
    elif source_type.lower() in {"nwb", "dandi_nwb"}:
        spikes = read_nwb_units_as_spiketrain(spike_source)
    else:
        raise ValueError(f"Unsupported source_type: {source_type}")
    windows = _load_windows(windows_path)
    windowed, labels, used_windows = build_windowed_spiketrains(spikes, windows, relative_times=True)
    inferred_units = (max(spikes.unit_ids) + 1) if spikes.unit_ids else 1
    n_units = int(num_units or inferred_units)
    if window_ms is None:
        max_duration_s = max((w.duration_s for w in used_windows), default=1.0)
        window_ms = max_duration_s * 1000.0
    extractor = BasicSpikeFeatureExtractor(num_units=n_units, window_ms=window_ms, readout_bins=readout_bins)
    features = [extractor.transform(st).values for st in windowed]
    if not features:
        X = np.zeros((0, n_units), dtype=float)
    else:
        X = np.vstack(features)
    y = np.asarray(labels)
    score = _fit_score_linear(X, y, train_fraction, seed)
    proxy = estimate_energy_proxy(
        event_counts=[0 for _ in windowed],
        spike_counts=[len(st.spike_times) for st in windowed],
        active_ratios=[len(set(st.unit_ids)) / max(1, n_units) for st in windowed],
        readout_features=int(X.shape[1]) if X.ndim == 2 else 0,
    )
    result = {
        "benchmark": "task_aligned_real_spikes",
        "metadata": make_run_metadata(
            "0.8",
            {
                "source_type": source_type,
                "spike_source": str(spike_source),
                "windows_path": str(windows_path),
                "train_fraction": train_fraction,
                "seed": seed,
                "readout_bins": readout_bins,
            },
        ),
        "window_summary": summarize_windows(windows),
        "metrics": {
            **score,
            "labeled_windows_used": int(len(windowed)),
            "feature_dim": int(X.shape[1]) if X.ndim == 2 else 0,
            "total_spikes_in_source": int(len(spikes.spike_times)),
        },
        "energy_proxy": proxy,
        "honesty_note": "This is a valid benchmark only when windows_path is mapped from real stimulus/behavior metadata.",
    }
    return result


def main(argv: list[str] | None = None) -> int:
    import argparse
    p = argparse.ArgumentParser(description="Run task-aligned real-spike benchmark")
    p.add_argument("spike_source")
    p.add_argument("windows_path")
    p.add_argument("--source-type", default="txt", choices=["txt", "nwb", "zenodo_txt", "dandi_nwb"])
    p.add_argument("--time-unit", default="s")
    p.add_argument("--train-fraction", type=float, default=0.7)
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--window-ms", type=float, default=None)
    p.add_argument("--readout-bins", type=int, default=4)
    p.add_argument("--output", default=None)
    a = p.parse_args(argv)
    result = run_task_aligned_spike_benchmark(
        a.spike_source,
        a.windows_path,
        source_type=a.source_type,
        time_unit=a.time_unit,
        train_fraction=a.train_fraction,
        seed=a.seed,
        window_ms=a.window_ms,
        readout_bins=a.readout_bins,
    )
    text = json.dumps(result, indent=2, ensure_ascii=False)
    if a.output:
        out = Path(a.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
