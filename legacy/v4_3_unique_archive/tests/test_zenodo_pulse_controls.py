from pathlib import Path

from biogpu.analysis.zenodo_pulse_controls import (
    compute_electrode_pulse_responses,
    summarize_recording_controls,
    write_control_outputs,
)


def _make_control_rec(tmp_path: Path) -> Path:
    rec = tmp_path / "EXP PTSD" / "01-01-2024" / "12345_10DIV" / "12345_10DIV_LightStim_Spot34_D-00144"
    (rec / "metadata").mkdir(parents=True)
    (rec / "stimulation_protocols").mkdir()
    (rec / "metadata" / "meta_data.csv").write_text(
        "recording_duration_sec\tsampling_fr_hz\tstimulation\n10\t1000\tLightStim\n",
        encoding="utf-8",
    )
    (rec / "stimulation_protocols" / "34_stimulation_protocol.csv").write_text(
        "start,end,target\n1.0,1.02,34\n3.0,3.02,34\n5.0,5.02,34\n",
        encoding="utf-8",
    )
    # Target electrode fires in post-stimulus response windows.
    (rec / "electrode034.csv").write_text("sample_num\n1030\n3040\n5060\n", encoding="utf-8")
    # Non-target electrode fires in pre windows, so it should not beat target.
    (rec / "electrode035.csv").write_text("sample_num\n930\n2940\n4960\n", encoding="utf-8")
    (rec / "electrode036.csv").write_text("sample_num\n", encoding="utf-8")
    return rec


def test_compute_electrode_pulse_responses_identifies_target(tmp_path: Path):
    rec = _make_control_rec(tmp_path)
    rows = compute_electrode_pulse_responses(rec, tmp_path, response_window_ms=100)
    assert len(rows) == 3
    target = [r for r in rows if r.is_target][0]
    assert target.electrode_id == 34
    assert target.response_delta_rate_hz > 0
    assert target.response_percentile == 100.0

    controls = summarize_recording_controls(rows)
    assert len(controls) == 1
    assert controls[0].target_electrode_present is True
    assert controls[0].target_response_percentile == 100.0
    assert controls[0].random_electrode_percentile_median < 100.0


def test_write_control_outputs_has_null_p_values(tmp_path: Path):
    _make_control_rec(tmp_path)
    out = tmp_path / "out"
    summary = write_control_outputs(
        tmp_path,
        out,
        response_window_ms=100,
        n_random_electrode_permutations=25,
        n_random_time_permutations=10,
        seed=1,
        make_plots=False,
    )
    assert summary["recordings_with_target"] == 1
    assert summary["random_electrode_null"]["permutations"] == 25
    assert summary["random_electrode_null"]["p_value_target_percentile_gt_random_electrode"] is not None
    assert (out / "pulse_control_summary.json").exists()
    assert (out / "PULSE_LEVEL_CONTROLS_REPORT.md").exists()
