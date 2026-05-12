from __future__ import annotations

from pathlib import Path

from biogpu.benchmarks.biogpu_v547_registry_revoke_yank_notification import run
from biogpu.sdk.registry_revoke_yank_notification_v547 import (
    build_incident_linkage_export_v547,
    build_local_yank_manifest_v547,
    build_recipient_notification_ack_trail_v547,
    build_registry_revoke_yank_policy_v547,
    build_revoke_yank_audit_bundle_v547,
    default_revoke_yank_scenarios_v547,
    evaluate_revoke_yank_scenario_v547,
    run_registry_revoke_yank_notification_workflow_v547,
    run_revoke_yank_effect_probe_v547,
    run_revoke_yank_matrix_v547,
    write_registry_revoke_yank_notification_outputs_v547,
)


def _fake_v546_dependency() -> dict[str, object]:
    artifact_sha256 = "a" * 64
    return {
        "private_registry_auth_feed_contract_ready": True,
        "artifact_name": "biogpu_core-5.0.0-py3-none-any.whl",
        "artifact_sha256": artifact_sha256,
        "expiring_feed_manifest": {
            "expiring_feed_manifest_ready": True,
            "feeds": [
                {"feed_id": "feed-alpha", "recipient_id": "recipient-alpha", "local_feed_token_id": "local-feed-token-alpha"},
                {"feed_id": "feed-beta", "recipient_id": "recipient-beta", "local_feed_token_id": "local-feed-token-beta"},
                {"feed_id": "feed-provenance", "recipient_id": "recipient-provenance", "local_feed_token_id": "local-feed-token-provenance"},
            ],
        },
        "real_private_registry_auth_ready": False,
        "live_private_registry_ready": False,
        "production_distribution_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }


def test_v547_policy_is_local_only():
    policy = build_registry_revoke_yank_policy_v547()

    assert policy["registry_revoke_yank_policy_ready"] is True
    assert policy["policy"]["requires_recipient_notification"] is True
    assert policy["policy"]["live_registry_yank_configured"] is False
    assert policy["production_yank_ready"] is False
    assert policy["full_biosdk_ready"] is False


def test_v547_matrix_allows_and_denies_expected_cases():
    dependency = _fake_v546_dependency()
    matrix = run_revoke_yank_matrix_v547(dependency, default_revoke_yank_scenarios_v547(dependency))

    assert matrix["revoke_yank_matrix_ready"] is True
    assert matrix["allowed_revoke_yank_count"] == 4
    assert matrix["denied_revoke_yank_count"] == 8
    assert "revoke_trigger_not_authorized" in matrix["reason_codes"]
    assert "recipient_ack_missing" in matrix["reason_codes"]
    assert "live_registry_yank_not_ready" in matrix["reason_codes"]
    assert "production_distribution_not_allowed" in matrix["reason_codes"]


def test_v547_evaluation_denies_live_registry_yank():
    dependency = _fake_v546_dependency()
    live = [scenario for scenario in default_revoke_yank_scenarios_v547(dependency) if scenario.scenario_id == "live-registry-yank"][0]
    decision = evaluate_revoke_yank_scenario_v547(live, dependency)

    assert decision.local_revoke_yank_allowed is False
    assert "live_registry_yank_not_ready" in decision.reason_codes
    assert decision.production_yank_ready is False


def test_v547_yank_manifest_notification_effect_incidents_and_bundle_are_ready():
    dependency = _fake_v546_dependency()
    policy = build_registry_revoke_yank_policy_v547()
    matrix = run_revoke_yank_matrix_v547(dependency)
    manifest = build_local_yank_manifest_v547(dependency, matrix)
    notification_trail = build_recipient_notification_ack_trail_v547(matrix)
    effect_probe = run_revoke_yank_effect_probe_v547(manifest)
    incident_export = build_incident_linkage_export_v547(matrix, notification_trail)
    bundle = build_revoke_yank_audit_bundle_v547(policy, matrix, manifest, notification_trail, effect_probe, incident_export)

    assert manifest["local_yank_manifest_ready"] is True
    assert manifest["yank_entry_count"] == 4
    assert notification_trail["recipient_notification_ack_trail_ready"] is True
    assert effect_probe["revoke_yank_effect_probe_ready"] is True
    assert incident_export["incident_linkage_export_ready"] is True
    assert bundle["revoke_yank_audit_bundle_ready"] is True
    assert bundle["production_yank_ready"] is False


def test_v547_workflow_ready_without_production_yank_claim(tmp_path):
    audit = run_registry_revoke_yank_notification_workflow_v547(Path.cwd(), tmp_path / "out")

    assert audit["overall_status"] == "registry_revoke_yank_notification_contract_ready_production_not_claimed"
    assert audit["registry_revoke_yank_notification_contract_ready"] is True
    assert audit["v546_dependency_ready"] is True
    assert audit["local_yank_manifest_ready"] is True
    assert audit["recipient_notification_ack_trail_ready"] is True
    assert audit["incident_linkage_export_ready"] is True
    assert audit["production_yank_ready"] is False
    assert audit["live_private_registry_ready"] is False
    assert audit["production_distribution_ready"] is False
    assert audit["full_biosdk_ready"] is False
    assert audit["bic_os_phase_locked"] is True


def test_v547_outputs_are_written(tmp_path):
    audit = run_registry_revoke_yank_notification_workflow_v547(Path.cwd(), tmp_path / "workflow")
    paths = write_registry_revoke_yank_notification_outputs_v547(audit, tmp_path / "out")

    assert Path(paths["summary_json"]).exists()
    assert Path(paths["policy_json"]).exists()
    assert Path(paths["matrix_json"]).exists()
    assert Path(paths["local_yank_manifest_json"]).exists()
    assert Path(paths["notification_trail_json"]).exists()
    assert Path(paths["effect_probe_json"]).exists()
    assert Path(paths["incident_linkage_json"]).exists()
    assert Path(paths["audit_bundle_json"]).exists()
    assert Path(paths["matrix_csv"]).exists()
    assert Path(paths["notification_trail_csv"]).exists()
    assert "Registry Revoke/Yank Notification Contract" in Path(paths["markdown_report"]).read_text(encoding="utf-8")


def test_v547_runner_writes_summary(tmp_path):
    result = run(root=Path.cwd(), out_dir=tmp_path / "out")

    assert result["summary"]["registry_revoke_yank_notification_contract_ready"] is True
    assert (tmp_path / "out" / "V547_REGISTRY_REVOKE_YANK_NOTIFICATION_SUMMARY.json").exists()