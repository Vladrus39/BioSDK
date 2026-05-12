from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.metrics import accuracy_score, balanced_accuracy_score, roc_auc_score
from sklearn.model_selection import LeaveOneGroupOut

from biogpu.analysis.zenodo_pulse_level import _count_ranges, _load_spike_seconds_by_electrode
from biogpu.data_ingest.zenodo_mea2100_preprocessed import discover_recording_dirs, parse_electrode_number
from biogpu.data_ingest.zenodo_protocol_windows import read_protocol_windows_for_recording, summarize_protocol_windows, discover_protocol_windows


@dataclass
class PulseFeatureMetadata:
    row_index: int
    recording_path: str
    culture: str
    date: str
    condition: str
    target_type: str
    target_id: int | None
    pulse_index: int
    start_s: float
    end_s: float
    duration_s: float


@dataclass
class PulseFeatureMatrix:
    X: np.ndarray
    metadata: list[PulseFeatureMetadata]
    electrodes: list[int]
    feature_names: list[str]
    response_window_ms: float


@dataclass
class CandidateFeatureTable:
    X: np.ndarray
    y: np.ndarray
    culture: np.ndarray
    metadata: list[dict[str, Any]]
    feature_names: list[str]


def _all_protocol_electrodes(root: Path) -> list[int]:
    electrodes: set[int] = set()
    for rec in discover_recording_dirs(root):
        if not read_protocol_windows_for_recording(rec, root):
            continue
        for f in rec.glob("electrode*.csv"):
            electrodes.add(parse_electrode_number(f))
    return sorted(electrodes)


def _valid_protocol_arrays(windows: list[Any]) -> tuple[list[Any], np.ndarray, np.ndarray, np.ndarray]:
    starts = np.asarray([float(w.start_s) for w in windows], dtype=float)
    ends = np.asarray([float(w.end_s) for w in windows], dtype=float)
    durations = np.maximum(ends - starts, 0.0)
    valid = durations > 0
    filtered = [w for w, ok in zip(windows, valid) if bool(ok)]
    return filtered, starts[valid], ends[valid], durations[valid]


def build_pulse_feature_matrix(
    root_path: str | Path,
    response_window_ms: float = 100.0,
    condition_filter: str | None = None,
) -> PulseFeatureMatrix:
    """Build one feature vector per real protocol pulse window.

    Feature blocks are fixed to the union of electrodes in protocol recordings:

    1. response_delta_count_eXXX = post-stimulus count - pre-onset count
    2. response_count_eXXX
    3. pre_response_count_eXXX
    4. exact_delta_count_eXXX = exact protocol window count - same-length pre-window count
    5. exact_count_eXXX
    6. exact_pre_count_eXXX

    The labels and groups are stored in metadata, not embedded in X.
    """
    root = Path(root_path)
    response_window_s = float(response_window_ms) / 1000.0
    electrodes = _all_protocol_electrodes(root)
    if not electrodes:
        return PulseFeatureMatrix(
            X=np.zeros((0, 0), dtype=np.float32),
            metadata=[],
            electrodes=[],
            feature_names=[],
            response_window_ms=float(response_window_ms),
        )

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

    blocks: list[np.ndarray] = []
    metadata: list[PulseFeatureMetadata] = []
    row_index = 0

    for rec in discover_recording_dirs(root):
        windows_all = read_protocol_windows_for_recording(rec, root)
        if not windows_all:
            continue
        if condition_filter is not None:
            windows_all = [w for w in windows_all if w.condition == condition_filter]
            if not windows_all:
                continue
        windows, starts, ends, durations = _valid_protocol_arrays(windows_all)
        if not windows:
            continue

        spikes_by_electrode, _hz, duration_s = _load_spike_seconds_by_electrode(rec)
        n = len(windows)
        E = len(electrodes)
        X_rec = np.zeros((n, E * 6), dtype=np.float32)

        response_starts = ends
        response_ends = np.minimum(duration_s, ends + response_window_s) if duration_s > 0 else ends + response_window_s
        response_durations = np.maximum(response_ends - response_starts, 0.0)
        response_pre_starts = np.maximum(0.0, starts - response_durations)
        response_pre_ends = starts

        exact_pre_starts = np.maximum(0.0, starts - durations)
        exact_pre_ends = starts

        for j, electrode_id in enumerate(electrodes):
            times = spikes_by_electrode.get(electrode_id, np.asarray([], dtype=float))
            resp = _count_ranges(times, response_starts, response_ends).astype(np.float32)
            pre = _count_ranges(times, response_pre_starts, response_pre_ends).astype(np.float32)
            exact = _count_ranges(times, starts, ends).astype(np.float32)
            exact_pre = _count_ranges(times, exact_pre_starts, exact_pre_ends).astype(np.float32)
            X_rec[:, j] = resp - pre
            X_rec[:, E + j] = resp
            X_rec[:, 2 * E + j] = pre
            X_rec[:, 3 * E + j] = exact - exact_pre
            X_rec[:, 4 * E + j] = exact
            X_rec[:, 5 * E + j] = exact_pre

        for w in windows:
            metadata.append(
                PulseFeatureMetadata(
                    row_index=row_index,
                    recording_path=w.recording_path,
                    culture=w.culture,
                    date=w.date,
                    condition=w.condition,
                    target_type=w.target_type,
                    target_id=w.target_id,
                    pulse_index=int(w.pulse_index),
                    start_s=float(w.start_s),
                    end_s=float(w.end_s),
                    duration_s=float(w.duration_s),
                )
            )
            row_index += 1
        blocks.append(X_rec)

    X = np.vstack(blocks) if blocks else np.zeros((0, len(feature_names)), dtype=np.float32)
    return PulseFeatureMatrix(
        X=X,
        metadata=metadata,
        electrodes=electrodes,
        feature_names=feature_names,
        response_window_ms=float(response_window_ms),
    )


