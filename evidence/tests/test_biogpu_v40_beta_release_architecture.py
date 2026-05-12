
from __future__ import annotations

import json

from fastapi.testclient import TestClient

from biogpu.beta.architecture_v40 import build_beta_release_architecture_v40, write_beta_release_outputs_v40
from biogpu.api.beta_server_v40 import app


def test_v40_architecture_contains_three_delivery_paths():
    arch = build_beta_release_architecture_v40()
    ids = {x["channel_id"] for x in arch["release_channels"]}
    assert "private_github_sdk" in ids
    assert "hosted_biogpu_server" in ids
    assert "enterprise_onprem_docker" in ids
    assert "lab_approved_live_addon" in ids


def test_v40_dataset_expansion_includes_raw_dandi_allen_api():
    arch = build_beta_release_architecture_v40()
    ids = {x["dataset_id"] for x in arch["dataset_expansion"]}
    assert "zenodo_14363732_raw_hdf5" in ids
    assert "dandi_nwb_discovery_pack" in ids
    assert "allen_brain_observatory_visual_coding" in ids
    assert "finalspark_read_only_live_hdf5" in ids


def test_v40_outputs_are_written(tmp_path):
    written = write_beta_release_outputs_v40(tmp_path)
    assert (tmp_path / "v40_beta_release_architecture.json").exists()
    data = json.loads((tmp_path / "v40_summary.json").read_text(encoding="utf-8"))
    assert data["release_channel_count"] >= 4
    assert data["first_paid_product"] == "Enterprise Read-Only BioSDK"
    assert "report_md" in written


def test_v40_beta_server_blocks_unsafe_mode():
    client = TestClient(app)
    assert client.get("/health").status_code == 200
    ok = client.post("/v40/runs/validate", json={"mode": "replay", "dataset_id": "zenodo_14363732_preprocessed"})
    assert ok.status_code == 200
    bad = client.post("/v40/runs/validate", json={"mode": "unapproved_live_stimulation", "dataset_id": "x"})
    assert bad.status_code == 403


def test_v40_keeps_deferred_powerpc_and_lab_backlog_visible():
    arch = build_beta_release_architecture_v40()
    ids = {x["item_id"] for x in arch["deferred_work_items"]}
    assert "D1_full_shuffle_1000" in ids
    assert "D2_extended_methods_5000" in ids
    assert "D3_bootstrap_confidence_intervals" in ids
    assert "D4_zenodo_raw_hdf5_ttl" in ids
    assert "D7_energy_latency_measurement" in ids
    assert "D10_lab_live_validation" in ids
