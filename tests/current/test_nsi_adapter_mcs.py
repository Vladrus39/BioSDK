"""NSI-1.0 Conformance Test — MCS MEA2100 Adapter.

Verifies that the MCS adapter:
1. Implements the full NSI-1.0 interface
2. Produces feature vectors with same column ordering as Giroldini adapter
3. Returns correct metadata shapes and types
4. Windows have consistent dimensions
"""
from __future__ import annotations

import numpy as np
from pathlib import Path

BIO = Path(r"C:\Users\vladi\Desktop\Braine\BiC OS\biogpu-core-v5_0_bic_os_first_mover_roadmap")

MCS_FILE = BIO / "data" / "external" / "api_exports" / "mcs_mea2100" / "2014-07-09T10-17-35W8_Standard_all_500_Hz.h5"
GIRO_FILE = next((BIO / "data" / "external" / "raw_hdf5").rglob("*.h5"), None)


def test_mcs_adapter_import():
    """MCS adapter class is importable and registered."""
    from biogpu.nsi.adapters import get_adapter, list_adapters

    adapters = list_adapters()
    assert "mcs_mea2100" in adapters, f"Expected mcs_mea2100 in {adapters}"
    assert "giroldini_mea" in adapters, f"Expected giroldini_mea in {adapters}"

    mcs_cls = get_adapter("mcs_mea2100")
    assert mcs_cls is not None
    assert mcs_cls.adapter_id == "mcs_mea2100"
    assert mcs_cls.vendor == "mcs"
    assert mcs_cls.modality == "mea"


def test_mcs_metadata():
    """MCS adapter returns valid metadata without loading full data."""
    from biogpu.nsi.adapters.mcs import MCSAdapter

    adapter = MCSAdapter()
    meta = adapter.metadata(MCS_FILE)

    assert meta.vendor == "mcs"
    assert meta.modality == "mea"
    assert meta.source_format == "hdf5"
    assert meta.channel_count == 17, f"Expected 17 channels, got {meta.channel_count}"
    assert meta.sample_rate_hz == 500.0
    assert meta.duration_s is not None
    assert meta.duration_s > 0
    assert meta.extra["stream_count"] == 3


def test_mcs_open():
    """MCS open() returns an NSIDataset with correct data shape."""
    from biogpu.nsi.adapters.mcs import MCSAdapter

    adapter = MCSAdapter()
    ds = adapter.open(MCS_FILE)

    assert ds.metadata.vendor == "mcs"
    assert ds.data is not None
    assert ds.data.shape[0] == 17, f"Expected 17 channels, got {ds.data.shape[0]}"
    assert ds.data.dtype == np.float32
    assert len(ds.feature_names) == 17 * 6  # 6 features per channel
    # Feature name ordering: ch0_rms, ch0_mav, ch0_zc, ch0_var, ch0_peak, ch0_skew, ch1_rms, ...
    assert ds.feature_names[0] == "ch0_rms"
    assert ds.feature_names[5] == "ch0_skew"
    assert ds.feature_names[6] == "ch1_rms"


def test_mcs_iter_windows():
    """MCS iter_windows yields correctly shaped arrays."""
    from biogpu.nsi.adapters.mcs import MCSAdapter

    adapter = MCSAdapter()
    window_s = 0.5  # 500 ms
    windows = list(adapter.iter_windows(MCS_FILE, window_s, overlap=0.0))

    assert len(windows) > 0, "No windows yielded"
    expected_samples = int(window_s * 500)  # 250 samples at 500 Hz
    for w in windows:
        assert w.shape[1] == expected_samples, f"Expected {expected_samples} samples, got {w.shape[1]}"


def test_mcs_feature_vector_shape():
    """Feature vector has shape (n_channels * 6,)."""
    from biogpu.nsi.adapters.mcs import MCSAdapter

    adapter = MCSAdapter()
    # Use a single window from the data
    ds = adapter.open(MCS_FILE)
    window = ds.data[:, :250]  # First 250 samples (~500ms at 500Hz)

    fv = adapter.feature_vector(window)
    assert fv.shape == (17 * 6,), f"Expected (102,), got {fv.shape}"
    assert fv.dtype == np.float32


def test_cross_vendor_feature_ordering():
    """Giroldini and MCS feature names follow identical column ordering.

    Both adapters generate features ch0_rms, ch0_mav, ..., chN_skew.
    For the same number of channels, the feature name lists must match exactly.
    """
    from biogpu.nsi.adapters.mcs import MCSAdapter
    from biogpu.nsi.adapters.giroldini import GiroldiniAdapter

    mcs = MCSAdapter()
    giro = GiroldiniAdapter()

    mcs_ds = mcs.open(MCS_FILE)
    assert GIRO_FILE is not None, "No Giroldini HDF5 files found"
    giro_ds = giro.open(GIRO_FILE)

    # Both use the same feature naming scheme
    # MCS: 17 channels, Giroldini: 59 channels
    # Feature names should follow the same pattern: ch{i}_{feat}
    assert mcs_ds.feature_names[0] == "ch0_rms"
    assert giro_ds.feature_names[0] == "ch0_rms"

    # Verify feature name structure matches
    for i in range(17):
        for j, feat in enumerate(["rms", "mav", "zc", "var", "peak", "skew"]):
            idx = i * 6 + j
            assert mcs_ds.feature_names[idx] == f"ch{i}_{feat}", \
                f"Mismatch at idx={idx}: {mcs_ds.feature_names[idx]} != ch{i}_{feat}"
            assert giro_ds.feature_names[idx] == f"ch{i}_{feat}", \
                f"Mismatch at idx={idx}: {giro_ds.feature_names[idx]} != ch{i}_{feat}"


def test_mcs_feature_values_are_finite():
    """All extracted features are finite (no NaN or inf)."""
    from biogpu.nsi.adapters.mcs import MCSAdapter

    adapter = MCSAdapter()
    ds = adapter.open(MCS_FILE)
    window = ds.data[:, :250]

    fv = adapter.feature_vector(window)
    assert np.all(np.isfinite(fv)), "Feature vector contains NaN or inf values"
    assert np.any(fv != 0), "Feature vector is all zeros — data might be empty"


def test_adapter_registry_counts():
    """At least 2 adapters registered (MCS + Giroldini)."""
    from biogpu.nsi.adapters import list_adapters
    adapters = list_adapters()
    assert len(adapters) >= 2, f"Expected at least 2 adapters, got {len(adapters)}: {adapters}"
