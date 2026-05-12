from __future__ import annotations

from pathlib import Path

from biogpu.benchmarks.biogpu_v546_private_registry_auth_feed import run
from biogpu.sdk.private_registry_auth_feed_v546 import (
    build_auth_feed_audit_bundle_v546,
    build_expiring_feed_manifest_v546,
    build_private_registry_auth_feed_policy_v546,
    build_registry_log_export_contract_v546,
    default_auth_feed_fixtures_v546,
    evaluate_auth_feed_request_v546,
    run_auth_feed_matrix_v546,
    run_expiring_feed_probe_v546,
    run_private_registry_auth_feed_workflow_v546,
    write_private_registry_auth_feed_outputs_v546,
)


def _fake_v545_dependency() -> dict[str, object]:
    artifact_sha256 = "a" * 64
    return {
        "recipient_onboarding_audit_contract_ready": True,
        "artifact_name": "biogpu_core-5.0.0-py3-none-any.whl",
        "artifact_sha256": artifact_sha256,
        "recipient_access_log": {
            "recipient_access_log_ready": True,
            "access_events": [
                {"recipient_id": "recipient-alpha", "local_access_grant_id": "local-grant-recipient-alpha"},
                {"recipient_id": "recipient-beta", "local_access_grant_id": "local-grant-recipient-beta"},
                {"recipient_id": "recipient-provenance", "local_access_grant_id": "local-grant-recipient-provenance"},
            ],
        },
        "real_recipient_onboarding_ready": False,
        "live_private_registry_ready": False,
        "production_distribution_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }


def test_v546_policy_is_local_only():
    policy = build_private_registry_auth_feed_policy_v546()

    assert policy["private_registry_auth_feed_policy_ready"] is True
    assert policy["policy"]["requires_local_token_signature"] is True
    assert policy["policy"]["live_registry_endpoint_configured"] is False
    assert policy["live_private_registry_ready"] is False
    assert policy["full_biosdk_ready"] is False


def test_v546_auth_feed_matrix_allows_and_denies_expected_cases():
    dependency = _fake_v545_dependency()
    matrix = run_auth_feed_matrix_v546(dependency, default_auth_feed_fixtures_v546(dependency))

    assert matrix["auth_feed_matrix_ready"] is True
    assert matrix["allowed_feed_count"] == 3
    assert matrix["denied_feed_count"] == 10
    assert "recipient_local_grant_missing" in matrix["reason_codes"]
    assert "local_token_signature_invalid" in matrix["reason_codes"]
    assert "feed_expired" in matrix["reason_codes"]
    assert "production_distribution_not_allowed" in matrix["reason_codes"]


def test_v546_evaluation_denies_invalid_signature():
    dependency = _fake_v545_dependency()
    invalid = [fixture for fixture in default_auth_feed_fixtures_v546(dependency) if fixture.request_id == "invalid-signature"][0]
    decision = evaluate_auth_feed_request_v546(invalid, dependency)

    assert decision.authenticated_for_local_feed is False
    assert "local_token_signature_invalid" in decision.reason_codes
    assert decision.live_private_registry_ready is False


def test_v546_manifest_expiry_probe_log_export_and_bundle_are_ready():
    dependency = _fake_v545_dependency()
    policy = build_private_registry_auth_feed_policy_v546()
    matrix = run_auth_feed_matrix_v546(dependency)
    manifest = build_expiring_feed_manifest_v546(dependency, matrix)
    probe = run_expiring_feed_probe_v546(dependency, matrix)
    log_export = build_registry_log_export_contract_v546(dependency, matrix)
    bundle = build_auth_feed_audit_bundle_v546(policy, matrix, manifest, probe, log_export)

    assert manifest["expiring_feed_manifest_ready"] is True
    assert manifest["feed_count"] == 3
    assert probe["expiring_feed_probe_ready"] is True
    assert log_export["registry_log_export_contract_ready"] is True
    assert log_export["event_count"] == 13
    assert bundle["auth_feed_audit_bundle_ready"] is True
    assert bundle["live_private_registry_ready"] is False


def test_v546_workflow_ready_without_live_registry_claim(tmp_path):
    audit = run_private_registry_auth_feed_workflow_v546(Path.cwd(), tmp_path / "out")

    assert audit["overall_status"] == "private_registry_auth_feed_contract_ready_production_not_claimed"
    assert audit["private_registry_auth_feed_contract_ready"] is True
    assert audit["v545_dependency_ready"] is True
    assert audit["auth_feed_matrix_ready"] is True
    assert audit["expiring_feed_probe_ready"] is True
    assert audit["registry_log_export_contract_ready"] is True
    assert audit["real_private_registry_auth_ready"] is False
    assert audit["live_private_registry_ready"] is False
    assert audit["production_distribution_ready"] is False
    assert audit["full_biosdk_ready"] is False
    assert audit["bic_os_phase_locked"] is True


def test_v546_outputs_are_written(tmp_path):
    audit = run_private_registry_auth_feed_workflow_v546(Path.cwd(), tmp_path / "workflow")
    paths = write_private_registry_auth_feed_outputs_v546(audit, tmp_path / "out")

    assert Path(paths["summary_json"]).exists()
    assert Path(paths["policy_json"]).exists()
    assert Path(paths["matrix_json"]).exists()
    assert Path(paths["feed_manifest_json"]).exists()
    assert Path(paths["expiry_probe_json"]).exists()
    assert Path(paths["registry_log_export_json"]).exists()
    assert Path(paths["audit_bundle_json"]).exists()
    assert Path(paths["matrix_csv"]).exists()
    assert Path(paths["registry_log_csv"]).exists()
    assert "Private Registry Auth Feed Contract" in Path(paths["markdown_report"]).read_text(encoding="utf-8")


def test_v546_runner_writes_summary(tmp_path):
    result = run(root=Path.cwd(), out_dir=tmp_path / "out")

    assert result["summary"]["private_registry_auth_feed_contract_ready"] is True
    assert (tmp_path / "out" / "V546_PRIVATE_REGISTRY_AUTH_FEED_SUMMARY.json").exists()