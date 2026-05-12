from pathlib import Path
from biogpu.data_ingest.stimulus_windows import StimulusWindow, write_stimulus_windows_csv
from biogpu.benchmarks.task_aligned_real import run_task_aligned_spike_benchmark


def test_task_aligned_spike_benchmark_runs(tmp_path: Path):
    spikes = tmp_path / "spikes.txt"
    # Two separable units/classes across four windows.
    spikes.write_text("1 0.10\n1 0.20\n2 0.70\n2 0.80\n1 1.10\n1 1.20\n2 1.70\n2 1.80\n", encoding="utf-8")
    windows = tmp_path / "windows.csv"
    write_stimulus_windows_csv([
        StimulusWindow(0.0, 0.5, label="A"),
        StimulusWindow(0.5, 1.0, label="B"),
        StimulusWindow(1.0, 1.5, label="A"),
        StimulusWindow(1.5, 2.0, label="B"),
    ], windows)
    result = run_task_aligned_spike_benchmark(str(spikes), str(windows), train_fraction=0.5, seed=1)
    assert result["benchmark"] == "task_aligned_real_spikes"
    assert result["window_summary"]["labeled_window_count"] == 4
    assert result["metrics"]["labeled_windows_used"] == 4
    assert result["metrics"]["accuracy"] is not None
