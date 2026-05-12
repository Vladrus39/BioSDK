"""NSI-1.0 adapter for Tressoldi H3 BBI (Brain-to-Brain Interface) EEG data.

The Tressoldi H3 dataset contains 20 EEG pairs (receiver + transmitter) from
a telepathy paradigm experiment. Each recording is an xlsx file with:
- Emotiv EPOC 14-channel EEG (AF3, F7, F3, FC5, T7, P7, O1, O2, P8, T8, FC6, F4, F8, AF4)
- 128 Hz sampling rate
- COUNTER, SYSTEM-TIME, and STIMOLO (stimulus marker) columns
- 21K-45K data rows (165-353 seconds)

The STIMOLO column encodes experimental conditions:
- 0: rest/baseline
- 1: stimulus active
- 2000: stimulus type marker

This allows labeled window extraction for stimulus-vs-rest classification.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterator
import numpy as np

from biogpu.nsi import (
    NSIAdapter, NSIDataset, NSIMetadata,
    _default_feature_vector, generate_feature_names,
)

# Emotiv EPOC channel names (in column order)
EMOTIV_EPOC_CHANNELS = [
    "AF3", "F7", "F3", "FC5", "T7", "P7", "O1",
    "O2", "P8", "T8", "FC6", "F4", "F8", "AF4",
]

# Column indices in xlsx
COL_COUNTER = 0
COL_SYSTEM_TIME = 1
COL_STIMOLO = 2
COL_EEG_START = 3
COL_EEG_END = 3 + len(EMOTIV_EPOC_CHANNELS)  # 17


def _parse_xlsx_metadata(path: Path) -> dict:
    """Parse metadata rows (row 1-2) from a Tressoldi xlsx file."""
    import openpyxl

    wb = openpyxl.load_workbook(str(path), read_only=True, data_only=True)
    ws = wb[wb.sheetnames[0]]

    meta_row = list(ws.iter_rows(min_row=1, max_row=1, values_only=True))[0]
    headers = list(ws.iter_rows(min_row=2, max_row=2, values_only=True))[0]

    meta = {}
    for v in meta_row:
        if v and ":" in str(v):
            key, _, val = str(v).partition(":")
            meta[key.strip().lower().replace(" ", "_")] = val.strip()
        elif v:
            meta["format"] = str(v)

    meta["headers"] = [str(h) for h in headers if h]
    meta["eeg_channels"] = [str(h) for h in headers[COL_EEG_START:COL_EEG_END] if h]

    # Parse sample rate
    sample_rate = meta.get("sampling_rate", "128")
    try:
        meta["sample_rate_hz"] = float(sample_rate)
    except ValueError:
        meta["sample_rate_hz"] = 128.0

    wb.close()
    return meta


def _load_xlsx_eeg(path: Path) -> tuple[np.ndarray, np.ndarray, dict]:
    """Load EEG data and STIMOLO markers from a Tressoldi xlsx file.

    Returns: (eeg_data, stimolo, meta_dict)
    - eeg_data: (n_channels, n_samples) float32 array
    - stimolo: (n_samples,) float32 array (0=rest, 1=stim, 2000=marker)
    - meta_dict: metadata from header rows
    """
    import openpyxl

    meta = _parse_xlsx_metadata(path)
    n_channels = len(meta["eeg_channels"])

    wb = openpyxl.load_workbook(str(path), read_only=True, data_only=True)
    ws = wb[wb.sheetnames[0]]

    # Count data rows and allocate
    n_data_rows = ws.max_row - 2
    eeg_data = np.zeros((n_channels, n_data_rows), dtype=np.float32)
    stimolo = np.zeros(n_data_rows, dtype=np.float32)

    for i, row in enumerate(ws.iter_rows(min_row=3, values_only=True)):
        if i >= n_data_rows:
            break
        # EEG channels (columns 3-16)
        for ch in range(n_channels):
            val = row[COL_EEG_START + ch]
            eeg_data[ch, i] = float(val) if val is not None else 0.0
        # STIMOLO
        val = row[COL_STIMOLO]
        stimolo[i] = float(val) if val is not None else 0.0

    wb.close()
    return eeg_data, stimolo, meta


class TressoldiAdapter(NSIAdapter):
    """NSI-1.0 adapter for Tressoldi H3 xlsx EEG data.

    Each xlsx file contains:
    - 14-channel Emotiv EPOC EEG at 128 Hz
    - STIMOLO markers for stimulus-vs-rest labeling
    - Subject/date/instrument metadata in row 1

    Supports opening individual files or receiver+transmitter pairs.
    """

    adapter_id = "tressoldi_h3"
    vendor = "tressoldi"
    modality = "eeg"

    def __init__(self):
        self._cached_data: dict[str, np.ndarray] = {}
        self._cached_stimolo: dict[str, np.ndarray] = {}
        self._cached_meta: dict[str, dict] = {}

    def open(self, path: str | Path) -> NSIDataset:
        """Open a Tressoldi xlsx file and return an NSIDataset.

        The dataset contains 14-channel EEG data and STIMOLO markers
        stored in metadata.extra.
        """
        p = Path(path)
        meta = self.metadata(p)

        eeg_data, stimolo, parsed_meta = _load_xlsx_eeg(p)
        n_ch = eeg_data.shape[0]
        feature_names = generate_feature_names(max(n_ch, 1))

        # Store STIMOLO for window labeling
        self._cached_stimolo[str(p)] = stimolo
        self._cached_meta[str(p)] = parsed_meta

        return NSIDataset(
            metadata=meta,
            data=eeg_data,
            feature_names=feature_names,
            _adapter=self,
        )

    def open_pair(self, receiver_path: str | Path, transmitter_path: str | Path) -> dict[str, NSIDataset]:
        """Open a receiver+transmitter pair.

        Returns: {"receiver": NSIDataset, "transmitter": NSIDataset}
        """
        return {
            "receiver": self.open(receiver_path),
            "transmitter": self.open(transmitter_path),
        }

    def metadata(self, path: str | Path) -> NSIMetadata:
        """Read metadata from a Tressoldi xlsx file."""
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Tressoldi file not found: {p}")

        file_size_mb = p.stat().st_size / (1024 * 1024)

        meta = _parse_xlsx_metadata(p)
        n_channels = len(meta.get("eeg_channels", []))
        sample_rate = meta.get("sample_rate_hz", 128.0)

        # Estimate duration without loading all data
        import openpyxl
        wb = openpyxl.load_workbook(str(p), read_only=True, data_only=True)
        ws = wb[wb.sheetnames[0]]
        n_samples = max(0, ws.max_row - 2)
        wb.close()

        duration_s = n_samples / sample_rate if sample_rate > 0 else None

        return NSIMetadata(
            source_path=str(p),
            source_format="xlsx",
            vendor=self.vendor,
            modality=self.modality,
            channel_count=n_channels,
            sample_rate_hz=sample_rate,
            duration_s=duration_s,
            extra={
                "file_size_mb": round(file_size_mb, 1),
                "n_samples": n_samples,
                "subject": meta.get("subject", ""),
                "date": meta.get("date", ""),
                "instrument": meta.get("instrument", ""),
                "channel_names": meta.get("eeg_channels", []),
            },
        )

    def iter_windows(self, path: str | Path, window_s: float, overlap: float = 0.0) -> Iterator[np.ndarray]:
        """Iterate over sliding windows of EEG data.

        Yields (n_channels, window_samples) arrays.
        """
        p = Path(path)
        meta = self.metadata(p)
        sr = meta.sample_rate_hz

        # Use cached data if available, else load
        cache_key = str(p)
        if cache_key not in self._cached_data:
            eeg_data, stimolo, _ = _load_xlsx_eeg(p)
            self._cached_data[cache_key] = eeg_data
            self._cached_stimolo[cache_key] = stimolo

        data = self._cached_data[cache_key]
        n_samples = data.shape[1]
        window_samples = max(1, int(window_s * sr))
        stride = max(1, int(window_samples * (1.0 - overlap)))

        start = 0
        while start + window_samples <= n_samples:
            yield np.asarray(data[:, start:start + window_samples], dtype=np.float32)
            start += stride

    def iter_labeled_windows(self, path: str | Path, window_s: float, overlap: float = 0.0) -> Iterator[tuple[np.ndarray, int]]:
        """Iterate over windows with stimulus labels.

        Yields (window, label) where:
        - label = 0: rest/baseline (STIMOLO == 0)
        - label = 1: stimulus active (STIMOLO != 0)

        The label is the majority STIMOLO value in the window.
        """
        p = Path(path)
        cache_key = str(p)

        # Ensure data is loaded
        if cache_key not in self._cached_data:
            eeg_data, stimolo, _ = _load_xlsx_eeg(p)
            self._cached_data[cache_key] = eeg_data
            self._cached_stimolo[cache_key] = stimolo

        data = self._cached_data[cache_key]
        stim = self._cached_stimolo[cache_key]

        meta = self.metadata(p)
        sr = meta.sample_rate_hz
        n_samples = data.shape[1]
        window_samples = max(1, int(window_s * sr))
        stride = max(1, int(window_samples * (1.0 - overlap)))

        start = 0
        while start + window_samples <= n_samples:
            window = np.asarray(data[:, start:start + window_samples], dtype=np.float32)
            # Label = majority STIMOLO value in window (>0 means stimulus)
            stim_seg = stim[start:start + window_samples]
            label = 1 if np.mean(stim_seg != 0) > 0.5 else 0
            yield window, label
            start += stride

    def feature_vector(self, window: np.ndarray, feature_names: list[str] | None = None) -> np.ndarray:
        """Extract features from a single window using default extraction."""
        return _default_feature_vector(window)

    def close(self) -> None:
        """Release cached data."""
        self._cached_data.clear()
        self._cached_stimolo.clear()
        self._cached_meta.clear()


# Auto-register
from biogpu.nsi.adapters import register_adapter
register_adapter(TressoldiAdapter)
