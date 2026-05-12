from pathlib import Path
from biogpu.schemas import SpikeTrain
from biogpu.data_ingest.stimulus_windows import (
    StimulusWindow,
    write_stimulus_windows_csv,
    read_stimulus_windows_csv,
    slice_spikes_to_window,
    build_windowed_spiketrains,
    summarize_windows,
)


def test_window_csv_and_slice(tmp_path: Path):
    csv_path = tmp_path / "windows.csv"
    windows = [StimulusWindow(0.0, 0.5, label="A"), StimulusWindow(0.5, 1.0, label="B")]
    write_stimulus_windows_csv(windows, csv_path)
    loaded = read_stimulus_windows_csv(csv_path)
    assert len(loaded) == 2
    spikes = SpikeTrain(unit_ids=[1, 1, 2], spike_times=[0.1, 0.6, 1.2])
    st = slice_spikes_to_window(spikes, loaded[0])
    assert st.unit_ids == [1]
    sts, labels, used = build_windowed_spiketrains(spikes, loaded)
    assert labels == ["A", "B"]
    assert summarize_windows(loaded)["labeled_window_count"] == 2
