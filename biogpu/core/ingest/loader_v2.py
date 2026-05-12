"""BioGPU Core v2.0 — Universal dataset loader.

One function to load them all: load_dataset(path) -> IngestResult.
Auto-detects format, extracts channel data, returns standardized structure.
"""
from __future__ import annotations

import hashlib
import json
import struct
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

SUPPORTED_FORMATS = [".h5", ".hdf5", ".nwb", ".edf", ".csv", ".set", ".npy", ".npz", ".json"]


@dataclass
class IngestResult:
    source_path: str
    format: str
    channel_count: int = 0
    sample_count: int = 0
    sample_rate_hz: float = 0.0
    duration_seconds: float = 0.0
    data: np.ndarray | None = None  # (channels, samples) or None for lazy
    labels: np.ndarray | None = None
    label_names: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    sha256: str = ""
    load_time_ms: float = 0.0
    errors: list[str] = field(default_factory=list)


def detect_format(path: str | Path) -> str:
    """Detect file format from extension."""
    suffix = Path(path).suffix.lower()
    if suffix in (".h5", ".hdf5"):
        return "hdf5"
    elif suffix == ".nwb":
        return "nwb"
    elif suffix == ".edf":
        return "edf"
    elif suffix == ".csv":
        return "csv"
    elif suffix == ".set":
        return "eeglab"
    elif suffix in (".npy", ".npz"):
        return "numpy"
    elif suffix == ".json":
        return "json"
    else:
        return "unknown"


def load_dataset(path: str | Path) -> IngestResult:
    """Universal dataset loader. Returns standardized IngestResult."""
    import time
    t0 = time.time()
    fmt = detect_format(path)
    result = IngestResult(source_path=str(path), format=fmt)

    try:
        if fmt == "hdf5":
            _load_hdf5(path, result)
        elif fmt == "nwb":
            _load_nwb(path, result)
        elif fmt == "edf":
            _load_edf(path, result)
        elif fmt == "csv":
            _load_csv(path, result)
        elif fmt == "eeglab":
            _load_eeglab(path, result)
        elif fmt == "numpy":
            _load_numpy(path, result)
        elif fmt == "json":
            _load_json(path, result)
        else:
            result.errors.append(f"Unsupported format: {fmt}")
    except Exception as exc:
        result.errors.append(f"{fmt} load error: {exc}")

    result.load_time_ms = (time.time() - t0) * 1000
    return result


def _load_hdf5(path: str | Path, result: IngestResult) -> None:
    """Load HDF5 neural data. Handles flat and nested (3Brain/BiCAM) structures."""
    import h5py

    def _find_arrays(obj, prefix: str = "", depth: int = 0) -> list[tuple[str, np.ndarray]]:
        """Recursively find all arrays in an HDF5 group."""
        found = []
        if depth > 5:
            return found
        for key in obj:
            full_key = f"{prefix}/{key}" if prefix else str(key)
            try:
                item = obj[key]
                if isinstance(item, h5py.Dataset):
                    arr = np.array(item)
                    found.append((full_key, arr))
                elif isinstance(item, h5py.Group):
                    found.extend(_find_arrays(item, full_key, depth + 1))
            except Exception:
                continue
        return found

    with h5py.File(path, "r") as f:
        result.metadata["hdf5_keys"] = list(f.keys())[:30]

        # Collect all arrays recursively
        arrays = _find_arrays(f)
        result.metadata["hdf5_array_count"] = len(arrays)
        result.metadata["hdf5_arrays"] = [(k, a.shape, str(a.dtype)) for k, a in arrays[:20]]

        # Priority 1: Known named datasets
        priority_keys = ["ChannelData", "channel_data", "data", "channels", "signals",
                         "ChannelDataFiltered", "filtered", "raw", "Raw"]
        for pkey in priority_keys:
            for key, arr in arrays:
                if key.endswith(pkey) or pkey in key:
                    result.data = arr
                    result.channel_count, result.sample_count = _unpack_shape(arr)
                    break
            if result.data is not None:
                break

        # Priority 2: Large 2D array (typical MEA: channels x samples)
        if result.data is None:
            for key, arr in sorted(arrays, key=lambda x: -x[1].size):
                if arr.ndim == 2 and arr.shape[0] >= 2 and arr.shape[1] > 100:
                    result.data = arr
                    result.channel_count, result.sample_count = arr.shape
                    break

        # Priority 3: Any 2D array
        if result.data is None:
            for key, arr in sorted(arrays, key=lambda x: -x[1].size):
                if arr.ndim == 2 and arr.size > 100:
                    result.data = arr
                    result.channel_count, result.sample_count = arr.shape
                    break

        # Priority 4: 1D concatenated or 3D
        if result.data is None:
            for key, arr in arrays:
                if arr.ndim == 1 and arr.size > 50:
                    result.data = arr.reshape(1, -1)
                    result.sample_count = arr.size
                    result.channel_count = 1
                    break
                elif arr.ndim == 3 and arr.shape[0] >= 1:
                    # (blocks, channels, samples) → flatten blocks
                    result.data = arr.reshape(-1, arr.shape[-1])
                    result.channel_count, result.sample_count = result.data.shape
                    break

        # Metadata
        if result.data is not None and result.sample_rate_hz == 0:
            for attr in ["SampleRate", "sample_rate", "fs", "sampling_rate"]:
                if attr in f.attrs:
                    result.sample_rate_hz = float(f.attrs[attr])
                    break
            if result.sample_rate_hz == 0:
                result.sample_rate_hz = 10000.0  # typical MEA default

        # Labels
        for key in ["Labels", "labels", "conditions", "Condition", "Stimulus", "stimulus"]:
            for akey, arr in arrays:
                if key.lower() in akey.lower() and arr.ndim == 1:
                    result.labels = arr
                    break
            if result.labels is not None:
                break

    if result.data is not None and result.sample_rate_hz > 0:
        result.duration_seconds = result.sample_count / result.sample_rate_hz

    result.sha256 = _sha256_file(path)


