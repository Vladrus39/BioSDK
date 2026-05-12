"""NSI-1.0 Conformance Test — Tressoldi H3 xlsx EEG Adapter.

Verifies that the Tressoldi adapter:
1. Implements the full NSI-1.0 interface
2. Opens xlsx EEG files (receiver and transmitter)
3. Returns correct metadata (14 channels, 128 Hz, Emotiv EPOC)
4. Windows have consistent dimensions
5. Feature names follow ch{i}_{feat} convention
6. Labeled windows correctly identify stimulus vs rest
7. open_pair() returns both receiver and transmitter
"""
from __future__ import annotations

import numpy as np
from pathlib import Path

BIO = Path(r"C:\Users\vladi\Desktop\Braine\BiC OS\biogpu-core-v5_0_bic_os_first_mover_roadmap")

TRESS_DIR = BIO / "data" / "external" / "tressoldi_h3" / "BBI_RawData"
RECEIVER = TRESS_DIR / "Pair1" / "r1.xlsx"
TRANSMITTER = TRESS_DIR / "Pair1" / "t1.xlsx"


def test_tressoldi_adapter_import():
    """Tressoldi adapter class is importable and registered."""
    from biogpu.nsi.adapters import get_adapter, list_adapters

    adapters = list_adapters()
    assert "tressoldi_h3" in adapters, f"Expected tressoldi_h3 in {adapters}"

    tress_cls = get_adapter("tressoldi_h3")
    assert tress_cls is not None
    assert tress_cls.adapter_id == "tressoldi_h3"
    assert tress_cls.vendor == "tressoldi"
    assert tress_cls.modality == "eeg"


def test_tressoldi_metadata():
    """Tressoldi adapter returns valid metadata for receiver xlsx."""
    from biogpu.nsi.adapters.tressoldi import TressoldiAdapter

    adapter = TressoldiAdapter()
    meta = adapter.metadata(RECEIVER)

    assert meta.vendor == "tressoldi"
    assert meta.source_format == "xlsx"
    assert meta.modality == "eeg"
    assert meta.channel_count == 14, f"Expected 14 channels, got {meta.channel_count}"
    assert meta.sample_rate_hz == 128.0
    assert meta.duration_s is not None
    assert meta.duration_s > 0
    assert meta.extra["subject"] == "Florentina"
    assert meta.extra["instrument"] == "Emotiv EPOC"
    assert len(meta.extra["channel_names"]) == 14
    assert meta.extra["channel_names"][0] == "AF3"


def test_tressoldi_open():
    """Tressoldi open() returns NSIDataset with correct data shape."""
    from biogpu.nsi.adapters.tressoldi import TressoldiAdapter

    adapter = TressoldiAdapter()
    ds = adapter.open(RECEIVER)

    assert ds.metadata.vendor == "tressoldi"
    assert ds.data is not None
    assert ds.data.shape[0] == 14, f"Expected 14 channels, got {ds.data.shape[0]}"
    assert ds.data.shape[1] > 10000, f"Expected >10000 samples, got {ds.data.shape[1]}"
    assert ds.data.dtype == np.float32
    assert len(ds.feature_names) == 14 * 6
    assert ds.feature_names[0] == "ch0_rms"
    assert ds.feature_names[5] == "ch0_skew"
    assert ds.feature_names[6] == "ch1_rms"


def test_tressoldi_iter_windows():
    """Tressoldi iter_windows yields correctly shaped arrays."""
    from biogpu.nsi.adapters.tressoldi import TressoldiAdapter

    adapter = TressoldiAdapter()
    window_s = 1.0
    windows = list(adapter.iter_windows(RECEIVER, window_s, overlap=0.0))

    assert len(windows) > 0, "No windows yielded"
    expected_samples = int(window_s * 128)  # 128 samples at 128 Hz
    for w in windows[:5]:
        assert w.ndim == 2, f"Window should be 2D, got {w.ndim}D"
        assert w.shape[0] == 14, f"Expected 14 channels, got {w.shape[0]}"
        assert w.shape[1] == expected_samples, f"Expected {expected_samples} samples, got {w.shape[1]}"
    adapter.close()


def test_tressoldi_labeled_windows():
    """iter_labeled_windows returns (window, label) tuples with 0/1 labels."""
    from biogpu.nsi.adapters.tressoldi import TressoldiAdapter

    adapter = TressoldiAdapter()
    labeled = list(adapter.iter_labeled_windows(RECEIVER, 1.0))

    assert len(labeled) > 0, "No labeled windows"
    for window, label in labeled[:5]:
        assert window.ndim == 2
        assert window.shape[0] == 14
        assert label in (0, 1), f"Label should be 0 or 1, got {label}"

    # Should have both stimulus and rest windows
    labels = [l for _, l in labeled]
    assert 0 in labels, "No rest windows found"
    assert 1 in labels, "No stimulus windows found"
    adapter.close()


def test_tressoldi_feature_vector_shape():
    """Feature vector has shape (n_channels * 6,)."""
    from biogpu.nsi.adapters.tressoldi import TressoldiAdapter

    adapter = TressoldiAdapter()
    ds = adapter.open(RECEIVER)
    window = ds.data[:, :128]  # First 128 samples (~1s at 128Hz)

    fv = adapter.feature_vector(window)
    assert fv.shape == (14 * 6,), f"Expected (84,), got {fv.shape}"
    assert fv.dtype == np.float32
    adapter.close()


def test_tressoldi_feature_values_are_finite():
    """All extracted features are finite (no NaN or inf)."""
    from biogpu.nsi.adapters.tressoldi import TressoldiAdapter

    adapter = TressoldiAdapter()
    ds = adapter.open(RECEIVER)
    mid = ds.data.shape[1] // 2
    window = ds.data[:, mid:mid + 128]

    fv = adapter.feature_vector(window)
    assert np.all(np.isfinite(fv)), "Feature vector contains NaN or inf values"
    assert np.any(fv != 0), "Feature vector is all zeros"
    adapter.close()


def test_tressoldi_open_pair():
    """open_pair() returns dict with receiver and transmitter NSIDatasets."""
    from biogpu.nsi.adapters.tressoldi import TressoldiAdapter

    adapter = TressoldiAdapter()
    pair = adapter.open_pair(RECEIVER, TRANSMITTER)

    assert "receiver" in pair
    assert "transmitter" in pair
    assert pair["receiver"].data.shape[0] == 14
    assert pair["transmitter"].data.shape[0] == 14
    # Both should have 14 channels, 128Hz
    assert pair["receiver"].metadata.channel_count == 14
    assert pair["transmitter"].metadata.channel_count == 14
    adapter.close()


def test_adapter_registry_counts():
    """At least 6 adapters registered."""
    from biogpu.nsi.adapters import list_adapters
    adapters = list_adapters()
    assert len(adapters) >= 6,         f"Expected at least 6 adapters, got {len(adapters)}: {adapters}"
    assert "tressoldi_h3" in adapters
