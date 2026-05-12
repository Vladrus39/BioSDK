from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

from biogpu.analysis.raw_native_stability_v59 import (
    build_raw_native_stability_audit_v59,
    group_heldout_target_readout_v59,
    load_raw_native_dataset_v59,
    split_half_repeatability_v59,
    target_eligibility_rows_v59,
    target_fingerprint_similarity_v59,
)
from biogpu.benchmarks.biogpu_v59_raw_native_stability_audit import run


METADATA_FIELDS = [
    "row_index",
    "source_file",
    "stream",
    "entity",
    "condition",
    "target_id",
    "date",
    "culture",
    "recording_id",
    "event_index",
    "timestamp_us",
    "timestamp_s",
    "sample_index",
    "sample_rate_hz",
    "window_pre_ms",
    "window_post_ms",
    "channel_count",
    "feature_count",
]


def _write_dataset(base_dir: Path, specs: list[tuple[str, str, str, np.ndarray]], events_per_group: int = 6) -> tuple[Path, Path]:
    features = []
    rows = []
    row_index = 0
    for source_file, condition, target_id, center in specs:
        for event_index in range(events_per_group):
            event_noise = np.full(center.shape, event_index * 0.001, dtype=np.float32)
            features.append((center + event_noise).astype(np.float32))
            rows.append(
                {
                    "row_index": row_index,
                    "source_file": source_file,
                    "stream": "Stream_0",
                    "entity": "EventEntity_0",
                    "condition": condition,
                    "target_id": target_id,
                    "date": "01-01-2022",
                    "culture": "synthetic_10DIV",
                    "recording_id": source_file.replace(".h5", ""),
                    "event_index": event_index,
                    "timestamp_us": 100000 + event_index * 1000,
                    "timestamp_s": 0.1 + event_index * 0.001,
                    "sample_index": 100 + event_index,
                    "sample_rate_hz": 1000.0,
                    "window_pre_ms": 10.0,
                    "window_post_ms": 20.0,
                    "channel_count": 2,
                    "feature_count": int(center.shape[0]),
                }
            )
            row_index += 1
    matrix_path = base_dir / "matrix.npz"
    metadata_path = base_dir / "metadata.csv"
    np.savez_compressed(matrix_path, X=np.vstack(features), feature_names=np.asarray([f"f{feature_index}" for feature_index in range(features[0].shape[0])], dtype=object))
    with metadata_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=METADATA_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return matrix_path, metadata_path


def _separable_specs() -> list[tuple[str, str, str, np.ndarray]]:
    return [
        ("target44_group_a.h5", "elecstim", "44", np.asarray([5, 0, 0, 0], dtype=np.float32)),
        ("target44_group_b.h5", "elecstim", "44", np.asarray([5.5, 0, 0, 0], dtype=np.float32)),
        ("target52_group_a.h5", "elecstim", "52", np.asarray([0, 5, 0, 0], dtype=np.float32)),
        ("target52_group_b.h5", "elecstim", "52", np.asarray([0, 5.5, 0, 0], dtype=np.float32)),
        ("target62_group_a.h5", "elecstim", "62", np.asarray([0, 0, 5, 0], dtype=np.float32)),
        ("target62_group_b.h5", "elecstim", "62", np.asarray([0, 0, 5.5, 0], dtype=np.float32)),
    ]


def test_v59_loads_v58_like_dataset(tmp_path):
    matrix_path, metadata_path = _write_dataset(tmp_path, _separable_specs()[:2])

    dataset = load_raw_native_dataset_v59(matrix_path, metadata_path)

    assert dataset.features.shape == (12, 4)
    assert dataset.rows[0].target_label == "elecstim:44"
    assert len(dataset.feature_names) == 4


def test_v59_target_eligibility_marks_repeated_targets(tmp_path):
    matrix_path, metadata_path = _write_dataset(tmp_path, _separable_specs() + [("single_light.h5", "lightstim", "34", np.ones(4, dtype=np.float32))])
    dataset = load_raw_native_dataset_v59(matrix_path, metadata_path)

    rows = target_eligibility_rows_v59(dataset, min_groups_per_target=2)
    statuses = {row["target_label"]: row["status"] for row in rows}

    assert statuses["elecstim:44"] == "eligible"
    assert statuses["lightstim:34"] == "single_recording_only"


def test_v59_split_half_repeatability_has_within_margin(tmp_path):
    matrix_path, metadata_path = _write_dataset(tmp_path, _separable_specs())
    dataset = load_raw_native_dataset_v59(matrix_path, metadata_path)

    result = split_half_repeatability_v59(dataset)

    assert result["status"] == "split_half_repeatability_available"
    assert result["within_recording_split_cosine"]["median"] > result["cross_recording_centroid_cosine"]["median"]
    assert len(result["by_recording"]) == 6


def test_v59_target_readout_and_fingerprint_support_separable_repeats(tmp_path):
    matrix_path, metadata_path = _write_dataset(tmp_path, _separable_specs())
    dataset = load_raw_native_dataset_v59(matrix_path, metadata_path)

    readout = group_heldout_target_readout_v59(dataset, label_shuffles=5, seed=1)
    fingerprint = target_fingerprint_similarity_v59(dataset, label_shuffles=5, seed=2)

    assert readout["status"] == "group_heldout_target_readout"
    assert readout["observed"]["balanced_accuracy"] == 1.0
    assert fingerprint["status"] == "target_fingerprint_similarity"
    assert fingerprint["observed"]["mean_margin_positive_minus_negative"] > 0


def test_v59_target_readout_reports_insufficient_repeats(tmp_path):
    specs = [
        ("target44_group_a.h5", "elecstim", "44", np.asarray([5, 0], dtype=np.float32)),
        ("target52_group_a.h5", "elecstim", "52", np.asarray([0, 5], dtype=np.float32)),
    ]
    matrix_path, metadata_path = _write_dataset(tmp_path, specs)
    dataset = load_raw_native_dataset_v59(matrix_path, metadata_path)

    readout = group_heldout_target_readout_v59(dataset)

    assert readout["status"] == "not_enough_repeated_targets"


def test_v59_runner_writes_outputs(tmp_path):
    matrix_path, metadata_path = _write_dataset(tmp_path, _separable_specs())

    result = run(matrix_npz=matrix_path, metadata_csv=metadata_path, out_dir=tmp_path / "out", label_shuffles=3, ensure_v58=False)

    assert result["summary"]["split_half_repeatability_status"] == "split_half_repeatability_available"
    assert (tmp_path / "out" / "V59_RAW_NATIVE_STABILITY_SUMMARY.json").exists()
    loaded = json.loads((tmp_path / "out" / "V59_RAW_NATIVE_STABILITY_SUMMARY.json").read_text(encoding="utf-8"))
    assert loaded["eligible_repeated_target_label_count"] == 3
