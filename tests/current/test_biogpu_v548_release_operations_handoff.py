from __future__ import annotations

from pathlib import Path

from biogpu.benchmarks.biogpu_v548_release_operations_handoff import run
from biogpu.sdk.release_operations_handoff_v548 import (
    build_claim_boundary_attestation_v548,
    build_operator_handoff_packet_v548,
    build_release_operations_audit_bundle_v548,
    build_release_operations_handoff_policy_v548,
    build_release_operations_runbook_v548,
    default_operator_handoff_fixtures_v548,
    evaluate_operator_handoff_v548,
    run_operator_handoff_matrix_v548,
    run_release_operations_handoff_workflow_v548,
    write_release_operations_handoff_outputs_v548,
)


def _fake_v547_dependency() -> dict[str, object]:
    artifact_sha256 = "a" * 64
    return {
        "registry_revoke_yank_notification_contract_ready": True,
        "artifact_name": "biogpu_core-5.0.0-py3-none-any.whl",
        "artifact_sha256": artifact_sha256,
        "registry_revoke_yank_notification_audit_sha256": "b" * 64,
        "production_yank_ready": False,
        "live_private_registry_ready": False,
        "production_distribution_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }


def test_v548_policy_is_local_only():
    policy = build_release_operations_handoff_policy_v548()

    assert policy["release_operations_handoff_policy_ready"] is True
    assert policy["policy"]["requires_v547_revoke_yank_contract"] is True
    assert policy["policy"]["live_operator_handoff_configured"] is False
    assert policy["production_release_ready"] is False
    assert policy["full_biosdk_ready"] is False


def test_v548_matrix_accepts_and_denies_expected_cases():
    dependency = _fake_v547_dependency()
    matrix = run_operator_handoff_matrix_v548(dependency, default_operator_handoff_fixtures_v548())

    assert matrix["operator_handoff_matrix_ready"] is True
    assert matrix["accepted_operator_handoff_count"] == 4
    assert matrix["denied_operator_handoff_count"] == 12
    assert "v547_revoke_yank_evidence_missing" in matrix["reason_codes"]
    assert "runbook_section_missing" in matrix["reason_codes"]
    assert "operator_role_not_authorized" in matrix["reason_codes"]
    assert "production_release_not_allowed" in matrix["reason_codes"]
    assert "bic_os_unlock_not_allowed" in matrix["reason_codes"]


def test_v548_evaluation_denies_production_release_request():
    dependency = _fake_v547_dependency()
    production = [fixture for fixture in default_operator_handoff_fixtures_v548() if fixture.handoff_id == "production-release-request"][0]
    decision = evaluate_operator_handoff_v548(production, dependency)

    assert decision.accepted_for_local_release_ops is False
    assert "production_release_not_allowed" in decision.reason_codes
    assert decision.production_release_ready is False


def test_v548_runbook_packet_claim_boundary_and_bundle_are_ready():
    dependency = _fake_v547_dependency()
    policy = build_release_operations_handoff_policy_v548()
    runbook = build_release_operations_runbook_v548(dependency, policy)
    matrix = run_operator_handoff_matrix_v548(dependency)
    handoff_packet = build_operator_handoff_packet_v548(dependency, runbook, matrix)
    claim_boundary = build_claim_boundary_attestation_v548(handoff_packet)
    bundle = build_release_operations_audit_bundle_v548(policy, runbook, matrix, handoff_packet, claim_boundary)

    assert runbook["release_operations_runbook_ready"] is True
    assert runbook["section_count"] == 8
    assert handoff_packet["operator_handoff_packet_ready"] is True
    assert handoff_packet["packet_count"] == 4
    assert claim_boundary["claim_boundary_attestation_ready"] is True
    assert bundle["release_operations_audit_bundle_ready"] is True
    assert bundle["production_release_ready"] is False


def test_v548_workflow_ready_without_production_or_os_claim(tmp_path):
    audit = run_release_operations_handoff_workflow_v548(Path.cwd(), tmp_path / "out")

    assert audit["overall_status"] == "release_operations_handoff_contract_ready_production_not_claimed"
    assert audit["release_operations_handoff_contract_ready"] is True
    assert audit["v547_dependency_ready"] is True
    assert audit["release_operations_runbook_ready"] is True
    assert audit["operator_handoff_matrix_ready"] is True
    assert audit["operator_handoff_packet_ready"] is True
    assert audit["direct_answer"]["do_we_still_need_many_layers_before_production_and_os"] == "yes"
    assert audit["production_release_ready"] is False
    assert audit["production_operations_ready"] is False
    assert audit["full_biosdk_ready"] is False
    assert audit["bic_os_phase_locked"] is True


def test_v548_outputs_are_written(tmp_path):
    audit = run_release_operations_handoff_workflow_v548(Path.cwd(), tmp_path / "workflow")
    paths = write_release_operations_handoff_outputs_v548(audit, tmp_path / "out")

    assert Path(paths["summary_json"]).exists()
    assert Path(paths["policy_json"]).exists()
    assert Path(paths["runbook_json"]).exists()
    assert Path(paths["handoff_matrix_json"]).exists()
    assert Path(paths["handoff_packet_json"]).exists()
    assert Path(paths["claim_boundary_json"]).exists()
    assert Path(paths["audit_bundle_json"]).exists()
    assert Path(paths["handoff_matrix_csv"]).exists()
    assert Path(paths["handoff_packet_csv"]).exists()
    assert "Release Operations Handoff Contract" in Path(paths["markdown_report"]).read_text(encoding="utf-8")


def test_v548_runner_writes_summary(tmp_path):
    result = run(root=Path.cwd(), out_dir=tmp_path / "out")

    assert result["summary"]["release_operations_handoff_contract_ready"] is True
    assert (tmp_path / "out" / "V548_RELEASE_OPERATIONS_HANDOFF_SUMMARY.json").exists()