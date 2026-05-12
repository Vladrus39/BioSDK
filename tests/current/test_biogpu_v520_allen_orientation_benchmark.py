from __future__ import annotations

import json
from pathlib import Path

import h5py
import numpy as np

from biogpu.benchmarks.biogpu_v520_allen_orientation_benchmark import run
from biogpu.sdk.allen_orientation_benchmark_v520 import build_allen_orientation_feature_matrix_v520, build_allen_orientation_sdk_benchmark_v520, write_allen_orientation_benchmark_outputs_v520


def _write_fixture(path: Path) -> None:
    path.parent.mkdir(parents=True)
    unit_spikes = [np.array([0.1, 1.1, 2.1, 4.1]), np.array([0.2, 2.2, 3.2, 5.2]), np.array([1.3, 3.3, 4.3, 5.3])]
    all_spikes = np.concatenate(unit_spikes)
    index = np.cumsum([len(item) for item in unit_spikes])
    with h5py.File(path, "w") as h5:
        h5.create_group("stimulus")
        units = h5.create_group("units")
        units.create_dataset("spike_times", data=all_spikes)
        units.create_dataset("spike_times_index", data=index)
        units.create_dataset("id", data=np.array([10, 11, 12], dtype=np.int64))
        units.create_dataset("firing_rate", data=np.array([2.0, 1.5, 1.0]))
        intervals = h5.create_group("intervals")
        table = intervals.create_group("drifting_gratings_presentations")
        starts = np.arange(0, 8, dtype=float)
        stops = starts + 0.5
        table.create_dataset("start_time", data=starts)
        table.create_dataset("stop_time", data=stops)
        table.create_dataset("orientation", data=np.array([0, 45, 0, 45, 0, 45, 0, 45], dtype=float))
        table.create_dataset("temporal_frequency", data=np.ones(8, dtype=float) * 4.0)


def test_v520_missing_sample_is_honest(tmp_path):
    summary = build_allen_orientation_sdk_benchmark_v520(tmp_path)
    assert summary["overall_status"] == "allen_orientation_benchmark_missing_validated_sample"
    assert summary["bic_os_phase_locked"] is True


def test_v520_builds_fixture_feature_matrix(tmp_path):
    sample = tmp_path / "data" / "external" / "allen" / "fixture.nwb"
    _write_fixture(sample)
    matrix = build_allen_orientation_feature_matrix_v520(sample, top_units=2, max_windows=8)
    assert matrix.features.shape == (8, 4)
    assert set(matrix.labels.tolist()) == {"0", "45"}
    assert len(matrix.unit_ids) == 2


def test_v520_fixture_benchmark_available(tmp_path):
    sample = tmp_path / "data" / "external" / "allen" / "fixture.nwb"
    _write_fixture(sample)
    summary = build_allen_orientation_sdk_benchmark_v520(tmp_path, top_units=2, max_windows=8, label_shuffles=5, seed=1)
    assert summary["overall_status"] == "allen_orientation_sdk_benchmark_available"
    assert summary["sample_count"] == 8
    assert summary["selected_unit_count"] == 2


def test_v520_write_outputs(tmp_path):
    sample = tmp_path / "data" / "external" / "allen" / "fixture.nwb"
    _write_fixture(sample)
    paths = write_allen_orientation_benchmark_outputs_v520(tmp_path, tmp_path / "out", top_units=2, max_windows=8, label_shuffles=5, seed=2)
    assert Path(paths["summary_json"]).exists()
    assert Path(paths["feature_matrix_npz"]).exists()
    assert Path(paths["trial_features_csv"]).exists()


def test_v520_runner_writes_summary(tmp_path):
    sample = tmp_path / "data" / "external" / "allen" / "fixture.nwb"
    _write_fixture(sample)
    result = run(root=tmp_path, out_dir=tmp_path / "out", top_units=2, max_windows=8, label_shuffles=5, seed=3)
    assert result["summary"]["overall_status"] == "allen_orientation_sdk_benchmark_available"
    assert json.loads((tmp_path / "out" / "V520_ALLEN_ORIENTATION_BENCHMARK_SUMMARY.json").read_text(encoding="utf-8"))["sample_count"] == 8
