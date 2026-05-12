"""BioGPU v3.6 bootstrap and aggregation utilities.

These helpers are intentionally lightweight so they can be run in this
environment, while full 1000/5000-shuffle sweeps remain a power-PC task.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable

import numpy as np


@dataclass(frozen=True)
class BootstrapCIV36:
    metric: str
    n: int
    mean: float
    median: float
    low: float
    high: float
    confidence: float
    iterations: int
    seed: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def bootstrap_mean_ci_v36(values: Iterable[float], confidence: float = 0.95, iterations: int = 2000, seed: int = 36, metric: str = "mean") -> BootstrapCIV36:
    arr = np.asarray(list(values), dtype=float)
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        raise ValueError("Cannot bootstrap empty/non-finite value array")
    if not (0.0 < confidence < 1.0):
        raise ValueError("confidence must be between 0 and 1")
    rng = np.random.default_rng(int(seed))
    n = int(arr.size)
    vals = []
    for _ in range(max(1, int(iterations))):
        sample = rng.choice(arr, size=n, replace=True)
        vals.append(float(np.mean(sample)))
    vals = np.asarray(vals, dtype=float)
    alpha = (1.0 - float(confidence)) / 2.0
    return BootstrapCIV36(
        metric=metric,
        n=n,
        mean=float(np.mean(arr)),
        median=float(np.median(arr)),
        low=float(np.quantile(vals, alpha)),
        high=float(np.quantile(vals, 1.0-alpha)),
        confidence=float(confidence),
        iterations=int(iterations),
        seed=int(seed),
    )


def aggregate_rows_with_ci_v36(rows: list[dict[str, Any]], group_key: str, value_key: str = "accuracy", confidence: float = 0.95, iterations: int = 2000, seed: int = 36) -> list[dict[str, Any]]:
    out=[]
    groups=sorted(set(str(r[group_key]) for r in rows if group_key in r))
    for i,g in enumerate(groups):
        vals=[float(r[value_key]) for r in rows if str(r.get(group_key))==g and value_key in r]
        if not vals:
            continue
        ci=bootstrap_mean_ci_v36(vals, confidence=confidence, iterations=iterations, seed=seed+i, metric=f"{value_key}_mean")
        out.append({
            group_key:g,
            "value_key":value_key,
            "n_runs":ci.n,
            "mean":ci.mean,
            "median":ci.median,
            "ci_low":ci.low,
            "ci_high":ci.high,
            "confidence":ci.confidence,
            "bootstrap_iterations":ci.iterations,
        })
    return out


def summarize_best_rows_v36(rows: list[dict[str, Any]], by: str) -> list[dict[str, Any]]:
    out=[]
    groups=sorted(set(str(r[by]) for r in rows if by in r))
    for g in groups:
        xs=[r for r in rows if str(r.get(by))==g]
        if not xs:
            continue
        best=max(xs, key=lambda r:(float(r.get("accuracy",0.0)), float(r.get("balanced_accuracy",0.0)), float(r.get("improvement_vs_shuffle_mean",0.0))))
        out.append(dict(best))
    return out
