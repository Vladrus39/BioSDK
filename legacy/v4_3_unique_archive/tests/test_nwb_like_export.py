import h5py
from biogpu.data import export_nwb_like_hdf5


def test_nwb_like_export_writes_hdf5(tmp_path):
    path = export_nwb_like_hdf5({
        "benchmark": "unit_test",
        "experiment_id": "exp1",
        "metrics": {"accuracy": 0.5},
        "baselines": {"raw_linear": 0.7},
        "stimulus": {"channels": [1, 2], "times": [0.0, 1.0]},
        "spikes": {"unit_ids": [1, 2], "spike_times": [0.1, 0.2]},
        "features": {"values": [0.1, 0.2], "names": ["a", "b"]},
    }, tmp_path / "exp1.h5")
    assert path.exists()
    with h5py.File(path, "r") as h5:
        assert h5.attrs["format"] == "biogpu-nwb-like-hdf5"
        assert h5["processing/metrics"].attrs["accuracy"] == 0.5
        assert "acquisition/spikes/unit_ids" in h5
