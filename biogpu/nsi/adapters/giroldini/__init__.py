"""NSI-1.0 adapter for Giroldini MEA HDF5 files (Zenodo 14363732).

Uses the same HDF5 path as MCS:
    Data/Recording_0/AnalogStream/Stream_N/ChannelData

Giroldini data: 59 channels, ~20 kHz, single stream, ~10 min recordings.
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

GIRO_HDF5_PATH = "Data/Recording_0/AnalogStream"


class GiroldiniAdapter(NSIAdapter):
    """NSI-1.0 adapter for Giroldini MEA HDF5 files (Zenodo 14363732)."""

    adapter_id = "giroldini_mea"
    vendor = "giroldini"
    modality = "mea"

    # Known sample rate (Hz) — Giroldini recordings at ~20 kHz
    SAMPLE_RATE_HZ = 20_000.0

    def open(self, path: str | Path) -> NSIDataset:
        """Open a Giroldini MEA HDF5 file and return an NSIDataset."""
        p = Path(path)
        meta = self.metadata(p)

        with h5py.File(p, "r") as f:
            analog = f[GIRO_HDF5_PATH]
            all_channels = []
            for stream_name in sorted(analog.keys()):
                ch_data = np.array(analog[stream_name]["ChannelData"], dtype=np.float32)
                all_channels.append(ch_data)

        data = np.concatenate(all_channels, axis=0) if all_channels else np.array([])

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
            raise FileNotFoundError(f"Giroldini file not found: {p}")

        file_size_mb = p.stat().st_size / (1024 * 1024)

        with h5py.File(p, "r") as f:
            analog = f[GIRO_HDF5_PATH]
            streams = sorted(analog.keys())
            total_channels = 0
            total_samples = 0
            for sn in streams:
                shape = analog[sn]["ChannelData"].shape
                total_channels += shape[0]
                total_samples = max(total_samples, shape[1])

        duration_s = total_samples / self.SAMPLE_RATE_HZ if self.SAMPLE_RATE_HZ > 0 else None

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
            },
        )

    def iter_windows(self, path: str | Path, window_s: float, overlap: float = 0.0) -> Iterator[np.ndarray]:
        """Iterate over sliding windows of raw Giroldini data."""
        p = Path(path)
        window_samples = int(window_s * self.SAMPLE_RATE_HZ)
        stride = max(1, int(window_samples * (1.0 - overlap)))

        with h5py.File(p, "r") as f:
            analog = f[GIRO_HDF5_PATH]
            for stream_name in sorted(analog.keys()):
                ch_data = np.array(analog[stream_name]["ChannelData"], dtype=np.float32)
                n_samples = ch_data.shape[1]
                start = 0
                while start + window_samples <= n_samples:
                    yield ch_data[:, start:start + window_samples]
                    start += stride

    def feature_vector(self, window: np.ndarray, feature_names: list[str] | None = None) -> np.ndarray:
        """Extract features from a single window using default extraction."""
        return _default_feature_vector(window)

    def close(self) -> None:
        """Giroldini adapter is stateless — no resources to release."""
        pass


# Auto-register
from biogpu.nsi.adapters import register_adapter
register_adapter(GiroldiniAdapter)
