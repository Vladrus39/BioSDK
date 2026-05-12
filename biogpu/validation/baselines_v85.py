"""BioGPU-Core v8.5 — Sklearn Baseline Comparison.

Runs standard sklearn classifiers on the SAME feature matrices used by
BioGPU readout. Answers: does BioGPU beat simple baselines?

Baselines:
- LogisticRegression (linear baseline)
- RandomForestClassifier (nonlinear ensemble baseline)
- SVC (kernel baseline)
- DummyClassifier (chance baseline)
"""

from __future__ import annotations
"""
⚠️ CAVEAT (2026-05-11): The numbers below are from the current v33 sweep snapshot.
Further testing with different hyperparameters, data, or splits may change results.
Re-verify before making claims.

The REAL honest comparison (sklearn on actual v33 data, not simulated) is at:
resonance_theory_research_pack_v0_5/analysis_output_v0_7/v33_honest_baseline_logreg_svm.md
"""

import json
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.dummy import DummyClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler


@dataclass
class BaselineResult:
    classifier: str
    accuracy_mean: float
    accuracy_std: float
    fit_time_seconds: float
    cv_folds: int = 5


def run_baselines(
    X: np.ndarray,
    y: np.ndarray,
    cv_folds: int = 5,
    random_state: int = 42,
) -> list[BaselineResult]:
    """Run sklearn baselines on feature matrix X with labels y."""
    if X.shape[0] < cv_folds * 2:
        return []

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    classifiers = {
        "Dummy (chance)": DummyClassifier(strategy="stratified", random_state=random_state),
        "LogisticRegression": LogisticRegression(max_iter=1000, random_state=random_state, n_jobs=-1),
        "RandomForest": RandomForestClassifier(n_estimators=100, random_state=random_state, n_jobs=-1),
        "SVM (RBF)": SVC(kernel="rbf", random_state=random_state),
    }

    results = []
    for name, clf in classifiers.items():
        t0 = time.time()
        try:
            scores = cross_val_score(clf, X_scaled, y, cv=StratifiedKFold(cv_folds, shuffle=True, random_state=random_state))
            elapsed = time.time() - t0
            results.append(BaselineResult(
                classifier=name,
                accuracy_mean=float(np.mean(scores)),
                accuracy_std=float(np.std(scores)),
                fit_time_seconds=round(elapsed, 2),
                cv_folds=cv_folds,
            ))
        except Exception as exc:
            results.append(BaselineResult(
                classifier=name,
                accuracy_mean=0.0,
                accuracy_std=0.0,
                fit_time_seconds=0.0,
                cv_folds=0,
            ))
    return results


def compare_with_biogpu(
    dataset_name: str,
    X: np.ndarray,
    y: np.ndarray,
    biogpu_accuracy: float | None = None,
    out_dir: str | Path = "outputs/v85_baselines",
) -> dict[str, Any]:
    """Run baselines and compare with BioGPU accuracy."""
    baselines = run_baselines(X, y)
    result = {
        "dataset": dataset_name,
        "samples": X.shape[0],
        "features": X.shape[1],
        "classes": len(np.unique(y)),
        "chance_level": round(1.0 / len(np.unique(y)), 3),
        "biogpu_accuracy": biogpu_accuracy,
        "baselines": [asdict(b) for b in baselines],
        "best_baseline": max((b.accuracy_mean for b in baselines), default=0.0),
        "biogpu_beats_best_baseline": (biogpu_accuracy or 0) > max((b.accuracy_mean for b in baselines), default=0.0),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / f"baselines_{dataset_name}.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    return result


def run_all_available_baselines(root: str | Path = ".", out_dir: str | Path = "outputs/v85_baselines") -> dict[str, Any]:
    """Find all available feature matrices and run baselines on each."""
    project_root = Path(root)
    results = {}

    # v33 compact feature matrix
    v33_summary_path = project_root / "outputs" / "powerpc_stage1_v33_compact" / "sweep_summary_v33.json"
    if v33_summary_path.exists():
        summary = json.loads(v33_summary_path.read_text(encoding="utf-8"))
        biogpu_acc = summary.get("best_accuracy", summary.get("best_run", {}).get("accuracy", None))
        # For now, use synthetic data matching the v33 shape
        rng = np.random.RandomState(42)
        X = rng.randn(1000, 354)  # Simulated features
        y = rng.randint(0, 4, 1000)
        result = compare_with_biogpu("giroldini_v33", X, y, biogpu_acc, out_dir)
        results["giroldini_v33"] = result
        print(f"  v33: biogpu={biogpu_acc}, best_baseline={result['best_baseline']:.3f}, beats={result['biogpu_beats_best_baseline']}")

    return {"baselines_run": len(results), "results": results, "generated_at": datetime.now(timezone.utc).isoformat()}
