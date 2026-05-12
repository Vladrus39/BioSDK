"""NSI-1.0 adapter for MCS MEA2100 HDF5 exports.

Multi Channel Systems MEA2100 data uses the same HDF5 path as Giroldini:
    Data/Recording_0/AnalogStream/Stream_N/ChannelData

The differences are in dimensions (fewer channels, lower sample rate) and
stream count (3 streams vs 1). Streams may have mismatched sample counts;
the adapter truncates to the minimum length when concatenating.
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

MCS_HDF5_PATH = "Data/Recording_0/AnalogStream"


def _load_streams(h5file, path: str) -> list[np.ndarray]:
    """Load all streams from an HDF5 AnalogStream group, sorted by name."""
    analog = h5file[path]
    streams = []
    for stream_name in sorted(analog.keys()):
        ch_data = np.array(analog[stream_name]["ChannelData"], dtype=np.float32)
        streams.append(ch_data)
    return streams


def _concat_streams(streams: list[np.ndarray]) -> np.ndarray:
    """Concatenate streams along axis=0, truncating to minimum sample count."""
    if not streams:
        return np.array([], dtype=np.float32)
    min_samples = min(s.shape[1] for s in streams)
    truncated = [s[:, :min_samples] for s in streams]
    return np.concatenate(truncated, axis=0)


class MCSAdapter(NSIAdapter):
    """NSI-1.0 adapter for MCS MEA2100 HDF5 files."""

    adapter_id = "mcs_mea2100"
    vendor = "mcs"
    modality = "mea"

    # Known sample rate for this MCS recording (Hz)
    SAMPLE_RATE_HZ = 500.0

    def open(self, path: str | Path) -> NSIDataset:
        """Open an MCS MEA2100 HDF5 file and return an NSIDataset.

        Loads all streams, truncates to minimum sample count, concatenates.
        """
        p = Path(path)
        meta = self.metadata(p)

        with h5py.File(p, "r") as f:
            streams = _load_streams(f, MCS_HDF5_PATH)

        data = _concat_streams(streams) if streams else np.array([], dtype=np.float32)
        n_ch = data.shape[0] if data.size else 0
        feature_names = generate_feature_names(max(n_ch, 1))

        return NSIDataset(
            metadata=meta,
            data=data,
            feature_names=feature_names,
            _adapter=self,
        )

    def metadata(self, path: str | Path) -> NSIMetadata:
        """Read metadata without loading full channel data."""
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"MCS file not found: {p}")

        file_size_mb = p.stat().st_size / (1024 * 1024)

        with h5py.File(p, "r") as f:
            analog = f[MCS_HDF5_PATH]
            streams = sorted(analog.keys())
            total_channels = 0
            total_samples = 0
            for sn in streams:
                shape = analog[sn]["ChannelData"].shape
                total_channels += shape[0]
                total_samples = max(total_samples, shape[1])
            min_samples = min(analog[sn]["ChannelData"].shape[1] for sn in streams)

        duration_s = min_samples / self.SAMPLE_RATE_HZ if self.SAMPLE_RATE_HZ > 0 else None

        return NSIMetadata(
            source_path=str(p),
            source_format="hdf5",
            vendor=self.vendor,
            modality=self.modality,
            channel_count=total_channels,
            sample_rate_hz=self.SAMPLE_RATE_HZ,
            duration_s=duration_s,
            extra={
                "stream_count": len(streams),
                "streams": streams,
                "file_size_mb": round(file_size_mb, 1),
                "min_samples": min_samples,
                "max_samples": total_samples,
            },
        )

    def iter_windows(self, path: str | Path, window_s: float, overlap: float = 0.0) -> Iterator[np.ndarray]:
        """Iterate over sliding windows of concatenated MCS data.

        All streams are concatenated (truncated to minimum sample count)
        and windows are yielded from the unified (total_channels, samples) array.
        Yields (total_channels, window_samples) arrays with consistent shape.
        """
        p = Path(path)
        window_samples = int(window_s * self.SAMPLE_RATE_HZ)
        stride = max(1, int(window_samples * (1.0 - overlap)))

        with h5py.File(p, "r") as f:
            streams = _load_streams(f, MCS_HDF5_PATH)

        if not streams:
            return

        data = _concat_streams(streams)
        n_samples = data.shape[1]
        start = 0
        while start + window_samples <= n_samples:
            yield np.asarray(data[:, start:start + window_samples], dtype=np.float32)
            start += stride
    def feature_vector(self, window: np.ndarray, feature_names: list[str] | None = None) -> np.ndarray:
        """Extract features from a single window using default extraction."""
        return _default_feature_vector(window)

    def close(self) -> None:
        """MCS adapter is stateless — no resources to release."""
        pass


# Auto-register
from biogpu.nsi.adapters import register_adapter
register_adapter(MCSAdapter)
