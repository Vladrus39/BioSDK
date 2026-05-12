from biogpu.cli import main


def test_cli_contract_real_mea(capsys):
    code = main(["contract", "real-mea"])
    assert code == 0
    captured = capsys.readouterr().out
    assert "dry_run" in captured


def test_cli_contract_maxone(capsys):
    code = main(["contract", "maxone-like"])
    assert code == 0
    captured = capsys.readouterr().out
    assert "26400" in captured


def test_cli_dandi_candidates(capsys):
    code = main(["public-data", "dandi-candidates"])
    assert code == 0
    captured = capsys.readouterr().out
    assert "000469" in captured


def test_cli_task_aligned(tmp_path, capsys):
    spikes = tmp_path / "spikes.txt"
    spikes.write_text("1 0.1\n2 0.6\n1 1.1\n2 1.6\n", encoding="utf-8")
    windows = tmp_path / "windows.csv"
    windows.write_text("start_s,end_s,label\n0,0.5,A\n0.5,1.0,B\n1.0,1.5,A\n1.5,2.0,B\n", encoding="utf-8")
    code = main(["public-data", "task-aligned", str(spikes), str(windows), "--train-fraction", "0.5"])
    assert code == 0
    captured = capsys.readouterr().out
    assert "task_aligned_real_spikes" in captured
