"""Raw-native HDF5 event-window feature benchmark, v5.8."""
from __future__ import annotations

import csv
import json
import re
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np


DEFAULT_RAW_ROOT = Path("data/external/raw_hdf5")
DEFAULT_RAW_EVENT_CANDIDATES = Path("outputs/v56_raw_hdf5_structure/V56_TTL_EVENT_CANDIDATES.csv")


@dataclass(frozen=True)
class RawNativeEventSourceV58:
    source_file: str
    hdf5_path: str
    stream: str
    entity: str
    label: str
    condition: str
    target_id: str
    date: str
    culture: str
    recording_id: str
    event_count: int
    median_interval_s: float | None
    candidate_kind: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RawNativeEventFeatureRowV58:
    row_index: int
    source_file: str
    stream: str
    entity: str
    condition: str
    target_id: str
    date: str
    culture: str
    recording_id: str
    event_index: int
    timestamp_us: int
    timestamp_s: float
    sample_index: int
    sample_rate_hz: float
    window_pre_ms: float
    window_post_ms: float
    channel_count: int
    feature_count: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RawNativeFeatureMatrixV58:
    X: np.ndarray
    feature_names: tuple[str, ...]
    rows: tuple[RawNativeEventFeatureRowV58, ...]
    sources: tuple[RawNativeEventSourceV58, ...]
    skipped_event_count: int
    skipped_source_count: int
    read_error_count: int
    read_errors: tuple[str, ...]
    window_pre_ms: float
    window_post_ms: float
    max_events_per_recording: int
    claim_boundary: str


def _path_parts(path: str) -> list[str]:
    return [part for part in re.split(r"[\\/]+", str(path)) if part]


def _candidate_path(raw_root: str | Path, source_file: str) -> Path:
    return Path(raw_root).joinpath(*_path_parts(source_file))


def _normalize_recording_id(source_file: str) -> str:
    parts = _path_parts(source_file)
    stem = Path(parts[-1] if parts else source_file).stem
    return re.sub(r"_D-00144$", "", stem, flags=re.IGNORECASE)


def _extract_date(source_file: str) -> str:
    for part in _path_parts(source_file):
        if re.match(r"\d{2}-\d{2}-\d{4}$", part):
            return part
    return ""


def _extract_culture(source_file: str) -> str:
    for part in _path_parts(source_file):
        match = re.match(r"(.+?_\d+DIV)", part, flags=re.IGNORECASE)
        if match:
            return match.group(1)
    return ""


def _extract_target_id(source_file: str) -> str:
    match = re.search(r"(?:LightStim[_-]*Spot|Spot|ElecStim|Stim|stim)(\d+)", source_file, flags=re.IGNORECASE)
    return match.group(1) if match else ""


def _condition_from_candidate(candidate_kind: str, source_file: str) -> str:
    text = f"{candidate_kind} {source_file}".lower()
    if "light" in text or "spot" in text or "digital" in text:
        return "lightstim"
    if "electrical" in text or "elecstim" in text or "stim" in text:
        return "elecstim"
    return "unknown"


def _int_or_zero(value: Any) -> int:
    try:
        return int(float(str(value or "0").strip()))
    except ValueError:
        return 0


def _float_or_none(value: Any) -> float | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def load_primary_event_sources_v58(
    raw_event_csv: str | Path = DEFAULT_RAW_EVENT_CANDIDATES,
    raw_root: str | Path = DEFAULT_RAW_ROOT,
) -> tuple[RawNativeEventSourceV58, ...]:
    csv_path = Path(raw_event_csv)
    if not csv_path.exists():
        return tuple()
    grouped: dict[str, list[dict[str, str]]] = {}
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            source_file = row.get("file", "")
            if source_file:
                grouped.setdefault(source_file, []).append(row)

    sources: list[RawNativeEventSourceV58] = []
    for source_file, rows in sorted(grouped.items()):
        primary = sorted(
            rows,
            key=lambda row: (-_int_or_zero(row.get("event_count")), str(row.get("stream", "")), str(row.get("entity", ""))),
        )[0]
        candidate_kind = str(primary.get("candidate_kind", ""))
        sources.append(
            RawNativeEventSourceV58(
                source_file=source_file,
                hdf5_path=str(_candidate_path(raw_root, source_file)),
                stream=str(primary.get("stream", "")),
                entity=str(primary.get("entity", "")),
                label=str(primary.get("label", "")),
                condition=_condition_from_candidate(candidate_kind, source_file),
                target_id=_extract_target_id(source_file),
                date=_extract_date(source_file),
                culture=_extract_culture(source_file),
                recording_id=_normalize_recording_id(source_file),
                event_count=_int_or_zero(primary.get("event_count")),
                median_interval_s=_float_or_none(primary.get("median_interval_s")),
                candidate_kind=candidate_kind,
            )
        )
    return tuple(sources)


