from pathlib import Path
from biogpu.benchmarks.real_spike_profile import run_zenodo_profile

def test_run_zenodo_profile(tmp_path: Path):
    p=tmp_path/"spikes.txt"; p.write_text("1 0.01\n1 0.02\n2 0.03\n", encoding="utf-8")
    r=run_zenodo_profile(str(tmp_path), window_ms=100, spike_glob="*.txt")
    assert r["metrics"]["spike_count"] == 3
    assert r["metrics"]["active_units"] == 2
