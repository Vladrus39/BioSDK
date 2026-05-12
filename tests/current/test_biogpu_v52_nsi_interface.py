from __future__ import annotations

import json

from biogpu.benchmarks.biogpu_v52_nsi_interface import run
from biogpu.standards.nsi_conformance_v52 import (
    run_all_dataset_importer_conformance,
    run_all_vendor_adapter_conformance,
)
from biogpu.standards.nsi_v10 import (
    CLAIM_LEVELS,
    NSI_SCHEMA_STATUS,
    NSI_VERSION,
    annotate_claim_level,
    nsi_spec,
    reference_nsi_objects,
    validate_nsi_object,
    validate_result_bundle,
)


def test_nsi_v10_schema_profile_is_frozen_and_json_schema_like():
    data = nsi_spec()
    assert data["standard"] == NSI_VERSION
    assert data["schema_status"] == NSI_SCHEMA_STATUS
    assert len(data["schemas"]) >= 7
    for schema in data["schemas"]:
        assert schema["schema"]["type"] == "object"
        assert schema["schema"]["required"] == schema["required_fields"]
        assert set(schema["required_fields"]).issubset(set(schema["schema"]["properties"]))


def test_reference_nsi_objects_validate():
    objects = reference_nsi_objects()
    assert set(objects) >= {
        "BioComputeTrace",
        "BioComputeTaskManifest",
        "BioComputeFeatureBatch",
        "BioComputeReadoutResult",
        "BioComputeResultBundle",
        "BioComputeSafetyProfile",
        "BioComputeAdapterContract",
    }
    for schema_name, payload in objects.items():
        report = validate_nsi_object(schema_name, payload)
        assert report.valid, report.to_dict()


def test_nsi_validator_reports_missing_required_field():
    payload = dict(reference_nsi_objects()["BioComputeTrace"])
    payload.pop("trace_id")
    report = validate_nsi_object("BioComputeTrace", payload)
    assert report.valid is False
    assert any(issue.path == "trace_id" for issue in report.errors)


def test_adapter_contract_blocks_write_methods_without_approval():
    payload = dict(reference_nsi_objects()["BioComputeAdapterContract"])
    payload["write_methods"] = ["send_stimulation_pattern"]
    report = validate_nsi_object("BioComputeAdapterContract", payload)
    assert report.valid is False
    assert any(issue.path == "write_methods" for issue in report.errors)


def test_result_bundle_validator_and_claim_levels():
    bundle = reference_nsi_objects()["BioComputeResultBundle"]
    report = validate_result_bundle(bundle)
    assert report.valid is True
    assert bundle["claim_level"] in CLAIM_LEVELS

    bad_bundle = dict(bundle)
    bad_bundle["audit_log"] = []
    bad_report = validate_result_bundle(bad_bundle)
    assert bad_report.valid is False


def test_claim_annotation_is_conservative():
    annotation = annotate_claim_level({"mode": "replay", "replay_data_validated": True})
    assert annotation["claim_level"] == "software_replay_only"
    assert "live_biogpu_proof" in annotation["blocked_claims"]
    assert "energy_or_performance_advantage" in annotation["blocked_claims"]


def test_dataset_importer_conformance_passes():
    reports = run_all_dataset_importer_conformance()
    assert len(reports) >= 6
    assert all(report.valid for report in reports)


def test_vendor_adapter_conformance_passes():
    reports = run_all_vendor_adapter_conformance()
    assert len(reports) >= 4
    assert all(report.valid for report in reports)


def test_v52_runner_writes_outputs(tmp_path):
    summary = run(tmp_path)
    assert summary["milestone"] == "v5.2"
    assert summary["gate"]["nsi_schemas_frozen"] is True
    assert summary["gate"]["adapter_conformance_passed"] is True
    assert summary["gate"]["result_bundle_validator_passed"] is True
    summary_path = tmp_path / "V52_NSI_INTERFACE_SUMMARY.json"
    assert summary_path.exists()
    data = json.loads(summary_path.read_text(encoding="utf-8"))
    assert data["phase"] == "nsi_interface"