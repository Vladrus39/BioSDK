from pathlib import Path

from biogpu.analysis.zenodo_pulse_readout import (
    build_candidate_target_table,
    build_pulse_feature_matrix,
    leave_one_culture_candidate_readout,
    leave_one_culture_target_id_readout,
    write_readout_outputs,
)


def _write_rec(root: Path, culture: str, target: int, rec_suffix: str, pulses: list[float]) -> None:
    rec = root / "EXP PTSD" / "01-01-2024" / culture / f"{culture}_LightStim_Spot{target}_{rec_suffix}"
    (rec / "metadata").mkdir(parents=True)
    (rec / "stimulation_protocols").mkdir()
    (rec / "metadata" / "meta_data.csv").write_text(
        "recording_duration_sec\tsampling_fr_hz\tstimulation\n10\t1000\tLightStim\n",
        encoding="utf-8",
    )
    protocol_lines = ["start,end,target"]
    target_samples = ["sample_num"]
    other = 35 if target == 34 else 34
    other_samples = ["sample_num"]
    for p in pulses:
        protocol_lines.append(f"{p},{p + 0.02},{target}")
        target_samples.append(str(int((p + 0.05) * 1000)))
        other_samples.append(str(int((p - 0.05) * 1000)))
    (rec / "stimulation_protocols" / f"{target}_stimulation_protocol.csv").write_text(
        "\n".join(protocol_lines) + "\n",
        encoding="utf-8",
    )
    (rec / f"electrode{target:03d}.csv").write_text("\n".join(target_samples) + "\n", encoding="utf-8")
    (rec / f"electrode{other:03d}.csv").write_text("\n".join(other_samples) + "\n", encoding="utf-8")


def _make_readout_root(tmp_path: Path) -> Path:
    _write_rec(tmp_path, "CULTURE_A_10DIV", 34, "A", [1.0, 3.0, 5.0])
    _write_rec(tmp_path, "CULTURE_A_10DIV", 35, "B", [1.5, 3.5, 5.5])
    _write_rec(tmp_path, "CULTURE_B_10DIV", 34, "C", [1.0, 3.0, 5.0])
    _write_rec(tmp_path, "CULTURE_B_10DIV", 35, "D", [1.5, 3.5, 5.5])
    return tmp_path


def test_build_pulse_feature_matrix_uses_one_row_per_pulse(tmp_path: Path):
    root = _make_readout_root(tmp_path)
    matrix = build_pulse_feature_matrix(root, response_window_ms=100)
    assert matrix.X.shape[0] == 12
    assert len(matrix.metadata) == 12
    assert set(matrix.electrodes) == {34, 35}
    assert matrix.X.shape[1] == 12  # 6 feature blocks x 2 electrodes


def test_target_id_and_candidate_readouts_run(tmp_path: Path):
    root = _make_readout_root(tmp_path)
    matrix = build_pulse_feature_matrix(root, response_window_ms=100)
    target = leave_one_culture_target_id_readout(matrix, n_label_shuffles=2, seed=1)
    assert target["sample_count"] == 12
    assert target["culture_count"] == 2
    assert target["observed"]["seen_label_accuracy"] is not None

    table = build_candidate_target_table(matrix, negative_per_pulse=1, seed=1)
    assert table.X.shape[0] == 24
    candidate = leave_one_culture_candidate_readout(table, n_label_shuffles=2, seed=2)
    assert candidate["pulse_count_used"] == 12
    assert candidate["observed"]["roc_auc"] >= 0.5


def test_write_readout_outputs(tmp_path: Path):
    root = _make_readout_root(tmp_path / "root")
    out = tmp_path / "out"
    summary = write_readout_outputs(
        root,
        out,
        response_window_ms=100,
        n_label_shuffles=2,
        negative_per_pulse=1,
        seed=3,
        make_plots=False,
    )
    assert summary["feature_matrix"]["pulse_count"] == 12
    assert (out / "pulse_feature_matrix.npz").exists()
    assert (out / "pulse_feature_metadata.csv").exists()
    assert (out / "candidate_target_readout_summary.json").exists()
    assert (out / "PULSE_LEVEL_READOUT_REPORT.md").exists()
