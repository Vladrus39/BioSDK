from __future__ import annotations

import numpy as np

from biogpu.analysis.zenodo_pulse_readout import CandidateFeatureTable, PulseFeatureMetadata, PulseFeatureMatrix
from biogpu.analysis.zenodo_pulse_v16 import (
    attach_bootstrap_cis,
    bootstrap_fold_metric_ci,
    run_feature_ablation,
    run_negative_sweep,
    select_candidate_features,
)
from biogpu.analysis.zenodo_pulse_readout import build_candidate_target_table, leave_one_culture_candidate_readout


def _toy_matrix() -> PulseFeatureMatrix:
    electrodes = [1, 2, 3]
    feature_names = []
    for prefix in (
        "response_delta_count",
        "response_count",
        "pre_response_count",
        "exact_delta_count",
        "exact_count",
        "exact_pre_count",
    ):
        feature_names.extend([f"{prefix}_e{e:03d}" for e in electrodes])
    rows = []
    meta = []
    cultures = ["c1", "c1", "c2", "c2", "c3", "c3"]
    targets = [1, 2, 1, 2, 1, 2]
    for i, (culture, target) in enumerate(zip(cultures, targets)):
        E = len(electrodes)
        row = np.zeros(E * 6, dtype=np.float32)
        j = electrodes.index(target)
        row[j] = 5.0
        row[E + j] = 6.0
        row[2 * E + j] = 1.0
        row[3 * E + j] = 4.0
        row[4 * E + j] = 5.0
        row[5 * E + j] = 1.0
        rows.append(row)
        meta.append(
            PulseFeatureMetadata(
                row_index=i,
                recording_path=f"rec_{culture}",
                culture=culture,
                date="2026-01-01",
                condition="lightstim",
                target_type="electrode",
                target_id=target,
                pulse_index=i,
                start_s=float(i),
                end_s=float(i) + 0.01,
                duration_s=0.01,
            )
        )
    return PulseFeatureMatrix(
        X=np.vstack(rows),
        metadata=meta,
        electrodes=electrodes,
        feature_names=feature_names,
        response_window_ms=100.0,
    )


def test_select_candidate_features_keeps_requested_columns() -> None:
    table = build_candidate_target_table(_toy_matrix(), negative_per_pulse=1, seed=1)
    selected = select_candidate_features(table, ["candidate_response_delta_count", "candidate_exact_delta_count"])
    assert selected.X.shape[1] == 2
    assert selected.feature_names == ["candidate_response_delta_count", "candidate_exact_delta_count"]
    assert np.array_equal(selected.y, table.y)


def test_bootstrap_fold_metric_ci_returns_interval() -> None:
    folds = [{"roc_auc": 0.8}, {"roc_auc": 0.9}, {"roc_auc": 1.0}]
    ci = bootstrap_fold_metric_ci(folds, metric="roc_auc", n_bootstraps=50, seed=1)
    assert ci["n_cultures_with_metric"] == 3
    assert 0.75 <= ci["ci_low"] <= ci["ci_high"] <= 1.0


def test_attach_bootstrap_cis_on_candidate_result() -> None:
    table = build_candidate_target_table(_toy_matrix(), negative_per_pulse=1, seed=2)
    result = leave_one_culture_candidate_readout(table, n_label_shuffles=2, seed=3)
    enriched = attach_bootstrap_cis(result, n_bootstraps=10, seed=4)
    assert "culture_bootstrap_ci" in enriched
    assert "roc_auc" in enriched["culture_bootstrap_ci"]


def test_run_negative_sweep_and_ablation_smoke() -> None:
    matrix = _toy_matrix()
    sweep = run_negative_sweep(matrix, negative_counts=[1, 2], label_shuffles=1, bootstrap_repeats=5, seed=5)
    ablation = run_feature_ablation(matrix, negative_per_pulse=1, label_shuffles=1, bootstrap_repeats=5, seed=6)
    assert len(sweep["rows"]) == 2
    assert any(r["feature_set"] == "raw_candidate_counts_only" for r in ablation["rows"])
