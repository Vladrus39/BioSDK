from __future__ import annotations

from pathlib import Path

from biogpu.benchmarks.biogpu_v554_remediation_evidence_closure import run
from biogpu.sdk.remediation_evidence_closure_v554 import (
    build_closure_attestation_blocker_register_v554,
    build_closure_attestation_packet_v554,
    build_remediation_evidence_closure_audit_bundle_v554,
    build_remediation_evidence_closure_policy_v554,
    build_remediation_evidence_matrix_v554,
    default_closure_attestation_gate_fixtures_v554,
    default_remediation_evidence_fixtures_v554,
    evaluate_closure_attestation_gate_v554,
    evaluate_remediation_evidence_v554,
    run_closure_attestation_gate_v554,
    run_remediation_evidence_closure_workflow_v554,
    write_remediation_evidence_closure_outputs_v554,
)


def _fake_v553_dependency() -> dict[str, object]:
    return {
        "external_review_finding_triage_contract_ready": True,
        "external_review_finding_triage_audit_sha256": "f" * 64,
        "review_finding_count": 10,
        "real_remediation_approval_count": 0,
        "review_finding_closed_count": 0,
        "remediation_blocker_count": 19,
        "artifact_name": "biogpu_core-5.0.0-py3-none-any.whl",
        "artifact_sha256": "a" * 64,
        "real_review_finding_closure_ready": False,
        "real_external_review_ready": False,
        "real_external_pilot_ready": False,
        "production_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }


def test_v554_policy_is_local_only():
    policy = build_remediation_evidence_closure_policy_v554()

    assert policy["remediation_evidence_closure_policy_ready"] is True
    assert policy["policy"]["requires_v553_finding_triage"] is True
    assert len(policy["policy"]["remediation_evidence_types"]) == 10
    assert len(policy["policy"]["closure_attestation_sections"]) == 7
    assert policy["real_closure_attestation_ready"] is False
    assert policy["bic_os_phase_locked"] is True


def test_v554_evidence_matrix_is_local_but_not_attested():
    dependency = _fake_v553_dependency()
    matrix = build_remediation_evidence_matrix_v554(dependency, default_remediation_evidence_fixtures_v554())

    assert matrix["remediation_evidence_matrix_ready"] is True
    assert matrix["remediation_evidence_record_count"] == 10
    assert matrix["local_remediation_evidence_verified_count"] == 10
    assert matrix["real_closure_attestation_ready_count"] == 0
    assert matrix["finding_closure_attested_count"] == 0
    assert "local_verified_open" in matrix["verification_statuses"]
    assert "external_reviewer_recheck_missing" in matrix["reason_codes"]
    assert "remediation_owner_attestation_missing" in matrix["reason_codes"]
    assert "closure_signature_missing" in matrix["reason_codes"]
    assert "real_closure_attestation_not_ready" in matrix["reason_codes"]
    assert "real_review_finding_closure_not_ready" in matrix["reason_codes"]
    assert "real_external_review_not_ready" in matrix["reason_codes"]
    assert "real_external_pilot_not_ready" in matrix["reason_codes"]
    assert "production_release_not_allowed" in matrix["reason_codes"]
    assert "bic_os_unlock_not_allowed" in matrix["reason_codes"]


def test_v554_evidence_evaluation_blocks_closure_attestation_request():
    dependency = _fake_v553_dependency()
    fixture = [item for item in default_remediation_evidence_fixtures_v554() if item.requests_finding_closure_attestation][0]
    decision = evaluate_remediation_evidence_v554(fixture, dependency)

    assert decision.local_remediation_evidence_verified is True
    assert decision.real_closure_attestation_ready is False
    assert decision.finding_closure_attested is False
    assert "real_closure_attestation_not_ready" in decision.reason_codes
    assert decision.real_external_review_ready is False


def test_v554_attestation_packet_gate_blockers_and_bundle_are_ready():
    dependency = _fake_v553_dependency()
    policy = build_remediation_evidence_closure_policy_v554()
    evidence_matrix = build_remediation_evidence_matrix_v554(dependency)
    closure_packet = build_closure_attestation_packet_v554(dependency, evidence_matrix)
    closure_gate = run_closure_attestation_gate_v554(dependency, evidence_matrix, closure_packet)
    blocker_register = build_closure_attestation_blocker_register_v554(evidence_matrix, closure_gate)
    bundle = build_remediation_evidence_closure_audit_bundle_v554(policy, evidence_matrix, closure_packet, closure_gate, blocker_register)

    assert closure_packet["closure_attestation_packet_ready"] is True
    assert closure_packet["closure_attestation_record_count"] == 10
    assert closure_packet["real_closure_attestation_ready_count"] == 0
    assert closure_packet["finding_closure_attested_count"] == 0
    assert closure_gate["closure_attestation_gate_ready"] is True
    assert closure_gate["accepted_local_closure_stage_count"] == 3
    assert closure_gate["denied_closure_attestation_gate_count"] == 9
    assert blocker_register["closure_attestation_blocker_register_ready"] is True
    assert blocker_register["blocker_count"] == 19
    assert bundle["remediation_evidence_closure_audit_bundle_ready"] is True
    assert bundle["real_external_review_ready"] is False


def test_v554_closure_gate_denies_missing_attestation():
    dependency = _fake_v553_dependency()
    evidence_matrix = build_remediation_evidence_matrix_v554(dependency)
    closure_packet = build_closure_attestation_packet_v554(dependency, evidence_matrix)
    fixture = [item for item in default_closure_attestation_gate_fixtures_v554() if item.gate_id == "missing-closure-attestation"][0]
    decision = evaluate_closure_attestation_gate_v554(fixture, dependency, evidence_matrix, closure_packet)

    assert decision.accepted_for_local_closure_stage is False
    assert "external_reviewer_recheck_missing" in decision.reason_codes
    assert "remediation_owner_attestation_missing" in decision.reason_codes
    assert "closure_signature_missing" in decision.reason_codes
    assert "real_closure_attestation_not_ready" in decision.reason_codes
    assert decision.real_closure_attestation_ready is False


def test_v554_workflow_ready_without_attestation_or_production_claim(tmp_path):
    audit = run_remediation_evidence_closure_workflow_v554(Path.cwd(), tmp_path / "out")

    assert audit["overall_status"] == "remediation_evidence_closure_contract_ready_attestation_not_claimed"
    assert audit["remediation_evidence_closure_contract_ready"] is True
    assert audit["v553_dependency_ready"] is True
    assert audit["remediation_evidence_matrix_ready"] is True
    assert audit["closure_attestation_packet_ready"] is True
    assert audit["real_closure_attestation_ready_count"] == 0
    assert audit["finding_closure_attested_count"] == 0
    assert audit["direct_answer"]["are_real_closure_attestations_ready"] == "no"
    assert audit["real_closure_attestation_ready"] is False
    assert audit["real_review_finding_closure_ready"] is False
    assert audit["real_external_review_ready"] is False
    assert audit["real_external_pilot_ready"] is False
    assert audit["production_ready"] is False
    assert audit["full_biosdk_ready"] is False
    assert audit["bic_os_phase_locked"] is True


def test_v554_outputs_are_written(tmp_path):
    audit = run_remediation_evidence_closure_workflow_v554(Path.cwd(), tmp_path / "workflow")
    paths = write_remediation_evidence_closure_outputs_v554(audit, tmp_path / "out")

    assert Path(paths["summary_json"]).exists()
    assert Path(paths["policy_json"]).exists()
    assert Path(paths["evidence_matrix_json"]).exists()
    assert Path(paths["closure_packet_json"]).exists()
    assert Path(paths["closure_gate_json"]).exists()
    assert Path(paths["blocker_register_json"]).exists()
    assert Path(paths["audit_bundle_json"]).exists()
    assert Path(paths["evidence_matrix_csv"]).exists()
    assert Path(paths["closure_gate_csv"]).exists()
    assert "Remediation Evidence Closure Contract" in Path(paths["markdown_report"]).read_text(encoding="utf-8")


def test_v554_runner_writes_summary(tmp_path):
    result = run(root=Path.cwd(), out_dir=tmp_path / "out")

    assert result["summary"]["remediation_evidence_closure_contract_ready"] is True
    assert (tmp_path / "out" / "V554_REMEDIATION_EVIDENCE_CLOSURE_SUMMARY.json").exists()