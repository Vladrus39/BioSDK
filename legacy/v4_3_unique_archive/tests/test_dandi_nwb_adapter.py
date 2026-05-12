from pathlib import Path
import h5py, numpy as np
from biogpu.data_ingest.dandi_nwb import inspect_nwb_units, read_nwb_units_as_spiketrain, DandiNWBConfig, DandiNWBSpikeAdapter

def _make(path: Path):
    with h5py.File(path,"w") as h5:
        u=h5.create_group("units"); u.create_dataset("spike_times", data=np.asarray([0.1,0.2,0.5,1.0])); u.create_dataset("spike_times_index", data=np.asarray([2,4]))

def test_inspect_and_read_nwb_units(tmp_path: Path):
    p=tmp_path/"test.nwb"; _make(p)
    assert inspect_nwb_units(p)["has_units"] is True
    spikes=read_nwb_units_as_spiketrain(p, window_ms=600)
    assert spikes.unit_ids == [0,0,1]

def test_dandi_adapter_health(tmp_path: Path):
    p=tmp_path/"test.nwb"; _make(p); adapter=DandiNWBSpikeAdapter(DandiNWBConfig(nwb_path=str(p))); adapter.connect()
    assert adapter.health_check()["has_units"] is True
