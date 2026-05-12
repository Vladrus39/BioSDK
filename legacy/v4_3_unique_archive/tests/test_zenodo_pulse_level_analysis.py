from pathlib import Path

from biogpu.analysis.zenodo_pulse_level import analyze_pulse_responses, pulse_response_summary


def test_pulse_response_analysis_counts_target_response(tmp_path: Path):
    root = tmp_path
    rec = root / "EXP PTSD" / "01-01-2024" / "12345_10DIV" / "12345_10DIV_LightStim_Spot34_D-00144"
    (rec / "metadata").mkdir(parents=True)
    (rec / "stimulation_protocols").mkdir()
    (rec / "metadata" / "meta_data.csv").write_text(
        "recording_duration_sec\tsampling_fr_hz\tstimulation\n10\t1000\tLightStim\n",
        encoding="utf-8",
    )
    # Protocol is in seconds here because values fit within duration_s.
    (rec / "stimulation_protocols" / "34_stimulation_protocol.csv").write_text(
        "start,end,target\n1.0,1.02,34\n3.0,3.02,34\n",
        encoding="utf-8",
    )
    # Target spikes occur in post-stimulus response windows, not in pre windows.
    (rec / "electrode034.csv").write_text("sample_num\n1030\n3040\n", encoding="utf-8")
    (rec / "electrode035.csv").write_text("sample_num\n900\n2900\n", encoding="utf-8")

    rows = analyze_pulse_responses(root, response_window_ms=100)
    assert len(rows) == 1
    r = rows[0]
    assert r.target_electrode_present is True
    assert r.target_response_delta_rate_hz > 0
    assert r.target_pulse_fraction_response_gt_pre == 1.0
    summary = pulse_response_summary(rows)
    assert summary["recordings_with_protocols"] == 1
    assert summary["lightstim"]["recordings"] == 1
