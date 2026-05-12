"""Quick check of Allen NWB file."""
import h5py, numpy as np
from pathlib import Path

nwb = Path("data/external/allen/dandi_000021/sub-703279277_ses-719161530_probe-729445654_ecephys.nwb")
print(f"File: {nwb}")
print(f"Size: {nwb.stat().st_size / 1024 / 1024:.1f} MB")

with h5py.File(nwb, "r") as f:
    print(f"Top keys: {list(f.keys())}")
    if "acquisition" in f:
        acq = f["acquisition"]
        print(f"Acquisition: {list(acq.keys())}")
        for k in acq:
            item = acq[k]
            if hasattr(item, 'shape'):
                print(f"  {k}: dataset shape={item.shape}, dtype={item.dtype}")
            else:
                print(f"  {k}: group with keys={list(item.keys())}")
                for sub in item:
                    subitem = item[sub]
                    if hasattr(subitem, 'shape'):
                        print(f"    {sub}: shape={subitem.shape}, dtype={subitem.dtype}")
    
    if "units" in f:
        units = f["units"]
        print(f"Units: {list(units.keys())}")
        if "spike_times" in units:
            print(f"  spike_times: {units['spike_times'].shape}")
        if "spike_times_index" in units:
            sti = units["spike_times_index"]
            print(f"  n_units: {sti.shape[0]}")
