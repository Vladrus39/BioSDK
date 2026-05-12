from __future__ import annotations

from pathlib import Path

from biogpu.benchmarks.biogpu_v535_tenant_incident_permissions import run
from biogpu.runtime.incident_permissions_v535 import (
    authorize_incident_action_v535,
    default_incident_principals_v535,
    run_incident_permission_matrix_v535,
    run_tenant_incident_permissions_workflow_v535,
    write_tenant_incident_permissions_outputs_v535,
)


def _minimal_v534_audit() -> dict:
    return {
        "version": "v5.34",
        "overall_status": "tamper_evident_incident_ledger_proof_ready_runtime_not_claimed",
        "tamper_evident_incident_ledger_ready": True,
        "chain_root": "chain-root-test",
        "ledger": {
            "ledger_id": "ledger-test",
            "chain_root": "chain-root-test",
            "retention_manifest_sha256": "retention-sha-test",
            "source_records": [
                {"record_type": "incident_opened", "source_id": "incident-test", "payload": {"incident_id": "incident-test", "status": "resolved", "related_job_id": "job-test"}}
            ],
        },
    }


def test_v535_authorizes_operator_and_denies_viewer_write():
    principals = default_incident_principals_v535()
    incident = {"incident_id": "incident-test", "tenant_id": "tenant_alpha"}

    operator_decision = authorize_incident_action_v535(principals["tenant_alpha_operator"], incident, "incident_acknowledge")
    viewer_decision = authorize_incident_action_v535(principals["tenant_alpha_viewer"], incident, "incident_acknowledge")

    assert operator_decision.accepted is True
    assert viewer_decision.accepted is False
    assert "missing_scope:incidents:acknowledge" in viewer_decision.errors


def test_v535_denies_cross_tenant_operator_action():
    principals = default_incident_principals_v535()
    incident = {"incident_id": "incident-test", "tenant_id": "tenant_alpha"}

    decision = authorize_incident_action_v535(principals["tenant_beta_operator"], incident, "incident_resolve")

    assert decision.accepted is False
    assert "tenant_mismatch" in decision.errors


def test_v535_permission_matrix_passes_expected_decisions():
    matrix = run_incident_permission_matrix_v535(_minimal_v534_audit())

    assert matrix["permission_matrix_ready"] is True
    assert matrix["tenant_isolation_passed"] is True
    assert matrix["viewer_write_denial_passed"] is True
    assert matrix["ledger_validation_scope_passed"] is True
    assert matrix["denied_count"] >= 4


def test_v535_workflow_ready_but_not_production_auth(tmp_path):
    audit = run_tenant_incident_permissions_workflow_v535(tmp_path)

    assert audit["overall_status"] == "tenant_incident_permissions_proof_ready_runtime_not_claimed"
    assert audit["tenant_incident_permissions_ready"] is True
    assert audit["permission_matrix_ready"] is True
    assert audit["tenant_isolation_passed"] is True
    assert audit["viewer_write_denial_passed"] is True
    assert audit["production_auth_ready"] is False
    assert audit["production_biocompute_runtime_ready"] is False
    assert audit["bic_os_phase_locked"] is True


def test_v535_write_outputs(tmp_path):
    audit = run_tenant_incident_permissions_workflow_v535(tmp_path)

    paths = write_tenant_incident_permissions_outputs_v535(audit, tmp_path / "out")
    assert Path(paths["summary_json"]).exists()
    assert Path(paths["principals_json"]).exists()
    assert Path(paths["decisions_json"]).exists()
    assert Path(paths["decisions_csv"]).exists()
    assert "Tenant Incident Permissions" in Path(paths["markdown_report"]).read_text(encoding="utf-8")


def test_v535_runner_writes_summary(tmp_path):
    result = run(root=tmp_path, out_dir=tmp_path / "out")

    assert result["summary"]["tenant_incident_permissions_ready"] is True
    assert (tmp_path / "out" / "V535_TENANT_INCIDENT_PERMISSIONS_SUMMARY.json").exists()