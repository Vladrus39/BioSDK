from __future__ import annotations

from pathlib import Path

from biogpu.benchmarks.biogpu_v555_closure_signoff_registry import run
from biogpu.sdk.closure_signoff_registry_v555 import (
    build_closure_signoff_audit_trail_v555,
    build_closure_signoff_registry_audit_bundle_v555,
    build_closure_signoff_registry_policy_v555,
    build_external_reviewer_signoff_packet_v555,
    build_signoff_registry_blocker_register_v555,
    build_signoff_registry_matrix_v555,
    default_signoff_registry_gate_fixtures_v555,
    default_signoff_registry_record_fixtures_v555,
    evaluate_signoff_registry_gate_v555,
    evaluate_signoff_registry_record_v555,
    run_closure_signoff_registry_workflow_v555,
    run_signoff_registry_gate_v555,
    write_closure_signoff_registry_outputs_v555,
)


def _fake_v554_dependency() -> dict[str, object]:
    return {
        "remediation_evidence_closure_contract_ready": True,
        "remediation_evidence_closure_audit_sha256": "d" * 64,
        "remediation_evidence_record_count": 10,
        "real_closure_attestation_ready_count": 0,
        "finding_closure_attested_count": 0,
        "closure_attestation_blocker_count": 19,
        "artifact_name": "biogpu_core-5.0.0-py3-none-any.whl",
        "artifact_sha256": "a" * 64,
        "real_closure_attestation_ready": False,
        "real_review_finding_closure_ready": False,
        "real_external_review_ready": False,
        "real_external_pilot_ready": False,
        "production_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }


def test_v555_policy_is_local_only_and_distance_is_locked():
    policy = build_closure_signoff_registry_policy_v555()

    assert policy["closure_signoff_registry_policy_ready"] is True
    assert policy["policy"]["requires_v554_closure_attestation"] is True
    assert len(policy["policy"]["signoff_registry_record_types"]) == 10
    assert len(policy["policy"]["signoff_audit_event_types"]) == 8
    assert policy["real_external_reviewer_signoff_ready"] is False
    assert policy["bic_os_phase_locked"] is True


def test_v555_signoff_registry_matrix_is_local_but_unsigned():
    dependency = _fake_v554_dependency()
    matrix = build_signoff_registry_matrix_v555(dependency, default_signoff_registry_record_fixtures_v555())

    assert matrix["signoff_registry_matrix_ready"] is True
    assert matrix["signoff_registry_record_count"] == 10
    assert matrix["local_signoff_registry_record_ready_count"] == 10
    assert matrix["local_audit_trail_ready_count"] == 10
    assert matrix["real_external_reviewer_signoff_ready_count"] == 0
    assert matrix["real_closure_signoff_ready_count"] == 0
    assert matrix["review_finding_closed_count"] == 0
    assert "external_reviewer_identity_missing" in matrix["reason_codes"]
    assert "external_reviewer_recheck_missing" in matrix["reason_codes"]
    assert "external_reviewer_signoff_missing" in matrix["reason_codes"]
    assert "immutable_closure_transcript_missing" in matrix["reason_codes"]
    assert "real_external_reviewer_signoff_not_ready" in matrix["reason_codes"]
    assert "real_closure_signoff_not_ready" in matrix["reason_codes"]
    assert "real_review_finding_closure_not_ready" in matrix["reason_codes"]
    assert "real_external_review_not_ready" in matrix["reason_codes"]
    assert "real_external_pilot_not_ready" in matrix["reason_codes"]
    assert "production_release_not_allowed" in matrix["reason_codes"]
    assert "bic_os_unlock_not_allowed" in matrix["reason_codes"]


def test_v555_record_evaluation_blocks_reviewer_signoff_request():
    dependency = _fake_v554_dependency()
    fixture = [item for item in default_signoff_registry_record_fixtures_v555() if item.requests_external_reviewer_signoff][0]
    decision = evaluate_signoff_registry_record_v555(fixture, dependency)

    assert decision.local_signoff_registry_record_ready is True
    assert decision.local_audit_trail_ready is True
    assert decision.real_external_reviewer_signoff_ready is False
    assert decision.review_finding_closed is False
    assert "real_external_reviewer_signoff_not_ready" in decision.reason_codes
    assert decision.real_external_review_ready is False


def test_v555_signoff_packet_gate_blockers_and_bundle_are_ready():
    dependency = _fake_v554_dependency()
    policy = build_closure_signoff_registry_policy_v555()
    registry_matrix = build_signoff_registry_matrix_v555(dependency)
    audit_trail = build_closure_signoff_audit_trail_v555(dependency, registry_matrix)
    signoff_packet = build_external_reviewer_signoff_packet_v555(dependency, registry_matrix, audit_trail)
    signoff_gate = run_signoff_registry_gate_v555(dependency, registry_matrix, audit_trail, signoff_packet)
    blocker_register = build_signoff_registry_blocker_register_v555(registry_matrix, signoff_gate)
    bundle = build_closure_signoff_registry_audit_bundle_v555(policy, registry_matrix, audit_trail, signoff_packet, signoff_gate, blocker_register)

    assert audit_trail["closure_signoff_audit_trail_ready"] is True
    assert audit_trail["audit_event_count"] == 80
    assert signoff_packet["external_reviewer_signoff_packet_ready"] is True
    assert signoff_packet["signoff_packet_record_count"] == 10
    assert signoff_packet["real_external_reviewer_signoff_ready_count"] == 0
    assert signoff_packet["real_closure_signoff_ready_count"] == 0
    assert signoff_packet["review_finding_closed_count"] == 0
    assert signoff_gate["signoff_registry_gate_ready"] is True
    assert signoff_gate["accepted_local_signoff_stage_count"] == 3
    assert signoff_gate["denied_signoff_registry_gate_count"] == 10
    assert blocker_register["signoff_registry_blocker_register_ready"] is True
    assert blocker_register["blocker_count"] == 20
    assert bundle["closure_signoff_registry_audit_bundle_ready"] is True
    assert bundle["real_external_review_ready"] is False


def test_v555_gate_denies_missing_real_signoff():
    dependency = _fake_v554_dependency()
    registry_matrix = build_signoff_registry_matrix_v555(dependency)
    audit_trail = build_closure_signoff_audit_trail_v555(dependency, registry_matrix)
    signoff_packet = build_external_reviewer_signoff_packet_v555(dependency, registry_matrix, audit_trail)
    fixture = [item for item in default_signoff_registry_gate_fixtures_v555() if item.gate_id == "missing-real-signoff"][0]
    decision = evaluate_signoff_registry_gate_v555(fixture, dependency, registry_matrix, audit_trail, signoff_packet)

    assert decision.accepted_for_local_signoff_stage is False
    assert "external_reviewer_identity_missing" in decision.reason_codes
    assert "external_reviewer_recheck_missing" in decision.reason_codes
    assert "external_reviewer_signoff_missing" in decision.reason_codes
    assert "immutable_closure_transcript_missing" in decision.reason_codes
    assert "real_external_reviewer_signoff_not_ready" in decision.reason_codes
    assert "real_closure_signoff_not_ready" in decision.reason_codes
    assert decision.real_external_reviewer_signoff_ready is False


def test_v555_workflow_ready_without_real_signoff_or_production_claim(tmp_path):
    audit = run_closure_signoff_registry_workflow_v555(Path.cwd(), tmp_path / "out")

    assert audit["overall_status"] == "closure_signoff_registry_contract_ready_signoff_not_claimed"
    assert audit["closure_signoff_registry_contract_ready"] is True
    assert audit["v554_dependency_ready"] is True
    assert audit["signoff_registry_matrix_ready"] is True
    assert audit["closure_signoff_audit_trail_ready"] is True
    assert audit["external_reviewer_signoff_packet_ready"] is True
    assert audit["real_external_reviewer_signoff_ready_count"] == 0
    assert audit["real_closure_signoff_ready_count"] == 0
    assert audit["review_finding_closed_count"] == 0
    assert audit["production_distance_assessment"]["distance"] == "far"
    assert audit["bic_os_distance_assessment"]["distance"] == "very_far"
    assert audit["direct_answer"]["is_production_ready"] == "no_far"
    assert audit["direct_answer"]["is_bic_os_ready"] == "no_very_far"
    assert audit["real_external_reviewer_signoff_ready"] is False
    assert audit["real_external_review_ready"] is False
    assert audit["real_external_pilot_ready"] is False
    assert audit["production_ready"] is False
    assert audit["full_biosdk_ready"] is False
    assert audit["bic_os_phase_locked"] is True


def test_v555_outputs_are_written(tmp_path):
    audit = run_closure_signoff_registry_workflow_v555(Path.cwd(), tmp_path / "workflow")
    paths = write_closure_signoff_registry_outputs_v555(audit, tmp_path / "out")

    assert Path(paths["summary_json"]).exists()
    assert Path(paths["policy_json"]).exists()
    assert Path(paths["registry_matrix_json"]).exists()
    assert Path(paths["audit_trail_json"]).exists()
    assert Path(paths["signoff_packet_json"]).exists()
    assert Path(paths["signoff_gate_json"]).exists()
    assert Path(paths["blocker_register_json"]).exists()
    assert Path(paths["audit_bundle_json"]).exists()
    assert Path(paths["registry_matrix_csv"]).exists()
    assert Path(paths["signoff_gate_csv"]).exists()
    assert "Closure Signoff Registry Contract" in Path(paths["markdown_report"]).read_text(encoding="utf-8")


def test_v555_runner_writes_summary(tmp_path):
    result = run(root=Path.cwd(), out_dir=tmp_path / "out")

    assert result["summary"]["closure_signoff_registry_contract_ready"] is True
    assert (tmp_path / "out" / "V555_CLOSURE_SIGNOFF_REGISTRY_SUMMARY.json").exists()