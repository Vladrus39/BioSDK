from __future__ import annotations

from pathlib import Path

from biogpu.benchmarks.biogpu_v538_storage_retention_contract import run
from biogpu.runtime.storage_retention_v538 import (
    build_local_access_contracts_v538,
    build_storage_bucket_contracts_v538,
    build_storage_payload_fixtures_v538,
    run_immutable_overwrite_probe_v538,
    run_storage_retention_contract_workflow_v538,
    validate_storage_object_integrity_v538,
    write_storage_fixture_objects_v538,
    write_storage_retention_contract_outputs_v538,
)


def _minimal_v537_audit() -> dict:
    return {
        "version": "v5.37",
        "overall_status": "identity_provider_contract_proof_ready_runtime_not_claimed",
        "identity_provider_contract_ready": True,
        "identity_validation_matrix_ready": True,
        "accepted_identity_fixture_count": 4,
        "denied_identity_fixture_count": 4,
        "production_auth_ready": False,
        "identity_audit_bundle": {"bundle_sha256": "a" * 64, "bundle_ready": True},
        "v536_dependency_summary": {"dashboard_audit_bundle": {"bundle_sha256": "b" * 64, "bundle_ready": True}},
    }


def test_v538_bucket_contracts_cover_required_storage_classes():
    buckets = build_storage_bucket_contracts_v538()

    assert set(buckets) == {"result_bundles", "audit_artifacts", "retention_manifests", "ledger_roots"}
    assert buckets["ledger_roots"].immutable_required is True
    assert buckets["retention_manifests"].retention_days >= 365
    assert all(bucket.production_object_storage_ready is False for bucket in buckets.values())


def test_v538_writes_and_validates_local_object_manifest(tmp_path):
    buckets = build_storage_bucket_contracts_v538()
    payloads = build_storage_payload_fixtures_v538(_minimal_v537_audit())
    stored = write_storage_fixture_objects_v538(payloads, buckets, tmp_path)
    validation = validate_storage_object_integrity_v538(stored["records"], stored["manifest"], buckets)

    assert validation["storage_object_integrity_ready"] is True
    assert validation["object_count"] == 4
    assert validation["immutable_roots_ready"] is True
    assert stored["manifest"]["all_objects_hashed"] is True


def test_v538_local_access_contract_and_immutable_denial(tmp_path):
    buckets = build_storage_bucket_contracts_v538()
    payloads = build_storage_payload_fixtures_v538(_minimal_v537_audit())
    stored = write_storage_fixture_objects_v538(payloads, buckets, tmp_path)

    access = build_local_access_contracts_v538(stored["records"])
    overwrite_probe = run_immutable_overwrite_probe_v538(stored["records"])

    assert access["local_access_contract_ready"] is True
    assert access["production_signed_url_ready"] is False
    assert overwrite_probe["immutable_overwrite_denial_ready"] is True
    assert overwrite_probe["denied_overwrite_count"] >= 2


def test_v538_workflow_ready_but_not_production_storage(tmp_path):
    audit = run_storage_retention_contract_workflow_v538(tmp_path)

    assert audit["overall_status"] == "storage_retention_contract_proof_ready_runtime_not_claimed"
    assert audit["storage_retention_contract_ready"] is True
    assert audit["storage_object_integrity_ready"] is True
    assert audit["retention_manifest_ready"] is True
    assert audit["immutable_overwrite_denial_ready"] is True
    assert audit["production_object_storage_ready"] is False
    assert audit["production_retention_backend_ready"] is False
    assert audit["production_biocompute_runtime_ready"] is False
    assert audit["bic_os_phase_locked"] is True


def test_v538_outputs_are_written(tmp_path):
    audit = run_storage_retention_contract_workflow_v538(tmp_path)

    paths = write_storage_retention_contract_outputs_v538(audit, tmp_path / "out")
    assert Path(paths["summary_json"]).exists()
    assert Path(paths["buckets_json"]).exists()
    assert Path(paths["manifest_json"]).exists()
    assert Path(paths["integrity_json"]).exists()
    assert Path(paths["access_json"]).exists()
    assert Path(paths["objects_csv"]).exists()
    assert "Storage Retention Contract" in Path(paths["markdown_report"]).read_text(encoding="utf-8")


def test_v538_runner_writes_summary(tmp_path):
    result = run(root=tmp_path, out_dir=tmp_path / "out")

    assert result["summary"]["storage_retention_contract_ready"] is True
    assert (tmp_path / "out" / "V538_STORAGE_RETENTION_CONTRACT_SUMMARY.json").exists()


def test_v538_reports_missing_real_storage_inputs(tmp_path):
    audit = run_storage_retention_contract_workflow_v538(tmp_path)

    assert audit["direct_answer"]["did_we_find_real_object_storage_config"] == "no"
    assert len(audit["missing_real_inputs"]) >= 6