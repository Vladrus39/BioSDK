"""NSI-1.0 Conformance Test — DANDI/NWB Adapter.

Verifies that the DANDI NWB adapter:
1. Implements the full NSI-1.0 interface
2. Opens Allen NWB files (continuous LFP) and DANDI spike-sorted NWBs
3. Returns correct metadata shapes and types
4. Windows have consistent dimensions
5. Feature names follow ch{i}_{feat} convention
"""
from __future__ import annotations

import numpy as np
from pathlib import Path

BIO = Path(r"C:\Users\vladi\Desktop\Braine\BiC OS\biogpu-core-v5_0_bic_os_first_mover_roadmap")

ALLEN_NWB = BIO / "data" / "external" / "allen" / "dandi_000021" / "sub-703279277_ses-719161530_probe-729445654_ecephys.nwb"
DANDI_NWB = BIO / "data" / "external" / "nwb" / "dandi_000469" / "sub-20_ses-2_ecephys+image.nwb"


def test_dandi_adapter_import():
    """DANDI adapter class is importable and registered."""
    from biogpu.nsi.adapters import get_adapter, list_adapters

    adapters = list_adapters()
    assert "dandi_nwb" in adapters, f"Expected dandi_nwb in {adapters}"

    dandi_cls = get_adapter("dandi_nwb")
    assert dandi_cls is not None
    assert dandi_cls.adapter_id == "dandi_nwb"
    assert dandi_cls.vendor == "dandi_allen"
    assert dandi_cls.modality == "ecephys"


def test_dandi_metadata_allen():
    """DANDI adapter returns valid metadata for Allen NWB file."""
    from biogpu.nsi.adapters.dandi import DandiNWBAdapter

    adapter = DandiNWBAdapter()
    meta = adapter.metadata(ALLEN_NWB)

    assert meta.vendor == "dandi_allen"
    assert meta.modality == "ecephys"
    assert meta.source_format == "nwb"
    assert meta.channel_count == 96, f"Expected 96 channels, got {meta.channel_count}"
    assert meta.sample_rate_hz is not None
    assert meta.sample_rate_hz > 0
    assert meta.duration_s is not None
    assert meta.duration_s > 0
    assert "session_id" in meta.extra


def test_dandi_metadata_spike_nwb():
    """DANDI adapter returns valid metadata for spike-sorted DANDI NWB."""
    from biogpu.nsi.adapters.dandi import DandiNWBAdapter

    adapter = DandiNWBAdapter()
    meta = adapter.metadata(DANDI_NWB)

    assert meta.vendor == "dandi_allen"
    assert meta.source_format == "nwb"
    assert meta.channel_count > 0, f"Expected >0 channels (units), got {meta.channel_count}"
    # Spike-sorted NWB: sample_rate ~100 Hz (10ms bins)
    assert meta.sample_rate_hz is not None


def test_dandi_open_allen():
    """DANDI open() returns NSIDataset with correct data from Allen NWB."""
    from biogpu.nsi.adapters.dandi import DandiNWBAdapter

    adapter = DandiNWBAdapter()
    ds = adapter.open(ALLEN_NWB)

    assert ds.metadata.vendor == "dandi_allen"
    assert ds.data is not None
    # Allen NWB: 96 channels LFP
    assert ds.data.shape[1] == 96 or ds.data.shape[0] == 96, \
        f"Expected 96 channels in shape {ds.data.shape}"
    assert ds.data.dtype == np.float32
    assert len(ds.feature_names) == 96 * 6, \
        f"Expected 576 features (96ch x 6), got {len(ds.feature_names)}"
    # Feature name ordering
    assert ds.feature_names[0] == "ch0_rms"
    assert ds.feature_names[5] == "ch0_skew"
    assert ds.feature_names[6] == "ch1_rms"


def test_dandi_iter_windows_allen():
    """DANDI iter_windows yields correctly shaped arrays from Allen NWB."""
    from biogpu.nsi.adapters.dandi import DandiNWBAdapter

    adapter = DandiNWBAdapter()
    window_s = 0.5
    windows = list(adapter.iter_windows(ALLEN_NWB, window_s, overlap=0.0))

    assert len(windows) > 0, "No windows yielded"
    meta = adapter.metadata(ALLEN_NWB)
    expected_samples = int(window_s * meta.sample_rate_hz)
    for w in windows[:5]:  # Check first 5
        assert w.ndim == 2, f"Window should be 2D, got {w.ndim}D"
        assert w.shape[0] == 96, f"Expected 96 channels, got {w.shape[0]}"
        assert w.shape[1] == expected_samples, \
            f"Expected {expected_samples} samples, got {w.shape[1]}"


def test_dandi_feature_vector_shape():
    """Feature vector has shape (n_channels * 6,)."""
    from biogpu.nsi.adapters.dandi import DandiNWBAdapter

    adapter = DandiNWBAdapter()
    ds = adapter.open(ALLEN_NWB)
    # Get a window-shaped slice from middle
    if ds.data.shape[0] == 96:
        mid = ds.data.shape[1] // 2
        window = ds.data[:, mid:mid + 1250]
    else:
        mid = ds.data.shape[0] // 2
        window = ds.data[mid:mid + 1250, :].T

    fv = adapter.feature_vector(window)
    assert fv.shape == (96 * 6,), f"Expected (576,), got {fv.shape}"
    assert fv.dtype == np.float32


def test_dandi_feature_values_are_finite():
    """All extracted features are finite (no NaN or inf)."""
    from biogpu.nsi.adapters.dandi import DandiNWBAdapter

    adapter = DandiNWBAdapter()
    ds = adapter.open(ALLEN_NWB)
    # Get a window from the middle of recording (not start, which may be quiet)
    if ds.data.shape[0] == 96:
        mid = ds.data.shape[1] // 2
        window = ds.data[:, mid:mid + 1250]
    else:
        mid = ds.data.shape[0] // 2
        window = ds.data[mid:mid + 1250, :].T

    fv = adapter.feature_vector(window)
    assert np.all(np.isfinite(fv)), "Feature vector contains NaN or inf"


def test_adapter_registry_counts():
    """At least 3 adapters registered (MCS + Giroldini + DANDI)."""
    from biogpu.nsi.adapters import list_adapters
    adapters = list_adapters()
    assert len(adapters) >= 3, \
        f"Expected at least 3 adapters, got {len(adapters)}: {adapters}"
    assert "dandi_nwb" in adapters
    assert "mcs_mea2100" in adapters
    assert "giroldini_mea" in adapters
