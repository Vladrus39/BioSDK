from __future__ import annotations

from pathlib import Path

from biogpu.benchmarks.biogpu_v549_production_readiness_gap import run
from biogpu.sdk.production_readiness_gap_v549 import (
    build_production_readiness_audit_bundle_v549,
    build_production_readiness_gap_matrix_v549,
    build_production_readiness_gap_policy_v549,
    build_readiness_blocker_register_v549,
    build_staged_pilot_acceptance_plan_v549,
    default_pilot_acceptance_fixtures_v549,
    default_production_readiness_gap_fixtures_v549,
    evaluate_pilot_acceptance_v549,
    evaluate_production_readiness_gap_v549,
    run_production_readiness_gap_workflow_v549,
    run_staged_pilot_acceptance_matrix_v549,
    write_production_readiness_gap_outputs_v549,
)


def _fake_v548_dependency() -> dict[str, object]:
    return {
        "release_operations_handoff_contract_ready": True,
        "artifact_name": "biogpu_core-5.0.0-py3-none-any.whl",
        "artifact_sha256": "a" * 64,
        "release_operations_handoff_audit_sha256": "b" * 64,
        "production_release_ready": False,
        "production_operations_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }


def test_v549_policy_is_local_only():
    policy = build_production_readiness_gap_policy_v549()

    assert policy["production_readiness_gap_policy_ready"] is True
    assert policy["policy"]["requires_v548_release_ops_handoff"] is True
    assert policy["production_ready"] is False
    assert policy["full_biosdk_ready"] is False
    assert policy["bic_os_phase_locked"] is True


def test_v549_gap_matrix_keeps_all_production_domains_blocked():
    dependency = _fake_v548_dependency()
    matrix = build_production_readiness_gap_matrix_v549(dependency, default_production_readiness_gap_fixtures_v549())

    assert matrix["production_readiness_gap_matrix_ready"] is True
    assert matrix["domain_count"] == 12
    assert matrix["open_gap_count"] == 12
    assert matrix["production_ready_domain_count"] == 0
    assert "real_input_missing" in matrix["reason_codes"]
    assert "production_ready_claim_blocked" in matrix["reason_codes"]
    assert "bic_os_unlock_blocked" in matrix["reason_codes"]


def test_v549_gap_evaluation_blocks_os_unlock_attempt():
    dependency = _fake_v548_dependency()
    os_fixture = [fixture for fixture in default_production_readiness_gap_fixtures_v549() if fixture.domain_id == "os_service_supervision"][0]
    decision = evaluate_production_readiness_gap_v549(os_fixture, dependency)

    assert decision.production_ready_for_domain is False
    assert decision.gap_open is True
    assert "bic_os_unlock_blocked" in decision.reason_codes
    assert decision.bic_os_phase_locked is True


def test_v549_pilot_matrix_plan_blocker_register_and_bundle_are_ready():
    dependency = _fake_v548_dependency()
    policy = build_production_readiness_gap_policy_v549()
    gap_matrix = build_production_readiness_gap_matrix_v549(dependency)
    pilot_matrix = run_staged_pilot_acceptance_matrix_v549(dependency, gap_matrix)
    pilot_plan = build_staged_pilot_acceptance_plan_v549(gap_matrix, pilot_matrix)
    blocker_register = build_readiness_blocker_register_v549(gap_matrix)
    bundle = build_production_readiness_audit_bundle_v549(policy, gap_matrix, pilot_matrix, pilot_plan, blocker_register)

    assert pilot_matrix["staged_pilot_acceptance_matrix_ready"] is True
    assert pilot_matrix["accepted_local_pilot_stage_count"] == 4
    assert pilot_matrix["denied_pilot_stage_count"] == 8
    assert pilot_plan["staged_pilot_acceptance_plan_ready"] is True
    assert blocker_register["readiness_blocker_register_ready"] is True
    assert blocker_register["blocker_count"] == 12
    assert bundle["production_readiness_audit_bundle_ready"] is True
    assert bundle["production_ready"] is False


def test_v549_pilot_evaluation_denies_production_release_request():
    dependency = _fake_v548_dependency()
    gap_matrix = build_production_readiness_gap_matrix_v549(dependency)
    production = [fixture for fixture in default_pilot_acceptance_fixtures_v549() if fixture.stage_id == "production-release-request"][0]
    decision = evaluate_pilot_acceptance_v549(production, dependency, gap_matrix)

    assert decision.accepted_for_local_pilot_stage is False
    assert "production_release_not_allowed" in decision.reason_codes
    assert decision.production_release_ready is False


def test_v549_workflow_ready_without_production_or_external_pilot_claim(tmp_path):
    audit = run_production_readiness_gap_workflow_v549(Path.cwd(), tmp_path / "out")

    assert audit["overall_status"] == "production_readiness_gap_contract_ready_production_not_claimed"
    assert audit["production_readiness_gap_contract_ready"] is True
    assert audit["v548_dependency_ready"] is True
    assert audit["production_readiness_gap_matrix_ready"] is True
    assert audit["staged_pilot_acceptance_plan_ready"] is True
    assert audit["open_gap_count"] == 12
    assert audit["production_ready_domain_count"] == 0
    assert audit["direct_answer"]["do_we_still_need_many_layers_before_production_and_os"] == "yes"
    assert audit["production_ready"] is False
    assert audit["real_external_pilot_ready"] is False
    assert audit["full_biosdk_ready"] is False
    assert audit["bic_os_phase_locked"] is True


def test_v549_outputs_are_written(tmp_path):
    audit = run_production_readiness_gap_workflow_v549(Path.cwd(), tmp_path / "workflow")
    paths = write_production_readiness_gap_outputs_v549(audit, tmp_path / "out")

    assert Path(paths["summary_json"]).exists()
    assert Path(paths["policy_json"]).exists()
    assert Path(paths["gap_matrix_json"]).exists()
    assert Path(paths["pilot_matrix_json"]).exists()
    assert Path(paths["pilot_plan_json"]).exists()
    assert Path(paths["blocker_register_json"]).exists()
    assert Path(paths["audit_bundle_json"]).exists()
    assert Path(paths["gap_matrix_csv"]).exists()
    assert Path(paths["pilot_matrix_csv"]).exists()
    assert "Production Readiness Gap Contract" in Path(paths["markdown_report"]).read_text(encoding="utf-8")


def test_v549_runner_writes_summary(tmp_path):
    result = run(root=Path.cwd(), out_dir=tmp_path / "out")

    assert result["summary"]["production_readiness_gap_contract_ready"] is True
    assert (tmp_path / "out" / "V549_PRODUCTION_READINESS_GAP_SUMMARY.json").exists()