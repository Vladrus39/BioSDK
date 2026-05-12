from __future__ import annotations

from pathlib import Path
from typing import Any

import h5py
import numpy as np


def export_nwb_like_hdf5(record: dict[str, Any], output_path: str | Path) -> Path:
    """Write an NWB-inspired HDF5 skeleton for BioGPU runs.

    This is NOT a valid NWB file yet. It is a deliberately conservative bridge:
    it uses HDF5 groups and names aligned with future PyNWB export so that the
    project can later map these fields to real NWB objects.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    metrics = record.get("metrics", {}) or {}
    baselines = record.get("baselines", {}) or {}
    stim = record.get("stimulus", {}) or {}
    features = record.get("features", {}) or {}
    spikes = record.get("spikes", {}) or {}

    with h5py.File(path, "w") as h5:
        h5.attrs["format"] = "biogpu-nwb-like-hdf5"
        h5.attrs["schema_version"] = str(record.get("schema_version", "0.6"))
        h5.attrs["project_version"] = str(record.get("project_version", "0.6"))
        h5.attrs["warning"] = "NWB-like skeleton only; not a valid NWB file"
        general = h5.create_group("general")
        general.attrs["benchmark"] = str(record.get("benchmark", "unknown"))
        general.attrs["experiment_id"] = str(record.get("experiment_id", "unknown"))

        processing = h5.create_group("processing")
        metrics_group = processing.create_group("metrics")
        for key, value in metrics.items():
            if isinstance(value, (int, float, np.number)):
                metrics_group.attrs[key] = float(value)
            else:
                metrics_group.attrs[key] = str(value)
        baselines_group = processing.create_group("baselines")
        for key, value in baselines.items():
            if isinstance(value, (int, float, np.number)):
                baselines_group.attrs[key] = float(value)
            else:
                baselines_group.attrs[key] = str(value)

        acquisition = h5.create_group("acquisition")
        acquisition.create_group("raw_electrophysiology_placeholder")
        spikes_group = acquisition.create_group("spikes")
        if "unit_ids" in spikes:
            spikes_group.create_dataset("unit_ids", data=np.asarray(spikes["unit_ids"], dtype=np.int64))
        if "spike_times" in spikes:
            spikes_group.create_dataset("spike_times", data=np.asarray(spikes["spike_times"], dtype=float))

        stimulus_group = h5.create_group("stimulus")
        for key, value in stim.items():
            if isinstance(value, (list, tuple, np.ndarray)):
                try:
                    stimulus_group.create_dataset(key, data=np.asarray(value))
                except TypeError:
                    stimulus_group.attrs[key] = str(value)
            else:
                stimulus_group.attrs[key] = str(value)

        features_group = processing.create_group("features")
        if "values" in features:
            features_group.create_dataset("values", data=np.asarray(features["values"], dtype=float))
        if "names" in features:
            names = np.asarray([str(x).encode("utf-8") for x in features["names"]])
            features_group.create_dataset("names", data=names)
    return path


def export_nwb_placeholder(*args, **kwargs):
    """Backward-compatible alias for older code paths."""
    return export_nwb_like_hdf5(*args, **kwargs)
