from __future__ import annotations
import h5py
import numpy as np

def save_arrays_hdf5(path: str, **arrays):
    with h5py.File(path, "w") as f:
        for name, arr in arrays.items():
            f.create_dataset(name, data=np.asarray(arr))
