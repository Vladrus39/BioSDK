"""NSI-1.0 adapter for GCP2 (Global Consciousness Project 2) CSV data.

GCP2 distributes device coherence time series via zipped CSV files.
Each file represents one device (physical random number generator),
with columns: device_number, epoch_time_utc, active_seconds, device_coherence, significance.

The adapter treats each device as one "channel" and coherence as the signal.
Multiple devices can be stacked into one NSIDataset for cross-device analysis.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterator
import csv
import io
import zipfile
import numpy as np

from biogpu.nsi import (
    NSIAdapter, NSIDataset, NSIMetadata,
    _default_feature_vector, generate_feature_names,
)


def _read_gcp2_zip(zip_path: Path) -> tuple[np.ndarray, dict]:
    """Read a GCP2 zipped CSV and return (time_series, metadata_dict).

    The time series is the device_coherence column as a 1D float32 array.
    """
    with zipfile.ZipFile(zip_path, "r") as zf:
        names = zf.namelist()
        if not names:
            raise ValueError(f"Empty zip file: {zip_path}")
        
        with zf.open(names[0]) as f:
            content = f.read().decode("utf-8", errors="replace")
    
    reader = csv.DictReader(io.StringIO(content))
    rows = list(reader)
    
    if not rows:
        raise ValueError(f"No data rows in {zip_path}")
    
    coherence = np.array([float(r["device_coherence"]) for r in rows], dtype=np.float32)
    
    # Extract metadata
    device_number = rows[0].get("device_number", "unknown")
    first_ts = rows[0].get("epoch_time_utc", "")
    last_ts = rows[-1].get("epoch_time_utc", "")
    active_seconds = rows[0].get("active_seconds", "")
    
    return coherence, {
        "device_number": device_number,
        "n_rows": len(rows),
        "first_epoch_utc": first_ts,
        "last_epoch_utc": last_ts,
        "active_seconds_per_row": active_seconds,
    }


class GCP2Adapter(NSIAdapter):
    """NSI-1.0 adapter for GCP2 device coherence CSV data.

    Each device is one CSV file (zipped). The adapter:
    - Reads the device_coherence column as a 1D signal
    - Or stacks multiple devices into a 2D (n_devices, n_samples) matrix
    - Sample rate is inferred from epoch_time_utc spacing (variable, ~60s)
    """

    adapter_id = "gcp2_csv"
    vendor = "gcp2"
    modality = "rng"

    # Approximate average sample interval in seconds (epoch_time_utc spacing)
    DEFAULT_SAMPLE_RATE_HZ = 1.0 / 60.0  # ~1 sample per minute

    def __init__(self):
        self._cached_data: dict[str, np.ndarray] = {}

    def open(self, path: str | Path) -> NSIDataset:
        """Open a GCP2 CSV (zip) file and return an NSIDataset.

        For a single file: data shape is (1, n_samples) — one channel.
        The channel represents device coherence over time.
        """
        p = Path(path)
        meta = self.metadata(p)

        coherence, extra_info = _read_gcp2_zip(p)
        # Reshape to (1, n_samples) for NSI convention (channels, samples)
        data = coherence.reshape(1, -1)
        n_ch = 1  # One device = one channel
        feature_names = generate_feature_names(max(n_ch, 1))

        # Merge extra info into metadata
        meta.extra.update(extra_info)

        return NSIDataset(
            metadata=meta,
            data=data,
            feature_names=feature_names,
            _adapter=self,
        )

    def open_multi(self, paths: list[Path]) -> NSIDataset:
        """Open multiple GCP2 device files and stack as channels.

        Each device becomes one channel. All series are truncated to
        the minimum length for consistent 2D shape.

        Returns NSIDataset with shape (n_devices, min_samples).
        """
        all_data = []
        all_meta_extra = []
        
        for p in paths:
            coherence, extra_info = _read_gcp2_zip(p)
            all_data.append(coherence)
            all_meta_extra.append(extra_info)
        
        if not all_data:
            raise ValueError("No GCP2 files provided")
        
        # Truncate to minimum length
        min_len = min(len(d) for d in all_data)
        stacked = np.stack([d[:min_len] for d in all_data], axis=0).astype(np.float32)
        
        # Build combined metadata from first file
        first_meta = self.metadata(paths[0])
        first_meta.extra["device_count"] = len(paths)
        first_meta.extra["device_numbers"] = [e["device_number"] for e in all_meta_extra]
        first_meta.extra["n_samples_per_device"] = min_len
        first_meta.channel_count = len(paths)
        
        n_ch = len(paths)
        feature_names = generate_feature_names(max(n_ch, 1))

        # Estimate duration from sample count
        if first_meta.sample_rate_hz > 0:
            first_meta.duration_s = min_len / first_meta.sample_rate_hz

        return NSIDataset(
            metadata=first_meta,
            data=stacked,
            feature_names=feature_names,
            _adapter=self,
        )

    def metadata(self, path: str | Path) -> NSIMetadata:
        """Read metadata from a GCP2 CSV zip file."""
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"GCP2 file not found: {p}")

        file_size_mb = p.stat().st_size / (1024 * 1024)

        coherence, extra_info = _read_gcp2_zip(p)
        n_samples = len(coherence)

        # Estimate sample rate from epoch_time_utc spacing
        # We don't parse all timestamps here; use default ~60s
        sample_rate = self.DEFAULT_SAMPLE_RATE_HZ

        duration_s = n_samples / sample_rate if sample_rate > 0 else None

        return NSIMetadata(
            source_path=str(p),
            source_format="csv",
            vendor=self.vendor,
            modality=self.modality,
            channel_count=1,  # Single device
            sample_rate_hz=sample_rate,
            duration_s=duration_s,
            extra={
                "file_size_mb": round(file_size_mb, 1),
                "n_samples": n_samples,
                **extra_info,
            },
        )

    def iter_windows(self, path: str | Path, window_s: float, overlap: float = 0.0) -> Iterator[np.ndarray]:
        """Iterate over sliding windows of device coherence.

        Yields (1, window_samples) arrays — one device at a time.
        For multi-device analysis, use open_multi() and then iterate
        the stacked data directly.
        """
        p = Path(path)

        if str(p) not in self._cached_data:
            coherence, _ = _read_gcp2_zip(p)
            self._cached_data[str(p)] = coherence.reshape(1, -1)

        data = self._cached_data[str(p)]
        n_samples = data.shape[1]
        ws = max(1, int(window_s * self.DEFAULT_SAMPLE_RATE_HZ))
        stride = max(1, int(ws * (1.0 - overlap)))

        start = 0
        while start + ws <= n_samples:
            yield np.asarray(data[:, start:start + ws], dtype=np.float32)
            start += stride

        # Clean up
        if str(p) in self._cached_data:
            del self._cached_data[str(p)]

    def feature_vector(self, window: np.ndarray, feature_names: list[str] | None = None) -> np.ndarray:
        """Extract features from a single window.

        For single-channel GCP2 data, the default features (RMS, MAV, etc.)
        are computed on the coherence time series.
        For multi-channel (multi-device), standard per-channel features apply.
        """
        return _default_feature_vector(window)

    def close(self) -> None:
        """Release cached data."""
        self._cached_data.clear()


# Auto-register
from biogpu.nsi.adapters import register_adapter
register_adapter(GCP2Adapter)
