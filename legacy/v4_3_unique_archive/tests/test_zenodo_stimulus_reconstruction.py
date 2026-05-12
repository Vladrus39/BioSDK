from pathlib import Path

from biogpu.data_ingest.zenodo_stimulus_reconstruction import (
    assess_pulse_window_availability,
    extract_target,
    normalize_condition,
    reconstruct_recording_level_windows,
)


def test_condition_and_target_parsing():
    assert normalize_condition("A_LightStim_Spot34_D-00144", {"stimulation": "LightStim"}) == "lightstim"
    assert extract_target("A_LightStim_Spot34_D-00144", "lightstim") == ("light_spot", 34)
    assert normalize_condition("A_Stim74_D-00144", {"stimulation": "ElecStim"}) == "elecstim"
    assert extract_target("A_Stim74_D-00144", "elecstim") == ("stimulation_electrode", 74)
    assert normalize_condition("A_D-00144", {"stimulation": ""}) == "baseline"


def test_reconstruct_recording_level_windows_tmp(tmp_path: Path):
    rec = tmp_path / "EXP PTSD" / "01-01-2022" / "123_10DIV" / "123_10DIV_LightStim_Spot55_D-00144"
    (rec / "metadata").mkdir(parents=True)
    (rec / "metadata" / "meta_data.csv").write_text(
        "recording_duration_sec\tsampling_fr_hz\tstimulation\tscale_factor\tpeak_lifetime_period_ms\trefractory_period_ms\n"
        "604.5\t20000\tLightStim\t8\t2\t1\n",
        encoding="utf-8",
    )
    (rec / "electrode012.csv").write_text("sample_num\n10\n", encoding="utf-8")
    windows = reconstruct_recording_level_windows(tmp_path)
    assert len(windows) == 1
    assert windows[0].condition == "lightstim"
    assert windows[0].target_id == 55
    assert windows[0].end_s == 604.5


def test_pulse_assessment_no_timing_fields(tmp_path: Path):
    meta = tmp_path / "r" / "metadata"
    meta.mkdir(parents=True)
    (meta / "meta_data.csv").write_text("recording_duration_sec\tsampling_fr_hz\nstim\t20000\n", encoding="utf-8")
    assessment = assess_pulse_window_availability(tmp_path)
    assert assessment["pulse_level_reconstruction_possible_from_preprocessed_metadata"] is False
