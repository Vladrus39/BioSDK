from __future__ import annotations

from pathlib import Path

from biogpu.benchmarks.biogpu_v545_recipient_onboarding_audit import run
from biogpu.sdk.recipient_onboarding_audit_v545 import (
    build_recipient_access_log_v545,
    build_recipient_audit_bundle_v545,
    build_recipient_onboarding_policy_v545,
    default_recipient_fixtures_v545,
    evaluate_recipient_onboarding_v545,
    run_access_expiry_probe_v545,
    run_recipient_onboarding_audit_workflow_v545,
    run_recipient_onboarding_matrix_v545,
    write_recipient_onboarding_audit_outputs_v545,
)


def _fake_v544_dependency() -> dict[str, object]:
    return {
        "private_registry_handoff_contract_ready": True,
        "local_registry_index_ready": True,
        "artifact_name": "biogpu_core-5.0.0-py3-none-any.whl",
        "artifact_sha256": "a" * 64,
        "private_registry_handoff_audit_sha256": "b" * 64,
        "real_recipient_onboarding_ready": False,
        "live_private_registry_ready": False,
        "production_distribution_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }


def test_v545_policy_is_local_only():
    policy = build_recipient_onboarding_policy_v545()

    assert policy["recipient_onboarding_policy_ready"] is True
    assert policy["policy"]["requires_named_local_account"] is True
    assert policy["policy"]["live_registry_accounts_configured"] is False
    assert policy["real_recipient_onboarding_ready"] is False
    assert policy["full_biosdk_ready"] is False


def test_v545_matrix_allows_and_denies_expected_cases():
    dependency = _fake_v544_dependency()
    matrix = run_recipient_onboarding_matrix_v545(dependency, default_recipient_fixtures_v545(str(dependency["artifact_sha256"])))

    assert matrix["recipient_onboarding_matrix_ready"] is True
    assert matrix["allowed_recipient_count"] == 3
    assert matrix["denied_recipient_count"] == 12
    assert "named_local_account_missing" in matrix["reason_codes"]
    assert "access_window_expired_or_missing" in matrix["reason_codes"]
    assert "live_private_registry_not_ready" in matrix["reason_codes"]
    assert "production_distribution_not_allowed" in matrix["reason_codes"]


def test_v545_evaluation_denies_revoked_recipient():
    dependency = _fake_v544_dependency()
    revoked = [fixture for fixture in default_recipient_fixtures_v545(str(dependency["artifact_sha256"])) if fixture.recipient_id == "revoked-recipient"][0]
    decision = evaluate_recipient_onboarding_v545(revoked, dependency)

    assert decision.onboarded_for_local_handoff is False
    assert "recipient_revoked" in decision.reason_codes
    assert decision.real_recipient_onboarding_ready is False


def test_v545_access_log_expiry_probe_and_bundle_are_ready():
    dependency = _fake_v544_dependency()
    policy = build_recipient_onboarding_policy_v545()
    matrix = run_recipient_onboarding_matrix_v545(dependency)
    access_log = build_recipient_access_log_v545(dependency, matrix)
    expiry_probe = run_access_expiry_probe_v545(dependency, matrix)
    bundle = build_recipient_audit_bundle_v545(policy, matrix, access_log, expiry_probe)

    assert access_log["recipient_access_log_ready"] is True
    assert access_log["event_count"] == 3
    assert expiry_probe["access_expiry_probe_ready"] is True
    assert bundle["recipient_audit_bundle_ready"] is True
    assert bundle["live_private_registry_ready"] is False


def test_v545_workflow_ready_without_real_onboarding_claim(tmp_path):
    audit = run_recipient_onboarding_audit_workflow_v545(Path.cwd(), tmp_path / "out")

    assert audit["overall_status"] == "recipient_onboarding_audit_contract_ready_production_not_claimed"
    assert audit["recipient_onboarding_audit_contract_ready"] is True
    assert audit["v544_dependency_ready"] is True
    assert audit["recipient_access_log_ready"] is True
    assert audit["access_expiry_probe_ready"] is True
    assert audit["real_recipient_onboarding_ready"] is False
    assert audit["live_private_registry_ready"] is False
    assert audit["production_distribution_ready"] is False
    assert audit["full_biosdk_ready"] is False
    assert audit["bic_os_phase_locked"] is True


def test_v545_outputs_are_written(tmp_path):
    audit = run_recipient_onboarding_audit_workflow_v545(Path.cwd(), tmp_path / "workflow")
    paths = write_recipient_onboarding_audit_outputs_v545(audit, tmp_path / "out")

    assert Path(paths["summary_json"]).exists()
    assert Path(paths["policy_json"]).exists()
    assert Path(paths["matrix_json"]).exists()
    assert Path(paths["access_log_json"]).exists()
    assert Path(paths["expiry_probe_json"]).exists()
    assert Path(paths["audit_bundle_json"]).exists()
    assert Path(paths["matrix_csv"]).exists()
    assert Path(paths["access_log_csv"]).exists()
    assert "Recipient Onboarding Audit Contract" in Path(paths["markdown_report"]).read_text(encoding="utf-8")


def test_v545_runner_writes_summary(tmp_path):
    result = run(root=Path.cwd(), out_dir=tmp_path / "out")

    assert result["summary"]["recipient_onboarding_audit_contract_ready"] is True
    assert (tmp_path / "out" / "V545_RECIPIENT_ONBOARDING_AUDIT_SUMMARY.json").exists()