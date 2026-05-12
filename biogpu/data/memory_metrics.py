from __future__ import annotations

from typing import Any
import numpy as np


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype=float).reshape(-1)
    b = np.asarray(b, dtype=float).reshape(-1)
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denom <= 1e-12:
        return 0.0
    return float(np.dot(a, b) / denom)


def class_centroid_separability(features: np.ndarray, labels: np.ndarray) -> float:
    """Simple readout-free separability score for reservoir states.

    Returns average between-class centroid distance divided by average within-class
    spread. Higher is better. This is not a proof of computation; it is a compact
    diagnostic for reservoir state geometry.
    """
    X = np.asarray(features, dtype=float)
    y = np.asarray(labels)
    classes = np.unique(y)
    if len(classes) < 2 or X.size == 0:
        return 0.0
    centroids = []
    within = []
    for cls in classes:
        Xi = X[y == cls]
        if Xi.size == 0:
            continue
        c = Xi.mean(axis=0)
        centroids.append(c)
        within.append(float(np.mean(np.linalg.norm(Xi - c, axis=1))))
    if len(centroids) < 2:
        return 0.0
    dists = []
    for i in range(len(centroids)):
        for j in range(i + 1, len(centroids)):
            dists.append(float(np.linalg.norm(centroids[i] - centroids[j])))
    denom = float(np.mean(within) + 1e-9)
    return float(np.mean(dists) / denom)


def temporal_trace_score(feature_sequence: list[np.ndarray] | np.ndarray) -> float:
    """Measures similarity between consecutive reservoir states.

    Useful as a recurrent-memory diagnostic. A value near 0 means consecutive
    states are unrelated; a high positive value means state carries temporal
    continuity. It does not by itself mean the memory is useful for the task.
    """
    X = np.asarray(feature_sequence, dtype=float)
    if X.ndim != 2 or X.shape[0] < 2:
        return 0.0
    sims = [cosine_similarity(X[i], X[i + 1]) for i in range(X.shape[0] - 1)]
    return float(np.mean(sims)) if sims else 0.0


def reservoir_memory_report(features: np.ndarray, labels: np.ndarray | None = None) -> dict[str, Any]:
    X = np.asarray(features, dtype=float)
    report: dict[str, Any] = {
        "num_states": int(X.shape[0]) if X.ndim >= 1 else 0,
        "num_features": int(X.shape[1]) if X.ndim == 2 else 0,
        "temporal_trace_score": temporal_trace_score(X) if X.ndim == 2 else 0.0,
        "mean_state_norm": float(np.mean(np.linalg.norm(X, axis=1))) if X.ndim == 2 and X.size else 0.0,
    }
    if labels is not None and X.ndim == 2:
        report["class_centroid_separability"] = class_centroid_separability(X, np.asarray(labels))
    return report
