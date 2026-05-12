from __future__ import annotations

import json
from pathlib import Path

from biogpu.benchmarks.biogpu_v519_vendor_user_upload_gate import run
from biogpu.sdk.vendor_upload_v519 import build_vendor_upload_gate_v519, validate_vendor_upload_sample_v519, write_vendor_upload_outputs_v519


def test_v519_missing_upload_sample_is_honest_gate(tmp_path):
    gate = build_vendor_upload_gate_v519(tmp_path)

    assert gate["overall_status"] == "vendor_user_upload_sample_missing_required"
    assert gate["sample_count"] == 0
    assert gate["validated_sample_count"] == 0
    assert gate["bic_os_phase_locked"] is True


def test_v519_safe_user_json_fixture_validates(tmp_path):
    sample = tmp_path / "data" / "external" / "user_upload_samples" / "safe_spikes.json"
    sample.parent.mkdir(parents=True)
    sample.write_text(json.dumps({"spike_times_s": [0.1, 0.2], "channels": [1, 2], "mode": "read_only_replay"}), encoding="utf-8")

    result = validate_vendor_upload_sample_v519(sample, tmp_path)
    report = result["report"]

    assert report["gate_status"] == "readonly_sample_validated"
    assert report["sample_family"] == "user_upload"
    assert report["safety_scan_passed"] is True
    assert report["import_status"] == "metadata_ready"


def test_v519_unsafe_live_field_is_blocked(tmp_path):
    sample = tmp_path / "data" / "external" / "vendor_exports" / "unsafe.json"
    sample.parent.mkdir(parents=True)
    sample.write_text(json.dumps({"voltage": 1.2, "channels": [1, 2]}), encoding="utf-8")

    result = validate_vendor_upload_sample_v519(sample, tmp_path)
    report = result["report"]

    assert report["gate_status"] == "sample_blocked_or_incomplete"
    assert report["safety_scan_passed"] is False
    assert "voltage" in report["forbidden_terms"]


def test_v519_vendor_hdf5_magic_fixture_routes_to_vendor_importer(tmp_path):
    sample = tmp_path / "data" / "external" / "vendor_exports" / "recording.h5"
    sample.parent.mkdir(parents=True)
    sample.write_bytes(b"\x89HDF\r\n\x1a\n" + b"\x00" * 16)

    gate = build_vendor_upload_gate_v519(tmp_path)
    report = gate["sample_reports"][0]

    assert gate["overall_status"] == "vendor_user_upload_readonly_samples_validated"
    assert report["importer_id"] == "vendor_export_v42"
    assert report["schema_hint"] == "hdf5_magic_present"
    assert report["sha256"]


def test_v519_write_outputs_and_runner(tmp_path):
    paths = write_vendor_upload_outputs_v519(tmp_path, tmp_path / "out")
    summary_path = Path(paths["summary_json"])

    assert summary_path.exists()
    assert Path(paths["intake_template_json"]).exists()
    assert Path(paths["sample_reports_csv"]).exists()

    result = run(root=tmp_path, out_dir=tmp_path / "out2")
    assert result["summary"]["overall_status"] == "vendor_user_upload_sample_missing_required"
