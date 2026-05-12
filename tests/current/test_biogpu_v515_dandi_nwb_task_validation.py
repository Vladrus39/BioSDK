from __future__ import annotations

import json
from pathlib import Path

import h5py

from biogpu.benchmarks.biogpu_v515_dandi_nwb_task_validation import run
from biogpu.sdk.nwb_task_validation_v515 import build_dandi_nwb_task_validation_gate_v515, find_local_nwb_samples_v515, validate_nwb_task_sample_v515, write_dandi_nwb_task_outputs_v515


def _write_minimal_nwb(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with h5py.File(path, "w") as h5:
        units = h5.create_group("units")
        units.create_dataset("spike_times", data=[0.1, 0.2, 0.4, 1.0])
        units.create_dataset("spike_times_index", data=[2, 4])
        intervals = h5.create_group("intervals")
        trials = intervals.create_group("trials")
        trials.create_dataset("start_time", data=[0.0, 0.5, 1.0])
        trials.create_dataset("stop_time", data=[0.25, 0.75, 1.25])
        trials.create_dataset("loads", data=[1, 2, 3])
        stimulus = h5.create_group("stimulus")
        presentation = stimulus.create_group("presentation")
        presentation.create_group("StimulusPresentation")


def test_v515_finds_local_nwb_samples(tmp_path):
    _write_minimal_nwb(tmp_path / "data" / "external" / "nwb" / "sample.nwb")

    samples = find_local_nwb_samples_v515(tmp_path)

    assert len(samples) == 1
    assert samples[0].name == "sample.nwb"


def test_v515_validates_units_trials_and_windows(tmp_path):
    path = tmp_path / "data" / "external" / "nwb" / "sample.nwb"
    _write_minimal_nwb(path)

    report = validate_nwb_task_sample_v515(path)
    validation = report["validation"]

    assert validation["gate_status"] == "dandi_nwb_task_sample_validated"
    assert validation["unit_count"] == 2
    assert validation["spike_times_count"] == 4
    assert validation["exported_window_count"] == 3
    assert validation["selected_interval_path"] == "/intervals/trials"
    assert validation["selected_label_column"] == "loads"


def test_v515_gate_reports_missing_sample(tmp_path):
    gate = build_dandi_nwb_task_validation_gate_v515(tmp_path)

    assert gate["overall_status"] == "dandi_nwb_sample_missing"
    assert gate["bic_os_phase_locked"] is True


def test_v515_write_outputs(tmp_path):
    _write_minimal_nwb(tmp_path / "data" / "external" / "nwb" / "sample.nwb")

    paths = write_dandi_nwb_task_outputs_v515(tmp_path, tmp_path / "out")

    assert Path(paths["summary_json"]).exists()
    assert Path(paths["sample_reports_json"]).exists()
    assert Path(paths["task_windows_csv"]).exists()
    summary = json.loads(Path(paths["summary_json"]).read_text(encoding="utf-8"))
    assert summary["overall_status"] == "dandi_nwb_task_sample_validated"


def test_v515_runner_writes_summary(tmp_path):
    _write_minimal_nwb(tmp_path / "data" / "external" / "nwb" / "sample.nwb")

    result = run(root=tmp_path, out_dir=tmp_path / "out")

    assert result["summary"]["validated_sample_count"] == 1
    assert result["summary"]["total_exported_window_count"] == 3
