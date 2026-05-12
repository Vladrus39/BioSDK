"""Raw-native stability and target coverage audit, v5.9."""
from __future__ import annotations

import csv
import itertools
import json
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np


DEFAULT_V58_MATRIX = Path("outputs/v58_raw_native_benchmark/V58_RAW_NATIVE_FEATURE_MATRIX.npz")
DEFAULT_V58_METADATA = Path("outputs/v58_raw_native_benchmark/V58_RAW_NATIVE_EVENT_METADATA.csv")
CLAIM_BOUNDARY_V59 = "raw-native event-window stability and target coverage audit only; no live biology, no GPU replacement, no energy claim and no v15/v50 raw equivalence claim"


@dataclass(frozen=True)
class RawNativeMetadataRowV59:
    row_index: int
    source_file: str
    condition: str
    target_id: str
    recording_id: str
    event_index: int
    timestamp_s: float

    @property
    def target_label(self) -> str:
        target = self.target_id if self.target_id else "unknown"
        condition = self.condition if self.condition else "unknown"
        return f"{condition}:{target}"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RawNativeDatasetV59:
    features: np.ndarray
    feature_names: tuple[str, ...]
    rows: tuple[RawNativeMetadataRowV59, ...]
    claim_boundary: str = CLAIM_BOUNDARY_V59


def _int_value(value: Any, default: int = 0) -> int:
    try:
        return int(float(str(value if value is not None else default).strip()))
    except ValueError:
        return int(default)


def _float_value(value: Any, default: float = 0.0) -> float:
    try:
        return float(str(value if value is not None else default).strip())
    except ValueError:
        return float(default)


def _summary(values: list[float]) -> dict[str, Any]:
    if not values:
        return {"count": 0, "mean": None, "median": None, "q05": None, "q95": None, "min": None, "max": None}
    values_array = np.asarray(values, dtype=np.float64)
    return {
        "count": int(values_array.shape[0]),
        "mean": float(np.mean(values_array)),
        "median": float(np.median(values_array)),
        "q05": float(np.quantile(values_array, 0.05)),
        "q95": float(np.quantile(values_array, 0.95)),
        "min": float(np.min(values_array)),
        "max": float(np.max(values_array)),
    }


def _unit_vector(vector: np.ndarray) -> np.ndarray:
    norm = float(np.linalg.norm(vector))
    return vector / norm if norm > 0 else vector


def _global_standardize(features: np.ndarray) -> np.ndarray:
    if features.size == 0:
        return features.astype(np.float32)
    mean = np.nanmean(features, axis=0)
    std = np.nanstd(features, axis=0)
    std[std == 0] = 1.0
    return np.nan_to_num((features - mean) / std).astype(np.float32)


