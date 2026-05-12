from __future__ import annotations

from pathlib import Path

from biogpu.benchmarks.biogpu_v552_external_reviewer_response_intake import run
from biogpu.sdk.external_reviewer_response_intake_v552 import (
    build_external_reviewer_response_audit_bundle_v552,
    build_external_reviewer_response_policy_v552,
    build_questionnaire_scoring_matrix_v552,
    build_signed_response_blocker_register_v552,
    build_signed_review_response_packet_v552,
    default_questionnaire_response_fixtures_v552,
    default_signed_review_response_gate_fixtures_v552,
    evaluate_questionnaire_response_v552,
    evaluate_signed_review_response_gate_v552,
    run_external_reviewer_response_intake_workflow_v552,
    run_signed_review_response_gate_v552,
    write_external_reviewer_response_intake_outputs_v552,
)


def _fake_v551_dependency() -> dict[str, object]:
    return {
        "partner_dataroom_review_packet_contract_ready": True,
        "partner_dataroom_review_packet_audit_sha256": "d" * 64,
        "required_dataroom_item_count": 12,
        "real_dataroom_item_ready_count": 0,
        "external_review_completed_count": 0,
        "external_review_blocker_count": 21,
        "artifact_name": "biogpu_core-5.0.0-py3-none-any.whl",
        "artifact_sha256": "a" * 64,
        "real_external_review_ready": False,
        "real_external_pilot_ready": False,
        "production_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }


def test_v552_policy_is_local_only():
    policy = build_external_reviewer_response_policy_v552()

    assert policy["external_reviewer_response_policy_ready"] is True
    assert policy["policy"]["requires_v551_dataroom_packet"] is True
    assert len(policy["policy"]["questionnaire_domains"]) == 10
    assert len(policy["policy"]["signed_response_sections"]) == 6
    assert policy["real_signed_review_response_ready"] is False
    assert policy["bic_os_phase_locked"] is True


def test_v552_questionnaire_scoring_matrix_is_local_but_not_signed():
    dependency = _fake_v551_dependency()
    matrix = build_questionnaire_scoring_matrix_v552(dependency, default_questionnaire_response_fixtures_v552())

    assert matrix["questionnaire_scoring_matrix_ready"] is True
    assert matrix["questionnaire_domain_count"] == 10
    assert matrix["local_questionnaire_score_ready_count"] == 10
    assert matrix["signed_review_response_ready_count"] == 0
    assert "strong_local_answer" in matrix["score_bands"]
    assert "partial_local_answer" in matrix["score_bands"]
    assert "blocked_before_real_review" in matrix["score_bands"]
    assert "external_reviewer_identity_missing" in matrix["reason_codes"]
    assert "external_reviewer_signature_missing" in matrix["reason_codes"]
    assert "review_session_timestamp_missing" in matrix["reason_codes"]
    assert "real_external_review_not_ready" in matrix["reason_codes"]
    assert "real_external_pilot_not_ready" in matrix["reason_codes"]
    assert "production_release_not_allowed" in matrix["reason_codes"]
    assert "bic_os_unlock_not_allowed" in matrix["reason_codes"]


def test_v552_questionnaire_response_blocks_external_review_completion():
    dependency = _fake_v551_dependency()
    fixture = [item for item in default_questionnaire_response_fixtures_v552() if item.requests_external_review_completion][0]
    decision = evaluate_questionnaire_response_v552(fixture, dependency)

    assert decision.local_questionnaire_score_ready is True
    assert decision.signed_review_response_ready is False
    assert "real_external_review_not_ready" in decision.reason_codes
    assert decision.real_external_review_ready is False


def test_v552_response_packet_gate_blockers_and_bundle_are_ready():
    dependency = _fake_v551_dependency()
    policy = build_external_reviewer_response_policy_v552()
    scoring_matrix = build_questionnaire_scoring_matrix_v552(dependency)
    response_packet = build_signed_review_response_packet_v552(dependency, scoring_matrix)
    response_gate = run_signed_review_response_gate_v552(dependency, scoring_matrix, response_packet)
    blocker_register = build_signed_response_blocker_register_v552(scoring_matrix, response_gate)
    bundle = build_external_reviewer_response_audit_bundle_v552(policy, scoring_matrix, response_packet, response_gate, blocker_register)

    assert response_packet["signed_review_response_packet_ready"] is True
    assert response_packet["response_packet_record_count"] == 10
    assert response_packet["signed_review_response_ready_count"] == 0
    assert response_packet["external_review_completed_count"] == 0
    assert response_gate["signed_review_response_gate_ready"] is True
    assert response_gate["accepted_local_response_stage_count"] == 3
    assert response_gate["denied_signed_response_gate_count"] == 9
    assert blocker_register["signed_response_blocker_register_ready"] is True
    assert blocker_register["blocker_count"] == 19
    assert bundle["external_reviewer_response_audit_bundle_ready"] is True
    assert bundle["real_external_review_ready"] is False


def test_v552_signed_response_gate_denies_completion_without_signature():
    dependency = _fake_v551_dependency()
    scoring_matrix = build_questionnaire_scoring_matrix_v552(dependency)
    response_packet = build_signed_review_response_packet_v552(dependency, scoring_matrix)
    fixture = [item for item in default_signed_review_response_gate_fixtures_v552() if item.gate_id == "missing-signed-review-response"][0]
    decision = evaluate_signed_review_response_gate_v552(fixture, dependency, scoring_matrix, response_packet)

    assert decision.accepted_for_local_response_stage is False
    assert "external_reviewer_identity_missing" in decision.reason_codes
    assert "external_reviewer_signature_missing" in decision.reason_codes
    assert "review_session_timestamp_missing" in decision.reason_codes
    assert "real_external_review_not_ready" in decision.reason_codes
    assert decision.real_signed_review_response_ready is False


def test_v552_workflow_ready_without_signed_response_or_production_claim(tmp_path):
    audit = run_external_reviewer_response_intake_workflow_v552(Path.cwd(), tmp_path / "out")

    assert audit["overall_status"] == "external_reviewer_response_intake_contract_ready_review_not_claimed"
    assert audit["external_reviewer_response_intake_contract_ready"] is True
    assert audit["v551_dependency_ready"] is True
    assert audit["questionnaire_scoring_matrix_ready"] is True
    assert audit["signed_review_response_packet_ready"] is True
    assert audit["signed_review_response_ready_count"] == 0
    assert audit["external_review_completed_count"] == 0
    assert audit["direct_answer"]["are_real_signed_review_responses_ready"] == "no"
    assert audit["real_signed_review_response_ready"] is False
    assert audit["real_external_review_ready"] is False
    assert audit["real_external_pilot_ready"] is False
    assert audit["production_ready"] is False
    assert audit["full_biosdk_ready"] is False
    assert audit["bic_os_phase_locked"] is True


def test_v552_outputs_are_written(tmp_path):
    audit = run_external_reviewer_response_intake_workflow_v552(Path.cwd(), tmp_path / "workflow")
    paths = write_external_reviewer_response_intake_outputs_v552(audit, tmp_path / "out")

    assert Path(paths["summary_json"]).exists()
    assert Path(paths["policy_json"]).exists()
    assert Path(paths["scoring_matrix_json"]).exists()
    assert Path(paths["response_packet_json"]).exists()
    assert Path(paths["response_gate_json"]).exists()
    assert Path(paths["blocker_register_json"]).exists()
    assert Path(paths["audit_bundle_json"]).exists()
    assert Path(paths["scoring_matrix_csv"]).exists()
    assert Path(paths["response_gate_csv"]).exists()
    assert "External Reviewer Response Intake Contract" in Path(paths["markdown_report"]).read_text(encoding="utf-8")


def test_v552_runner_writes_summary(tmp_path):
    result = run(root=Path.cwd(), out_dir=tmp_path / "out")

    assert result["summary"]["external_reviewer_response_intake_contract_ready"] is True
    assert (tmp_path / "out" / "V552_EXTERNAL_REVIEWER_RESPONSE_INTAKE_SUMMARY.json").exists()