from __future__ import annotations

import numpy as np

from biogpu.analysis.zenodo_pulse_readout import CandidateFeatureTable
from biogpu.analysis.zenodo_pulse_v17 import leave_one_culture_binary_readout, summarize_v17_rows


def test_v17_leave_one_culture_binary_readout_separates_toy_data() -> None:
    rng = np.random.default_rng(123)
    X_rows = []
    y = []
    cultures = []
    meta = []
    for ci, culture in enumerate(["culture_a", "culture_b", "culture_c"]):
        for _ in range(8):
            X_rows.append([2.5 + 0.1 * ci + rng.normal(0, 0.05), 1.0])
            y.append(1)
            cultures.append(culture)
            meta.append({"culture": culture, "is_target": 1})
            X_rows.append([-2.5 + 0.1 * ci + rng.normal(0, 0.05), 1.0])
            y.append(0)
            cultures.append(culture)
            meta.append({"culture": culture, "is_target": 0})
    table = CandidateFeatureTable(
        X=np.asarray(X_rows, dtype=np.float32),
        y=np.asarray(y, dtype=int),
        culture=np.asarray(cultures, dtype=object),
        metadata=meta,
        feature_names=["candidate_response_delta_count", "pulse_context"],
    )
    result = leave_one_culture_binary_readout(table, readout="logistic_l2", label_shuffles=1, seed=7)
    assert result["observed"]["roc_auc"] > 0.99
    assert result["observed"]["balanced_accuracy"] > 0.99
    assert result["label_shuffle_baseline"]["shuffles"] == 1


def test_v17_summary_rows_groups_multiple_negative_seeds() -> None:
    rows = [
        {"negative_per_pulse": 1, "feature_set": "raw", "readout": "logistic_l2", "observed_roc_auc": 0.8, "observed_balanced_accuracy": 0.7, "shuffle_roc_auc_median": 0.5},
        {"negative_per_pulse": 1, "feature_set": "raw", "readout": "logistic_l2", "observed_roc_auc": 0.9, "observed_balanced_accuracy": 0.8, "shuffle_roc_auc_median": 0.5},
    ]
    summary = summarize_v17_rows(rows)
    assert len(summary) == 1
    assert summary[0]["negative_seed_runs"] == 2
    assert abs(summary[0]["roc_auc_mean"] - 0.85) < 1e-9
