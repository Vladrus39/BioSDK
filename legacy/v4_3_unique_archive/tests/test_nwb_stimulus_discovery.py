from pathlib import Path
import h5py,numpy as np
from biogpu.data_ingest.nwb_stimulus_discovery import inspect_nwb_structure, discover_stimulus_tables, build_windows_from_simple_intervals

def _make_fake_nwb(path:Path):
    with h5py.File(path,'w') as h5:
        units=h5.create_group('units'); units.create_dataset('spike_times',data=np.array([0.1,0.2,1.1])); units.create_dataset('spike_times_index',data=np.array([2,3]))
        trials=h5.create_group('intervals').create_group('trials'); trials.create_dataset('start_time',data=np.array([0.0,1.0])); trials.create_dataset('stop_time',data=np.array([0.5,1.5])); trials.create_dataset('condition',data=np.array([b'A',b'B']))

def test_nwb_discovery_finds_trials(tmp_path:Path):
    p=tmp_path/'fake.nwb'; _make_fake_nwb(p)
    info=inspect_nwb_structure(p); assert info['has_units'] is True
    cands=discover_stimulus_tables(p); assert any(c.path=='/intervals/trials' for c in cands)

def test_build_windows_from_simple_intervals(tmp_path:Path):
    p=tmp_path/'fake.nwb'; _make_fake_nwb(p)
    windows=build_windows_from_simple_intervals(p,'/intervals/trials',label_column='condition')
    assert len(windows)==2 and windows[0]['label']=='A'
