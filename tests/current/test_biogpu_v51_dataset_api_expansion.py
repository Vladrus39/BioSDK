"""Tests for BioGPU-Core v5.1 Dataset & API expansion phase.

Covers:
  - zenodo_raw_hdf5_gate: offline gate when raw files not present
  - dandi_discovery: curated candidate manifest
  - dandi_nwb: inspect_nwb_units offline gate
  - orientation dataset: synthetic generation
  - biogpu_v51_dataset_api_expansion: full probe runner
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# zenodo_raw_hdf5_gate
# ---------------------------------------------------------------------------

class TestZenodoRawHDF5Gate:
    def test_probe_all_returns_report_structure(self):
        from biogpu.data_ingest.zenodo_raw_hdf5_gate import probe_all_raw_hdf5_assets
        report = probe_all_raw_hdf5_assets()
        assert hasattr(report, "overall_status")
        assert hasattr(report, "assets")
        assert len(report.assets) >= 2

    def test_gate_not_downloaded_when_no_raw_dir(self, tmp_path):
        from biogpu.data_ingest.zenodo_raw_hdf5_gate import probe_all_raw_hdf5_assets
        # tmp_path has no data/external/raw_hdf5 dir
        report = probe_all_raw_hdf5_assets(project_root=tmp_path)
        assert report.overall_status in ("not_downloaded", "empty_dir", "partial")
        for asset in report.assets:
            assert asset.gate_status in ("not_downloaded", "empty_dir", "partial")

    def test_probe_available_when_h5_files_present(self, tmp_path):
        from biogpu.data_ingest.zenodo_raw_hdf5_gate import probe_all_raw_hdf5_assets
        raw_dir = tmp_path / "data" / "external" / "raw_hdf5"
        raw_dir.mkdir(parents=True)
        # Create two stub .h5 files
        (raw_dir / "rec001.h5").write_bytes(b"\x89HDF\r\n\x1a\n" + b"\x00" * 8)
        (raw_dir / "rec002.h5").write_bytes(b"\x89HDF\r\n\x1a\n" + b"\x00" * 8)
        report = probe_all_raw_hdf5_assets(project_root=tmp_path)
        hdf5_probe = next(a for a in report.assets if a.asset_id == "zenodo_14363732_raw_hdf5")
        assert hdf5_probe.gate_status == "available"
        assert hdf5_probe.file_count == 2

    def test_probe_to_dict_is_json_serialisable(self, tmp_path):
        from biogpu.data_ingest.zenodo_raw_hdf5_gate import probe_all_raw_hdf5_assets
        report = probe_all_raw_hdf5_assets(project_root=tmp_path)
        d = report.to_dict()
        # Must not raise
        json.dumps(d)

    def test_write_json_creates_file(self, tmp_path):
        from biogpu.data_ingest.zenodo_raw_hdf5_gate import probe_all_raw_hdf5_assets
        report = probe_all_raw_hdf5_assets(project_root=tmp_path)
        out = tmp_path / "out" / "gate_report.json"
        report.write_json(out)
        assert out.exists()
        data = json.loads(out.read_text(encoding="utf-8"))
        assert "overall_status" in data

    def test_inspect_raw_hdf5_file_missing(self, tmp_path):
        from biogpu.data_ingest.zenodo_raw_hdf5_gate import inspect_raw_hdf5_file
        result = inspect_raw_hdf5_file(tmp_path / "nonexistent.h5")
        assert result["exists"] is False
        assert result["gate_status"] == "not_downloaded"

    def test_asset_manifest_has_download_hints(self):
        from biogpu.data_ingest.zenodo_raw_hdf5_gate import RAW_HDF5_ASSET_MANIFEST
        for descriptor in RAW_HDF5_ASSET_MANIFEST:
            assert descriptor["download_hint"]
            assert descriptor["asset_id"]
            assert "14363732" in descriptor["download_hint"] or "Zenodo" in descriptor["download_hint"]


# ---------------------------------------------------------------------------
# dandi_discovery
# ---------------------------------------------------------------------------

class TestDandiDiscovery:
    def test_curated_candidates_not_empty(self):
        from biogpu.data_ingest.dandi_discovery import curated_candidates
        candidates = curated_candidates()
        assert len(candidates) >= 1

    def test_candidates_have_required_fields(self):
        from biogpu.data_ingest.dandi_discovery import curated_candidates
        for c in curated_candidates():
            assert c.dandiset_id
            assert c.name
            assert c.download_hint
            assert c.has_units in (True, False)

    def test_write_candidate_manifest(self, tmp_path):
        from biogpu.data_ingest.dandi_discovery import write_candidate_manifest
        out = tmp_path / "sub" / "candidates.json"
        result_path = write_candidate_manifest(out)
        assert result_path.exists()
        data = json.loads(out.read_text(encoding="utf-8"))
        assert "candidates" in data
        assert len(data["candidates"]) >= 1

    def test_keyword_score_returns_int(self):
        from biogpu.data_ingest.dandi_discovery import keyword_score
        score = keyword_score({"description": "ecephys spike units NWB"})
        assert isinstance(score, int)
        assert score >= 2


# ---------------------------------------------------------------------------
# dandi_nwb: offline gate (no real NWB file)
# ---------------------------------------------------------------------------

class TestDandiNWBOfflineGate:
    def test_inspect_nwb_units_missing_path(self, tmp_path):
        from biogpu.data_ingest.dandi_nwb import inspect_nwb_units
        result = inspect_nwb_units(tmp_path / "missing.nwb")
        assert result["exists"] is False

    def test_adapter_connect_raises_on_missing_file(self, tmp_path):
        from biogpu.data_ingest.dandi_nwb import DandiNWBSpikeAdapter, DandiNWBConfig
        adapter = DandiNWBSpikeAdapter(DandiNWBConfig(nwb_path=str(tmp_path / "missing.nwb")))
        with pytest.raises(FileNotFoundError):
            adapter.connect()

    def test_health_check_shows_not_connected(self, tmp_path):
        from biogpu.data_ingest.dandi_nwb import DandiNWBSpikeAdapter, DandiNWBConfig
        adapter = DandiNWBSpikeAdapter(DandiNWBConfig(nwb_path=str(tmp_path / "missing.nwb")))
        hc = adapter.health_check()
        assert hc["connected"] is False


# ---------------------------------------------------------------------------
# Orientation dataset (synthetic, always available)
# ---------------------------------------------------------------------------

class TestOrientationDataset:
    def test_generate_returns_correct_count(self):
        from biogpu.datasets.orientation import generate_orientation_dataset
        patterns = generate_orientation_dataset(size=8, samples_per_class=10)
        assert len(patterns) == 40  # 4 orientations × 10 samples

    def test_labels_cover_all_orientations(self):
        from biogpu.datasets.orientation import generate_orientation_dataset, ORIENTATIONS
        patterns = generate_orientation_dataset(size=8, samples_per_class=5)
        labels = {p.label for p in patterns}
        assert len(labels) == len(ORIENTATIONS)

    def test_pattern_shape_correct(self):
        from biogpu.datasets.orientation import generate_orientation_dataset
        patterns = generate_orientation_dataset(size=12, samples_per_class=4)
        for p in patterns:
            assert p.data.shape == (12, 12)

    def test_deterministic_with_seed(self):
        from biogpu.datasets.orientation import generate_orientation_dataset
        p1 = generate_orientation_dataset(size=8, samples_per_class=5, seed=99)
        p2 = generate_orientation_dataset(size=8, samples_per_class=5, seed=99)
        import numpy as np
        for a, b in zip(p1, p2):
            np.testing.assert_array_equal(a.data, b.data)


# ---------------------------------------------------------------------------
# v51 full probe runner
# ---------------------------------------------------------------------------

class TestV51DatasetExpansionProbeRunner:
    def test_main_completes_and_writes_summary(self, tmp_path):
        from biogpu.benchmarks.biogpu_v51_dataset_api_expansion import main
        summary = main(project_root=str(tmp_path), output_dir=str(tmp_path / "out"))
        assert summary["milestone"] == "v5.1"
        assert isinstance(summary["probes"], list)
        assert len(summary["probes"]) >= 4

    def test_summary_json_written(self, tmp_path):
        from biogpu.benchmarks.biogpu_v51_dataset_api_expansion import main
        out = tmp_path / "out"
        main(project_root=str(tmp_path), output_dir=str(out))
        summary_path = out / "V51_DATASET_EXPANSION_SUMMARY.json"
        assert summary_path.exists()
        data = json.loads(summary_path.read_text(encoding="utf-8"))
        assert data["phase"] == "dataset_api_expansion"

    def test_gate_keys_present(self, tmp_path):
        from biogpu.benchmarks.biogpu_v51_dataset_api_expansion import main
        summary = main(project_root=str(tmp_path), output_dir=str(tmp_path / "out"))
        gate = summary["gate"]
        assert "raw_hdf5_available" in gate
        assert "nwb_available" in gate
        assert gate["orientation_synthetic_available"] is True

    def test_raw_hdf5_gate_not_downloaded_in_empty_root(self, tmp_path):
        from biogpu.benchmarks.biogpu_v51_dataset_api_expansion import main
        summary = main(project_root=str(tmp_path), output_dir=str(tmp_path / "out"))
        assert summary["gate"]["raw_hdf5_available"] is False

    def test_dandi_candidates_probe_present(self, tmp_path):
        from biogpu.benchmarks.biogpu_v51_dataset_api_expansion import main
        summary = main(project_root=str(tmp_path), output_dir=str(tmp_path / "out"))
        dandi_probe = next(
            (p for p in summary["probes"] if p.get("probe") == "dandi_discovery"), None
        )
        assert dandi_probe is not None
        assert dandi_probe["candidate_count"] >= 1
