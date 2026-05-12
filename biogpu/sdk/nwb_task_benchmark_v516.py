"""BioSDK DANDI/NWB task benchmark, v5.16."""
from __future__ import annotations

import csv
import json
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import h5py
import numpy as np
from sklearn.model_selection import StratifiedKFold

from biogpu.sdk.nwb_task_validation_v515 import find_local_nwb_samples_v515, validate_nwb_task_sample_v515


DEFAULT_OUT = Path("outputs/v516_dandi_nwb_task_benchmark")


@dataclass(frozen=True)
class NWBTaskFeatureRowV516:
    nwb_path: str
    stimulus_id: str
    start_s: float
    end_s: float
    duration_s: float
    label: str
    source_interval_path: str
    total_spikes: int
    unit_counts: tuple[int, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class NWBTaskFeatureMatrixV516:
    features: np.ndarray
    labels: np.ndarray
    feature_names: tuple[str, ...]
    rows: tuple[NWBTaskFeatureRowV516, ...]
    unit_ids: tuple[str, ...]
    nwb_path: str
    claim_boundary: str


def _read_unit_spike_times(nwb_path: str | Path) -> tuple[tuple[str, ...], list[np.ndarray]]:
    unit_ids: list[str] = []
    unit_spike_times: list[np.ndarray] = []
    with h5py.File(nwb_path, "r") as nwb_file:
        if "units" not in nwb_file or "spike_times" not in nwb_file["units"] or "spike_times_index" not in nwb_file["units"]:
            raise ValueError("NWB file must expose /units/spike_times and /units/spike_times_index")
        spike_times = np.asarray(nwb_file["units/spike_times"][:], dtype=float)
        spike_index = np.asarray(nwb_file["units/spike_times_index"][:], dtype=int)
        raw_ids = np.asarray(nwb_file["units/id"][:], dtype=object) if "id" in nwb_file["units"] else np.arange(len(spike_index))
        start_index = 0
        for unit_index, stop_index in enumerate(spike_index):
            unit_ids.append(str(raw_ids[unit_index]))
            unit_spike_times.append(spike_times[start_index:stop_index])
            start_index = int(stop_index)
    return tuple(unit_ids), unit_spike_times


def build_nwb_task_feature_matrix_v516(nwb_path: str | Path) -> NWBTaskFeatureMatrixV516:
    path = Path(nwb_path)
    validation_report = validate_nwb_task_sample_v515(path)
    validation = validation_report["validation"]
    if validation.get("gate_status") != "dandi_nwb_task_sample_validated":
        raise ValueError(f"NWB task sample is not validated: {validation.get('gate_status')}")
    unit_ids, unit_spike_times = _read_unit_spike_times(path)
    feature_names: list[str] = []
    for unit_id in unit_ids:
        feature_names.extend([f"unit_{unit_id}_spike_count", f"unit_{unit_id}_rate_hz"])
    feature_rows: list[list[float]] = []
    labels: list[str] = []
    rows: list[NWBTaskFeatureRowV516] = []
    for window in validation_report["windows"]:
        label = window.get("label")
        if label is None:
            continue
        start_s = float(window["start_s"])
        end_s = float(window["end_s"])
        duration_s = max(end_s - start_s, 1e-9)
        unit_counts: list[int] = []
        features: list[float] = []
        for spike_times in unit_spike_times:
            count = int(np.sum((spike_times >= start_s) & (spike_times <= end_s)))
            unit_counts.append(count)
            features.extend([float(count), float(count) / duration_s])
        feature_rows.append(features)
        label_text = str(label)
        labels.append(label_text)
        rows.append(
            NWBTaskFeatureRowV516(
                nwb_path=str(path),
                stimulus_id=str(window.get("stimulus_id")),
                start_s=start_s,
                end_s=end_s,
                duration_s=duration_s,
                label=label_text,
                source_interval_path=str(window.get("source_interval_path")),
                total_spikes=int(sum(unit_counts)),
                unit_counts=tuple(unit_counts),
            )
        )
    feature_matrix = np.asarray(feature_rows, dtype=float) if feature_rows else np.zeros((0, len(feature_names)), dtype=float)
    return NWBTaskFeatureMatrixV516(
        features=feature_matrix,
        labels=np.asarray(labels, dtype=object),
        feature_names=tuple(feature_names),
        rows=tuple(rows),
        unit_ids=unit_ids,
        nwb_path=str(path),
        claim_boundary="v5.16 uses spike-count/rate features from one validated DANDI/NWB sample; it is a single-sample SDK benchmark, not multi-dataset proof.",
    )


def _standardize_train_test(train_features: np.ndarray, test_features: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mean = train_features.mean(axis=0)
    std = train_features.std(axis=0)
    std[std == 0] = 1.0
    return (train_features - mean) / std, (test_features - mean) / std


def _centroid_predict(train_features: np.ndarray, train_labels: np.ndarray, test_features: np.ndarray) -> np.ndarray:
    classes = np.array(sorted(set(str(value) for value in train_labels.tolist())), dtype=object)
    centroids = []
    for class_name in classes:
        centroids.append(train_features[train_labels == class_name].mean(axis=0))
    centroid_matrix = np.vstack(centroids)
    distances = ((test_features[:, None, :] - centroid_matrix[None, :, :]) ** 2).sum(axis=2)
    return classes[np.argmin(distances, axis=1)]


def _balanced_accuracy(true_labels: np.ndarray, predicted_labels: np.ndarray) -> float:
    recalls: list[float] = []
    for class_name in sorted(set(str(value) for value in true_labels.tolist())):
        mask = true_labels == class_name
        if np.any(mask):
            recalls.append(float(np.mean(predicted_labels[mask] == class_name)))
    return float(np.mean(recalls)) if recalls else 0.0


def _one_sided_high_p_value(observed: float, null_values: list[float]) -> float | None:
    if not null_values:
        return None
    return float((1 + sum(1 for value in null_values if value >= observed)) / (1 + len(null_values)))


def stratified_load_readout_v516(
    matrix: NWBTaskFeatureMatrixV516,
    n_splits: int = 5,
    label_shuffles: int = 100,
    seed: int = 516,
) -> dict[str, Any]:
    if matrix.features.shape[0] == 0 or len(matrix.labels) == 0:
        return {"status": "not_enough_data", "sample_count": 0, "claim_boundary": matrix.claim_boundary}
    label_counts = Counter(str(value) for value in matrix.labels.tolist())
    if len(label_counts) < 2:
        return {"status": "not_enough_labels", "sample_count": int(len(matrix.labels)), "label_counts": dict(sorted(label_counts.items())), "claim_boundary": matrix.claim_boundary}
    fold_count = min(int(n_splits), min(label_counts.values()))
    if fold_count < 2:
        return {"status": "not_enough_samples_per_label", "sample_count": int(len(matrix.labels)), "label_counts": dict(sorted(label_counts.items())), "claim_boundary": matrix.claim_boundary}

    splitter = StratifiedKFold(n_splits=fold_count, shuffle=True, random_state=int(seed))
    true_all: list[str] = []
    predicted_all: list[str] = []
    fold_indices: list[tuple[np.ndarray, np.ndarray]] = []
    folds: list[dict[str, Any]] = []
    for fold_number, (train_index, test_index) in enumerate(splitter.split(matrix.features, matrix.labels)):
        train_features, test_features = _standardize_train_test(matrix.features[train_index], matrix.features[test_index])
        predicted = _centroid_predict(train_features, matrix.labels[train_index], test_features)
        true = matrix.labels[test_index]
        true_all.extend(str(value) for value in true.tolist())
        predicted_all.extend(str(value) for value in predicted.tolist())
        fold_indices.append((train_index, test_index))
        folds.append(
            {
                "fold": int(fold_number),
                "n_train": int(len(train_index)),
                "n_test": int(len(test_index)),
                "accuracy": float(np.mean(predicted == true)),
                "balanced_accuracy": _balanced_accuracy(true, predicted),
            }
        )
    true_array = np.asarray(true_all, dtype=object)
    predicted_array = np.asarray(predicted_all, dtype=object)
    observed = {
        "accuracy": float(np.mean(predicted_array == true_array)),
        "balanced_accuracy": _balanced_accuracy(true_array, predicted_array),
    }
    rng = np.random.default_rng(int(seed))
    null_balanced: list[float] = []
    for _ in range(int(label_shuffles)):
        shuffle_true: list[str] = []
        shuffle_predicted: list[str] = []
        for train_index, test_index in fold_indices:
            shuffled_labels = np.array(matrix.labels[train_index], dtype=object)
            rng.shuffle(shuffled_labels)
            train_features, test_features = _standardize_train_test(matrix.features[train_index], matrix.features[test_index])
            predicted = _centroid_predict(train_features, shuffled_labels, test_features)
            shuffle_true.extend(str(value) for value in matrix.labels[test_index].tolist())
            shuffle_predicted.extend(str(value) for value in predicted.tolist())
        null_balanced.append(_balanced_accuracy(np.asarray(shuffle_true, dtype=object), np.asarray(shuffle_predicted, dtype=object)))
    return {
        "status": "single_sample_stratified_task_readout",
        "readout": "standardized_nearest_centroid_stratified_load_readout",
        "sample_count": int(len(matrix.labels)),
        "feature_count": int(matrix.features.shape[1]),
        "unit_count": int(len(matrix.unit_ids)),
        "label_counts": dict(sorted(label_counts.items())),
        "fold_count": int(fold_count),
        "observed": observed,
        "label_shuffle_baseline": {
            "shuffles": int(len(null_balanced)),
            "balanced_accuracy_median": float(np.median(null_balanced)) if null_balanced else None,
            "balanced_accuracy_q05": float(np.quantile(null_balanced, 0.05)) if null_balanced else None,
            "balanced_accuracy_q95": float(np.quantile(null_balanced, 0.95)) if null_balanced else None,
            "p_value_balanced_accuracy_gt_shuffle": _one_sided_high_p_value(observed["balanced_accuracy"], null_balanced),
        },
        "folds": folds,
        "claim_boundary": matrix.claim_boundary,
        "honesty_note": "Exploratory single-sample DANDI/NWB task readout. It proves SDK parser+feature+readout workflow on one public NWB sample only, not full BioSDK or biological OS readiness.",
    }


def build_dandi_nwb_sdk_benchmark_v516(root: str | Path = ".", label_shuffles: int = 100, seed: int = 516) -> dict[str, Any]:
    project_root = Path(root).resolve()
    samples = find_local_nwb_samples_v515(project_root)
    if not samples:
        return {
            "version": "v5.16",
            "overall_status": "dandi_nwb_benchmark_missing_sample",
            "active_phase": "biosdk_public_core",
            "bic_os_phase_locked": True,
            "sample_count": 0,
            "claim_boundary": "No local DANDI/NWB sample is available for v5.16 benchmark.",
        }
    matrix = build_nwb_task_feature_matrix_v516(samples[0])
    readout = stratified_load_readout_v516(matrix, label_shuffles=label_shuffles, seed=seed)
    overall_status = "dandi_nwb_sdk_task_benchmark_available" if readout.get("status") == "single_sample_stratified_task_readout" else "dandi_nwb_sdk_task_benchmark_incomplete"
    return {
        "version": "v5.16",
        "phase": "dandi_nwb_sdk_task_benchmark",
        "overall_status": overall_status,
        "active_phase": "biosdk_public_core",
        "bic_os_phase_locked": True,
        "nwb_path": matrix.nwb_path,
        "sample_count": int(matrix.features.shape[0]),
        "unit_count": int(len(matrix.unit_ids)),
        "feature_count": int(matrix.features.shape[1]),
        "label_counts": dict(sorted(Counter(str(value) for value in matrix.labels.tolist()).items())),
        "readout_status": readout.get("status"),
        "observed": readout.get("observed"),
        "label_shuffle_baseline": readout.get("label_shuffle_baseline"),
        "honesty_note": readout.get("honesty_note"),
        "claim_boundary": matrix.claim_boundary,
    }


def write_dandi_nwb_benchmark_outputs_v516(
    root: str | Path = ".",
    out_dir: str | Path = DEFAULT_OUT,
    label_shuffles: int = 100,
    seed: int = 516,
) -> dict[str, str]:
    project_root = Path(root).resolve()
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    samples = find_local_nwb_samples_v515(project_root)
    if not samples:
        summary = build_dandi_nwb_sdk_benchmark_v516(project_root, label_shuffles=label_shuffles, seed=seed)
        summary_path = out / "V516_DANDI_NWB_TASK_BENCHMARK_SUMMARY.json"
        summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        return {"summary_json": str(summary_path)}
    matrix = build_nwb_task_feature_matrix_v516(samples[0])
    readout = stratified_load_readout_v516(matrix, label_shuffles=label_shuffles, seed=seed)
    summary = build_dandi_nwb_sdk_benchmark_v516(project_root, label_shuffles=label_shuffles, seed=seed)
    paths = {
        "summary_json": out / "V516_DANDI_NWB_TASK_BENCHMARK_SUMMARY.json",
        "feature_matrix_npz": out / "V516_DANDI_NWB_TASK_FEATURE_MATRIX.npz",
        "trial_features_csv": out / "V516_DANDI_NWB_TRIAL_FEATURES.csv",
        "readout_json": out / "V516_DANDI_NWB_TASK_READOUT.json",
        "markdown_report": out / "BIOGPU_V516_DANDI_NWB_TASK_BENCHMARK_REPORT.md",
    }
    paths["summary_json"].write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["readout_json"].write_text(json.dumps(readout, indent=2, ensure_ascii=False), encoding="utf-8")
    np.savez_compressed(
        paths["feature_matrix_npz"],
        features=matrix.features.astype(np.float32),
        labels=matrix.labels,
        feature_names=np.asarray(matrix.feature_names, dtype=object),
        unit_ids=np.asarray(matrix.unit_ids, dtype=object),
        stimulus_id=np.asarray([row.stimulus_id for row in matrix.rows], dtype=object),
        nwb_path=np.asarray([matrix.nwb_path], dtype=object),
    )
    _write_trial_features_csv(paths["trial_features_csv"], matrix)
    paths["markdown_report"].write_text(_markdown_report(summary), encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}


def _write_trial_features_csv(path: Path, matrix: NWBTaskFeatureMatrixV516) -> None:
    fields = ["stimulus_id", "start_s", "end_s", "duration_s", "label", "total_spikes", *matrix.feature_names]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row_index, row in enumerate(matrix.rows):
            payload: dict[str, Any] = {
                "stimulus_id": row.stimulus_id,
                "start_s": row.start_s,
                "end_s": row.end_s,
                "duration_s": row.duration_s,
                "label": row.label,
                "total_spikes": row.total_spikes,
            }
            for feature_index, feature_name in enumerate(matrix.feature_names):
                payload[feature_name] = float(matrix.features[row_index, feature_index])
            writer.writerow(payload)


def _markdown_report(summary: dict[str, Any]) -> str:
    observed = summary.get("observed") or {}
    shuffle = summary.get("label_shuffle_baseline") or {}
    lines = [
        "# BioGPU-Core v5.16 DANDI/NWB Task Benchmark",
        "",
        f"- Overall status: `{summary['overall_status']}`",
        f"- Sample count: `{summary.get('sample_count')}`",
        f"- Unit count: `{summary.get('unit_count')}`",
        f"- Feature count: `{summary.get('feature_count')}`",
        f"- Observed balanced accuracy: `{observed.get('balanced_accuracy')}`",
        f"- Shuffle median balanced accuracy: `{shuffle.get('balanced_accuracy_median')}`",
        f"- Shuffle p-value: `{shuffle.get('p_value_balanced_accuracy_gt_shuffle')}`",
        f"- BiC OS locked: `{summary.get('bic_os_phase_locked')}`",
        "",
        "## Boundary",
        "",
        summary.get("claim_boundary", ""),
        "",
        "## Honesty Note",
        "",
        summary.get("honesty_note", ""),
        "",
    ]
    return "\n".join(lines)