def _select_evenly(values: np.ndarray, max_count: int) -> np.ndarray:
    if max_count <= 0 or len(values) <= max_count:
        return values
    indices = np.linspace(0, len(values) - 1, int(max_count), dtype=int)
    return values[sorted(set(int(index) for index in indices))]


def _sample_rate_hz(channel_data: Any, recording_group: Any) -> float:
    sample_count = int(channel_data.shape[1]) if len(channel_data.shape) >= 2 else 0
    duration_us = 0
    if recording_group is not None and "Duration" in recording_group.attrs:
        duration_us = int(recording_group.attrs.get("Duration", 0))
    if duration_us > 0 and sample_count > 0:
        return float(sample_count / (duration_us / 1_000_000.0))
    return 20_000.0


def _feature_names(channel_count: int) -> tuple[str, ...]:
    names: list[str] = []
    for prefix in ("delta_mean", "delta_abs_mean", "delta_rms", "response_ptp"):
        for channel_index in range(channel_count):
            names.append(f"{prefix}_ch{channel_index:03d}")
    return tuple(names)


def _window_features(window: np.ndarray, pre_samples: int) -> np.ndarray:
    baseline = window[:, :pre_samples].astype(np.float32)
    response = window[:, pre_samples:].astype(np.float32)
    baseline_mean = baseline.mean(axis=1)
    response_mean = response.mean(axis=1)
    baseline_abs = np.abs(baseline).mean(axis=1)
    response_abs = np.abs(response).mean(axis=1)
    baseline_rms = np.sqrt(np.mean(np.square(baseline), axis=1))
    response_rms = np.sqrt(np.mean(np.square(response), axis=1))
    response_ptp = np.ptp(response, axis=1)
    return np.concatenate([
        response_mean - baseline_mean,
        response_abs - baseline_abs,
        response_rms - baseline_rms,
        response_ptp,
    ]).astype(np.float32)