def _standardize_train_test(train_features: np.ndarray, test_features: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mean = np.nanmean(train_features, axis=0)
    std = np.nanstd(train_features, axis=0)
    std[std == 0] = 1.0
    return np.nan_to_num((train_features - mean) / std).astype(np.float32), np.nan_to_num((test_features - mean) / std).astype(np.float32)


def _nearest_centroid_predict(train_features: np.ndarray, train_labels: np.ndarray, test_features: np.ndarray) -> np.ndarray:
    classes = np.asarray(sorted(set(str(value) for value in train_labels.tolist())), dtype=object)
    centroid_rows = []
    for class_label in classes:
        centroid_rows.append(train_features[train_labels == class_label].mean(axis=0))
    centroids = np.vstack(centroid_rows)
    distances = ((test_features[:, None, :] - centroids[None, :, :]) ** 2).sum(axis=2)
    return classes[np.argmin(distances, axis=1)]


def _balanced_accuracy(true_labels: np.ndarray, predicted_labels: np.ndarray) -> float:
    recalls: list[float] = []
    for class_label in sorted(set(str(value) for value in true_labels.tolist())):
        mask = true_labels == class_label
        if np.any(mask):
            recalls.append(float(np.mean(predicted_labels[mask] == class_label)))
    return float(np.mean(recalls)) if recalls else 0.0


def _one_sided_high_p_value(observed: float, null_values: list[float]) -> float | None:
    if not null_values:
        return None
    return float((1 + sum(1 for value in null_values if value >= observed)) / (1 + len(null_values)))


def _target_signal_status(observed_value: float | None, shuffle_median: float | None, p_value: float | None) -> str:
    if observed_value is None or shuffle_median is None or p_value is None:
        return "baseline_not_available"
    if observed_value > shuffle_median and p_value <= 0.05:
        return "exploratory_supported"
    return "not_supported"


def load_raw_native_dataset_v59(
    matrix_npz: str | Path = DEFAULT_V58_MATRIX,
    metadata_csv: str | Path = DEFAULT_V58_METADATA,
) -> RawNativeDatasetV59:
    matrix_path = Path(matrix_npz)
    metadata_path = Path(metadata_csv)
    if not matrix_path.exists():
        raise FileNotFoundError(f"missing v5.8 feature matrix: {matrix_path}")
    if not metadata_path.exists():
        raise FileNotFoundError(f"missing v5.8 event metadata: {metadata_path}")

    loaded = np.load(matrix_path, allow_pickle=True)
    features = np.asarray(loaded["X"], dtype=np.float32)
    feature_names = tuple(str(value) for value in loaded.get("feature_names", np.asarray([], dtype=object)).tolist())
    if not feature_names and features.ndim == 2:
        feature_names = tuple(f"feature_{feature_index:04d}" for feature_index in range(features.shape[1]))

    rows: list[RawNativeMetadataRowV59] = []
    with metadata_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for csv_row in reader:
            rows.append(
                RawNativeMetadataRowV59(
                    row_index=_int_value(csv_row.get("row_index"), len(rows)),
                    source_file=str(csv_row.get("source_file", "")),
                    condition=str(csv_row.get("condition", "")),
                    target_id=str(csv_row.get("target_id", "")),
                    recording_id=str(csv_row.get("recording_id", "")),
                    event_index=_int_value(csv_row.get("event_index"), 0),
                    timestamp_s=_float_value(csv_row.get("timestamp_s"), 0.0),
                )
            )
    if features.shape[0] != len(rows):
        raise ValueError(f"v5.8 feature row count mismatch: matrix={features.shape[0]} metadata={len(rows)}")
    return RawNativeDatasetV59(features=features, feature_names=feature_names, rows=tuple(rows))


def target_eligibility_rows_v59(dataset: RawNativeDatasetV59, min_groups_per_target: int = 2) -> list[dict[str, Any]]:
    by_label: dict[str, list[RawNativeMetadataRowV59]] = defaultdict(list)
    for row in dataset.rows:
        by_label[row.target_label].append(row)

    output_rows: list[dict[str, Any]] = []
    for target_label, rows in sorted(by_label.items()):
        groups = sorted(set(row.source_file for row in rows))
        condition, _, target_id = target_label.partition(":")
        eligible = len(groups) >= int(min_groups_per_target)
        output_rows.append(
            {
                "target_label": target_label,
                "condition": condition,
                "target_id": target_id,
                "row_count": int(len(rows)),
                "recording_group_count": int(len(groups)),
                "eligible_for_group_heldout_target_readout": bool(eligible),
                "status": "eligible" if eligible else "single_recording_only",
            }
        )
    return output_rows


def split_half_repeatability_v59(dataset: RawNativeDatasetV59, min_events_per_recording: int = 4) -> dict[str, Any]:
    if dataset.features.shape[0] == 0:
        return {"status": "not_enough_data", "claim_boundary": dataset.claim_boundary}

    standardized = _global_standardize(dataset.features)
    rows_by_group: dict[str, list[int]] = defaultdict(list)
    for row_index, row in enumerate(dataset.rows):
        rows_by_group[row.source_file].append(row_index)

    split_rows: list[dict[str, Any]] = []
    group_centroids: list[tuple[str, str, str, np.ndarray]] = []
    for source_file, row_indices in sorted(rows_by_group.items()):
        if len(row_indices) < int(min_events_per_recording):
            continue
        first_half = row_indices[::2]
        second_half = row_indices[1::2]
        if not first_half or not second_half:
            continue
        first_centroid = _unit_vector(standardized[first_half].mean(axis=0))
        second_centroid = _unit_vector(standardized[second_half].mean(axis=0))
        full_centroid = _unit_vector(standardized[row_indices].mean(axis=0))
        representative = dataset.rows[row_indices[0]]
        split_rows.append(
            {
                "source_file": source_file,
                "condition": representative.condition,
                "target_label": representative.target_label,
                "event_count": int(len(row_indices)),
                "split_half_cosine": float(np.dot(first_centroid, second_centroid)),
            }
        )
        group_centroids.append((source_file, representative.condition, representative.target_label, full_centroid))

    cross_all: list[float] = []
    cross_same_condition: list[float] = []
    cross_different_condition: list[float] = []
    for left_centroid, right_centroid in itertools.combinations(group_centroids, 2):
        similarity = float(np.dot(left_centroid[3], right_centroid[3]))
        cross_all.append(similarity)
        if left_centroid[1] == right_centroid[1]:
            cross_same_condition.append(similarity)
        else:
            cross_different_condition.append(similarity)

    within_values = [float(row["split_half_cosine"]) for row in split_rows]
    cross_values = cross_all
    pairwise_probability = None
    if within_values and cross_values:
        comparisons = [1.0 if within_value > cross_value else 0.0 for within_value in within_values for cross_value in cross_values]
        pairwise_probability = float(np.mean(comparisons))

    status = "split_half_repeatability_available" if within_values and cross_values else "not_enough_recording_groups"
    within_summary = _summary(within_values)
    cross_summary = _summary(cross_values)
    return {
        "status": status,
        "recording_group_count": int(len(rows_by_group)),
        "valid_split_count": int(len(split_rows)),
        "within_recording_split_cosine": within_summary,
        "cross_recording_centroid_cosine": cross_summary,
        "cross_recording_same_condition_cosine": _summary(cross_same_condition),
        "cross_recording_different_condition_cosine": _summary(cross_different_condition),
        "median_margin_within_vs_cross": None if within_summary["median"] is None or cross_summary["median"] is None else float(within_summary["median"] - cross_summary["median"]),
        "pairwise_probability_within_gt_cross": pairwise_probability,
        "by_recording": split_rows,
        "claim_boundary": dataset.claim_boundary,
        "honesty_note": "High split-half repeatability shows raw event-window extraction is internally stable within recordings. It is not target-ID decoding proof and not raw equivalence for v15/v50 rows.",
    }


def _eligible_label_set(dataset: RawNativeDatasetV59, condition: str, min_groups_per_target: int) -> set[str]:
    group_sets: dict[str, set[str]] = defaultdict(set)
    for row in dataset.rows:
        if condition != "all" and row.condition != condition:
            continue
        group_sets[row.target_label].add(row.source_file)
    return {target_label for target_label, groups in group_sets.items() if len(groups) >= int(min_groups_per_target)}


def group_heldout_target_readout_v59(
    dataset: RawNativeDatasetV59,
    condition: str = "elecstim",
    min_groups_per_target: int = 2,
    label_shuffles: int = 200,
    seed: int = 59,
) -> dict[str, Any]:
    eligible_labels = _eligible_label_set(dataset, condition, min_groups_per_target)
    if len(eligible_labels) < 2:
        return {
            "status": "not_enough_repeated_targets",
            "eligible_target_label_count": int(len(eligible_labels)),
            "condition": condition,
            "claim_boundary": dataset.claim_boundary,
        }

    selected_indices = [row_index for row_index, row in enumerate(dataset.rows) if row.target_label in eligible_labels and (condition == "all" or row.condition == condition)]
    selected_features = dataset.features[selected_indices]
    labels = np.asarray([dataset.rows[row_index].target_label for row_index in selected_indices], dtype=object)
    groups = np.asarray([dataset.rows[row_index].source_file for row_index in selected_indices], dtype=object)
    unique_groups = sorted(set(str(value) for value in groups.tolist()))

    true_all: list[str] = []
    pred_all: list[str] = []
    folds: list[dict[str, Any]] = []
    fold_indices: list[tuple[np.ndarray, np.ndarray]] = []
    for fold_index, heldout_group in enumerate(unique_groups):
        test_mask = groups == heldout_group
        train_mask = ~test_mask
        if len(set(str(value) for value in labels[train_mask].tolist())) < len(eligible_labels):
            continue
        train_features, test_features = _standardize_train_test(selected_features[train_mask], selected_features[test_mask])
        predicted = _nearest_centroid_predict(train_features, labels[train_mask], test_features)
        true_values = labels[test_mask]
        true_all.extend(str(value) for value in true_values.tolist())
        pred_all.extend(str(value) for value in predicted.tolist())
        fold_indices.append((np.where(train_mask)[0], np.where(test_mask)[0]))
        folds.append(
            {
                "fold": int(fold_index),
                "heldout_recording": heldout_group,
                "target_label": str(true_values[0]) if len(set(true_values.tolist())) == 1 else "mixed",
                "n_test": int(np.sum(test_mask)),
                "accuracy": float(np.mean(predicted == true_values)),
            }
        )

    if not true_all:
        return {
            "status": "no_valid_group_folds",
            "eligible_target_label_count": int(len(eligible_labels)),
            "condition": condition,
            "claim_boundary": dataset.claim_boundary,
        }

    true_array = np.asarray(true_all, dtype=object)
    pred_array = np.asarray(pred_all, dtype=object)
    observed = {
        "accuracy": float(np.mean(pred_array == true_array)),
        "balanced_accuracy": _balanced_accuracy(true_array, pred_array),
    }

    rng = np.random.default_rng(int(seed))
    null_balanced: list[float] = []
    for _shuffle_index in range(max(0, int(label_shuffles))):
        shuffle_true: list[str] = []
        shuffle_pred: list[str] = []
        for train_indices, test_indices in fold_indices:
            shuffled_train_labels = np.asarray(labels[train_indices], dtype=object).copy()
            rng.shuffle(shuffled_train_labels)
            train_features, test_features = _standardize_train_test(selected_features[train_indices], selected_features[test_indices])
            predicted = _nearest_centroid_predict(train_features, shuffled_train_labels, test_features)
            shuffle_true.extend(str(value) for value in labels[test_indices].tolist())
            shuffle_pred.extend(str(value) for value in predicted.tolist())
        null_balanced.append(_balanced_accuracy(np.asarray(shuffle_true, dtype=object), np.asarray(shuffle_pred, dtype=object)))

    shuffle_median = float(np.median(null_balanced)) if null_balanced else None
    p_value = _one_sided_high_p_value(observed["balanced_accuracy"], null_balanced)
    return {
        "status": "group_heldout_target_readout",
        "target_signal_status": _target_signal_status(observed["balanced_accuracy"], shuffle_median, p_value),
        "condition": condition,
        "sample_count": int(len(labels)),
        "feature_count": int(selected_features.shape[1]),
        "eligible_target_labels": sorted(eligible_labels),
        "eligible_target_label_count": int(len(eligible_labels)),
        "recording_group_count": int(len(unique_groups)),
        "valid_fold_count": int(len(folds)),
        "readout": "standardized_nearest_centroid_group_heldout_target",
        "observed": observed,
        "label_shuffle_baseline": {
            "shuffles": int(len(null_balanced)),
            "balanced_accuracy_median": shuffle_median,
            "balanced_accuracy_q05": float(np.quantile(null_balanced, 0.05)) if null_balanced else None,
            "balanced_accuracy_q95": float(np.quantile(null_balanced, 0.95)) if null_balanced else None,
            "p_value_balanced_accuracy_gt_shuffle": p_value,
        },
        "folds": folds,
        "claim_boundary": dataset.claim_boundary,
        "honesty_note": "This target-ID readout is restricted to targets with repeated raw recordings. Single-recording targets are excluded from the held-out target claim.",
    }


def target_fingerprint_similarity_v59(
    dataset: RawNativeDatasetV59,
    condition: str = "elecstim",
    min_groups_per_target: int = 2,
    label_shuffles: int = 200,
    seed: int = 159,
) -> dict[str, Any]:
    eligible_labels = _eligible_label_set(dataset, condition, min_groups_per_target)
    if len(eligible_labels) < 2:
        return {
            "status": "not_enough_repeated_targets",
            "eligible_target_label_count": int(len(eligible_labels)),
            "condition": condition,
            "claim_boundary": dataset.claim_boundary,
        }

    selected_indices = [row_index for row_index, row in enumerate(dataset.rows) if row.target_label in eligible_labels and (condition == "all" or row.condition == condition)]
    selected_features = _global_standardize(dataset.features[selected_indices])
    selected_rows = [dataset.rows[row_index] for row_index in selected_indices]

    rows_by_group: dict[str, list[int]] = defaultdict(list)
    for row_index, row in enumerate(selected_rows):
        rows_by_group[row.source_file].append(row_index)

    centroids: list[tuple[str, str, np.ndarray]] = []
    for source_file, row_indices in sorted(rows_by_group.items()):
        target_label = selected_rows[row_indices[0]].target_label
        centroids.append((source_file, target_label, _unit_vector(selected_features[row_indices].mean(axis=0))))

    positive_similarities, negative_similarities = _target_pair_similarities(centroids, [target_label for _source_file, target_label, _centroid in centroids])
    if not positive_similarities or not negative_similarities:
        return {
            "status": "not_enough_pair_contrasts",
            "eligible_target_label_count": int(len(eligible_labels)),
            "condition": condition,
            "claim_boundary": dataset.claim_boundary,
        }

    observed_margin = float(np.mean(positive_similarities) - np.mean(negative_similarities))
    pairwise_probability = float(np.mean([1.0 if positive > negative else 0.0 for positive in positive_similarities for negative in negative_similarities]))
    rng = np.random.default_rng(int(seed))
    base_labels = np.asarray([target_label for _source_file, target_label, _centroid in centroids], dtype=object)
    null_margins: list[float] = []
    for _shuffle_index in range(max(0, int(label_shuffles))):
        shuffled_labels = base_labels.copy()
        rng.shuffle(shuffled_labels)
        shuffled_positive, shuffled_negative = _target_pair_similarities(centroids, [str(value) for value in shuffled_labels.tolist()])
        if shuffled_positive and shuffled_negative:
            null_margins.append(float(np.mean(shuffled_positive) - np.mean(shuffled_negative)))

    shuffle_median = float(np.median(null_margins)) if null_margins else None
    p_value = _one_sided_high_p_value(observed_margin, null_margins)
    return {
        "status": "target_fingerprint_similarity",
        "target_signal_status": _target_signal_status(observed_margin, shuffle_median, p_value),
        "condition": condition,
        "eligible_target_labels": sorted(eligible_labels),
        "eligible_target_label_count": int(len(eligible_labels)),
        "recording_group_count": int(len(centroids)),
        "positive_pair_count": int(len(positive_similarities)),
        "negative_pair_count": int(len(negative_similarities)),
        "observed": {
            "positive_similarity": _summary(positive_similarities),
            "negative_similarity": _summary(negative_similarities),
            "mean_margin_positive_minus_negative": observed_margin,
            "pairwise_probability_positive_gt_negative": pairwise_probability,
        },
        "label_shuffle_baseline": {
            "shuffles": int(len(null_margins)),
            "margin_median": shuffle_median,
            "margin_q05": float(np.quantile(null_margins, 0.05)) if null_margins else None,
            "margin_q95": float(np.quantile(null_margins, 0.95)) if null_margins else None,
            "p_value_margin_gt_shuffle": p_value,
        },
        "claim_boundary": dataset.claim_boundary,
        "honesty_note": "Target fingerprint similarity compares repeated-target recording centroids against different-target recording centroids. Sparse repeated targets limit conclusion strength.",
    }


def _target_pair_similarities(centroids: list[tuple[str, str, np.ndarray]], labels: list[str]) -> tuple[list[float], list[float]]:
    positive: list[float] = []
    negative: list[float] = []
    for left_index, right_index in itertools.combinations(range(len(centroids)), 2):
        similarity = float(np.dot(centroids[left_index][2], centroids[right_index][2]))
        if labels[left_index] == labels[right_index]:
            positive.append(similarity)
        else:
            negative.append(similarity)
    return positive, negative


def build_raw_native_stability_audit_v59(
    dataset: RawNativeDatasetV59,
    min_groups_per_target: int = 2,
    label_shuffles: int = 200,
    seed: int = 59,
) -> dict[str, Any]:
    eligibility = target_eligibility_rows_v59(dataset, min_groups_per_target=min_groups_per_target)
    repeatability = split_half_repeatability_v59(dataset)
    target_readout = group_heldout_target_readout_v59(
        dataset,
        condition="elecstim",
        min_groups_per_target=min_groups_per_target,
        label_shuffles=label_shuffles,
        seed=seed,
    )
    fingerprint = target_fingerprint_similarity_v59(
        dataset,
        condition="elecstim",
        min_groups_per_target=min_groups_per_target,
        label_shuffles=label_shuffles,
        seed=seed + 100,
    )

    condition_counts = Counter(row.condition for row in dataset.rows)
    target_counts = Counter(row.target_label for row in dataset.rows)
    eligible_targets = [row for row in eligibility if row["eligible_for_group_heldout_target_readout"]]
    target_signal_statuses = [str(target_readout.get("target_signal_status", "unknown")), str(fingerprint.get("target_signal_status", "unknown"))]
    if repeatability.get("status") == "split_half_repeatability_available" and all(status == "not_supported" for status in target_signal_statuses):
        overall_status = "raw_native_repeatability_available_target_signal_not_supported"
    elif repeatability.get("status") == "split_half_repeatability_available":
        overall_status = "raw_native_stability_audit_available"
    else:
        overall_status = "raw_native_stability_audit_limited"

    summary = {
        "version": "v5.9",
        "overall_status": overall_status,
        "feature_row_count": int(dataset.features.shape[0]),
        "feature_count": int(dataset.features.shape[1]) if dataset.features.ndim == 2 else 0,
        "recording_group_count": int(len(set(row.source_file for row in dataset.rows))),
        "condition_counts": dict(sorted(condition_counts.items())),
        "target_label_count": int(len(target_counts)),
        "eligible_repeated_target_label_count": int(len(eligible_targets)),
        "eligible_repeated_target_labels": [str(row["target_label"]) for row in eligible_targets],
        "split_half_repeatability_status": repeatability.get("status"),
        "split_half_cosine_median": (repeatability.get("within_recording_split_cosine") or {}).get("median"),
        "cross_recording_cosine_median": (repeatability.get("cross_recording_centroid_cosine") or {}).get("median"),
        "split_vs_cross_median_margin": repeatability.get("median_margin_within_vs_cross"),
        "target_readout_status": target_readout.get("status"),
        "target_readout_signal_status": target_readout.get("target_signal_status"),
        "target_readout_balanced_accuracy": (target_readout.get("observed") or {}).get("balanced_accuracy"),
        "target_readout_shuffle_p_value": (target_readout.get("label_shuffle_baseline") or {}).get("p_value_balanced_accuracy_gt_shuffle"),
        "target_fingerprint_status": fingerprint.get("status"),
        "target_fingerprint_signal_status": fingerprint.get("target_signal_status"),
        "target_fingerprint_margin": (fingerprint.get("observed") or {}).get("mean_margin_positive_minus_negative"),
        "target_fingerprint_shuffle_p_value": (fingerprint.get("label_shuffle_baseline") or {}).get("p_value_margin_gt_shuffle"),
        "label_shuffles": int(label_shuffles),
        "claim_boundary": dataset.claim_boundary,
        "honesty_note": "v5.9 confirms raw event-window repeatability and audits target-level limits. It does not turn sparse repeated-target evidence into a target decoding claim.",
    }
    return {
        "summary": summary,
        "eligibility_rows": eligibility,
        "repeatability": repeatability,
        "target_readout": target_readout,
        "target_fingerprint": fingerprint,
    }


def write_raw_native_stability_outputs_v59(audit: dict[str, Any], out_dir: str | Path) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary_json": out / "V59_RAW_NATIVE_STABILITY_SUMMARY.json",
        "target_eligibility_csv": out / "V59_RAW_NATIVE_TARGET_ELIGIBILITY.csv",
        "split_half_json": out / "V59_RAW_NATIVE_SPLIT_HALF_REPEATABILITY.json",
        "split_half_by_recording_csv": out / "V59_RAW_NATIVE_SPLIT_HALF_BY_RECORDING.csv",
        "target_readout_json": out / "V59_RAW_NATIVE_TARGET_READOUT.json",
        "target_fingerprint_json": out / "V59_RAW_NATIVE_TARGET_FINGERPRINT.json",
        "markdown_report": out / "BIOGPU_V59_RAW_NATIVE_STABILITY_AUDIT_REPORT.md",
    }
    paths["summary_json"].write_text(json.dumps(audit["summary"], indent=2, ensure_ascii=False), encoding="utf-8")
    _write_rows_csv(paths["target_eligibility_csv"], audit["eligibility_rows"])
    paths["split_half_json"].write_text(json.dumps(audit["repeatability"], indent=2, ensure_ascii=False), encoding="utf-8")
    _write_rows_csv(paths["split_half_by_recording_csv"], audit["repeatability"].get("by_recording", []))
    paths["target_readout_json"].write_text(json.dumps(audit["target_readout"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["target_fingerprint_json"].write_text(json.dumps(audit["target_fingerprint"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["markdown_report"].write_text(_markdown_report_v59(audit), encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}


def _write_rows_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = list(rows[0].keys()) if rows else ["empty"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _markdown_report_v59(audit: dict[str, Any]) -> str:
    summary = audit["summary"]
    repeatability = audit["repeatability"]
    target_readout = audit["target_readout"]
    fingerprint = audit["target_fingerprint"]
    lines = [
        "# BioGPU-Core v5.9 Raw-Native Stability Audit",
        "",
        "## Summary",
        "",
        f"- Overall status: `{summary['overall_status']}`",
        f"- Feature rows: `{summary['feature_row_count']}`",
        f"- Feature count: `{summary['feature_count']}`",
        f"- Recording groups: `{summary['recording_group_count']}`",
        f"- Eligible repeated target labels: `{summary['eligible_repeated_target_labels']}`",
        "",
        "## Split-Half Repeatability",
        "",
        f"- Status: `{repeatability.get('status')}`",
        f"- Within-recording split cosine median: `{summary.get('split_half_cosine_median')}`",
        f"- Cross-recording centroid cosine median: `{summary.get('cross_recording_cosine_median')}`",
        f"- Median margin: `{summary.get('split_vs_cross_median_margin')}`",
        "",
        "## Target Audit",
        "",
        f"- Target readout status: `{target_readout.get('status')}`",
        f"- Target readout signal status: `{target_readout.get('target_signal_status')}`",
        f"- Target readout balanced accuracy: `{summary.get('target_readout_balanced_accuracy')}`",
        f"- Target readout p-value: `{summary.get('target_readout_shuffle_p_value')}`",
        f"- Fingerprint signal status: `{fingerprint.get('target_signal_status')}`",
        f"- Fingerprint margin: `{summary.get('target_fingerprint_margin')}`",
        f"- Fingerprint p-value: `{summary.get('target_fingerprint_shuffle_p_value')}`",
        "",
        "## Claim Boundary",
        "",
        summary["claim_boundary"],
        "",
        "## Interpretation",
        "",
        "v5.9 supports the claim that raw event-window feature extraction is internally repeatable within recordings. It does not support a strong target-ID decoding claim on the current raw subset because repeated target coverage is sparse and the target-level readouts are not statistically strong.",
        "",
    ]
    return "\n".join(lines)
