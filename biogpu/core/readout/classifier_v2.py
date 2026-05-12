"""BioGPU Core v2.0 — Classifier/readout with baseline comparison.

Runs BioGPU features through multiple classifiers AND baseline models
(logistic regression, random forest, linear SVM) on the same features.
Reports honest comparison.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import LinearSVC
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import LabelEncoder

BENCHMARK_DECODERS = {
    "logreg": ("Logistic Regression", LogisticRegression(max_iter=1000, random_state=42)),
    "random_forest": ("Random Forest", RandomForestClassifier(n_estimators=100, random_state=42)),
    "linear_svm": ("Linear SVM", LinearSVC(max_iter=2000, random_state=42, dual=False)),
    "mlp": ("MLP (BioGPU)", MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=500, random_state=42)),
}


@dataclass
class ReadoutResult:
    decoder: str
    accuracy: float
    accuracy_std: float
    n_folds: int = 5
    n_samples: int = 0
    n_classes: int = 0
    chance_level: float = 0.0
    above_chance: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


def run_readout(
    features: np.ndarray,
    labels: np.ndarray,
    decoder_name: str = "mlp",
    n_folds: int = 5,
) -> ReadoutResult:
    """Run a single decoder on feature matrix."""
    if features.size == 0 or len(features) < 10:
        return ReadoutResult(decoder=decoder_name, accuracy=0.0, accuracy_std=0.0)

    # Encode labels
    le = LabelEncoder()
    y = le.fit_transform(labels)
    n_classes = len(le.classes_)

    chance = 1.0 / max(n_classes, 1)

    if decoder_name not in BENCHMARK_DECODERS:
        return ReadoutResult(decoder=decoder_name, accuracy=0.0, accuracy_std=0.0,
                             n_classes=n_classes, chance_level=chance)

    _, model = BENCHMARK_DECODERS[decoder_name]

    try:
        cv = StratifiedKFold(n_splits=min(n_folds, max(2, min(np.bincount(y)))))
        scores = cross_val_score(model, features, y, cv=cv, scoring="accuracy")
        acc = float(np.mean(scores))
        acc_std = float(np.std(scores))
    except Exception:
        # Fallback: single split
        from sklearn.model_selection import train_test_split
        X_tr, X_te, y_tr, y_te = train_test_split(features, y, test_size=0.3, stratify=y, random_state=42)
        model.fit(X_tr, y_tr)
        acc = float(model.score(X_te, y_te))
        acc_std = 0.0

    return ReadoutResult(
        decoder=decoder_name,
        accuracy=acc,
        accuracy_std=acc_std,
        n_folds=n_folds,
        n_samples=len(features),
        n_classes=n_classes,
        chance_level=chance,
        above_chance=acc > chance + 0.01,
    )


def run_baselines(
    features: np.ndarray,
    labels: np.ndarray,
    n_folds: int = 5,
) -> dict[str, ReadoutResult]:
    """Run ALL decoders (BioGPU + baselines) on the same features.

    Returns dict of {decoder_name: ReadoutResult} for honest comparison.
    """
    results = {}
    for name in BENCHMARK_DECODERS:
        results[name] = run_readout(features, labels, name, n_folds)
    return results


def run_ablation(
    features: np.ndarray,
    labels: np.ndarray,
    feature_groups: dict[str, list[int]],
    n_folds: int = 5,
) -> dict[str, dict[str, ReadoutResult]]:
    """Run ablation: remove one group at a time, measure impact.

    Args:
        features: (n_samples, n_features) matrix
        labels: class labels
        feature_groups: {group_name: [feature_indices]}

    Returns: {group_name: {decoder: ReadoutResult}}
    """
    from biogpu.core.features.extractor_v2 import FEATURE_NAMES
    all_indices = list(range(len(FEATURE_NAMES)))
    results: dict[str, dict[str, ReadoutResult]] = {}

    # Full model baseline
    results["all_features"] = run_baselines(features, labels, n_folds)

    # Drop each group
    for group_name, indices in feature_groups.items():
        keep = [i for i in all_indices if i not in indices]
        if len(keep) == 0:
            continue
        subset = features[:, keep]
        results[f"drop_{group_name}"] = run_baselines(subset, labels, n_folds)

    return results
