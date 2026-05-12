from __future__ import annotations

from pathlib import Path

from biogpu.benchmarks.biogpu_v553_external_review_finding_triage import run
from biogpu.sdk.external_review_finding_triage_v553 import (
    build_external_review_finding_triage_audit_bundle_v553,
    build_external_review_finding_triage_policy_v553,
    build_remediation_blocker_register_v553,
    build_remediation_plan_packet_v553,
    build_review_finding_triage_matrix_v553,
    default_remediation_closure_gate_fixtures_v553,
    default_review_finding_fixtures_v553,
    evaluate_remediation_closure_gate_v553,
    evaluate_review_finding_v553,
    run_external_review_finding_triage_workflow_v553,
    run_remediation_closure_gate_v553,
    write_external_review_finding_triage_outputs_v553,
)


def _fake_v552_dependency() -> dict[str, object]:
    return {
        "external_reviewer_response_intake_contract_ready": True,
        "external_reviewer_response_intake_audit_sha256": "e" * 64,
        "questionnaire_domain_count": 10,
        "signed_review_response_ready_count": 0,
        "external_review_completed_count": 0,
        "signed_response_blocker_count": 19,
        "artifact_name": "biogpu_core-5.0.0-py3-none-any.whl",
        "artifact_sha256": "a" * 64,
        "real_external_review_ready": False,
        "real_external_pilot_ready": False,
        "production_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }


def test_v553_policy_is_local_only():
    policy = build_external_review_finding_triage_policy_v553()

    assert policy["external_review_finding_triage_policy_ready"] is True
    assert policy["policy"]["requires_v552_response_intake"] is True
    assert len(policy["policy"]["finding_categories"]) == 10
    assert len(policy["policy"]["remediation_plan_sections"]) == 7
    assert policy["real_review_finding_closure_ready"] is False
    assert policy["bic_os_phase_locked"] is True


def test_v553_finding_triage_matrix_is_local_but_not_closed():
    dependency = _fake_v552_dependency()
    matrix = build_review_finding_triage_matrix_v553(dependency, default_review_finding_fixtures_v553())

    assert matrix["review_finding_triage_matrix_ready"] is True
    assert matrix["review_finding_count"] == 10
    assert matrix["local_finding_triage_ready_count"] == 10
    assert matrix["local_remediation_plan_ready_count"] == 10
    assert matrix["real_remediation_approval_count"] == 0
    assert matrix["review_finding_closed_count"] == 0
    assert "blocker_before_external_review_or_pilot" in matrix["remediation_priorities"]
    assert "must_remediate_before_review_closure" in matrix["remediation_priorities"]
    assert "track_before_review_closure" in matrix["remediation_priorities"]
    assert "external_reviewer_identity_missing" in matrix["reason_codes"]
    assert "external_reviewer_signature_missing" in matrix["reason_codes"]
    assert "remediation_approval_missing" in matrix["reason_codes"]
    assert "real_review_finding_closure_not_ready" in matrix["reason_codes"]
    assert "real_external_review_not_ready" in matrix["reason_codes"]
    assert "real_external_pilot_not_ready" in matrix["reason_codes"]
    assert "production_release_not_allowed" in matrix["reason_codes"]
    assert "bic_os_unlock_not_allowed" in matrix["reason_codes"]


def test_v553_finding_evaluation_blocks_closure_request():
    dependency = _fake_v552_dependency()
    fixture = [item for item in default_review_finding_fixtures_v553() if item.requests_review_closure][0]
    decision = evaluate_review_finding_v553(fixture, dependency)

    assert decision.local_finding_triage_ready is True
    assert decision.local_remediation_plan_ready is True
    assert decision.review_finding_closed is False
    assert "real_review_finding_closure_not_ready" in decision.reason_codes
    assert decision.real_external_review_ready is False


def test_v553_remediation_packet_gate_blockers_and_bundle_are_ready():
    dependency = _fake_v552_dependency()
    policy = build_external_review_finding_triage_policy_v553()
    triage_matrix = build_review_finding_triage_matrix_v553(dependency)
    remediation_packet = build_remediation_plan_packet_v553(dependency, triage_matrix)
    closure_gate = run_remediation_closure_gate_v553(dependency, triage_matrix, remediation_packet)
    blocker_register = build_remediation_blocker_register_v553(triage_matrix, closure_gate)
    bundle = build_external_review_finding_triage_audit_bundle_v553(policy, triage_matrix, remediation_packet, closure_gate, blocker_register)

    assert remediation_packet["remediation_plan_packet_ready"] is True
    assert remediation_packet["remediation_plan_record_count"] == 10
    assert remediation_packet["real_remediation_approval_count"] == 0
    assert remediation_packet["review_finding_closed_count"] == 0
    assert closure_gate["remediation_closure_gate_ready"] is True
    assert closure_gate["accepted_local_triage_stage_count"] == 3
    assert closure_gate["denied_remediation_closure_gate_count"] == 9
    assert blocker_register["remediation_blocker_register_ready"] is True
    assert blocker_register["blocker_count"] == 19
    assert bundle["external_review_finding_triage_audit_bundle_ready"] is True
    assert bundle["real_external_review_ready"] is False


def test_v553_closure_gate_denies_open_findings():
    dependency = _fake_v552_dependency()
    triage_matrix = build_review_finding_triage_matrix_v553(dependency)
    remediation_packet = build_remediation_plan_packet_v553(dependency, triage_matrix)
    fixture = [item for item in default_remediation_closure_gate_fixtures_v553() if item.gate_id == "closure-with-open-findings"][0]
    decision = evaluate_remediation_closure_gate_v553(fixture, dependency, triage_matrix, remediation_packet)

    assert decision.accepted_for_local_triage_stage is False
    assert "review_findings_still_open" in decision.reason_codes
    assert "real_review_finding_closure_not_ready" in decision.reason_codes
    assert "real_external_review_not_ready" in decision.reason_codes
    assert decision.real_review_finding_closure_ready is False


def test_v553_workflow_ready_without_closure_or_production_claim(tmp_path):
    audit = run_external_review_finding_triage_workflow_v553(Path.cwd(), tmp_path / "out")

    assert audit["overall_status"] == "external_review_finding_triage_contract_ready_closure_not_claimed"
    assert audit["external_review_finding_triage_contract_ready"] is True
    assert audit["v552_dependency_ready"] is True
    assert audit["review_finding_triage_matrix_ready"] is True
    assert audit["remediation_plan_packet_ready"] is True
    assert audit["real_remediation_approval_count"] == 0
    assert audit["review_finding_closed_count"] == 0
    assert audit["direct_answer"]["are_real_review_findings_closed"] == "no"
    assert audit["real_review_finding_closure_ready"] is False
    assert audit["real_external_review_ready"] is False
    assert audit["real_external_pilot_ready"] is False
    assert audit["production_ready"] is False
    assert audit["full_biosdk_ready"] is False
    assert audit["bic_os_phase_locked"] is True


def test_v553_outputs_are_written(tmp_path):
    audit = run_external_review_finding_triage_workflow_v553(Path.cwd(), tmp_path / "workflow")
    paths = write_external_review_finding_triage_outputs_v553(audit, tmp_path / "out")

    assert Path(paths["summary_json"]).exists()
    assert Path(paths["policy_json"]).exists()
    assert Path(paths["triage_matrix_json"]).exists()
    assert Path(paths["remediation_packet_json"]).exists()
    assert Path(paths["closure_gate_json"]).exists()
    assert Path(paths["blocker_register_json"]).exists()
    assert Path(paths["audit_bundle_json"]).exists()
    assert Path(paths["triage_matrix_csv"]).exists()
    assert Path(paths["closure_gate_csv"]).exists()
    assert "External Review Finding Triage Contract" in Path(paths["markdown_report"]).read_text(encoding="utf-8")


def test_v553_runner_writes_summary(tmp_path):
    result = run(root=Path.cwd(), out_dir=tmp_path / "out")

    assert result["summary"]["external_review_finding_triage_contract_ready"] is True
    assert (tmp_path / "out" / "V553_EXTERNAL_REVIEW_FINDING_TRIAGE_SUMMARY.json").exists()