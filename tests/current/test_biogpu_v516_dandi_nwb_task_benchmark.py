from __future__ import annotations

import json
from pathlib import Path

import h5py

from biogpu.benchmarks.biogpu_v516_dandi_nwb_task_benchmark import run
from biogpu.sdk.nwb_task_benchmark_v516 import build_dandi_nwb_sdk_benchmark_v516, build_nwb_task_feature_matrix_v516, stratified_load_readout_v516, write_dandi_nwb_benchmark_outputs_v516


def _write_separable_nwb(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    starts = []
    stops = []
    labels = []
    spike_times_unit_0 = []
    spike_times_unit_1 = []
    for trial_index in range(12):
        start_s = float(trial_index * 2)
        stop_s = start_s + 1.0
        label = 1 if trial_index % 2 == 0 else 2
        starts.append(start_s)
        stops.append(stop_s)
        labels.append(label)
        if label == 1:
            spike_times_unit_0.extend([start_s + 0.1, start_s + 0.2, start_s + 0.3])
            spike_times_unit_1.append(start_s + 0.5)
        else:
            spike_times_unit_0.append(start_s + 0.5)
            spike_times_unit_1.extend([start_s + 0.1, start_s + 0.2, start_s + 0.3])
    all_spikes = spike_times_unit_0 + spike_times_unit_1
    with h5py.File(path, "w") as nwb_file:
        units = nwb_file.create_group("units")
        units.create_dataset("id", data=[0, 1])
        units.create_dataset("spike_times", data=all_spikes)
        units.create_dataset("spike_times_index", data=[len(spike_times_unit_0), len(all_spikes)])
        intervals = nwb_file.create_group("intervals")
        trials = intervals.create_group("trials")
        trials.create_dataset("start_time", data=starts)
        trials.create_dataset("stop_time", data=stops)
        trials.create_dataset("loads", data=labels)
        stimulus = nwb_file.create_group("stimulus")
        stimulus.create_group("presentation")


def test_v516_builds_spike_count_feature_matrix(tmp_path):
    path = tmp_path / "data" / "external" / "nwb" / "sample.nwb"
    _write_separable_nwb(path)

    matrix = build_nwb_task_feature_matrix_v516(path)

    assert matrix.features.shape == (12, 4)
    assert matrix.unit_ids == ("0", "1")
    assert set(matrix.labels.tolist()) == {"1", "2"}
    assert matrix.rows[0].total_spikes == 4


def test_v516_stratified_readout_runs_above_simple_baseline(tmp_path):
    path = tmp_path / "data" / "external" / "nwb" / "sample.nwb"
    _write_separable_nwb(path)
    matrix = build_nwb_task_feature_matrix_v516(path)

    readout = stratified_load_readout_v516(matrix, n_splits=3, label_shuffles=3, seed=2)

    assert readout["status"] == "single_sample_stratified_task_readout"
    assert readout["observed"]["balanced_accuracy"] >= 0.9
    assert readout["label_shuffle_baseline"]["shuffles"] == 3


def test_v516_gate_reports_missing_sample(tmp_path):
    summary = build_dandi_nwb_sdk_benchmark_v516(tmp_path, label_shuffles=1)

    assert summary["overall_status"] == "dandi_nwb_benchmark_missing_sample"
    assert summary["bic_os_phase_locked"] is True


def test_v516_write_outputs(tmp_path):
    _write_separable_nwb(tmp_path / "data" / "external" / "nwb" / "sample.nwb")

    paths = write_dandi_nwb_benchmark_outputs_v516(tmp_path, tmp_path / "out", label_shuffles=2)

    assert Path(paths["summary_json"]).exists()
    assert Path(paths["feature_matrix_npz"]).exists()
    assert Path(paths["trial_features_csv"]).exists()
    summary = json.loads(Path(paths["summary_json"]).read_text(encoding="utf-8"))
    assert summary["overall_status"] == "dandi_nwb_sdk_task_benchmark_available"


def test_v516_runner_writes_summary(tmp_path):
    _write_separable_nwb(tmp_path / "data" / "external" / "nwb" / "sample.nwb")

    result = run(root=tmp_path, out_dir=tmp_path / "out", label_shuffles=2)

    assert result["summary"]["sample_count"] == 12
    assert result["summary"]["readout_status"] == "single_sample_stratified_task_readout"
