from __future__ import annotations

from pathlib import Path

from biogpu.benchmarks.biogpu_v556_external_signoff_transcript_intake import run
from biogpu.sdk.external_signoff_transcript_intake_v556 import (
    build_external_signoff_intake_matrix_v556,
    build_external_signoff_transcript_intake_audit_bundle_v556,
    build_external_signoff_transcript_intake_policy_v556,
    build_signed_closure_transcript_packet_v556,
    build_transcript_acceptance_blocker_register_v556,
    default_signoff_intake_record_fixtures_v556,
    default_transcript_acceptance_gate_fixtures_v556,
    evaluate_signoff_intake_record_v556,
    evaluate_transcript_acceptance_gate_v556,
    run_external_signoff_transcript_intake_workflow_v556,
    run_transcript_acceptance_gate_v556,
    write_external_signoff_transcript_intake_outputs_v556,
)


def _fake_v555_dependency() -> dict[str, object]:
    return {
        "closure_signoff_registry_contract_ready": True,
        "closure_signoff_registry_audit_sha256": "e" * 64,
        "signoff_registry_record_count": 10,
        "real_external_reviewer_signoff_ready_count": 0,
        "real_closure_signoff_ready_count": 0,
        "review_finding_closed_count": 0,
        "artifact_name": "biogpu_core-5.0.0-py3-none-any.whl",
        "artifact_sha256": "a" * 64,
        "real_external_reviewer_signoff_ready": False,
        "real_closure_signoff_ready": False,
        "real_review_finding_closure_ready": False,
        "real_external_review_ready": False,
        "real_external_pilot_ready": False,
        "production_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }


def test_v556_policy_is_local_only_and_requires_signed_material():
    policy = build_external_signoff_transcript_intake_policy_v556()

    assert policy["external_signoff_transcript_intake_policy_ready"] is True
    assert policy["policy"]["requires_v555_signoff_registry"] is True
    assert policy["policy"]["requires_signed_signoff_manifest"] is True
    assert policy["policy"]["requires_signed_closure_transcript"] is True
    assert len(policy["policy"]["signoff_intake_record_types"]) == 10
    assert len(policy["policy"]["transcript_acceptance_sections"]) == 8
    assert policy["real_external_signoff_accepted"] is False
    assert policy["signed_closure_transcript_accepted"] is False
    assert policy["bic_os_phase_locked"] is True


def test_v556_intake_matrix_is_local_but_not_accepted():
    dependency = _fake_v555_dependency()
    matrix = build_external_signoff_intake_matrix_v556(dependency, default_signoff_intake_record_fixtures_v556())

    assert matrix["external_signoff_intake_matrix_ready"] is True
    assert matrix["signoff_intake_record_count"] == 10
    assert matrix["local_signoff_intake_record_ready_count"] == 10
    assert matrix["local_transcript_reference_ready_count"] == 10
    assert matrix["real_external_signoff_accepted_count"] == 0
    assert matrix["signed_closure_transcript_accepted_count"] == 0
    assert matrix["review_finding_closed_count"] == 0
    assert "external_reviewer_identity_payload_missing" in matrix["reason_codes"]
    assert "reviewer_authorization_payload_missing" in matrix["reason_codes"]
    assert "signed_signoff_manifest_payload_missing" in matrix["reason_codes"]
    assert "signed_closure_transcript_payload_missing" in matrix["reason_codes"]
    assert "real_external_signoff_intake_not_accepted" in matrix["reason_codes"]
    assert "signed_closure_transcript_not_accepted" in matrix["reason_codes"]
    assert "real_review_finding_closure_not_ready" in matrix["reason_codes"]
    assert "production_release_not_allowed" in matrix["reason_codes"]
    assert "bic_os_unlock_not_allowed" in matrix["reason_codes"]


def test_v556_record_evaluation_blocks_external_signoff_acceptance():
    dependency = _fake_v555_dependency()
    fixture = [item for item in default_signoff_intake_record_fixtures_v556() if item.requests_real_external_signoff_acceptance][0]
    decision = evaluate_signoff_intake_record_v556(fixture, dependency)

    assert decision.local_signoff_intake_record_ready is True
    assert decision.local_transcript_reference_ready is True
    assert decision.real_external_signoff_accepted is False
    assert decision.signed_closure_transcript_accepted is False
    assert decision.review_finding_closed is False
    assert "real_external_signoff_intake_not_accepted" in decision.reason_codes
    assert "signed_signoff_manifest_payload_missing" in decision.reason_codes


def test_v556_transcript_packet_gate_blockers_and_bundle_are_ready():
    dependency = _fake_v555_dependency()
    policy = build_external_signoff_transcript_intake_policy_v556()
    intake_matrix = build_external_signoff_intake_matrix_v556(dependency)
    transcript_packet = build_signed_closure_transcript_packet_v556(dependency, intake_matrix)
    transcript_gate = run_transcript_acceptance_gate_v556(dependency, intake_matrix, transcript_packet)
    blocker_register = build_transcript_acceptance_blocker_register_v556(intake_matrix, transcript_gate)
    bundle = build_external_signoff_transcript_intake_audit_bundle_v556(policy, intake_matrix, transcript_packet, transcript_gate, blocker_register)

    assert transcript_packet["signed_closure_transcript_packet_ready"] is True
    assert transcript_packet["transcript_packet_section_count"] == 8
    assert transcript_packet["local_transcript_packet_section_ready_count"] == 8
    assert transcript_packet["real_external_signoff_accepted_count"] == 0
    assert transcript_packet["signed_closure_transcript_accepted_count"] == 0
    assert transcript_gate["transcript_acceptance_gate_ready"] is True
    assert transcript_gate["accepted_local_intake_stage_count"] == 3
    assert transcript_gate["denied_transcript_acceptance_gate_count"] == 10
    assert blocker_register["transcript_acceptance_blocker_register_ready"] is True
    assert blocker_register["blocker_count"] == 20
    assert bundle["external_signoff_transcript_intake_audit_bundle_ready"] is True
    assert bundle["real_external_review_ready"] is False


def test_v556_gate_denies_signed_transcript_acceptance_request():
    dependency = _fake_v555_dependency()
    intake_matrix = build_external_signoff_intake_matrix_v556(dependency)
    transcript_packet = build_signed_closure_transcript_packet_v556(dependency, intake_matrix)
    fixture = [item for item in default_transcript_acceptance_gate_fixtures_v556() if item.gate_id == "signed-transcript-acceptance-request"][0]
    decision = evaluate_transcript_acceptance_gate_v556(fixture, dependency, intake_matrix, transcript_packet)

    assert decision.accepted_for_local_intake_stage is False
    assert "external_reviewer_identity_payload_missing" in decision.reason_codes
    assert "reviewer_authorization_payload_missing" in decision.reason_codes
    assert "signed_signoff_manifest_payload_missing" in decision.reason_codes
    assert "signed_closure_transcript_payload_missing" in decision.reason_codes
    assert "closure_timestamp_payload_missing" in decision.reason_codes
    assert "owner_counter_attestation_payload_missing" in decision.reason_codes
    assert "immutable_transcript_anchor_payload_missing" in decision.reason_codes
    assert "signed_closure_transcript_not_accepted" in decision.reason_codes
    assert "real_review_finding_closure_not_ready" in decision.reason_codes
    assert decision.signed_closure_transcript_accepted is False


def test_v556_workflow_ready_without_real_acceptance_or_production_claim(tmp_path):
    audit = run_external_signoff_transcript_intake_workflow_v556(Path.cwd(), tmp_path / "out")

    assert audit["overall_status"] == "external_signoff_transcript_intake_contract_ready_signoff_not_accepted"
    assert audit["external_signoff_transcript_intake_contract_ready"] is True
    assert audit["v555_dependency_ready"] is True
    assert audit["external_signoff_intake_matrix_ready"] is True
    assert audit["signed_closure_transcript_packet_ready"] is True
    assert audit["transcript_acceptance_gate_ready"] is True
    assert audit["real_external_signoff_accepted_count"] == 0
    assert audit["signed_closure_transcript_accepted_count"] == 0
    assert audit["review_finding_closed_count"] == 0
    assert audit["production_distance_assessment"]["distance"] == "far"
    assert audit["bic_os_distance_assessment"]["distance"] == "very_far"
    assert audit["direct_answer"]["is_production_ready"] == "no_far"
    assert audit["direct_answer"]["is_bic_os_ready"] == "no_very_far"
    assert audit["real_external_signoff_intake_ready"] is False
    assert audit["real_external_signoff_accepted"] is False
    assert audit["signed_closure_transcript_accepted"] is False
    assert audit["real_external_review_ready"] is False
    assert audit["real_external_pilot_ready"] is False
    assert audit["production_ready"] is False
    assert audit["full_biosdk_ready"] is False
    assert audit["bic_os_phase_locked"] is True


def test_v556_outputs_are_written(tmp_path):
    audit = run_external_signoff_transcript_intake_workflow_v556(Path.cwd(), tmp_path / "workflow")
    paths = write_external_signoff_transcript_intake_outputs_v556(audit, tmp_path / "out")

    assert Path(paths["summary_json"]).exists()
    assert Path(paths["policy_json"]).exists()
    assert Path(paths["intake_matrix_json"]).exists()
    assert Path(paths["transcript_packet_json"]).exists()
    assert Path(paths["transcript_gate_json"]).exists()
    assert Path(paths["blocker_register_json"]).exists()
    assert Path(paths["audit_bundle_json"]).exists()
    assert Path(paths["intake_matrix_csv"]).exists()
    assert Path(paths["transcript_gate_csv"]).exists()
    assert "External Signoff Transcript Intake Contract" in Path(paths["markdown_report"]).read_text(encoding="utf-8")


def test_v556_runner_writes_summary(tmp_path):
    result = run(root=Path.cwd(), out_dir=tmp_path / "out")

    assert result["summary"]["external_signoff_transcript_intake_contract_ready"] is True
    assert (tmp_path / "out" / "V556_EXTERNAL_SIGNOFF_TRANSCRIPT_INTAKE_SUMMARY.json").exists()