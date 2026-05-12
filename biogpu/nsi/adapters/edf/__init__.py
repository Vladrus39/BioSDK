"""NSI-1.0 adapter for EDF (European Data Format) sleep PSG and EEG files.

Handles EDF/BDF files via MNE-Python (mne.io.read_raw_edf).
Vendor: PhysioNet (Sleep PSG), OpenNeuro (EEG ds007558), or any EDF source.
Modality: sleep_psg, eeg

EDF files store multi-channel time series with standardized headers.
Each channel is a discrete signal (EEG, EOG, EMG, respiratory, etc.)
sampled at a uniform or per-channel rate.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterator
import numpy as np

from biogpu.nsi import (
    NSIAdapter, NSIDataset, NSIMetadata,
    _default_feature_vector, generate_feature_names,
)

# Lazy import MNE to avoid hard dependency error at import time
_mne = None

def _get_mne():
    global _mne
    if _mne is None:
        try:
            import mne
            _mne = mne
        except ImportError:
            raise ImportError(
                "MNE-Python is required for EDF files. "
                "Install with: pip install mne"
            )
    return _mne


class EDFAdapter(NSIAdapter):
    """NSI-1.0 adapter for EDF/BDF files (Sleep PSG, EEG).

    Uses MNE-Python for robust EDF parsing. Supports:
    - Sleep PSG from PhysioNet (7+ channels, 100 Hz)
    - EEG from OpenNeuro ds007558 (19-21 channels, 200 Hz)
    - Any standard EDF/BDF file
    """

    adapter_id = "physionet_edf"
    vendor = "physionet_openneuro"
    modality = "sleep_psg_eeg"

    def __init__(self):
        self._cached_data: dict[str, np.ndarray] = {}
        self._cached_meta: dict[str, NSIMetadata] = {}

    def open(self, path: str | Path) -> NSIDataset:
        """Open an EDF file and return an NSIDataset with full data loaded."""
        p = Path(path)
        meta = self.metadata(p)

        mne = _get_mne()
        raw = mne.io.read_raw_edf(str(p), preload=True, verbose=False)
        data = raw.get_data().astype(np.float32)  # shape: (n_channels, n_samples)
        n_ch = data.shape[0]
        feature_names = generate_feature_names(max(n_ch, 1))

        return NSIDataset(
            metadata=meta,
            data=data,
            feature_names=feature_names,
            _adapter=self,
        )

    def metadata(self, path: str | Path) -> NSIMetadata:
        """Read metadata from an EDF file without loading full data."""
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"EDF file not found: {p}")

        file_size_mb = p.stat().st_size / (1024 * 1024)

        mne = _get_mne()
        raw = mne.io.read_raw_edf(str(p), preload=False, verbose=False)
        info = raw.info
        n_channels = len(raw.ch_names)
        sample_rate = info["sfreq"]
        n_samples = raw.n_times
        duration_s = n_samples / sample_rate if sample_rate > 0 else None

        return NSIMetadata(
            source_path=str(p),
            source_format="edf",
            vendor=self.vendor,
            modality=self.modality,
            channel_count=n_channels,
            sample_rate_hz=float(sample_rate),
            duration_s=duration_s,
            extra={
                "file_size_mb": round(file_size_mb, 1),
                "channel_names": raw.ch_names,
                "n_samples": n_samples,
                "highpass": info.get("highpass", None),
                "lowpass": info.get("lowpass", None),
            },
        )

    def iter_windows(self, path: str | Path, window_s: float, overlap: float = 0.0) -> Iterator[np.ndarray]:
        """Iterate over sliding windows of raw EDF data.

        Yields (n_channels, window_samples) arrays.
        """
        p = Path(path)
        meta = self.metadata(p)
        sr = meta.sample_rate_hz

        # Load data once
        if str(p) not in self._cached_data:
            mne = _get_mne()
            raw = mne.io.read_raw_edf(str(p), preload=True, verbose=False)
            self._cached_data[str(p)] = raw.get_data().astype(np.float32)

        data = self._cached_data[str(p)]
        n_samples = data.shape[1]
        window_samples = max(1, int(window_s * sr))
        stride = max(1, int(window_samples * (1.0 - overlap)))

        start = 0
        while start + window_samples <= n_samples:
            yield np.asarray(data[:, start:start + window_samples], dtype=np.float32)
            start += stride

        # Clean up cache after iteration
        if str(p) in self._cached_data:
            del self._cached_data[str(p)]

    def feature_vector(self, window: np.ndarray, feature_names: list[str] | None = None) -> np.ndarray:
        """Extract features from a single window using default extraction."""
        return _default_feature_vector(window)

    def close(self) -> None:
        """Release cached data."""
        self._cached_data.clear()
        self._cached_meta.clear()


# Auto-register
from biogpu.nsi.adapters import register_adapter
register_adapter(EDFAdapter)
