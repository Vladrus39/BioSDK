"""NSI-1.0 (Neural Substrate Interface) — Vendor-neutral neural data protocol.

A unified open() for neural data: one call, any format, consistent output.
Proven on: Giroldini HDF5, MCS HDF5, DANDI NWB, Allen NWB, Sleep EDF, GCP2 CSV.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator
import numpy as np


@dataclass
class NSIMetadata:
    """Vendor-neutral metadata for a neural recording."""
    source_path: str
    source_format: str  # hdf5, nwb, edf, csv
    vendor: str         # giroldini, mcs, dandi, allen, physionet, gcp2
    modality: str       # mea, eeg, sleep_psg, rng
    channel_count: int
    sample_rate_hz: float
    duration_s: float | None = None
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class NSIDataset:
    """Unified neural dataset handle returned by NSI-1.0 open()."""
    metadata: NSIMetadata
    data: np.ndarray | None = None           # Full raw data (may be None if too large)
    windows: list[np.ndarray] | None = None   # Pre-extracted windows
    feature_names: list[str] = field(default_factory=list)
    _adapter: Any = None

    def __repr__(self) -> str:
        shape = self.data.shape if self.data is not None else "lazy"
        return (f"NSIDataset(vendor={self.metadata.vendor}, modality={self.metadata.modality}, "
                f"channels={self.metadata.channel_count}, shape={shape})")


class NSIAdapter(ABC):
    """Base class for NSI-1.0 adapters.

    Each vendor format gets one adapter. The adapter translates vendor-specific
    data into the common NSIDataset format with consistent feature extraction.
    """

    adapter_id: str = ""
    vendor: str = ""
    modality: str = ""

    @abstractmethod
    def open(self, path: str | Path) -> NSIDataset:
        """Open a neural recording and return an NSIDataset handle."""
        ...

    @abstractmethod
    def metadata(self, path: str | Path) -> NSIMetadata:
        """Return metadata without loading full data."""
        ...

    @abstractmethod
    def iter_windows(self, path: str | Path, window_s: float, overlap: float = 0.0) -> Iterator[np.ndarray]:
        """Iterate over sliding windows of raw data."""
        ...

    def feature_vector(self, window: np.ndarray, feature_names: list[str] | None = None) -> np.ndarray:
        """Extract features from a single window. Override for vendor-specific extraction."""
        return _default_feature_vector(window)

    def close(self) -> None:
        """Release any held resources."""
        pass


# ── Default feature extraction (RMS, MAV, ZC, VAR, PEAK, SKEW per channel) ──

DEFAULT_FEATURE_NAMES = ["rms", "mav", "zc", "var", "peak", "skew"]


def _default_feature_vector(window: np.ndarray) -> np.ndarray:
    """Extract 6 features per channel from a (channels, samples) window.

    Returns shape (n_channels * 6,).
    """
    n_ch = window.shape[0]
    features = []
    for ch in range(n_ch):
        seg = window[ch, :].astype(np.float64)
        rms = float(np.sqrt(np.mean(seg**2)))
        mav = float(np.mean(np.abs(seg)))
        zc = float(np.sum(np.diff(np.signbit(seg))))
        var = float(np.var(seg))
        peak = float(np.max(np.abs(seg)))
        sk = float(np.mean(seg**3) / (np.std(seg)**3 + 1e-10))
        features.extend([rms, mav, zc, var, peak, sk])
    return np.array(features, dtype=np.float32)


def generate_feature_names(n_channels: int, feature_set: list[str] | None = None) -> list[str]:
    """Generate feature names like 'ch0_rms', 'ch0_mav', ..."""
    feat_names = feature_set or DEFAULT_FEATURE_NAMES
    names = []
    for ch in range(n_channels):
        for fn in feat_names:
            names.append(f"ch{ch}_{fn}")
    return names
