"""BioGPU-Core v8.5 — Feature Ablation Analysis.

Systematically removes groups of features and measures accuracy degradation.
Answers: which features actually matter?
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np


FEATURE_GROUPS = {
    "temporal": ["mean_firing_rate", "isi_mean", "isi_std", "burst_index", "cv_isi"],
    "spectral": ["delta_power", "theta_power", "alpha_power", "beta_power", "gamma_power"],
    "amplitude": ["spike_amplitude_mean", "spike_amplitude_std", "snr", "peak_to_valley"],
    "connectivity": ["pairwise_correlation", "coherence_delta", "coherence_theta", "coherence_alpha"],
    "morphology": ["waveform_duration", "half_width", "repolarization_slope", "recovery_slope"],
    "lfp": ["lfp_mean", "lfp_std", "lfp_theta_power", "lfp_gamma_power", "lfp_spindle_power"],
}


@dataclass
class AblationResult:
    group_removed: str
    accuracy_after: float
    accuracy_drop: float
    accuracy_drop_pct: float
    features_removed: int


def run_ablation(
    X: np.ndarray,
    y: np.ndarray,
    feature_names: list[str],
    baseline_accuracy: float,
    classifier_fn,
) -> list[AblationResult]:
    """Remove each feature group and measure accuracy drop."""
    results = []
    name_to_idx = {name: i for i, name in enumerate(feature_names)}

    for group_name, group_features in FEATURE_GROUPS.items():
        indices = [name_to_idx[f] for f in group_features if f in name_to_idx]
        if not indices:
            continue

        mask = np.ones(X.shape[1], dtype=bool)
        mask[indices] = False
        X_ablated = X[:, mask]

        try:
            acc = classifier_fn(X_ablated, y)
            drop = baseline_accuracy - acc
            drop_pct = (drop / baseline_accuracy) * 100 if baseline_accuracy > 0 else 0
            results.append(AblationResult(
                group_removed=group_name,
                accuracy_after=acc,
                accuracy_drop=drop,
                accuracy_drop_pct=round(drop_pct, 1),
                features_removed=len(indices),
            ))
        except Exception:
            pass

    results.sort(key=lambda r: r.accuracy_drop, reverse=True)
    return results
