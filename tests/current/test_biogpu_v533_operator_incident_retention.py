from __future__ import annotations

from pathlib import Path

from biogpu.benchmarks.biogpu_v533_operator_incident_retention import run
from biogpu.runtime.incident_workflow_v533 import (
    IncidentRetentionPolicyV533,
    acknowledge_incident_v533,
    apply_incident_retention_policy_v533,
    build_dead_letter_incident_v533,
    build_operator_incident_timeline_v533,
    resolve_incident_v533,
    run_operator_incident_retention_workflow_v533,
    write_operator_incident_retention_outputs_v533,
)


def _minimal_v532_audit() -> dict:
    return {
        "version": "v5.32",
        "overall_status": "bounded_retry_dead_letter_proof_ready_runtime_not_claimed",
        "bounded_retry_dead_letter_ready": True,
        "dead_letter_job_id": "job-test-retry-2",
        "retry_job_ids": ["job-test-retry-1", "job-test-retry-2"],
        "max_retry_attempts": 2,
        "production_retry_policy_ready": False,
        "probe": {"dead_letter_queue": [{"job_id": "job-test-retry-2", "final_attempt": 2, "status": "dead_lettered"}]},
    }


def test_v533_operator_acknowledgement_and_resolution_transitions():
    incident = build_dead_letter_incident_v533(_minimal_v532_audit(), created_at="2026-05-07T04:20:00+00:00")
    ack = acknowledge_incident_v533(incident, action_time="2026-05-07T04:21:00+00:00")
    resolved = resolve_incident_v533(ack["incident"], action_time="2026-05-07T04:22:00+00:00")

    assert ack["action"]["accepted"] is True
    assert ack["incident"]["status"] == "acknowledged"
    assert resolved["action"]["accepted"] is True
    assert resolved["incident"]["status"] == "resolved"
    assert resolved["incident"]["details"]["live_actuation_enabled"] is False


def test_v533_timeline_contains_operator_actions():
    timeline = build_operator_incident_timeline_v533(_minimal_v532_audit())

    assert timeline["timeline_ready"] is True
    assert timeline["operator_acknowledgement_ready"] is True
    assert timeline["incident_resolution_ready"] is True
    assert timeline["state_sequence"] == ["open", "acknowledged", "resolved"]
    assert len(timeline["actions"]) == 2


def test_v533_retention_manifest_is_non_destructive(tmp_path):
    timeline = build_operator_incident_timeline_v533(_minimal_v532_audit())
    manifest = apply_incident_retention_policy_v533(timeline, tmp_path, IncidentRetentionPolicyV533(retain_resolved_days=7))

    assert manifest["non_destructive_full_export"] is True
    assert manifest["source_incident_count"] == 2
    assert manifest["retained_incident_count"] == 1
    assert manifest["archived_incident_count"] == 1
    assert Path(manifest["full_export_path"]).exists()


def test_v533_workflow_ready_but_not_production_incident_management(tmp_path):
    audit = run_operator_incident_retention_workflow_v533(tmp_path)

    assert audit["overall_status"] == "operator_incident_retention_proof_ready_runtime_not_claimed"
    assert audit["operator_incident_retention_ready"] is True
    assert audit["operator_acknowledgement_ready"] is True
    assert audit["incident_resolution_ready"] is True
    assert audit["incident_retention_manifest_ready"] is True
    assert audit["incident_audit_bundle_ready"] is True
    assert audit["production_operator_workflow_ready"] is False
    assert audit["production_biocompute_runtime_ready"] is False
    assert audit["bic_os_phase_locked"] is True


def test_v533_write_outputs(tmp_path):
    audit = run_operator_incident_retention_workflow_v533(tmp_path)

    paths = write_operator_incident_retention_outputs_v533(audit, tmp_path / "out")
    assert Path(paths["summary_json"]).exists()
    assert Path(paths["timeline_json"]).exists()
    assert Path(paths["acknowledgement_json"]).exists()
    assert Path(paths["retention_manifest_json"]).exists()
    assert Path(paths["incidents_csv"]).exists()
    assert "Operator Incident" in Path(paths["markdown_report"]).read_text(encoding="utf-8")


def test_v533_runner_writes_summary(tmp_path):
    result = run(root=tmp_path, out_dir=tmp_path / "out")

    assert result["summary"]["operator_incident_retention_ready"] is True
    assert (tmp_path / "out" / "V533_OPERATOR_INCIDENT_RETENTION_SUMMARY.json").exists()