def build_raw_native_feature_matrix_v58(
    raw_root: str | Path = DEFAULT_RAW_ROOT,
    raw_event_csv: str | Path = DEFAULT_RAW_EVENT_CANDIDATES,
    max_events_per_recording: int = 16,
    window_pre_ms: float = 20.0,
    window_post_ms: float = 80.0,
) -> RawNativeFeatureMatrixV58:
    try:
        import h5py  # type: ignore
    except ImportError:
        return RawNativeFeatureMatrixV58(
            X=np.zeros((0, 0), dtype=np.float32),
            feature_names=tuple(),
            rows=tuple(),
            sources=tuple(),
            skipped_event_count=0,
            skipped_source_count=0,
            read_error_count=1,
            read_errors=("h5py_not_installed",),
            window_pre_ms=float(window_pre_ms),
            window_post_ms=float(window_post_ms),
            max_events_per_recording=int(max_events_per_recording),
            claim_boundary=_claim_boundary(),
        )

    sources = load_primary_event_sources_v58(raw_event_csv=raw_event_csv, raw_root=raw_root)
    features: list[np.ndarray] = []
    metadata_rows: list[RawNativeEventFeatureRowV58] = []
    skipped_events = 0
    skipped_sources = 0
    read_errors: list[str] = []
    feature_names: tuple[str, ...] = tuple()

    for source in sources:
        hdf5_path = Path(source.hdf5_path)
        if not hdf5_path.exists():
            skipped_sources += 1
            read_errors.append(f"missing_hdf5:{source.source_file}")
            continue
        try:
            with h5py.File(hdf5_path, "r") as handle:
                recording_group = handle.get("Data/Recording_0")
                channel_data = handle["Data/Recording_0/AnalogStream/Stream_0/ChannelData"]
                event_dataset = handle[f"Data/Recording_0/EventStream/{source.stream}/{source.entity}"]
                event_values = event_dataset[()]
                timestamps_us = np.asarray(event_values[0], dtype=np.int64)
                timestamps_us = timestamps_us[timestamps_us >= 0]
                timestamps_us = _select_evenly(timestamps_us, int(max_events_per_recording))
                sample_rate = _sample_rate_hz(channel_data, recording_group)
                pre_samples = max(1, int(round(float(window_pre_ms) * sample_rate / 1000.0)))
                post_samples = max(1, int(round(float(window_post_ms) * sample_rate / 1000.0)))
                sample_count = int(channel_data.shape[1])
                channel_count = int(channel_data.shape[0])
                for event_index, timestamp_us in enumerate(timestamps_us.tolist()):
                    sample_index = int(round((int(timestamp_us) / 1_000_000.0) * sample_rate))
                    start = sample_index - pre_samples
                    end = sample_index + post_samples
                    if start < 0 or end > sample_count:
                        skipped_events += 1
                        continue
                    window = np.asarray(channel_data[:, start:end], dtype=np.float32)
                    if window.shape[1] != pre_samples + post_samples:
                        skipped_events += 1
                        continue
                    feature_vector = _window_features(window, pre_samples)
                    features.append(feature_vector)
                    metadata_rows.append(
                        RawNativeEventFeatureRowV58(
                            row_index=len(metadata_rows),
                            source_file=source.source_file,
                            stream=source.stream,
                            entity=source.entity,
                            condition=source.condition,
                            target_id=source.target_id,
                            date=source.date,
                            culture=source.culture,
                            recording_id=source.recording_id,
                            event_index=int(event_index),
                            timestamp_us=int(timestamp_us),
                            timestamp_s=round(int(timestamp_us) / 1_000_000.0, 6),
                            sample_index=sample_index,
                            sample_rate_hz=round(float(sample_rate), 6),
                            window_pre_ms=float(window_pre_ms),
                            window_post_ms=float(window_post_ms),
                            channel_count=channel_count,
                            feature_count=int(feature_vector.shape[0]),
                        )
                    )
        except Exception as exc:  # pragma: no cover - depends on external HDF5 failures
            skipped_sources += 1
            read_errors.append(f"read_failed:{source.source_file}:{type(exc).__name__}:{exc}")

    if features:
        max_feature_count = max(int(vector.shape[0]) for vector in features)
        X = np.zeros((len(features), max_feature_count), dtype=np.float32)
        for row_index, vector in enumerate(features):
            X[row_index, : int(vector.shape[0])] = vector.astype(np.float32)
        feature_names = _feature_names(max_feature_count // 4)
    else:
        X = np.zeros((0, 0), dtype=np.float32)
        feature_names = tuple()
    return RawNativeFeatureMatrixV58(
        X=X,
        feature_names=feature_names,
        rows=tuple(metadata_rows),
        sources=sources,
        skipped_event_count=skipped_events,
        skipped_source_count=skipped_sources,
        read_error_count=len(read_errors),
        read_errors=tuple(read_errors[:20]),
        window_pre_ms=float(window_pre_ms),
        window_post_ms=float(window_post_ms),
        max_events_per_recording=int(max_events_per_recording),
        claim_boundary=_claim_boundary(),
    )


def _claim_boundary() -> str:
    return "raw-native event-window feature extraction and condition readout only; no live biology, no GPU replacement and no raw equivalence for v15/v50 rows"


def summarize_raw_native_matrix_v58(matrix: RawNativeFeatureMatrixV58) -> dict[str, Any]:
    conditions = Counter(row.condition for row in matrix.rows)
    targets = Counter(f"{row.condition}:{row.target_id}" for row in matrix.rows if row.target_id)
    recordings = sorted(set(row.source_file for row in matrix.rows))
    status = "raw_native_features_available" if matrix.X.shape[0] > 0 else "no_raw_native_features"
    if matrix.read_error_count and matrix.X.shape[0] == 0:
        status = "raw_native_feature_extraction_failed"
    return {
        "version": "v5.8",
        "overall_status": status,
        "raw_event_source_count": len(matrix.sources),
        "feature_row_count": int(matrix.X.shape[0]),
        "feature_count": int(matrix.X.shape[1]) if len(matrix.X.shape) == 2 else 0,
        "recording_count_with_features": len(recordings),
        "condition_counts": dict(sorted(conditions.items())),
        "target_counts": dict(sorted(targets.items())),
        "window_pre_ms": matrix.window_pre_ms,
        "window_post_ms": matrix.window_post_ms,
        "max_events_per_recording": matrix.max_events_per_recording,
        "skipped_event_count": matrix.skipped_event_count,
        "skipped_source_count": matrix.skipped_source_count,
        "read_error_count": matrix.read_error_count,
        "read_errors_sample": list(matrix.read_errors[:5]),
        "claim_boundary": matrix.claim_boundary,
    }


def _standardize_train_test(X_train: np.ndarray, X_test: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mean = X_train.mean(axis=0)
    std = X_train.std(axis=0)
    std[std == 0] = 1.0
    return (X_train - mean) / std, (X_test - mean) / std


def _centroid_predict(X_train: np.ndarray, y_train: np.ndarray, X_test: np.ndarray) -> np.ndarray:
    classes = np.array(sorted(set(str(value) for value in y_train.tolist())), dtype=object)
    centroids = []
    for cls in classes:
        centroids.append(X_train[y_train == cls].mean(axis=0))
    centroid_matrix = np.vstack(centroids)
    distances = ((X_test[:, None, :] - centroid_matrix[None, :, :]) ** 2).sum(axis=2)
    return classes[np.argmin(distances, axis=1)]


def _balanced_accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    recalls: list[float] = []
    for cls in sorted(set(str(value) for value in y_true.tolist())):
        mask = y_true == cls
        if np.any(mask):
            recalls.append(float(np.mean(y_pred[mask] == cls)))
    return float(np.mean(recalls)) if recalls else 0.0


def _one_sided_high_p_value(observed: float, null_values: list[float]) -> float | None:
    if not null_values:
        return None
    return float((1 + sum(1 for value in null_values if value >= observed)) / (1 + len(null_values)))


def group_heldout_condition_readout_v58(
    matrix: RawNativeFeatureMatrixV58,
    label_shuffles: int = 25,
    seed: int = 58,
) -> dict[str, Any]:
    if matrix.X.shape[0] == 0 or not matrix.rows:
        return {"status": "not_enough_data", "sample_count": int(matrix.X.shape[0]), "claim_boundary": matrix.claim_boundary}
    y = np.asarray([row.condition for row in matrix.rows], dtype=object)
    groups = np.asarray([row.source_file for row in matrix.rows], dtype=object)
    classes = sorted(set(str(value) for value in y.tolist()))
    if len(classes) < 2:
        return {"status": "not_enough_conditions", "sample_count": int(len(y)), "condition_count": len(classes), "claim_boundary": matrix.claim_boundary}
    unique_groups = sorted(set(str(value) for value in groups.tolist()))
    true_all: list[str] = []
    pred_all: list[str] = []
    folds: list[dict[str, Any]] = []
    fold_indices: list[tuple[np.ndarray, np.ndarray]] = []
    for fold_index, group in enumerate(unique_groups):
        test_mask = groups == group
        train_mask = ~test_mask
        if len(set(str(value) for value in y[train_mask].tolist())) < len(classes):
            continue
        X_train, X_test = _standardize_train_test(matrix.X[train_mask], matrix.X[test_mask])
        pred = _centroid_predict(X_train, y[train_mask], X_test)
        true = y[test_mask]
        true_all.extend(str(value) for value in true.tolist())
        pred_all.extend(str(value) for value in pred.tolist())
        fold_indices.append((np.where(train_mask)[0], np.where(test_mask)[0]))
        folds.append({
            "fold": int(fold_index),
            "heldout_recording": group,
            "n_test": int(np.sum(test_mask)),
            "condition": str(true[0]) if len(set(true.tolist())) == 1 else "mixed",
            "accuracy": float(np.mean(pred == true)),
        })
    if not true_all:
        return {"status": "no_valid_group_folds", "sample_count": int(len(y)), "condition_count": len(classes), "claim_boundary": matrix.claim_boundary}
    true_arr = np.asarray(true_all, dtype=object)
    pred_arr = np.asarray(pred_all, dtype=object)
    observed = {
        "accuracy": float(np.mean(pred_arr == true_arr)),
        "balanced_accuracy": _balanced_accuracy(true_arr, pred_arr),
    }
    rng = np.random.default_rng(int(seed))
    null_balanced: list[float] = []
    for _ in range(int(label_shuffles)):
        shuffle_true: list[str] = []
        shuffle_pred: list[str] = []
        for train_idx, test_idx in fold_indices:
            y_train = np.array(y[train_idx], dtype=object)
            rng.shuffle(y_train)
            X_train, X_test = _standardize_train_test(matrix.X[train_idx], matrix.X[test_idx])
            pred = _centroid_predict(X_train, y_train, X_test)
            shuffle_true.extend(str(value) for value in y[test_idx].tolist())
            shuffle_pred.extend(str(value) for value in pred.tolist())
        null_balanced.append(_balanced_accuracy(np.asarray(shuffle_true, dtype=object), np.asarray(shuffle_pred, dtype=object)))
    return {
        "status": "group_heldout_condition_readout",
        "sample_count": int(len(y)),
        "feature_count": int(matrix.X.shape[1]),
        "condition_counts": dict(sorted(Counter(str(value) for value in y.tolist()).items())),
        "recording_group_count": len(unique_groups),
        "valid_fold_count": len(folds),
        "readout": "standardized_nearest_centroid_group_heldout",
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
        "honesty_note": "This is a raw-native condition/modality readout under held-out recordings. It is not target-ID proof, not v15/v50 raw equivalence, and not a live BioGPU claim.",
    }


def write_raw_native_outputs_v58(
    matrix: RawNativeFeatureMatrixV58,
    readout: dict[str, Any],
    out_dir: str | Path,
) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary_json": out / "V58_RAW_NATIVE_FEATURE_SUMMARY.json",
        "feature_matrix_npz": out / "V58_RAW_NATIVE_FEATURE_MATRIX.npz",
        "event_metadata_csv": out / "V58_RAW_NATIVE_EVENT_METADATA.csv",
        "sources_csv": out / "V58_RAW_NATIVE_EVENT_SOURCES.csv",
        "condition_readout_json": out / "V58_RAW_NATIVE_CONDITION_READOUT.json",
        "markdown_report": out / "BIOGPU_V58_RAW_NATIVE_BENCHMARK_REPORT.md",
    }
    summary = summarize_raw_native_matrix_v58(matrix)
    summary["condition_readout_status"] = readout.get("status")
    summary["condition_readout_observed"] = readout.get("observed")
    summary["condition_readout_shuffle_baseline"] = readout.get("label_shuffle_baseline")
    paths["summary_json"].write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    np.savez_compressed(
        paths["feature_matrix_npz"],
        X=matrix.X.astype(np.float32),
        feature_names=np.asarray(matrix.feature_names, dtype=object),
        condition=np.asarray([row.condition for row in matrix.rows], dtype=object),
        target_id=np.asarray([row.target_id for row in matrix.rows], dtype=object),
        source_file=np.asarray([row.source_file for row in matrix.rows], dtype=object),
        recording_id=np.asarray([row.recording_id for row in matrix.rows], dtype=object),
        timestamp_s=np.asarray([row.timestamp_s for row in matrix.rows], dtype=np.float64),
        window_pre_ms=np.asarray([matrix.window_pre_ms], dtype=np.float64),
        window_post_ms=np.asarray([matrix.window_post_ms], dtype=np.float64),
    )
    _write_rows_csv(paths["event_metadata_csv"], [row.to_dict() for row in matrix.rows])
    _write_rows_csv(paths["sources_csv"], [source.to_dict() for source in matrix.sources])
    paths["condition_readout_json"].write_text(json.dumps(readout, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["markdown_report"].write_text(_markdown_report(summary, readout), encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}


def _write_rows_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = list(rows[0].keys()) if rows else ["empty"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _markdown_report(summary: dict[str, Any], readout: dict[str, Any]) -> str:
    observed = readout.get("observed") or {}
    shuffle = readout.get("label_shuffle_baseline") or {}
    lines = [
        "# BioGPU-Core v5.8 Raw-Native Benchmark Report",
        "",
        "## Summary",
        "",
        f"- Overall status: `{summary['overall_status']}`",
        f"- Raw event sources: `{summary['raw_event_source_count']}`",
        f"- Feature rows: `{summary['feature_row_count']}`",
        f"- Feature count: `{summary['feature_count']}`",
        f"- Recordings with features: `{summary['recording_count_with_features']}`",
        f"- Condition counts: `{summary['condition_counts']}`",
        f"- Skipped events: `{summary['skipped_event_count']}`",
        "",
        "## Group-Heldout Condition Readout",
        "",
        f"- Status: `{readout.get('status')}`",
        f"- Observed balanced accuracy: `{observed.get('balanced_accuracy')}`",
        f"- Shuffle median balanced accuracy: `{shuffle.get('balanced_accuracy_median')}`",
        f"- Shuffle p-value: `{shuffle.get('p_value_balanced_accuracy_gt_shuffle')}`",
        "",
        "## Claim Boundary",
        "",
        summary["claim_boundary"],
        "",
        "## Interpretation",
        "",
        "v5.8 is the first raw-native feature benchmark over the downloaded HDF5 archive. It extracts features directly from analog ChannelData windows around embedded EventStream timestamps. This supports a raw-derived software benchmark, but it does not establish raw equivalence for v15/v50 PC validation rows or any live biological-compute claim.",
        "",
    ]
    return "\n".join(lines)
