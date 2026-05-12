from __future__ import annotations

import json

import pytest

from biogpu.benchmarks.biogpu_v56_raw_hdf5_structure import run
from biogpu.data_ingest.zenodo_raw_hdf5_v56 import (
    discover_raw_hdf5_files,
    inspect_raw_hdf5_file_v56,
    inspect_raw_hdf5_tree_v56,
)

h5py = pytest.importorskip("h5py")


def _write_fake_mcs_hdf5(path):
    import numpy as np

    with h5py.File(path, "w") as handle:
        handle.attrs["GeneratingApplicationName"] = b"Multi Channel DataManager"
        handle.attrs["McsHdf5ProtocolType"] = b"RawData"
        handle.attrs["McsHdf5ProtocolVersion"] = 3
        data = handle.create_group("Data")
        recording = data.create_group("Recording_0")
        recording.attrs["Duration"] = 1_000_000
        analog_stream = recording.create_group("AnalogStream").create_group("Stream_0")
        analog_stream.create_dataset("ChannelData", data=np.zeros((2, 20_000), dtype="int32"))
        analog_stream.create_dataset("InfoChannel", data=np.zeros((2,), dtype=[("ChannelID", "i4")]))
        event_stream = recording.create_group("EventStream").create_group("Stream_0")
        event_stream.attrs["Label"] = b"Digital Event Detector (1);Digital Event Detector; Digital Events1"
        events = np.array([
            [100_000, 300_000, 500_000],
            [0, 0, 0],
            [-1, -1, -1],
            [-1, -1, -1],
            [-1, -1, -1],
        ], dtype="int64")
        event_stream.create_dataset("EventEntity_0", data=events)


def test_v56_discovers_hdf5_files(tmp_path):
    _write_fake_mcs_hdf5(tmp_path / "sample.h5")
    assert discover_raw_hdf5_files(tmp_path) == [tmp_path / "sample.h5"]


def test_v56_inspects_mcs_raw_structure_and_events(tmp_path):
    path = tmp_path / "sample.h5"
    _write_fake_mcs_hdf5(path)
    result = inspect_raw_hdf5_file_v56(path, tmp_path)
    assert result.valid_hdf5 is True
    assert result.protocol_type == "RawData"
    assert result.channel_count == 2
    assert result.sample_count == 20_000
    assert result.sample_rate_hz == 20_000.0
    assert result.event_candidate_count == 1
    assert result.event_total_count == 3
    assert result.event_candidates[0].median_interval_s == 0.2


def test_v56_tree_report_aggregates_event_candidates(tmp_path):
    _write_fake_mcs_hdf5(tmp_path / "a.h5")
    _write_fake_mcs_hdf5(tmp_path / "b.h5")
    report = inspect_raw_hdf5_tree_v56(tmp_path)
    assert report.overall_status == "raw_hdf5_events_available"
    assert report.file_count == 2
    assert report.valid_file_count == 2
    assert report.files_with_events == 2
    assert report.event_candidate_count == 2
    assert report.event_total_count == 6


def test_v56_missing_root_reports_not_downloaded(tmp_path):
    report = inspect_raw_hdf5_tree_v56(tmp_path / "missing")
    assert report.overall_status == "not_downloaded"
    assert report.file_count == 0


def test_v56_runner_writes_outputs(tmp_path):
    root = tmp_path / "raw"
    root.mkdir()
    _write_fake_mcs_hdf5(root / "sample.h5")
    result = run(root=root, out_dir=tmp_path / "out")
    summary = result["summary"]
    assert summary["overall_status"] == "raw_hdf5_events_available"
    assert (tmp_path / "out" / "V56_TTL_EVENT_CANDIDATES.csv").exists()
    loaded = json.loads((tmp_path / "out" / "V56_RAW_HDF5_STRUCTURE_SUMMARY.json").read_text(encoding="utf-8"))
    assert loaded["event_total_count"] == 3
