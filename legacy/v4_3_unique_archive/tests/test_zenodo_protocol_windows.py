from pathlib import Path

from biogpu.data_ingest.zenodo_protocol_windows import read_protocol_windows_for_recording, summarize_protocol_windows


def _make_rec(tmp_path: Path) -> Path:
    rec = tmp_path / "EXP PTSD" / "01-01-2024" / "12345_10DIV" / "12345_10DIV_LightStim_Spot34_D-00144"
    (rec / "metadata").mkdir(parents=True)
    (rec / "stimulation_protocols").mkdir()
    (rec / "metadata" / "meta_data.csv").write_text(
        "recording_duration_sec\tsampling_fr_hz\tstimulation\n604.5\t20000\tLightStim\n",
        encoding="utf-8",
    )
    (rec / "electrode034.csv").write_text("sample_num\n100\n", encoding="utf-8")
    (rec / "stimulation_protocols" / "34_stimulation_protocol.csv").write_text(
        "start,end,target\n1869.65,1889.65,34\n3869.65,3889.65,34\n",
        encoding="utf-8",
    )
    return rec


def test_protocol_windows_infer_ms(tmp_path: Path):
    rec = _make_rec(tmp_path)
    windows = read_protocol_windows_for_recording(rec, tmp_path)
    assert len(windows) == 2
    assert windows[0].inferred_time_unit == "ms"
    assert round(windows[0].start_s, 5) == 1.86965
    assert round(windows[0].duration_s, 5) == 0.02
    assert windows[0].target_id == 34
    assert windows[0].quality == "exact_protocol_csv_pulse_window"


def test_protocol_window_summary(tmp_path: Path):
    rec = _make_rec(tmp_path)
    summary = summarize_protocol_windows(read_protocol_windows_for_recording(rec, tmp_path))
    assert summary["pulse_window_count"] == 2
    assert summary["recording_count_with_protocols"] == 1
    assert summary["targets_by_condition"]["lightstim"] == [34]