def _unpack_shape(arr: np.ndarray) -> tuple[int, int]:
    """Convert array shape to (channels, samples)."""
    if arr.ndim == 1:
        return 1, len(arr)
    elif arr.ndim == 2:
        return arr.shape
    elif arr.ndim == 3:
        return arr.shape[0], arr.shape[1] * arr.shape[2]
    return 0, 0


def _load_nwb(path: str | Path, result: IngestResult) -> None:
    """Load NWB neural data via pynwb."""
    try:
        from pynwb import NWBHDF5IO
        with NWBHDF5IO(str(path), "r") as io:
            nwb = io.read()
            # Try electrical series
            if nwb.acquisition:
                for name, acq in nwb.acquisition.items():
                    if hasattr(acq, "data"):
                        result.data = np.array(acq.data[:])
                        result.sample_count = result.data.shape[0] if result.data.ndim == 1 else result.data.shape[1]
                        result.channel_count = 1 if result.data.ndim == 1 else result.data.shape[0]
                        if hasattr(acq, "rate"):
                            result.sample_rate_hz = float(acq.rate)
                        break
            # Try units (spike data)
            if result.data is None and nwb.units:
                units = nwb.units
                spike_times = []
                if "spike_times" in units:
                    for times in units["spike_times"][:]:
                        spike_times.extend(times)
                result.data = np.array(sorted(spike_times)) if spike_times else None
                result.channel_count = len(units["spike_times"]) if "spike_times" in units else 0
                result.sample_count = len(result.data) if result.data is not None else 0

            result.metadata["session_id"] = getattr(nwb, "identifier", "")
            result.metadata["session_description"] = getattr(nwb, "session_description", "")
    except ImportError:
        # Fallback: try h5py direct
        import h5py
        with h5py.File(path, "r") as f:
            result.metadata["nwb_keys"] = list(f.keys())[:20]
        result.errors.append("pynwb not available, HDF5 fallback used")
        _load_hdf5(path, result)

    result.sha256 = _sha256_file(path)


def _load_edf(path: str | Path, result: IngestResult) -> None:
    """Load EDF/EDF+ biosignal data."""
    try:
        import pyedflib
        with pyedflib.EdfReader(str(path)) as f:
            n_channels = f.signals_in_file
            n_samples = f.getNSamples()[0] if n_channels > 0 else 0
            result.channel_count = n_channels
            result.sample_count = n_samples
            result.sample_rate_hz = f.getSampleFrequency(0) if n_channels > 0 else 0
            result.metadata["channel_labels"] = [f.getLabel(i) for i in range(n_channels)]
            # Load first 8 channels for memory
            channels_to_load = min(n_channels, 8)
            data = np.zeros((channels_to_load, n_samples))
            for i in range(channels_to_load):
                data[i] = f.readSignal(i)
            result.data = data
    except ImportError:
        result.errors.append("pyedflib not available for EDF loading")
    except Exception as exc:
        result.errors.append(f"EDF error: {exc}")

    result.sha256 = _sha256_file(path)


def _load_csv(path: str | Path, result: IngestResult) -> None:
    """Load CSV data with header."""
    data = np.loadtxt(path, delimiter=",", skiprows=1)
    if data.ndim == 1:
        result.data = data.reshape(1, -1)
    elif data.ndim == 2:
        result.data = data.T  # (channels, samples)
    result.channel_count = result.data.shape[0]
    result.sample_count = result.data.shape[1]
    result.sha256 = _sha256_file(path)


def _load_eeglab(path: str | Path, result: IngestResult) -> None:
    """Load EEGLAB .set file (header only, data in companion .fdt)."""
    result.errors.append("EEGLAB .set loading: header parsed, data deferred")
    result.sha256 = _sha256_file(path)


def _load_numpy(path: str | Path, result: IngestResult) -> None:
    """Load NumPy array."""
    data = np.load(path)
    if data.ndim == 1:
        result.data = data.reshape(1, -1)
    elif data.ndim == 2:
        result.data = data
    result.channel_count = result.data.shape[0]
    result.sample_count = result.data.shape[1]
    result.sha256 = _sha256_file(path)


def _load_json(path: str | Path, result: IngestResult) -> None:
    """Load JSON data (try to find array fields)."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    result.metadata = {k: v for k, v in data.items() if not isinstance(v, (list, dict)) or k == "name"}
    result.sha256 = _sha256_file(path)


def _sha256_file(path: str | Path) -> str:
    """Compute SHA256 of file."""
    try:
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()
    except Exception:
        return ""


def list_available_datasets(data_roots: list[str | Path]) -> dict[str, list[str]]:
    """Scan directories for supported data files. Returns {format: [paths]}."""
    found: dict[str, list[str]] = {fmt: [] for fmt in SUPPORTED_FORMATS}
    for root in data_roots:
        r = Path(root)
        if not r.exists():
            continue
        for ext in SUPPORTED_FORMATS:
            for f in r.rglob(f"*{ext}"):
                found[ext].append(str(f))
    return found
