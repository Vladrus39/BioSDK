from __future__ import annotations

import csv
import json

import numpy as np
import pytest

from biogpu.benchmarks.biogpu_v58_raw_native_benchmark import run
from biogpu.data_ingest.raw_native_benchmark_v58 import (
    build_raw_native_feature_matrix_v58,
    group_heldout_condition_readout_v58,
    load_primary_event_sources_v58,
)

h5py = pytest.importorskip("h5py")


RAW_FIELDS = [
    "file",
    "stream",
    "entity",
    "label",
    "detector_kind",
    "event_count",
    "first_timestamp_s",
    "last_timestamp_s",
    "median_interval_s",
    "info_type_values",
    "sample_timestamps_us",
    "candidate_kind",
]


def _write_event_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=RAW_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _event_row(file_name, condition="light", target="34", entity="EventEntity_0", event_count=3):
    kind = "light_or_digital_stimulation_event" if condition == "light" else "electrical_stimulation_event"
    label = "Digital Event Detector" if condition == "light" else "Stimulator (1);Stimulator; STG Events1"
    return {
        "file": file_name,
        "stream": "Stream_0",
        "entity": entity,
        "label": label,
        "detector_kind": "digital_port_event" if condition == "light" else "stimulator_event",
        "event_count": str(event_count),
        "first_timestamp_s": "0.1",
        "last_timestamp_s": "0.3",
        "median_interval_s": "0.1",
        "info_type_values": "",
        "sample_timestamps_us": "100000;200000;300000",
        "candidate_kind": kind,
    }


def _write_fake_hdf5(path, offset):
    path.parent.mkdir(parents=True, exist_ok=True)
    sample_rate = 1_000
    samples = 500
    base = np.zeros((2, samples), dtype="int32")
    base[:, 100:180] = offset
    base[:, 200:280] = offset * 2
    base[:, 300:380] = offset * 3
    with h5py.File(path, "w") as handle:
        handle.attrs["McsHdf5ProtocolType"] = b"RawData"
        data = handle.create_group("Data")
        recording = data.create_group("Recording_0")
        recording.attrs["Duration"] = 500_000
        analog = recording.create_group("AnalogStream").create_group("Stream_0")
        analog.create_dataset("ChannelData", data=base)
        analog.create_dataset("InfoChannel", data=np.zeros((2,), dtype=[("ChannelID", "i4")]))
        event_stream = recording.create_group("EventStream").create_group("Stream_0")
        events = np.array([
            [100_000, 200_000, 300_000],
            [0, 0, 0],
            [-1, -1, -1],
            [-1, -1, -1],
            [-1, -1, -1],
        ], dtype="int64")
        event_stream.create_dataset("EventEntity_0", data=events)
        event_stream.create_dataset("EventEntity_1", data=events)


def test_v58_loads_primary_event_sources(tmp_path):
    raw_csv = tmp_path / "events.csv"
    file_name = "11-11-2022\\41438_13DIV\\41438_13DIV_LightStim_Spot34_D-00144.h5"
    _write_event_csv(raw_csv, [_event_row(file_name, event_count=3), {**_event_row(file_name, entity="EventEntity_1"), "event_count": "2"}])

    sources = load_primary_event_sources_v58(raw_csv, tmp_path / "raw")

    assert len(sources) == 1
    assert sources[0].entity == "EventEntity_0"
    assert sources[0].condition == "lightstim"
    assert sources[0].target_id == "34"


def test_v58_extracts_raw_native_features_from_hdf5_windows(tmp_path):
    raw_root = tmp_path / "raw"
    file_name = "11-11-2022\\41438_13DIV\\41438_13DIV_LightStim_Spot34_D-00144.h5"
    _write_fake_hdf5(raw_root / "11-11-2022" / "41438_13DIV" / "41438_13DIV_LightStim_Spot34_D-00144.h5", offset=10)
    raw_csv = tmp_path / "events.csv"
    _write_event_csv(raw_csv, [_event_row(file_name)])

    matrix = build_raw_native_feature_matrix_v58(raw_root=raw_root, raw_event_csv=raw_csv, max_events_per_recording=2, window_pre_ms=10, window_post_ms=20)

    assert matrix.X.shape == (2, 8)
    assert len(matrix.rows) == 2
    assert matrix.rows[0].sample_rate_hz == 1000.0
    assert matrix.skipped_event_count == 0


def test_v58_missing_hdf5_is_reported_without_crash(tmp_path):
    raw_csv = tmp_path / "events.csv"
    _write_event_csv(raw_csv, [_event_row("11-11-2022\\41438_13DIV\\missing_LightStim_Spot34_D-00144.h5")])

    matrix = build_raw_native_feature_matrix_v58(raw_root=tmp_path / "raw", raw_event_csv=raw_csv)


    assert matrix.X.shape[0] == 0
    assert matrix.skipped_source_count == 1
    assert matrix.read_error_count == 1


def test_v58_group_heldout_condition_readout_runs_on_separable_features(tmp_path):
    raw_root = tmp_path / "raw"
    rows = []
    for idx, (condition, stem, offset) in enumerate([
        ("light", "A_10DIV_LightStim_Spot34_D-00144.h5", 10),
        ("light", "B_10DIV_LightStim_Spot55_D-00144.h5", 12),
        ("elec", "C_10DIV_Stim21_D-00144.h5", 100),
        ("elec", "D_10DIV_Stim44_D-00144.h5", 120),
    ]):
        folder = f"0{idx + 1}-01-2022"
        culture = stem.split("_")[0] + "_10DIV"
        file_name = f"{folder}\\{culture}\\{stem}"
        _write_fake_hdf5(raw_root / folder / culture / stem, offset=offset)
        rows.append(_event_row(file_name, condition=condition, target="34" if condition == "light" else "21"))
    raw_csv = tmp_path / "events.csv"
    _write_event_csv(raw_csv, rows)
    matrix = build_raw_native_feature_matrix_v58(raw_root=raw_root, raw_event_csv=raw_csv, max_events_per_recording=3, window_pre_ms=10, window_post_ms=20)

    readout = group_heldout_condition_readout_v58(matrix, label_shuffles=3, seed=1)

    assert readout["status"] == "group_heldout_condition_readout"
    assert readout["valid_fold_count"] == 4
    assert readout["observed"]["balanced_accuracy"] >= 0.5


def test_v58_runner_writes_outputs(tmp_path):
    raw_root = tmp_path / "raw"
    file_name = "11-11-2022\\41438_13DIV\\41438_13DIV_LightStim_Spot34_D-00144.h5"
    _write_fake_hdf5(raw_root / "11-11-2022" / "41438_13DIV" / "41438_13DIV_LightStim_Spot34_D-00144.h5", offset=10)
    raw_csv = tmp_path / "events.csv"
    _write_event_csv(raw_csv, [_event_row(file_name)])

    result = run(raw_root=raw_root, raw_event_csv=raw_csv, out_dir=tmp_path / "out", max_events_per_recording=2, window_pre_ms=10, window_post_ms=20, label_shuffles=1, ensure_v56=False)

    assert result["summary"]["overall_status"] == "raw_native_features_available"
    assert (tmp_path / "out" / "V58_RAW_NATIVE_FEATURE_MATRIX.npz").exists()
    loaded = json.loads((tmp_path / "out" / "V58_RAW_NATIVE_FEATURE_SUMMARY.json").read_text(encoding="utf-8"))
    assert loaded["feature_row_count"] == 2
