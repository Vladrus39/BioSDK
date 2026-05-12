from __future__ import annotations

from pathlib import Path

from biogpu.benchmarks.biogpu_v536_dashboard_route_contract import run
from biogpu.runtime.dashboard_routes_v536 import (
    build_dashboard_route_contracts_v536,
    build_dashboard_view_payloads_v536,
    run_dashboard_access_matrix_v536,
    run_dashboard_route_contract_workflow_v536,
    validate_dashboard_contracts_v536,
    write_dashboard_route_contract_outputs_v536,
)


def _minimal_v535_audit() -> dict:
    incident = {
        "incident_id": "incident-test",
        "tenant_id": "tenant_alpha",
        "status": "open",
        "ledger_id": "ledger-test",
        "ledger_chain_root": "chain-root-test",
        "retention_manifest_sha256": "retention-sha-test",
    }
    decisions = [
        {"check_name": "viewer_acknowledge_denied", "accepted": False, "passed": True},
        {"check_name": "operator_acknowledge_allowed", "accepted": True, "passed": True},
        {"check_name": "cross_tenant_operator_denied", "accepted": False, "passed": True},
        {"check_name": "auditor_validate_ledger_allowed", "accepted": True, "passed": True},
    ]
    return {
        "version": "v5.35",
        "overall_status": "tenant_incident_permissions_proof_ready_runtime_not_claimed",
        "tenant_incident_permissions_ready": True,
        "v534_dependency_ready": True,
        "permission_matrix": {
            "incident": incident,
            "decisions": decisions,
            "decision_count": len(decisions),
            "passed_count": len(decisions),
            "denied_count": 2,
            "tenant_isolation_passed": True,
            "viewer_write_denial_passed": True,
            "ledger_validation_scope_passed": True,
        },
        "v534_dependency_summary": {"incident_ledger_chain_valid": True, "chain_root": "chain-root-test"},
    }


def test_v536_route_contracts_validate_required_scopes():
    routes = build_dashboard_route_contracts_v536()
    payloads = build_dashboard_view_payloads_v536(_minimal_v535_audit())
    validation = validate_dashboard_contracts_v536(routes, payloads)

    assert validation["dashboard_contract_validation_ready"] is True
    assert validation["route_count"] >= 9
    assert validation["route_contracts_have_required_scopes"] is True
    assert validation["mutating_routes_do_not_execute_live"] is True
    assert validation["production_dashboard_claims_absent"] is True


def test_v536_access_matrix_reuses_v535_permissions():
    routes = build_dashboard_route_contracts_v536()
    matrix = run_dashboard_access_matrix_v536(_minimal_v535_audit(), routes)

    assert matrix["dashboard_access_matrix_ready"] is True
    assert matrix["viewer_write_denial_passed"] is True
    assert matrix["tenant_isolation_passed"] is True
    assert matrix["ledger_validation_scope_passed"] is True
    assert matrix["denied_count"] >= 4


def test_v536_workflow_ready_but_not_production_dashboard(tmp_path):
    audit = run_dashboard_route_contract_workflow_v536(tmp_path)

    assert audit["overall_status"] == "dashboard_route_contract_proof_ready_runtime_not_claimed"
    assert audit["dashboard_route_contract_ready"] is True
    assert audit["dashboard_contract_validation_ready"] is True
    assert audit["dashboard_access_matrix_ready"] is True
    assert audit["v535_dependency_ready"] is True
    assert audit["production_dashboard_ready"] is False
    assert audit["production_auth_ready"] is False
    assert audit["production_biocompute_runtime_ready"] is False
    assert audit["bic_os_phase_locked"] is True


def test_v536_outputs_are_written(tmp_path):
    audit = run_dashboard_route_contract_workflow_v536(tmp_path)

    paths = write_dashboard_route_contract_outputs_v536(audit, tmp_path / "out")
    assert Path(paths["summary_json"]).exists()
    assert Path(paths["routes_json"]).exists()
    assert Path(paths["views_json"]).exists()
    assert Path(paths["access_json"]).exists()
    assert Path(paths["routes_csv"]).exists()
    assert "Dashboard Route Contract" in Path(paths["markdown_report"]).read_text(encoding="utf-8")


def test_v536_runner_writes_summary(tmp_path):
    result = run(root=tmp_path, out_dir=tmp_path / "out")

    assert result["summary"]["dashboard_route_contract_ready"] is True
    assert (tmp_path / "out" / "V536_DASHBOARD_ROUTE_CONTRACT_SUMMARY.json").exists()


def test_v536_direct_answer_lists_real_data_and_api_requirements(tmp_path):
    audit = run_dashboard_route_contract_workflow_v536(tmp_path)

    assert audit["direct_answer"]["are_we_configured_to_move_to_model_plus_os_after_real_proof"] == "yes_gradually"
    assert audit["direct_answer"]["when_estimate"] == "milestone_based_not_calendar_based"
    assert len(audit["real_data_or_api_requirements"]) >= 8