"""BioSDK Allen visual-coding orientation benchmark, v5.20."""
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

from biogpu.sdk.allen_orientation_v518 import find_allen_nwb_samples_v518, validate_allen_orientation_nwb_v518


DEFAULT_OUT = Path("outputs/v520_allen_orientation_benchmark")
DEFAULT_INTERVAL_PATH = "/intervals/drifting_gratings_presentations"


@dataclass(frozen=True)
class AllenOrientationFeatureRowV520:
    nwb_path: str
    stimulus_id: str
    start_s: float
    end_s: float
    duration_s: float
    orientation_deg: str
    temporal_frequency_hz: str | None
    source_interval_path: str
    total_spikes: int
    unit_counts: tuple[int, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AllenOrientationFeatureMatrixV520:
    features: np.ndarray
    labels: np.ndarray
    feature_names: tuple[str, ...]
    rows: tuple[AllenOrientationFeatureRowV520, ...]
    unit_ids: tuple[str, ...]
    nwb_path: str
    interval_path: str
    claim_boundary: str


def find_validated_allen_samples_v520(root: str | Path = ".") -> list[Path]:
    samples: list[Path] = []
    for path in find_allen_nwb_samples_v518(root):
        try:
            report = validate_allen_orientation_nwb_v518(path)["report"]
        except Exception:
            continue
        if report.get("gate_status") == "allen_orientation_sample_validated":
            samples.append(Path(path))
    return samples


def _format_label(value: float) -> str:
    if float(value).is_integer():
        return str(int(value))
    return f"{float(value):.3f}".rstrip("0").rstrip(".")


def _read_orientation_windows(nwb_file: h5py.File, interval_path: str = DEFAULT_INTERVAL_PATH, max_windows: int = 800) -> list[dict[str, Any]]:
    key = interval_path.strip("/")
    if key not in nwb_file:
        raise KeyError(f"Allen interval path not found: {interval_path}")
    group = nwb_file[key]
    required = ("start_time", "stop_time", "orientation")
    missing = [name for name in required if name not in group]
    if missing:
        raise ValueError(f"{interval_path} missing required columns: {missing}")
    starts = np.asarray(group["start_time"][:], dtype=float)
    stops = np.asarray(group["stop_time"][:], dtype=float)
    orientations = np.asarray(group["orientation"][:], dtype=float)
    temporal_frequency = np.asarray(group["temporal_frequency"][:], dtype=float) if "temporal_frequency" in group else None
    rows: list[dict[str, Any]] = []
    for row_index, (start_s, end_s, orientation) in enumerate(zip(starts, stops, orientations)):
        if not np.isfinite(orientation):
            continue
        tf_value = None
        if temporal_frequency is not None and np.isfinite(temporal_frequency[row_index]):
            tf_value = _format_label(float(temporal_frequency[row_index]))
        rows.append(
            {
                "stimulus_id": f"{interval_path.strip('/').replace('/', '_')}_{row_index}",
                "start_s": float(start_s),
                "end_s": float(end_s),
                "orientation_deg": _format_label(float(orientation)),
                "temporal_frequency_hz": tf_value,
                "source_interval_path": interval_path,
            }
        )
        if len(rows) >= int(max_windows):
            break
    return rows


def _select_top_unit_indices(nwb_file: h5py.File, top_units: int) -> tuple[np.ndarray, tuple[str, ...]]:
    units = nwb_file["units"]
    spike_index = np.asarray(units["spike_times_index"][:], dtype=int)
    if "firing_rate" in units:
        scores = np.asarray(units["firing_rate"][:], dtype=float)
        scores = np.nan_to_num(scores, nan=0.0, posinf=0.0, neginf=0.0)
    else:
        starts = np.concatenate(([0], spike_index[:-1]))
        scores = spike_index - starts
    unit_count = len(spike_index)
    selected = np.argsort(scores)[::-1][: max(1, min(int(top_units), unit_count))]
    selected = np.asarray(sorted(selected.tolist()), dtype=int)
    raw_ids = np.asarray(units["id"][:], dtype=object) if "id" in units else np.arange(unit_count)
    unit_ids = tuple(str(raw_ids[index]) for index in selected)
    return selected, unit_ids


def build_allen_orientation_feature_matrix_v520(
    nwb_path: str | Path,
    top_units: int = 64,
    max_windows: int = 800,
    interval_path: str = DEFAULT_INTERVAL_PATH,
) -> AllenOrientationFeatureMatrixV520:
    path = Path(nwb_path)
    validation = validate_allen_orientation_nwb_v518(path)["report"]
    if validation.get("gate_status") != "allen_orientation_sample_validated":
        raise ValueError(f"Allen sample is not validated: {validation.get('gate_status')}")
    with h5py.File(path, "r") as nwb_file:
        if "units" not in nwb_file or "spike_times" not in nwb_file["units"] or "spike_times_index" not in nwb_file["units"]:
            raise ValueError("Allen NWB file must expose /units/spike_times and /units/spike_times_index")
        windows = _read_orientation_windows(nwb_file, interval_path=interval_path, max_windows=max_windows)
        if not windows:
            raise ValueError("No finite orientation windows found")
        starts = np.asarray([row["start_s"] for row in windows], dtype=float)
        stops = np.asarray([row["end_s"] for row in windows], dtype=float)
        durations = np.maximum(stops - starts, 1e-9)
        selected_indices, unit_ids = _select_top_unit_indices(nwb_file, top_units=top_units)
        spike_times_dataset = nwb_file["units/spike_times"]
        spike_index = np.asarray(nwb_file["units/spike_times_index"][:], dtype=int)
        feature_columns: list[np.ndarray] = []
        unit_count_rows: list[np.ndarray] = []
        for unit_index in selected_indices:
            start_index = int(spike_index[unit_index - 1]) if unit_index > 0 else 0
            stop_index = int(spike_index[unit_index])
            spike_times = np.asarray(spike_times_dataset[start_index:stop_index], dtype=float)
            counts = np.searchsorted(spike_times, stops, side="right") - np.searchsorted(spike_times, starts, side="left")
            counts = counts.astype(float)
            feature_columns.append(counts)
            feature_columns.append(counts / durations)
            unit_count_rows.append(counts.astype(int))
        features = np.vstack(feature_columns).T if feature_columns else np.zeros((len(windows), 0), dtype=float)
        feature_names: list[str] = []
        for unit_id in unit_ids:
            feature_names.extend([f"unit_{unit_id}_spike_count", f"unit_{unit_id}_rate_hz"])
        labels = np.asarray([row["orientation_deg"] for row in windows], dtype=object)
        unit_counts_matrix = np.vstack(unit_count_rows).T if unit_count_rows else np.zeros((len(windows), 0), dtype=int)
        rows = tuple(
            AllenOrientationFeatureRowV520(
                nwb_path=str(path),
                stimulus_id=str(window["stimulus_id"]),
                start_s=float(window["start_s"]),
                end_s=float(window["end_s"]),
                duration_s=float(max(window["end_s"] - window["start_s"], 1e-9)),
                orientation_deg=str(window["orientation_deg"]),
                temporal_frequency_hz=window.get("temporal_frequency_hz"),
                source_interval_path=str(window["source_interval_path"]),
                total_spikes=int(np.sum(unit_counts_matrix[row_index])),
                unit_counts=tuple(int(value) for value in unit_counts_matrix[row_index].tolist()),
            )
            for row_index, window in enumerate(windows)
        )
    return AllenOrientationFeatureMatrixV520(
        features=features.astype(float),
        labels=labels,
        feature_names=tuple(feature_names),
        rows=rows,
        unit_ids=unit_ids,
        nwb_path=str(path),
        interval_path=interval_path,
        claim_boundary="v5.20 uses one Allen visual-coding NWB session and a bounded top-unit orientation readout; it is public neurophysiology SDK evidence, not full BioSDK or BiC OS readiness.",
    )


def _standardize_train_test(train_features: np.ndarray, test_features: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mean = train_features.mean(axis=0)
    std = train_features.std(axis=0)
    std[std == 0] = 1.0
    return (train_features - mean) / std, (test_features - mean) / std


def _centroid_predict(train_features: np.ndarray, train_labels: np.ndarray, test_features: np.ndarray) -> np.ndarray:
    classes = np.array(sorted(set(str(value) for value in train_labels.tolist())), dtype=object)
    centroids = [train_features[train_labels == class_name].mean(axis=0) for class_name in classes]
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


def stratified_orientation_readout_v520(
    matrix: AllenOrientationFeatureMatrixV520,
    n_splits: int = 5,
    label_shuffles: int = 100,
    seed: int = 520,
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
        folds.append({"fold": int(fold_number), "n_train": int(len(train_index)), "n_test": int(len(test_index)), "accuracy": float(np.mean(predicted == true)), "balanced_accuracy": _balanced_accuracy(true, predicted)})
    true_array = np.asarray(true_all, dtype=object)
    predicted_array = np.asarray(predicted_all, dtype=object)
    observed = {"accuracy": float(np.mean(predicted_array == true_array)), "balanced_accuracy": _balanced_accuracy(true_array, predicted_array)}
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
        "status": "single_sample_allen_orientation_readout",
        "readout": "standardized_nearest_centroid_orientation_readout",
        "sample_count": int(len(matrix.labels)),
        "feature_count": int(matrix.features.shape[1]),
        "unit_count": int(len(matrix.unit_ids)),
        "label_counts": dict(sorted(label_counts.items())) if label_counts else {},
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
        "honesty_note": "Exploratory single-session Allen visual-coding orientation readout with bounded top-unit features. It proves parser+feature+readout workflow on one public Allen NWB session only.",
    }


def build_allen_orientation_sdk_benchmark_v520(root: str | Path = ".", top_units: int = 64, max_windows: int = 800, label_shuffles: int = 100, seed: int = 520) -> dict[str, Any]:
    samples = find_validated_allen_samples_v520(root)
    if not samples:
        return {
            "version": "v5.20",
            "overall_status": "allen_orientation_benchmark_missing_validated_sample",
            "active_phase": "biosdk_public_core",
            "bic_os_phase_locked": True,
            "sample_count": 0,
            "claim_boundary": "No validated Allen orientation sample is available for v5.20 benchmark.",
        }
    matrix = build_allen_orientation_feature_matrix_v520(samples[0], top_units=top_units, max_windows=max_windows)
    readout = stratified_orientation_readout_v520(matrix, label_shuffles=label_shuffles, seed=seed)
    overall_status = "allen_orientation_sdk_benchmark_available" if readout.get("status") == "single_sample_allen_orientation_readout" else "allen_orientation_sdk_benchmark_incomplete"
    return {
        "version": "v5.20",
        "phase": "allen_orientation_sdk_benchmark",
        "overall_status": overall_status,
        "active_phase": "biosdk_public_core",
        "bic_os_phase_locked": True,
        "nwb_path": matrix.nwb_path,
        "interval_path": matrix.interval_path,
        "sample_count": int(matrix.features.shape[0]),
        "selected_unit_count": int(len(matrix.unit_ids)),
        "feature_count": int(matrix.features.shape[1]),
        "label_counts": dict(sorted(Counter(str(value) for value in matrix.labels.tolist()).items())),
        "readout_status": readout.get("status"),
        "observed": readout.get("observed"),
        "label_shuffle_baseline": readout.get("label_shuffle_baseline"),
        "top_units": int(top_units),
        "max_windows": int(max_windows),
        "honesty_note": readout.get("honesty_note"),
        "claim_boundary": matrix.claim_boundary,
    }


def write_allen_orientation_benchmark_outputs_v520(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT, top_units: int = 64, max_windows: int = 800, label_shuffles: int = 100, seed: int = 520) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    samples = find_validated_allen_samples_v520(root)
    summary = build_allen_orientation_sdk_benchmark_v520(root, top_units=top_units, max_windows=max_windows, label_shuffles=label_shuffles, seed=seed)
    summary_path = out / "V520_ALLEN_ORIENTATION_BENCHMARK_SUMMARY.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    if not samples or summary.get("overall_status") != "allen_orientation_sdk_benchmark_available":
        return {"summary_json": str(summary_path)}
    matrix = build_allen_orientation_feature_matrix_v520(samples[0], top_units=top_units, max_windows=max_windows)
    readout = stratified_orientation_readout_v520(matrix, label_shuffles=label_shuffles, seed=seed)
    paths = {
        "summary_json": summary_path,
        "feature_matrix_npz": out / "V520_ALLEN_ORIENTATION_FEATURE_MATRIX.npz",
        "trial_features_csv": out / "V520_ALLEN_ORIENTATION_TRIAL_FEATURES.csv",
        "readout_json": out / "V520_ALLEN_ORIENTATION_READOUT.json",
        "markdown_report": out / "BIOGPU_V520_ALLEN_ORIENTATION_BENCHMARK_REPORT.md",
    }
    paths["readout_json"].write_text(json.dumps(readout, indent=2, ensure_ascii=False), encoding="utf-8")
    np.savez_compressed(paths["feature_matrix_npz"], features=matrix.features.astype(np.float32), labels=matrix.labels, feature_names=np.asarray(matrix.feature_names, dtype=object), unit_ids=np.asarray(matrix.unit_ids, dtype=object), stimulus_id=np.asarray([row.stimulus_id for row in matrix.rows], dtype=object), nwb_path=np.asarray([matrix.nwb_path], dtype=object))
    _write_trial_features_csv(paths["trial_features_csv"], matrix)
    paths["markdown_report"].write_text(_markdown_report(summary), encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}


def _write_trial_features_csv(path: Path, matrix: AllenOrientationFeatureMatrixV520) -> None:
    fields = ["stimulus_id", "start_s", "end_s", "duration_s", "orientation_deg", "temporal_frequency_hz", "total_spikes", *matrix.feature_names]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row_index, row in enumerate(matrix.rows):
            payload: dict[str, Any] = {"stimulus_id": row.stimulus_id, "start_s": row.start_s, "end_s": row.end_s, "duration_s": row.duration_s, "orientation_deg": row.orientation_deg, "temporal_frequency_hz": row.temporal_frequency_hz, "total_spikes": row.total_spikes}
            for feature_index, feature_name in enumerate(matrix.feature_names):
                payload[feature_name] = float(matrix.features[row_index, feature_index])
            writer.writerow(payload)


def _markdown_report(summary: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# BioGPU-Core v5.20 Allen Orientation Benchmark",
            "",
            f"- Overall status: `{summary['overall_status']}`",
            f"- Samples/windows: `{summary.get('sample_count', 0)}`",
            f"- Selected units: `{summary.get('selected_unit_count', 0)}`",
            f"- Feature count: `{summary.get('feature_count', 0)}`",
            f"- Readout status: `{summary.get('readout_status')}`",
            f"- Observed balanced accuracy: `{(summary.get('observed') or {}).get('balanced_accuracy')}`",
            f"- Shuffle p-value: `{(summary.get('label_shuffle_baseline') or {}).get('p_value_balanced_accuracy_gt_shuffle')}`",
            f"- BiC OS locked: `{summary['bic_os_phase_locked']}`",
            "",
            "## Boundary",
            "",
            summary["claim_boundary"],
            "",
        ]
    )
