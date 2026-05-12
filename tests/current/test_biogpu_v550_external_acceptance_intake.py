from __future__ import annotations

from pathlib import Path

from biogpu.benchmarks.biogpu_v550_external_acceptance_intake import run
from biogpu.sdk.external_acceptance_intake_v550 import (
    build_external_acceptance_audit_bundle_v550,
    build_external_acceptance_evidence_matrix_v550,
    build_external_acceptance_evidence_schema_v550,
    build_external_acceptance_intake_policy_v550,
    build_external_acceptance_packet_v550,
    build_real_pilot_intake_blocker_register_v550,
    default_external_acceptance_evidence_fixtures_v550,
    default_real_pilot_intake_gate_fixtures_v550,
    evaluate_external_acceptance_evidence_v550,
    evaluate_real_pilot_intake_gate_v550,
    run_external_acceptance_intake_workflow_v550,
    run_real_pilot_intake_gate_v550,
    write_external_acceptance_intake_outputs_v550,
)


def _fake_v549_dependency() -> dict[str, object]:
    return {
        "production_readiness_gap_contract_ready": True,
        "artifact_name": "biogpu_core-5.0.0-py3-none-any.whl",
        "artifact_sha256": "a" * 64,
        "production_readiness_gap_audit_sha256": "b" * 64,
        "open_gap_count": 12,
        "production_ready_domain_count": 0,
        "production_ready": False,
        "real_external_pilot_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }


def test_v550_policy_and_schema_are_local_only():
    policy = build_external_acceptance_intake_policy_v550()
    schema = build_external_acceptance_evidence_schema_v550(policy)

    assert policy["external_acceptance_intake_policy_ready"] is True
    assert policy["policy"]["requires_v549_readiness_gap_contract"] is True
    assert schema["external_acceptance_evidence_schema_ready"] is True
    assert len(schema["required_evidence_types"]) == 10
    assert policy["real_external_pilot_ready"] is False
    assert schema["bic_os_phase_locked"] is True


def test_v550_evidence_matrix_validates_schema_but_blocks_real_acceptance():
    dependency = _fake_v549_dependency()
    matrix = build_external_acceptance_evidence_matrix_v550(dependency, default_external_acceptance_evidence_fixtures_v550())

    assert matrix["external_acceptance_evidence_matrix_ready"] is True
    assert matrix["evidence_record_count"] == 10
    assert matrix["schema_valid_record_count"] == 10
    assert matrix["real_acceptance_ready_count"] == 0
    assert "real_submitter_identity_missing" in matrix["reason_codes"]
    assert "external_signature_missing" in matrix["reason_codes"]
    assert "real_pilot_request_blocked" in matrix["reason_codes"]
    assert "production_release_not_allowed" in matrix["reason_codes"]
    assert "bic_os_unlock_not_allowed" in matrix["reason_codes"]


def test_v550_evidence_evaluation_blocks_live_pilot_request():
    dependency = _fake_v549_dependency()
    fixture = [item for item in default_external_acceptance_evidence_fixtures_v550() if item.requests_live_pilot][0]
    decision = evaluate_external_acceptance_evidence_v550(fixture, dependency)

    assert decision.schema_record_valid is True
    assert decision.real_acceptance_record_ready is False
    assert "real_pilot_request_blocked" in decision.reason_codes
    assert decision.real_external_pilot_ready is False


def test_v550_intake_gate_packet_blocker_register_and_bundle_are_ready():
    dependency = _fake_v549_dependency()
    policy = build_external_acceptance_intake_policy_v550()
    schema = build_external_acceptance_evidence_schema_v550(policy)
    evidence_matrix = build_external_acceptance_evidence_matrix_v550(dependency)
    intake_gate = run_real_pilot_intake_gate_v550(dependency, evidence_matrix)
    packet = build_external_acceptance_packet_v550(dependency, schema, evidence_matrix, intake_gate)
    blocker_register = build_real_pilot_intake_blocker_register_v550(evidence_matrix, intake_gate)
    bundle = build_external_acceptance_audit_bundle_v550(policy, schema, evidence_matrix, intake_gate, packet, blocker_register)

    assert intake_gate["real_pilot_intake_gate_ready"] is True
    assert intake_gate["accepted_local_intake_stage_count"] == 3
    assert intake_gate["denied_intake_gate_count"] == 9
    assert packet["external_acceptance_packet_ready"] is True
    assert packet["packet_record_count"] == 10
    assert blocker_register["real_pilot_intake_blocker_register_ready"] is True
    assert blocker_register["blocker_count"] == 19
    assert bundle["external_acceptance_audit_bundle_ready"] is True
    assert bundle["real_external_pilot_ready"] is False


def test_v550_intake_gate_denies_production_release_request():
    dependency = _fake_v549_dependency()
    evidence_matrix = build_external_acceptance_evidence_matrix_v550(dependency)
    fixture = [item for item in default_real_pilot_intake_gate_fixtures_v550() if item.gate_id == "production-release-request"][0]
    decision = evaluate_real_pilot_intake_gate_v550(fixture, dependency, evidence_matrix)

    assert decision.accepted_for_local_intake_stage is False
    assert "production_release_not_allowed" in decision.reason_codes
    assert decision.production_release_ready is False


def test_v550_workflow_ready_without_real_pilot_or_production_claim(tmp_path):
    audit = run_external_acceptance_intake_workflow_v550(Path.cwd(), tmp_path / "out")

    assert audit["overall_status"] == "external_acceptance_intake_contract_ready_pilot_not_claimed"
    assert audit["external_acceptance_intake_contract_ready"] is True
    assert audit["v549_dependency_ready"] is True
    assert audit["external_acceptance_evidence_schema_ready"] is True
    assert audit["real_pilot_intake_gate_ready"] is True
    assert audit["real_acceptance_ready_count"] == 0
    assert audit["direct_answer"]["are_real_external_acceptance_records_ready"] == "no"
    assert audit["real_external_pilot_ready"] is False
    assert audit["production_ready"] is False
    assert audit["full_biosdk_ready"] is False
    assert audit["bic_os_phase_locked"] is True


def test_v550_outputs_are_written(tmp_path):
    audit = run_external_acceptance_intake_workflow_v550(Path.cwd(), tmp_path / "workflow")
    paths = write_external_acceptance_intake_outputs_v550(audit, tmp_path / "out")

    assert Path(paths["summary_json"]).exists()
    assert Path(paths["policy_json"]).exists()
    assert Path(paths["schema_json"]).exists()
    assert Path(paths["evidence_matrix_json"]).exists()
    assert Path(paths["intake_gate_json"]).exists()
    assert Path(paths["packet_json"]).exists()
    assert Path(paths["blocker_register_json"]).exists()
    assert Path(paths["audit_bundle_json"]).exists()
    assert Path(paths["evidence_matrix_csv"]).exists()
    assert Path(paths["intake_gate_csv"]).exists()
    assert "External Acceptance Intake Contract" in Path(paths["markdown_report"]).read_text(encoding="utf-8")


def test_v550_runner_writes_summary(tmp_path):
    result = run(root=Path.cwd(), out_dir=tmp_path / "out")

    assert result["summary"]["external_acceptance_intake_contract_ready"] is True
    assert (tmp_path / "out" / "V550_EXTERNAL_ACCEPTANCE_INTAKE_SUMMARY.json").exists()