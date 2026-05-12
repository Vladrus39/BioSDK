"""NSI-1.0 Conformance Test — GCP2 CSV Adapter.

Verifies that the GCP2 adapter:
1. Implements the full NSI-1.0 interface
2. Opens GCP2 zipped CSV files (History and Latest)
3. Returns correct metadata shapes and types
4. Windows have consistent dimensions
5. Feature names follow ch{i}_{feat} convention
6. Multi-device stacking works (open_multi)
"""
from __future__ import annotations

import numpy as np
from pathlib import Path

BIO = Path(r"C:\Users\vladi\Desktop\Braine\BiC OS\biogpu-core-v5_0_bic_os_first_mover_roadmap")

GCP2_DIR = BIO / "data" / "external" / "gcp2_coherence"
GCP2_HISTORY = GCP2_DIR / "GCP2_Device_Coherence_Device_20_History.csv.zip"
GCP2_LATEST = GCP2_DIR / "GCP2_Device_Coherence_Device_15_Latest.csv.zip"


def test_gcp2_adapter_import():
    """GCP2 adapter class is importable and registered."""
    from biogpu.nsi.adapters import get_adapter, list_adapters

    adapters = list_adapters()
    assert "gcp2_csv" in adapters, f"Expected gcp2_csv in {adapters}"

    gcp2_cls = get_adapter("gcp2_csv")
    assert gcp2_cls is not None
    assert gcp2_cls.adapter_id == "gcp2_csv"
    assert gcp2_cls.vendor == "gcp2"
    assert gcp2_cls.modality == "rng"


def test_gcp2_metadata_history():
    """GCP2 adapter returns valid metadata for History CSV."""
    from biogpu.nsi.adapters.gcp2 import GCP2Adapter

    adapter = GCP2Adapter()
    meta = adapter.metadata(GCP2_HISTORY)

    assert meta.vendor == "gcp2"
    assert meta.source_format == "csv"
    assert meta.modality == "rng"
    assert meta.channel_count == 1, f"Expected 1 channel, got {meta.channel_count}"
    assert meta.sample_rate_hz > 0
    assert meta.duration_s is not None
    assert meta.duration_s > 0
    assert meta.extra["n_samples"] > 100000, f"Expected >100k samples, got {meta.extra['n_samples']}"
    assert meta.extra["device_number"] == "20"


def test_gcp2_metadata_latest():
    """GCP2 adapter returns valid metadata for Latest CSV (single row)."""
    from biogpu.nsi.adapters.gcp2 import GCP2Adapter

    adapter = GCP2Adapter()
    meta = adapter.metadata(GCP2_LATEST)

    assert meta.vendor == "gcp2"
    assert meta.source_format == "csv"
    assert meta.channel_count == 1
    # Latest files have only 1 row
    assert meta.extra["n_samples"] > 0  # Latest files have variable row counts


def test_gcp2_open_history():
    """GCP2 open() returns NSIDataset with correct data from History file."""
    from biogpu.nsi.adapters.gcp2 import GCP2Adapter

    adapter = GCP2Adapter()
    ds = adapter.open(GCP2_HISTORY)

    assert ds.metadata.vendor == "gcp2"
    assert ds.data is not None
    assert ds.data.ndim == 2
    assert ds.data.shape[0] == 1, f"Expected 1 channel, got {ds.data.shape[0]}"
    assert ds.data.shape[1] > 100000, f"Expected >100k samples, got {ds.data.shape[1]}"
    assert ds.data.dtype == np.float32
    assert len(ds.feature_names) == 1 * 6
    assert ds.feature_names[0] == "ch0_rms"


def test_gcp2_open_multi():
    """GCP2 open_multi() stacks multiple devices as channels."""
    from biogpu.nsi.adapters.gcp2 import GCP2Adapter

    adapter = GCP2Adapter()
    # Use 3 history files
    history_files = sorted(GCP2_DIR.glob("*History*.zip"))[:3]
    assert len(history_files) == 3, f"Expected 3 history files, got {len(history_files)}"

    ds = adapter.open_multi(history_files)

    assert ds.data is not None
    assert ds.data.ndim == 2
    assert ds.data.shape[0] == 3, f"Expected 3 devices (channels), got {ds.data.shape[0]}"
    assert ds.data.shape[1] > 0
    assert ds.metadata.channel_count == 3
    assert len(ds.feature_names) == 3 * 6
    assert ds.feature_names[0] == "ch0_rms"
    assert ds.feature_names[6] == "ch1_rms"


def test_gcp2_iter_windows():
    """GCP2 iter_windows yields correctly shaped arrays."""
    from biogpu.nsi.adapters.gcp2 import GCP2Adapter

    adapter = GCP2Adapter()
    window_s = 600.0  # 10 minutes in seconds
    windows = list(adapter.iter_windows(GCP2_HISTORY, window_s, overlap=0.0))

    assert len(windows) > 0, "No windows yielded"
    expected_samples = max(1, int(window_s * adapter.DEFAULT_SAMPLE_RATE_HZ))
    for w in windows[:5]:
        assert w.ndim == 2
        assert w.shape[0] == 1, f"Expected 1 channel, got {w.shape[0]}"
        assert w.shape[1] == expected_samples, f"Expected {expected_samples} samples, got {w.shape[1]}"


def test_gcp2_feature_vector_shape():
    """Feature vector has shape (n_channels * 6,)."""
    from biogpu.nsi.adapters.gcp2 import GCP2Adapter

    adapter = GCP2Adapter()
    ds = adapter.open(GCP2_HISTORY)
    window = ds.data[:, :10]  # First 10 samples

    fv = adapter.feature_vector(window)
    assert fv.shape == (1 * 6,), f"Expected (6,), got {fv.shape}"
    assert fv.dtype == np.float32


def test_gcp2_feature_values_are_finite():
    """All extracted features are finite (no NaN or inf)."""
    from biogpu.nsi.adapters.gcp2 import GCP2Adapter

    adapter = GCP2Adapter()
    ds = adapter.open(GCP2_HISTORY)
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
    assert "gcp2_csv" in adapters
