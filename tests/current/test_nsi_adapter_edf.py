"""NSI-1.0 Conformance Test — EDF (Sleep PSG) Adapter.

Verifies that the EDF adapter:
1. Implements the full NSI-1.0 interface
2. Opens Sleep PSG EDF files and OpenNeuro EEG EDF files
3. Returns correct metadata shapes and types
4. Windows have consistent dimensions
5. Feature names follow ch{i}_{feat} convention
"""
from __future__ import annotations

import numpy as np
from pathlib import Path

BIO = Path(r"C:\Users\vladi\Desktop\Braine\BiC OS\biogpu-core-v5_0_bic_os_first_mover_roadmap")

SLEEP_PSG = BIO / "data" / "external" / "sleep_psg" / "SC4001E0-PSG.edf"
OPENNEURO_EEG = next((BIO / "data" / "external" / "eeg_ds007558").rglob("*.edf"), None)


def test_edf_adapter_import():
    """EDF adapter class is importable and registered."""
    from biogpu.nsi.adapters import get_adapter, list_adapters

    adapters = list_adapters()
    assert "physionet_edf" in adapters, f"Expected physionet_edf in {adapters}"

    edf_cls = get_adapter("physionet_edf")
    assert edf_cls is not None
    assert edf_cls.adapter_id == "physionet_edf"
    assert edf_cls.vendor == "physionet_openneuro"
    assert "sleep" in edf_cls.modality or "eeg" in edf_cls.modality


def test_edf_metadata_sleep_psg():
    """EDF adapter returns valid metadata for Sleep PSG EDF."""
    from biogpu.nsi.adapters.edf import EDFAdapter

    adapter = EDFAdapter()
    meta = adapter.metadata(SLEEP_PSG)

    assert meta.vendor == "physionet_openneuro"
    assert meta.source_format == "edf"
    assert meta.channel_count == 7, f"Expected 7 channels, got {meta.channel_count}"
    assert meta.sample_rate_hz == 100.0
    assert meta.duration_s is not None
    assert meta.duration_s > 0
    assert "channel_names" in meta.extra
    assert len(meta.extra["channel_names"]) == 7


def test_edf_metadata_openneuro():
    """EDF adapter returns valid metadata for OpenNeuro EEG EDF."""
    if OPENNEURO_EEG is None:
        import pytest
        pytest.skip("No OpenNeuro EDF files found")

    from biogpu.nsi.adapters.edf import EDFAdapter

    adapter = EDFAdapter()
    meta = adapter.metadata(OPENNEURO_EEG)

    assert meta.source_format == "edf"
    assert meta.channel_count >= 19, f"Expected >=19 channels, got {meta.channel_count}"
    assert meta.sample_rate_hz > 0
    assert meta.duration_s is not None
    assert meta.duration_s > 0


def test_edf_open():
    """EDF open() returns an NSIDataset with correct data shape."""
    from biogpu.nsi.adapters.edf import EDFAdapter

    adapter = EDFAdapter()
    ds = adapter.open(SLEEP_PSG)

    assert ds.metadata.vendor == "physionet_openneuro"
    assert ds.data is not None
    assert ds.data.shape[0] == 7, f"Expected 7 channels, got {ds.data.shape[0]}"
    assert ds.data.dtype == np.float32
    assert len(ds.feature_names) == 7 * 6  # 6 features per channel
    assert ds.feature_names[0] == "ch0_rms"
    assert ds.feature_names[5] == "ch0_skew"


def test_edf_iter_windows():
    """EDF iter_windows yields correctly shaped arrays."""
    from biogpu.nsi.adapters.edf import EDFAdapter

    adapter = EDFAdapter()
    window_s = 1.0  # 1 second
    windows = list(adapter.iter_windows(SLEEP_PSG, window_s, overlap=0.0))

    assert len(windows) > 0, "No windows yielded"
    expected_samples = int(window_s * 100)  # 100 samples at 100 Hz
    for w in windows[:5]:
        assert w.shape[0] == 7, f"Expected 7 channels, got {w.shape[0]}"
        assert w.shape[1] == expected_samples, f"Expected {expected_samples} samples, got {w.shape[1]}"


def test_edf_feature_vector_shape():
    """Feature vector has shape (n_channels * 6,)."""
    from biogpu.nsi.adapters.edf import EDFAdapter

    adapter = EDFAdapter()
    ds = adapter.open(SLEEP_PSG)
    window = ds.data[:, :100]  # First 100 samples (~1s at 100Hz)

    fv = adapter.feature_vector(window)
    assert fv.shape == (7 * 6,), f"Expected (42,), got {fv.shape}"
    assert fv.dtype == np.float32


def test_edf_feature_values_are_finite():
    """All extracted features are finite (no NaN or inf)."""
    from biogpu.nsi.adapters.edf import EDFAdapter

    adapter = EDFAdapter()
    ds = adapter.open(SLEEP_PSG)
    mid = ds.data.shape[1] // 2
    window = ds.data[:, mid:mid + 100]

    fv = adapter.feature_vector(window)
    assert np.all(np.isfinite(fv)), "Feature vector contains NaN or inf values"
    assert np.any(fv != 0), "Feature vector is all zeros"


def test_adapter_registry_counts():
    """At least 5 adapters registered (MCS + Giroldini + DANDI + EDF + GCP2)."""
    from biogpu.nsi.adapters import list_adapters
    adapters = list_adapters()
    assert len(adapters) >= 5,         f"Expected at least 5 adapters, got {len(adapters)}: {adapters}"
    assert "physionet_edf" in adapters