def _metadata_arrays(matrix: PulseFeatureMatrix) -> dict[str, np.ndarray]:
    return {
        "target_id": np.asarray([m.target_id if m.target_id is not None else -1 for m in matrix.metadata], dtype=int),
        "culture": np.asarray([m.culture for m in matrix.metadata], dtype=object),
        "condition": np.asarray([m.condition for m in matrix.metadata], dtype=object),
        "recording_path": np.asarray([m.recording_path for m in matrix.metadata], dtype=object),
        "pulse_index": np.asarray([m.pulse_index for m in matrix.metadata], dtype=int),
    }


def _centroid_predict_scores(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Fast standardize + nearest-centroid readout.

    This is intentionally simple and stable. It is a readout/separability probe, not a tuned classifier.
    """
    X_train = np.asarray(X_train, dtype=np.float32)
    X_test = np.asarray(X_test, dtype=np.float32)
    mean = X_train.mean(axis=0)
    std = X_train.std(axis=0)
    std[std < 1e-6] = 1.0
    Z_train = (X_train - mean) / std
    Z_test = (X_test - mean) / std
    classes = np.asarray(sorted(set(int(v) for v in y_train)), dtype=int)
    centers = np.vstack([Z_train[y_train == c].mean(axis=0) for c in classes]).astype(np.float32)
    distances = (
        (Z_test * Z_test).sum(axis=1)[:, None]
        + (centers * centers).sum(axis=1)[None, :]
        - 2.0 * (Z_test @ centers.T)
    )
    scores = -distances
    pred = classes[np.argmax(scores, axis=1)]
    return pred, scores, classes



def _top_k_accuracy_from_scores(y_true: np.ndarray, scores: np.ndarray, classes: np.ndarray, k: int = 3) -> float:
    if len(y_true) == 0 or scores.size == 0 or len(classes) == 0:
        return float("nan")
    kk = max(1, min(int(k), len(classes)))
    top_idx = np.argsort(scores, axis=1)[:, -kk:]
    top_labels = classes[top_idx]
    return float(np.mean(np.any(top_labels == y_true[:, None], axis=1)))

def _one_sided_high_p_value(observed: float, null_values: list[float]) -> float | None:
    clean = [float(v) for v in null_values if np.isfinite(v)]
    if not clean or not np.isfinite(observed):
        return None
    return float((1 + sum(v >= observed for v in clean)) / (len(clean) + 1))


def leave_one_culture_target_id_readout(
    matrix: PulseFeatureMatrix,
    condition_filter: str | None = None,
    n_label_shuffles: int = 20,
    seed: int = 23,
) -> dict[str, Any]:
    arrays = _metadata_arrays(matrix)
    X = matrix.X
    y = arrays["target_id"]
    groups = arrays["culture"].astype(str)
    conditions = arrays["condition"].astype(str)
    mask = y >= 0
    if condition_filter is not None:
        mask &= conditions == condition_filter
    X = X[mask]
    y = y[mask].astype(int)
    groups = groups[mask]
    conditions = conditions[mask]

    if len(X) == 0 or len(set(groups)) < 2 or len(set(y)) < 2:
        return {
            "task": "target_id_from_pulse_feature_vector_leave_one_culture_out",
            "condition_filter": condition_filter or "all",
            "sample_count": int(len(X)),
            "status": "not_enough_data",
        }

    global_classes = np.asarray(sorted(set(int(v) for v in y)), dtype=int)
    logo = LeaveOneGroupOut()
    fold_rows: list[dict[str, Any]] = []
    all_pred: list[np.ndarray] = []
    all_true: list[np.ndarray] = []
    all_scores: list[np.ndarray] = []
    all_seen: list[np.ndarray] = []

    for fold_idx, (train_idx, test_idx) in enumerate(logo.split(X, y, groups)):
        if len(set(y[train_idx])) < 2:
            continue
        pred, scores, train_classes = _centroid_predict_scores(X[train_idx], y[train_idx], X[test_idx])
        aligned_scores = np.full((len(test_idx), len(global_classes)), -1e9, dtype=np.float32)
        for j, c in enumerate(train_classes):
            loc = np.where(global_classes == c)[0]
            if len(loc):
                aligned_scores[:, int(loc[0])] = scores[:, j]
        seen = np.isin(y[test_idx], np.unique(y[train_idx]))
        seen_acc = float(accuracy_score(y[test_idx][seen], pred[seen])) if bool(np.any(seen)) else None
        fold_rows.append(
            {
                "fold": int(fold_idx),
                "heldout_culture": str(groups[test_idx][0]),
                "n_test": int(len(test_idx)),
                "condition_counts": {str(k): int(v) for k, v in zip(*np.unique(conditions[test_idx], return_counts=True))},
                "target_counts": {str(k): int(v) for k, v in zip(*np.unique(y[test_idx], return_counts=True))},
                "test_label_seen_fraction": float(np.mean(seen)),
                "accuracy": float(accuracy_score(y[test_idx], pred)),
                "seen_label_accuracy": seen_acc,
            }
        )
        all_pred.append(pred)
        all_true.append(y[test_idx])
        all_scores.append(aligned_scores)
        all_seen.append(seen)

    pred_all = np.concatenate(all_pred)
    true_all = np.concatenate(all_true)
    scores_all = np.vstack(all_scores)
    seen_all = np.concatenate(all_seen)
    observed_accuracy = float(accuracy_score(true_all, pred_all))
    observed_balanced = float(balanced_accuracy_score(true_all, pred_all))
    observed_seen_accuracy = float(accuracy_score(true_all[seen_all], pred_all[seen_all])) if bool(np.any(seen_all)) else None
    observed_top3 = float(_top_k_accuracy_from_scores(true_all, scores_all, global_classes, k=3))
    observed_seen_top3 = (
        float(_top_k_accuracy_from_scores(true_all[seen_all], scores_all[seen_all], global_classes, k=3))
        if bool(np.any(seen_all))
        else None
    )

    rng = np.random.default_rng(seed)
    shuffle_rows: list[dict[str, Any]] = []
    splits = list(logo.split(X, y, groups))
    for shuffle_idx in range(int(n_label_shuffles)):
        p_all: list[np.ndarray] = []
        t_all: list[np.ndarray] = []
        s_all: list[np.ndarray] = []
        seen_s_all: list[np.ndarray] = []
        for train_idx, test_idx in splits:
            y_train_shuffled = y[train_idx].copy()
            rng.shuffle(y_train_shuffled)
            if len(set(y_train_shuffled)) < 2:
                continue
            pred, scores, train_classes = _centroid_predict_scores(X[train_idx], y_train_shuffled, X[test_idx])
            aligned_scores = np.full((len(test_idx), len(global_classes)), -1e9, dtype=np.float32)
            for j, c in enumerate(train_classes):
                loc = np.where(global_classes == c)[0]
                if len(loc):
                    aligned_scores[:, int(loc[0])] = scores[:, j]
            seen = np.isin(y[test_idx], np.unique(y[train_idx]))
            p_all.append(pred)
            t_all.append(y[test_idx])
            s_all.append(aligned_scores)
            seen_s_all.append(seen)
        if not p_all:
            continue
        pp = np.concatenate(p_all)
        tt = np.concatenate(t_all)
        ss = np.vstack(s_all)
        seen_s = np.concatenate(seen_s_all)
        shuffle_rows.append(
            {
                "shuffle": int(shuffle_idx),
                "accuracy": float(accuracy_score(tt, pp)),
                "seen_label_accuracy": float(accuracy_score(tt[seen_s], pp[seen_s])) if bool(np.any(seen_s)) else None,
                "top3_accuracy": float(_top_k_accuracy_from_scores(tt, ss, global_classes, k=3)),
            }
        )

    null_seen = [float(r["seen_label_accuracy"]) for r in shuffle_rows if r.get("seen_label_accuracy") is not None]
    null_acc = [float(r["accuracy"]) for r in shuffle_rows]
    return {
        "task": "target_id_from_pulse_feature_vector_leave_one_culture_out",
        "condition_filter": condition_filter or "all",
        "sample_count": int(len(X)),
        "culture_count": int(len(set(groups))),
        "target_class_count": int(len(global_classes)),
        "feature_count": int(X.shape[1]),
        "readout": "standardized_nearest_centroid",
        "observed": {
            "accuracy": observed_accuracy,
            "balanced_accuracy": observed_balanced,
            "test_label_seen_fraction": float(np.mean(seen_all)),
            "seen_label_accuracy": observed_seen_accuracy,
            "top3_accuracy": observed_top3,
            "seen_label_top3_accuracy": observed_seen_top3,
        },
        "label_shuffle_baseline": {
            "shuffles": int(len(shuffle_rows)),
            "accuracy_median": float(np.median(null_acc)) if null_acc else None,
            "accuracy_q05": float(np.quantile(null_acc, 0.05)) if null_acc else None,
            "accuracy_q95": float(np.quantile(null_acc, 0.95)) if null_acc else None,
            "seen_label_accuracy_median": float(np.median(null_seen)) if null_seen else None,
            "seen_label_accuracy_q05": float(np.quantile(null_seen, 0.05)) if null_seen else None,
            "seen_label_accuracy_q95": float(np.quantile(null_seen, 0.95)) if null_seen else None,
            "p_value_accuracy_gt_shuffle": _one_sided_high_p_value(observed_accuracy, null_acc),
            "p_value_seen_label_accuracy_gt_shuffle": _one_sided_high_p_value(observed_seen_accuracy if observed_seen_accuracy is not None else float("nan"), null_seen),
        },
        "folds": fold_rows,
        "shuffle_rows": shuffle_rows,
        "honesty_note": "Target-ID readout is hard under leave-one-culture-out because many stimulated targets occur in only one culture. Report seen-label metrics separately from all-label metrics to avoid hiding this limitation.",
    }


def build_candidate_target_table(
    matrix: PulseFeatureMatrix,
    negative_per_pulse: int = 1,
    seed: int = 41,
) -> CandidateFeatureTable:
    """Build a binary target-vs-random-electrode readout table.

    Each pulse contributes the true target electrode as a positive candidate and sampled non-target
    electrodes from the same pulse/recording as negative candidates. Features are derived only from
    spike response values, not from the electrode id.
    """
    arrays = _metadata_arrays(matrix)
    y_target = arrays["target_id"]
    culture = arrays["culture"].astype(str)
    E = len(matrix.electrodes)
    if matrix.X.shape[1] < E * 3:
        return CandidateFeatureTable(
            X=np.zeros((0, 0), dtype=np.float32),
            y=np.zeros(0, dtype=int),
            culture=np.asarray([], dtype=object),
            metadata=[],
            feature_names=[],
        )
    response_delta = matrix.X[:, :E]
    response_count = matrix.X[:, E : 2 * E]
    pre_count = matrix.X[:, 2 * E : 3 * E]
    exact_delta = matrix.X[:, 3 * E : 4 * E] if matrix.X.shape[1] >= E * 4 else np.zeros_like(response_delta)

    order = np.argsort(response_delta, axis=1)
    ranks = np.empty_like(order, dtype=np.float32)
    ranks[np.arange(len(response_delta))[:, None], order] = np.arange(E, dtype=np.float32)
    percentile = (ranks + 1.0) / float(E)
    pulse_mean = response_delta.mean(axis=1)
    pulse_std = response_delta.std(axis=1)
    pulse_std[pulse_std < 1e-6] = 1.0
    pulse_max = response_delta.max(axis=1)

    rng = np.random.default_rng(seed)
    rows: list[list[float]] = []
    labels: list[int] = []
    groups: list[str] = []
    meta: list[dict[str, Any]] = []
    electrode_to_idx = {int(e): idx for idx, e in enumerate(matrix.electrodes)}
    negative_per_pulse = max(1, int(negative_per_pulse))

    for i, md in enumerate(matrix.metadata):
        target_id = int(y_target[i])
        if target_id not in electrode_to_idx:
            continue
        target_j = electrode_to_idx[target_id]
        available_neg = [j for j in range(E) if j != target_j]
        neg_js = list(rng.choice(available_neg, size=min(negative_per_pulse, len(available_neg)), replace=False))
        candidate_js = [target_j] + [int(j) for j in neg_js]
        candidate_labels = [1] + [0] * len(neg_js)
        for j, lab in zip(candidate_js, candidate_labels):
            rows.append(
                [
                    float(response_delta[i, j]),
                    float(response_count[i, j]),
                    float(pre_count[i, j]),
                    float(exact_delta[i, j]),
                    float(percentile[i, j]),
                    float((response_delta[i, j] - pulse_mean[i]) / pulse_std[i]),
                    float(pulse_mean[i]),
                    float(pulse_max[i]),
                ]
            )
            labels.append(int(lab))
            groups.append(str(culture[i]))
            meta.append(
                {
                    "pulse_row_index": int(i),
                    "recording_path": md.recording_path,
                    "culture": md.culture,
                    "condition": md.condition,
                    "target_id": target_id,
                    "candidate_electrode": int(matrix.electrodes[j]),
                    "is_target": int(lab),
                }
            )
    return CandidateFeatureTable(
        X=np.asarray(rows, dtype=np.float32),
        y=np.asarray(labels, dtype=int),
        culture=np.asarray(groups, dtype=object),
        metadata=meta,
        feature_names=[
            "candidate_response_delta_count",
            "candidate_response_count",
            "candidate_pre_response_count",
            "candidate_exact_delta_count",
            "candidate_response_delta_percentile_within_pulse",
            "candidate_response_delta_zscore_within_pulse",
            "pulse_mean_response_delta_count",
            "pulse_max_response_delta_count",
        ],
    )


def _binary_centroid_predict_scores(X_train: np.ndarray, y_train: np.ndarray, X_test: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    X_train = np.asarray(X_train, dtype=np.float32)
    X_test = np.asarray(X_test, dtype=np.float32)
    mean = X_train.mean(axis=0)
    std = X_train.std(axis=0)
    std[std < 1e-6] = 1.0
    Z_train = (X_train - mean) / std
    Z_test = (X_test - mean) / std
    center0 = Z_train[y_train == 0].mean(axis=0) if np.any(y_train == 0) else np.zeros(Z_train.shape[1], dtype=np.float32)
    center1 = Z_train[y_train == 1].mean(axis=0) if np.any(y_train == 1) else np.zeros(Z_train.shape[1], dtype=np.float32)
    d0 = ((Z_test - center0) ** 2).sum(axis=1)
    d1 = ((Z_test - center1) ** 2).sum(axis=1)
    score = d0 - d1  # positive means closer to target center
    pred = (score >= 0).astype(int)
    return pred, score


def leave_one_culture_candidate_readout(
    table: CandidateFeatureTable,
    n_label_shuffles: int = 20,
    seed: int = 29,
) -> dict[str, Any]:
    X = table.X
    y = table.y.astype(int)
    groups = table.culture.astype(str)
    if len(X) == 0 or len(set(groups)) < 2 or len(set(y)) < 2:
        return {
            "task": "target_vs_random_electrode_candidate_readout_leave_one_culture_out",
            "sample_count": int(len(X)),
            "status": "not_enough_data",
        }
    logo = LeaveOneGroupOut()
    splits = list(logo.split(X, y, groups))
    fold_rows: list[dict[str, Any]] = []
    pred_all: list[np.ndarray] = []
    true_all: list[np.ndarray] = []
    score_all: list[np.ndarray] = []
    for fold_idx, (train_idx, test_idx) in enumerate(splits):
        pred, score = _binary_centroid_predict_scores(X[train_idx], y[train_idx], X[test_idx])
        pred_all.append(pred)
        true_all.append(y[test_idx])
        score_all.append(score)
        fold_rows.append(
            {
                "fold": int(fold_idx),
                "heldout_culture": str(groups[test_idx][0]),
                "n_test": int(len(test_idx)),
                "positive_fraction": float(np.mean(y[test_idx])),
                "accuracy": float(accuracy_score(y[test_idx], pred)),
                "balanced_accuracy": float(balanced_accuracy_score(y[test_idx], pred)),
                "roc_auc": float(roc_auc_score(y[test_idx], score)) if len(set(y[test_idx])) == 2 else None,
            }
        )
    pred_obs = np.concatenate(pred_all)
    true_obs = np.concatenate(true_all)
    score_obs = np.concatenate(score_all)
    observed = {
        "accuracy": float(accuracy_score(true_obs, pred_obs)),
        "balanced_accuracy": float(balanced_accuracy_score(true_obs, pred_obs)),
        "roc_auc": float(roc_auc_score(true_obs, score_obs)),
    }

    rng = np.random.default_rng(seed)
    shuffle_rows: list[dict[str, Any]] = []
    for shuffle_idx in range(int(n_label_shuffles)):
        p_all: list[np.ndarray] = []
        t_all: list[np.ndarray] = []
        s_all: list[np.ndarray] = []
        for train_idx, test_idx in splits:
            y_train_shuffled = y[train_idx].copy()
            rng.shuffle(y_train_shuffled)
            pred, score = _binary_centroid_predict_scores(X[train_idx], y_train_shuffled, X[test_idx])
            p_all.append(pred)
            t_all.append(y[test_idx])
            s_all.append(score)
        pp = np.concatenate(p_all)
        tt = np.concatenate(t_all)
        ss = np.concatenate(s_all)
        shuffle_rows.append(
            {
                "shuffle": int(shuffle_idx),
                "accuracy": float(accuracy_score(tt, pp)),
                "balanced_accuracy": float(balanced_accuracy_score(tt, pp)),
                "roc_auc": float(roc_auc_score(tt, ss)),
            }
        )
    null_auc = [float(r["roc_auc"]) for r in shuffle_rows]
    null_bal = [float(r["balanced_accuracy"]) for r in shuffle_rows]
    return {
        "task": "target_vs_random_electrode_candidate_readout_leave_one_culture_out",
        "sample_count": int(len(X)),
        "pulse_count_used": int(sum(1 for r in table.metadata if int(r.get("is_target", 0)) == 1)),
        "culture_count": int(len(set(groups))),
        "positive_fraction": float(np.mean(y)),
        "feature_count": int(X.shape[1]),
        "readout": "standardized_nearest_centroid_binary",
        "observed": observed,
        "label_shuffle_baseline": {
            "shuffles": int(len(shuffle_rows)),
            "roc_auc_median": float(np.median(null_auc)) if null_auc else None,
            "roc_auc_q05": float(np.quantile(null_auc, 0.05)) if null_auc else None,
            "roc_auc_q95": float(np.quantile(null_auc, 0.95)) if null_auc else None,
            "balanced_accuracy_median": float(np.median(null_bal)) if null_bal else None,
            "balanced_accuracy_q05": float(np.quantile(null_bal, 0.05)) if null_bal else None,
            "balanced_accuracy_q95": float(np.quantile(null_bal, 0.95)) if null_bal else None,
            "p_value_roc_auc_gt_shuffle": _one_sided_high_p_value(observed["roc_auc"], null_auc),
            "p_value_balanced_accuracy_gt_shuffle": _one_sided_high_p_value(observed["balanced_accuracy"], null_bal),
        },
        "folds": fold_rows,
        "shuffle_rows": shuffle_rows,
        "honesty_note": "This binary readout asks whether the true target electrode response is separable from a same-pulse random non-target electrode under leave-one-culture-out evaluation. It is a stronger separability control than recording-level target percentiles, but still not a full task-performance BioGPU advantage claim.",
    }


def _write_metadata_csv(rows: list[Any], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(asdict(rows[0]).keys()) if rows else [f.name for f in PulseFeatureMetadata.__dataclass_fields__.values()]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def _write_dict_csv(rows: list[dict[str, Any]], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if fieldnames:
            writer.writeheader()
            writer.writerows(rows)


def _write_candidate_metadata_csv(table: CandidateFeatureTable, path: str | Path) -> None:
    _write_dict_csv(table.metadata, path)


def _safe_json(obj: Any) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False)


def render_readout_report(summary: dict[str, Any]) -> str:
    return f"""# Zenodo 14363732 — Pulse-level readout benchmark v1.5

## Purpose

v1.3 found real pulse-aligned target responses. v1.4 checked random-electrode and random-time controls.

v1.5 moves to train/test readouts:

1. Build one spike-response feature vector for every protocol pulse window.
2. Split train/test by held-out culture, not by random pulse.
3. Compare observed separability with label-shuffled baselines.
4. Report multiclass target-ID readout separately from binary target-vs-random-electrode separability.

## Summary

```json
{_safe_json(summary)}
```

## Interpretation rules

- `pulse_feature_matrix.npz` contains the full pulse-level feature matrix for all real protocol windows.
- `target_id_readout` is intentionally strict: many target IDs appear in only one culture, so leave-one-culture-out can include unseen labels. The report therefore separates all-label accuracy from seen-label accuracy.
- `candidate_target_readout` is the cleaner separability test: the model sees candidate electrode response features and must distinguish the true stimulated target electrode from a same-pulse random electrode.
- A result above shuffled baseline supports real biological separability. It is still not a claim that BioGPU outperforms silicon GPUs.
"""


def write_readout_outputs(
    root_path: str | Path,
    out_dir: str | Path,
    response_window_ms: float = 100.0,
    n_label_shuffles: int = 50,
    negative_per_pulse: int = 1,
    seed: int = 23,
    make_plots: bool = False,
    target_label_shuffles: int | None = None,
    candidate_label_shuffles: int | None = None,
) -> dict[str, Any]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    target_shuffle_count = int(1 if target_label_shuffles is None else target_label_shuffles)
    candidate_shuffle_count = int(n_label_shuffles if candidate_label_shuffles is None else candidate_label_shuffles)

    windows = discover_protocol_windows(root_path)
    protocol_summary = summarize_protocol_windows(windows)
    matrix = build_pulse_feature_matrix(root_path, response_window_ms=response_window_ms)
    arrays = _metadata_arrays(matrix)

    np.savez_compressed(
        out / "pulse_feature_matrix.npz",
        X=matrix.X,
        target_id=arrays["target_id"],
        culture=arrays["culture"],
        condition=arrays["condition"],
        recording_path=arrays["recording_path"],
        pulse_index=arrays["pulse_index"],
        electrodes=np.asarray(matrix.electrodes, dtype=int),
        feature_names=np.asarray(matrix.feature_names, dtype=object),
        response_window_ms=np.asarray([float(response_window_ms)], dtype=float),
    )
    _write_metadata_csv(matrix.metadata, out / "pulse_feature_metadata.csv")
    (out / "pulse_feature_columns.txt").write_text("\n".join(matrix.feature_names) + "\n", encoding="utf-8")

    target_all = leave_one_culture_target_id_readout(
        matrix,
        condition_filter=None,
        n_label_shuffles=target_shuffle_count,
        seed=seed,
    )
    target_light = leave_one_culture_target_id_readout(
        matrix,
        condition_filter="lightstim",
        n_label_shuffles=target_shuffle_count,
        seed=seed + 1,
    )
    table = build_candidate_target_table(matrix, negative_per_pulse=negative_per_pulse, seed=seed + 2)
    candidate = leave_one_culture_candidate_readout(table, n_label_shuffles=candidate_shuffle_count, seed=seed + 3)

    _write_candidate_metadata_csv(table, out / "candidate_target_readout_metadata.csv")
    np.savez_compressed(
        out / "candidate_target_readout_features.npz",
        X=table.X,
        y=table.y,
        culture=table.culture,
        feature_names=np.asarray(table.feature_names, dtype=object),
    )

    summary = {
        "task": "pulse_level_readout_v1_5",
        "protocol_summary": protocol_summary,
        "feature_matrix": {
            "pulse_count": int(matrix.X.shape[0]),
            "feature_count": int(matrix.X.shape[1]),
            "electrode_count": int(len(matrix.electrodes)),
            "response_window_ms": float(response_window_ms),
            "conditions": {str(k): int(v) for k, v in zip(*np.unique(arrays["condition"], return_counts=True))} if len(matrix.metadata) else {},
            "cultures": int(len(set(str(v) for v in arrays["culture"]))) if len(matrix.metadata) else 0,
        },
        "target_id_readout_all_conditions": {k: v for k, v in target_all.items() if k not in ("folds", "shuffle_rows")},
        "target_id_readout_lightstim_only": {k: v for k, v in target_light.items() if k not in ("folds", "shuffle_rows")},
        "candidate_target_readout": {k: v for k, v in candidate.items() if k not in ("folds", "shuffle_rows")},
        "shuffle_counts": {
            "target_id_label_shuffles": int(target_shuffle_count),
            "candidate_label_shuffles": int(candidate_shuffle_count),
        },
        "honesty_note": "v1.5 uses all real protocol pulse windows to build spike-response feature vectors. The cleanest positive result is candidate target-vs-random separability; target-ID multiclass remains limited by target/culture coverage.",
    }

    (out / "pulse_readout_summary.json").write_text(_safe_json(summary), encoding="utf-8")
    (out / "target_id_readout_all_conditions.json").write_text(_safe_json(target_all), encoding="utf-8")
    (out / "target_id_readout_lightstim_only.json").write_text(_safe_json(target_light), encoding="utf-8")
    (out / "candidate_target_readout_summary.json").write_text(_safe_json(candidate), encoding="utf-8")
    _write_dict_csv(target_all.get("folds", []), out / "target_id_readout_all_conditions_folds.csv")
    _write_dict_csv(target_all.get("shuffle_rows", []), out / "target_id_readout_all_conditions_label_shuffle.csv")
    _write_dict_csv(target_light.get("folds", []), out / "target_id_readout_lightstim_folds.csv")
    _write_dict_csv(target_light.get("shuffle_rows", []), out / "target_id_readout_lightstim_label_shuffle.csv")
    _write_dict_csv(candidate.get("folds", []), out / "candidate_target_readout_folds.csv")
    _write_dict_csv(candidate.get("shuffle_rows", []), out / "candidate_target_readout_label_shuffle.csv")
    (out / "PULSE_LEVEL_READOUT_REPORT.md").write_text(render_readout_report(summary), encoding="utf-8")

    if make_plots:
        _write_readout_plots(target_all, target_light, candidate, out)
    return summary


def _write_readout_plots(target_all: dict[str, Any], target_light: dict[str, Any], candidate: dict[str, Any], out: Path) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return

    cand_null = [r.get("roc_auc") for r in candidate.get("shuffle_rows", []) if r.get("roc_auc") is not None]
    cand_obs = candidate.get("observed", {}).get("roc_auc")
    if cand_null and cand_obs is not None:
        plt.figure(figsize=(7, 4))
        plt.hist(cand_null, bins=min(20, max(5, len(cand_null))))
        plt.axvline(float(cand_obs), linestyle="--")
        plt.xlabel("ROC AUC")
        plt.ylabel("Label-shuffle count")
        plt.title("Candidate target-vs-random readout vs shuffled baseline")
        plt.tight_layout()
        plt.savefig(out / "candidate_target_readout_shuffle_auc.png", dpi=150)
        plt.close()

    for name, result in (("all_conditions", target_all), ("lightstim", target_light)):
        null = [r.get("seen_label_accuracy") for r in result.get("shuffle_rows", []) if r.get("seen_label_accuracy") is not None]
        obs = result.get("observed", {}).get("seen_label_accuracy")
        if null and obs is not None:
            plt.figure(figsize=(7, 4))
            plt.hist(null, bins=min(20, max(5, len(null))))
            plt.axvline(float(obs), linestyle="--")
            plt.xlabel("Seen-label accuracy")
            plt.ylabel("Label-shuffle count")
            plt.title(f"Target-ID readout ({name}) vs shuffled baseline")
            plt.tight_layout()
            plt.savefig(out / f"target_id_readout_{name}_shuffle_seen_accuracy.png", dpi=150)
            plt.close()
