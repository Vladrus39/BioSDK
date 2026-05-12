from __future__ import annotations

from pathlib import Path

from biogpu.benchmarks.biogpu_v544_private_registry_handoff import run
from biogpu.evidence.ledger_v53 import sha256_file
from biogpu.sdk.private_registry_handoff_v544 import (
    authorize_handoff_access_v544,
    build_handoff_artifact_record_v544,
    build_local_registry_index_v544,
    build_private_registry_handoff_contract_v544,
    default_handoff_principal_fixtures_v544,
    run_handoff_access_matrix_v544,
    run_handoff_revocation_probe_v544,
    run_private_registry_handoff_workflow_v544,
    stage_local_handoff_artifact_v544,
    write_private_registry_handoff_outputs_v544,
)


def _fake_v543_dependency(tmp_path: Path) -> tuple[dict[str, object], Path]:
    wheel = tmp_path / "biogpu_core-5.0.0-py3-none-any.whl"
    wheel.write_bytes(b"fake wheel bytes for v544 contract tests")
    digest = sha256_file(wheel)
    return {
        "release_approval_revocation_contract_ready": True,
        "local_candidate_handoff_approved": True,
        "artifact_name": wheel.name,
        "artifact_sha256": digest,
        "release_approval_audit_sha256": "c" * 64,
    }, wheel


def test_v544_contract_is_local_only():
    contract = build_private_registry_handoff_contract_v544()

    assert contract["private_registry_handoff_contract_ready"] is True
    assert contract["contract"]["live_registry_endpoint_configured"] is False
    assert contract["live_private_registry_ready"] is False
    assert contract["public_registry_ready"] is False
    assert contract["full_biosdk_ready"] is False


def test_v544_artifact_record_and_staging_are_ready(tmp_path):
    dependency, wheel = _fake_v543_dependency(tmp_path)
    record = build_handoff_artifact_record_v544(dependency, wheel)
    staged = stage_local_handoff_artifact_v544(record, tmp_path / "out")

    assert record["handoff_artifact_record_ready"] is True
    assert record["artifact_file_sha256_matches"] is True
    assert staged["local_handoff_package_ready"] is True
    assert staged["staged_artifact_sha256"] == dependency["artifact_sha256"]


def test_v544_access_matrix_allows_and_denies_expected_cases(tmp_path):
    dependency, wheel = _fake_v543_dependency(tmp_path)
    record = build_handoff_artifact_record_v544(dependency, wheel)
    matrix = run_handoff_access_matrix_v544(record, default_handoff_principal_fixtures_v544(record["artifact_sha256"]))

    assert matrix["handoff_access_matrix_ready"] is True
    assert matrix["allowed_count"] == 4
    assert matrix["denied_count"] == 8
    assert "claim_boundary_not_accepted" in matrix["reason_codes"]
    assert "artifact_digest_mismatch" in matrix["reason_codes"]
    assert "production_distribution_not_allowed" in matrix["reason_codes"]


def test_v544_authorization_blocks_revoked_access(tmp_path):
    dependency, wheel = _fake_v543_dependency(tmp_path)
    record = build_handoff_artifact_record_v544(dependency, wheel)
    revoked = [principal for principal in default_handoff_principal_fixtures_v544(record["artifact_sha256"]) if principal.principal_id == "revoked-recipient"][0]
    decision = authorize_handoff_access_v544(revoked, record)

    assert decision.allowed is False
    assert "access_revoked" in decision.reason_codes
    assert decision.private_registry_ready is False


def test_v544_revocation_probe_and_index_are_ready(tmp_path):
    dependency, wheel = _fake_v543_dependency(tmp_path)
    record = build_handoff_artifact_record_v544(dependency, wheel)
    staged = stage_local_handoff_artifact_v544(record, tmp_path / "out")
    matrix = run_handoff_access_matrix_v544(record)
    probe = run_handoff_revocation_probe_v544(record)
    index = build_local_registry_index_v544(record, staged, matrix, probe)

    assert probe["handoff_revocation_probe_ready"] is True
    assert index["local_registry_index_ready"] is True
    assert index["live_registry_endpoint"] is None
    assert index["private_registry_ready"] is False


def test_v544_workflow_ready_without_registry_claims(tmp_path):
    audit = run_private_registry_handoff_workflow_v544(Path.cwd(), tmp_path / "out")

    assert audit["overall_status"] == "private_registry_handoff_contract_ready_production_not_claimed"
    assert audit["private_registry_handoff_contract_ready"] is True
    assert audit["v543_dependency_ready"] is True
    assert audit["local_handoff_package_ready"] is True
    assert audit["local_registry_index_ready"] is True
    assert audit["live_private_registry_ready"] is False
    assert audit["production_distribution_ready"] is False
    assert audit["full_biosdk_ready"] is False
    assert audit["bic_os_phase_locked"] is True


def test_v544_outputs_are_written(tmp_path):
    audit = run_private_registry_handoff_workflow_v544(Path.cwd(), tmp_path / "workflow")
    paths = write_private_registry_handoff_outputs_v544(audit, tmp_path / "out")

    assert Path(paths["summary_json"]).exists()
    assert Path(paths["contract_json"]).exists()
    assert Path(paths["artifact_record_json"]).exists()
    assert Path(paths["handoff_package_json"]).exists()
    assert Path(paths["access_matrix_json"]).exists()
    assert Path(paths["revocation_probe_json"]).exists()
    assert Path(paths["registry_index_json"]).exists()
    assert Path(paths["access_matrix_csv"]).exists()
    assert "Private Registry Handoff Contract" in Path(paths["markdown_report"]).read_text(encoding="utf-8")


def test_v544_runner_writes_summary(tmp_path):
    result = run(root=Path.cwd(), out_dir=tmp_path / "out")

    assert result["summary"]["private_registry_handoff_contract_ready"] is True
    assert (tmp_path / "out" / "V544_PRIVATE_REGISTRY_HANDOFF_SUMMARY.json").exists()