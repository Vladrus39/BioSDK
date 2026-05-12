from __future__ import annotations

from pathlib import Path

from biogpu.benchmarks.biogpu_v543_release_approval_revocation import run
from biogpu.sdk.release_approval_v543 import (
    build_release_approval_policy_v543,
    build_release_decision_record_v543,
    build_release_revocation_policy_v543,
    default_release_review_fixtures_v543,
    evaluate_release_review_v543,
    run_release_approval_matrix_v543,
    run_release_approval_revocation_workflow_v543,
    run_release_revocation_drill_v543,
    write_release_approval_revocation_outputs_v543,
)


def test_v543_policy_allows_only_local_candidate_handoff():
    policy = build_release_approval_policy_v543()

    assert policy["release_approval_policy_ready"] is True
    assert policy["policy"]["local_candidate_handoff_allowed"] is True
    assert policy["policy"]["production_distribution_allowed"] is False
    assert policy["policy"]["full_biosdk_claim_allowed"] is False
    assert policy["production_release_ready"] is False


def test_v543_approval_matrix_allows_required_roles_and_denies_overclaims():
    matrix = run_release_approval_matrix_v543(default_release_review_fixtures_v543())

    assert matrix["release_approval_matrix_ready"] is True
    assert matrix["allowed_local_review_count"] == 4
    assert matrix["denied_review_count"] == 6
    assert set(matrix["allowed_roles"]) == {"release_manager", "provenance_reviewer", "safety_reviewer", "ops_reviewer"}
    assert "production_distribution_not_allowed" in matrix["reason_codes"]
    assert "full_biosdk_claim_not_allowed" in matrix["reason_codes"]
    assert "live_actuation_not_allowed" in matrix["reason_codes"]


def test_v543_review_denies_missing_boundary():
    fixture = [review for review in default_release_review_fixtures_v543() if review.review_id == "missing-boundary"][0]
    decision = evaluate_release_review_v543(fixture)

    assert decision.allowed_for_local_candidate is False
    assert "claim_boundary_not_acknowledged" in decision.reason_codes
    assert decision.production_distribution_ready is False


def test_v543_revocation_policy_and_drill_are_ready():
    policy = build_release_revocation_policy_v543()
    drill = run_release_revocation_drill_v543(policy)

    assert policy["release_revocation_policy_ready"] is True
    assert drill["release_revocation_drill_ready"] is True
    assert drill["revoked_count"] == 4
    assert drill["local_handoff_blocked_count"] == 4
    assert drill["production_registry_yank_ready"] is False


def test_v543_release_decision_approves_local_only():
    matrix = run_release_approval_matrix_v543(default_release_review_fixtures_v543())
    revocation_policy = build_release_revocation_policy_v543()
    drill = run_release_revocation_drill_v543(revocation_policy)
    decision = build_release_decision_record_v543(
        {"signed_artifact_provenance_contract_ready": True, "artifact_name": "test.whl", "artifact_sha256": "a" * 64, "provenance_audit_sha256": "b" * 64},
        matrix,
        drill,
    )

    assert decision["local_candidate_handoff_approved"] is True
    assert decision["production_release_approved"] is False
    assert decision["full_biosdk_claim_approved"] is False
    assert len(decision["release_decision_sha256"]) == 64


def test_v543_workflow_ready_without_production_claims(tmp_path):
    audit = run_release_approval_revocation_workflow_v543(Path.cwd(), tmp_path / "out")

    assert audit["overall_status"] == "release_approval_revocation_contract_ready_production_not_claimed"
    assert audit["release_approval_revocation_contract_ready"] is True
    assert audit["v542_dependency_ready"] is True
    assert audit["local_candidate_handoff_approved"] is True
    assert audit["production_release_approved"] is False
    assert audit["production_distribution_ready"] is False
    assert audit["full_biosdk_ready"] is False
    assert audit["bic_os_phase_locked"] is True


def test_v543_outputs_are_written(tmp_path):
    audit = run_release_approval_revocation_workflow_v543(Path.cwd(), tmp_path / "workflow")
    paths = write_release_approval_revocation_outputs_v543(audit, tmp_path / "out")

    assert Path(paths["summary_json"]).exists()
    assert Path(paths["approval_policy_json"]).exists()
    assert Path(paths["approval_matrix_json"]).exists()
    assert Path(paths["revocation_policy_json"]).exists()
    assert Path(paths["revocation_drill_json"]).exists()
    assert Path(paths["release_decision_json"]).exists()
    assert Path(paths["approval_matrix_csv"]).exists()
    assert Path(paths["revocation_events_csv"]).exists()
    assert "Release Approval and Revocation Contract" in Path(paths["markdown_report"]).read_text(encoding="utf-8")


def test_v543_runner_writes_summary(tmp_path):
    result = run(root=Path.cwd(), out_dir=tmp_path / "out")

    assert result["summary"]["release_approval_revocation_contract_ready"] is True
    assert (tmp_path / "out" / "V543_RELEASE_APPROVAL_REVOCATION_SUMMARY.json").exists()