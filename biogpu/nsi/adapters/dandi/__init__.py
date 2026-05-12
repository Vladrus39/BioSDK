"""NSI-1.0 adapter for DANDI/Allen NWB ecephys files.

Handles NWB files with ElectricalSeries (LFP or ephys) in /acquisition.
For spike-sorted NWBs (units only), bins spikes to create a rate signal.

NWB is HDF5-based, but the schema differs from raw MEA HDF5:
    - Continuous data: /acquisition/<name>/data (n_samples x n_channels)
    - Electrodes: /acquisition/<name>/electrodes
    - Timestamps: /acquisition/<name>/timestamps
    - Spike data: /units/spike_times + /units/spike_times_index
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterator
import h5py
import numpy as np

from biogpu.nsi import (
    NSIAdapter, NSIDataset, NSIMetadata,
    _default_feature_vector, generate_feature_names,
)


def _find_electrical_series(h5file: h5py.File) -> tuple[str, str, np.ndarray, float]:
    """Find the first ElectricalSeries in acquisition.
    
    Returns: (group_path, data_key, data_array, sample_rate)
    """
    if "acquisition" not in h5file:
        raise ValueError("No /acquisition group in NWB file")

    acq = h5file["acquisition"]
    for series_name in acq:
        series = acq[series_name]
        if not isinstance(series, h5py.Group):
            continue
        
        # NWB ElectricalSeries is a group with 2D 'data' and 'timestamps'
        if "data" in series and hasattr(series["data"], 'shape') and len(series["data"].shape) >= 2:
            data = np.array(series["data"], dtype=np.float32)
            timestamps = np.array(series["timestamps"], dtype=np.float64) if "timestamps" in series else None
            
            if timestamps is not None and len(timestamps) > 1:
                sr = 1.0 / np.median(np.diff(timestamps[:1000]))
            else:
                sr = 30000.0
            
            return (f"acquisition/{series_name}", "data", data, float(sr))
        
        # Some NWB files have sub-groups
        for sub_name in series:
            sub = series[sub_name]
            if isinstance(sub, h5py.Group) and "data" in sub and hasattr(sub["data"], 'shape') and len(sub["data"].shape) >= 2:
                data = np.array(sub["data"], dtype=np.float32)
                timestamps = np.array(sub["timestamps"], dtype=np.float64) if "timestamps" in sub else None
                
                if timestamps is not None and len(timestamps) > 1:
                    sr = 1.0 / np.median(np.diff(timestamps[:1000]))
                else:
                    sr = 30000.0
                
                return (f"acquisition/{series_name}/{sub_name}", "data", data, float(sr))
    
    raise ValueError("No ElectricalSeries with 'data' found in /acquisition")


def _bin_spikes_to_rate(spike_times: np.ndarray, spike_index: np.ndarray, 
                        bin_ms: float, total_duration_s: float) -> np.ndarray:
    """Convert spike times to binned rate matrix (n_units x n_bins)."""
    n_units = len(spike_index)
    n_bins = int(total_duration_s * 1000 / bin_ms)
    rate = np.zeros((n_units, n_bins), dtype=np.float32)
    
    for u in range(n_units):
        start = spike_index[u - 1] if u > 0 else 0
        end = spike_index[u]
        times = np.array(spike_times[start:end], dtype=np.float64)
        if len(times) == 0:
            continue
        bins = np.floor(times * 1000 / bin_ms).astype(int)
        bins = bins[bins < n_bins]
        np.add.at(rate[u], bins, 1)
    
    # Convert to Hz
    rate = rate * 1000 / bin_ms
    return rate


class DandiNWBAdapter(NSIAdapter):
    """NSI-1.0 adapter for DANDI/Allen NWB ecephys files.

    Supports both continuous LFP/acquisition data and spike-sorted units.
    For spike data, bins spikes into a continuous rate representation.
    """

    adapter_id = "dandi_nwb"
    vendor = "dandi_allen"
    modality = "ecephys"

    def open(self, path: str | Path) -> NSIDataset:
        """Open an NWB file and return an NSIDataset."""
        p = Path(path)
        meta = self.metadata(p)

        with h5py.File(p, "r") as f:
            try:
                group_path, data_key, data, sample_rate = _find_electrical_series(f)
                meta.sample_rate_hz = sample_rate
                n_ch = data.shape[1]
            except ValueError:
                # No acquisition data — try spike units
                if "units" in f and "spike_times" in f["units"]:
                    st = np.array(f["units"]["spike_times"], dtype=np.float64)
                    sti = np.array(f["units"]["spike_times_index"], dtype=np.int64)
                    # Get total duration from timestamps or max spike time
                    if "timestamps_reference_time" in f:
                        total_s = float(st.max()) if len(st) > 0 else 600.0
                    else:
                        total_s = float(st.max()) if len(st) > 0 else 600.0
                    data = _bin_spikes_to_rate(st, sti, bin_ms=10.0, total_duration_s=total_s)
                    n_ch = data.shape[0]
                    meta.sample_rate_hz = 100.0  # 10ms bins = 100 Hz
                else:
                    raise ValueError(f"NWB file has neither acquisition data nor spike units: {p}")

        feature_names = generate_feature_names(max(n_ch, 1))

        return NSIDataset(
            metadata=meta,
            data=data,
            feature_names=feature_names,
            _adapter=self,
        )

    def metadata(self, path: str | Path) -> NSIMetadata:
        """Read metadata from an NWB file."""
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"NWB file not found: {p}")

        file_size_mb = p.stat().st_size / (1024 * 1024)

        with h5py.File(p, "r") as f:
            session_id = ""
            if "general" in f and "session_id" in f["general"]:
                session_id = str(f["general"]["session_id"][()])
            
            # Try acquisition first
            try:
                group_path, data_key, data, sample_rate = _find_electrical_series(f)
                n_ch = data.shape[1]
                n_samples = data.shape[0]
                duration_s = n_samples / sample_rate if sample_rate > 0 else None
            except ValueError:
                # Try spike units
                if "units" in f and "spike_times" in f["units"]:
                    st = f["units"]["spike_times"]
                    sti = f["units"]["spike_times_index"]
                    n_ch = sti.shape[0]
                    n_samples = st.shape[0]
                    sample_rate = 100.0
                    duration_s = float(st[-1]) if len(st) > 0 else None
                else:
                    n_ch = 0
                    n_samples = 0
                    sample_rate = 0.0
                    duration_s = None

        return NSIMetadata(
            source_path=str(p),
            source_format="nwb",
            vendor=self.vendor,
            modality=self.modality,
            channel_count=n_ch,
            sample_rate_hz=sample_rate,
            duration_s=duration_s,
            extra={
                "file_size_mb": round(file_size_mb, 1),
                "session_id": session_id,
                "n_samples": n_samples,
            },
        )

    def iter_windows(self, path: str | Path, window_s: float, overlap: float = 0.0) -> Iterator[np.ndarray]:
        """Iterate over sliding windows of continuous data."""
        p = Path(path)
        meta = self.metadata(p)
        
        with h5py.File(p, "r") as f:
            try:
                _, _, data, _ = _find_electrical_series(f)
            except ValueError:
                # Spike data
                if "units" in f:
                    st = np.array(f["units"]["spike_times"], dtype=np.float64)
                    sti = np.array(f["units"]["spike_times_index"], dtype=np.int64)
                    total_s = float(st.max()) if len(st) > 0 else 600.0
                    data = _bin_spikes_to_rate(st, sti, bin_ms=10.0, total_duration_s=total_s)
                else:
                    return
            
            sr = meta.sample_rate_hz if meta.sample_rate_hz > 0 else 100.0
            window_samples = int(window_s * sr)
            stride = max(1, int(window_samples * (1.0 - overlap)))
            
            if data.ndim == 2 and data.shape[1] < data.shape[0]:
                # Shape is (n_samples, n_channels) — typical NWB, transpose
                data = data.T
            
            if data.ndim == 2:
                # Shape is (n_channels, n_samples)
                n_samples = data.shape[1]
                start = 0
                while start + window_samples <= n_samples:
                    yield np.asarray(data[:, start:start + window_samples], dtype=np.float32)
                    start += stride
            else:
                return  # No data to iterate

    def feature_vector(self, window: np.ndarray, feature_names: list[str] | None = None) -> np.ndarray:
        """Extract features from a single window."""
        return _default_feature_vector(window)

    def close(self) -> None:
        """DANDI adapter is stateless."""
        pass


# Auto-register
from biogpu.nsi.adapters import register_adapter
register_adapter(DandiNWBAdapter)
