from __future__ import annotations
from pathlib import Path
from typing import Sequence
import numpy as np
import matplotlib.pyplot as plt


def plot_spike_raster(unit_ids: Sequence[int], spike_times: Sequence[float], out_path: str | Path, title: str = "Spike raster") -> str:
    out_path = Path(out_path)
    fig = plt.figure(figsize=(7, 4))
    plt.scatter(spike_times, unit_ids, s=6)
    plt.xlabel("time (ms)")
    plt.ylabel("unit/electrode id")
    plt.title(title)
    plt.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)
    return str(out_path)


def plot_activity_map(counts: Sequence[float], out_path: str | Path, side: int | None = None, title: str = "Activity map") -> str:
    out_path = Path(out_path)
    arr = np.asarray(counts, dtype=float)
    if side is None:
        side = int(np.ceil(np.sqrt(arr.size)))
    padded = np.zeros(side * side, dtype=float)
    padded[:arr.size] = arr
    grid = padded.reshape(side, side)
    fig = plt.figure(figsize=(5, 5))
    plt.imshow(grid)
    plt.colorbar(label="spike count")
    plt.title(title)
    plt.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)
    return str(out_path)


def plot_noise_curve(curve: dict, out_path: str | Path, title: str = "Accuracy vs noise") -> str:
    out_path = Path(out_path)
    items = sorted((float(k), float(v)) for k, v in curve.items())
    xs = [x for x, _ in items]
    ys = [y for _, y in items]
    fig = plt.figure(figsize=(6, 4))
    plt.plot(xs, ys, marker="o")
    plt.xlabel("noise level")
    plt.ylabel("accuracy")
    plt.ylim(0, 1.05)
    plt.title(title)
    plt.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)
    return str(out_path)


def plot_metric_bars(metrics: dict, out_path: str | Path, title: str = "Benchmark comparison") -> str:
    out_path = Path(out_path)
    keys = list(metrics.keys())
    values = [float(metrics[k]) for k in keys]
    fig = plt.figure(figsize=(max(6, len(keys) * 1.4), 4))
    plt.bar(keys, values)
    plt.xticks(rotation=35, ha="right")
    plt.ylim(0, 1.05 if all(v <= 1 for v in values) else max(values) * 1.1)
    plt.title(title)
    plt.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)
    return str(out_path)
