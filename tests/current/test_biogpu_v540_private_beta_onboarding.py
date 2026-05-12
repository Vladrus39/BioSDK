from __future__ import annotations

from pathlib import Path

from biogpu.benchmarks.biogpu_v540_private_beta_onboarding import run
from biogpu.sdk.private_beta_onboarding_v540 import (
    authorize_beta_participant_v540,
    build_beta_onboarding_artifacts_v540,
    build_private_beta_program_contract_v540,
    build_release_operations_contract_v540,
    default_beta_participant_fixtures_v540,
    run_beta_onboarding_decision_matrix_v540,
    run_private_beta_onboarding_contract_workflow_v540,
    write_private_beta_onboarding_outputs_v540,
)


def test_v540_program_contract_is_local_only():
    contract = build_private_beta_program_contract_v540(Path.cwd())

    assert contract["artifact_contract_ready"] is True
    assert contract["external_beta_ready"] is False
    assert contract["production_distribution_ready"] is False
    assert contract["full_biosdk_ready"] is False
    assert len(contract["contract_sha256"]) == 64


def test_v540_release_operations_contract_keeps_registry_blocked():
    contract = build_release_operations_contract_v540(Path.cwd())

    channels = {channel["name"]: channel for channel in contract["release_channels"]}
    assert contract["release_operations_contract_ready"] is True
    assert channels["local_wheel_handoff"]["ready"] is True
    assert channels["public_package_index"]["ready"] is False
    assert contract["public_distribution_ready"] is False


def test_v540_onboarding_artifacts_are_complete_without_production_claims():
    artifacts = build_beta_onboarding_artifacts_v540()
    required = [artifact for artifact in artifacts if artifact["required_before_handoff"]]

    assert len(required) == 6
    assert all(artifact["local_only_ready"] for artifact in required)
    assert not any(artifact["production_ready"] for artifact in artifacts)


def test_v540_participant_matrix_allows_and_denies_expected_cases():
    matrix = run_beta_onboarding_decision_matrix_v540(default_beta_participant_fixtures_v540())

    assert matrix["participant_gate_ready"] is True
    assert matrix["allowed_count"] == 3
    assert matrix["denied_count"] == 4
    assert "missing_data_use_agreement" in matrix["reason_codes"]
    assert "live_actuation_not_allowed" in matrix["reason_codes"]
    assert "production_sla_not_available" in matrix["reason_codes"]
    assert matrix["live_actuation_enabled"] is False


def test_v540_authorization_blocks_live_actuation():
    live_request = [fixture for fixture in default_beta_participant_fixtures_v540() if fixture.participant_id == "live-request-01"][0]
    decision = authorize_beta_participant_v540(live_request)

    assert decision.allowed is False
    assert "live_actuation_not_allowed" in decision.reason_codes
    assert decision.live_actuation_enabled is False


def test_v540_workflow_ready_without_claiming_external_beta(tmp_path):
    audit = run_private_beta_onboarding_contract_workflow_v540(Path.cwd(), tmp_path / "out")

    assert audit["overall_status"] == "private_beta_onboarding_contract_ready_release_not_claimed"
    assert audit["private_beta_onboarding_contract_ready"] is True
    assert audit["v539_dependency_ready"] is True
    assert audit["release_operations_contract_ready"] is True
    assert audit["participant_gate_ready"] is True
    assert audit["external_beta_ready"] is False
    assert audit["full_biosdk_ready"] is False
    assert audit["bic_os_phase_locked"] is True


def test_v540_outputs_are_written(tmp_path):
    audit = run_private_beta_onboarding_contract_workflow_v540(Path.cwd(), tmp_path / "workflow")
    paths = write_private_beta_onboarding_outputs_v540(audit, tmp_path / "out")

    assert Path(paths["summary_json"]).exists()
    assert Path(paths["program_contract_json"]).exists()
    assert Path(paths["artifacts_json"]).exists()
    assert Path(paths["release_operations_json"]).exists()
    assert Path(paths["participant_matrix_json"]).exists()
    assert Path(paths["participant_matrix_csv"]).exists()
    assert "Private Beta Onboarding Contract" in Path(paths["markdown_report"]).read_text(encoding="utf-8")


def test_v540_runner_writes_summary(tmp_path):
    result = run(root=Path.cwd(), out_dir=tmp_path / "out")

    assert result["summary"]["private_beta_onboarding_contract_ready"] is True
    assert (tmp_path / "out" / "V540_PRIVATE_BETA_ONBOARDING_SUMMARY.json").exists()