from __future__ import annotations

from pathlib import Path

from biogpu.benchmarks.biogpu_v531_recovery_alerting import run
from biogpu.runtime.recovery_v531 import (
    build_recovery_audit_bundle_v531,
    build_stale_heartbeat_alert_v531,
    run_recovery_alerting_workflow_v531,
    run_worker_failure_recovery_probe_v531,
    write_recovery_alerting_outputs_v531,
)


def test_v531_stale_heartbeat_alert_detects_running_stale_runtime():
    heartbeat = {
        "runtime_id": "runtime-test",
        "status": "running",
        "last_heartbeat_at": "1970-01-01T00:00:00+00:00",
        "heartbeat_index": 1,
    }

    alert = build_stale_heartbeat_alert_v531(heartbeat, observed_at="2026-05-07T04:10:00+00:00", max_age_seconds=60)

    assert alert.accepted is True
    assert alert.status == "stale_heartbeat_detected"
    assert alert.severity == "critical"
    assert alert.production_alerting_ready is False


def test_v531_worker_failure_recovery_probe_retries_timeout(tmp_path):
    probe = run_worker_failure_recovery_probe_v531(tmp_path, tmp_path / "out")

    assert probe["recovery_probe_ready"] is True
    assert probe["failure_classification"]["kind"] == "worker_timeout"
    assert probe["failure_classification"]["retryable"] is True
    assert probe["retry_action"]["accepted"] is True
    assert probe["worker_step"]["status"] == "succeeded"
    assert probe["recovered_job"]["status"] == "succeeded"


def test_v531_recovery_audit_bundle_writes_hash(tmp_path):
    alert = build_stale_heartbeat_alert_v531({"runtime_id": "runtime-test", "status": "running", "last_heartbeat_at": "1970-01-01T00:00:00+00:00"}, observed_at="2026-05-07T04:10:00+00:00")
    probe = run_worker_failure_recovery_probe_v531(tmp_path, tmp_path / "probe")

    bundle = build_recovery_audit_bundle_v531(alert, probe, tmp_path / "bundle")

    assert bundle["bundle_ready"] is True
    assert len(bundle["bundle_sha256"]) == 64
    assert Path(bundle["bundle_path"]).exists()


def test_v531_workflow_ready_but_not_production_recovery(tmp_path):
    audit = run_recovery_alerting_workflow_v531(tmp_path)

    assert audit["overall_status"] == "recovery_alerting_proof_ready_runtime_not_claimed"
    assert audit["recovery_alerting_ready"] is True
    assert audit["stale_heartbeat_alert_passed"] is True
    assert audit["failure_classification_passed"] is True
    assert audit["worker_recovery_passed"] is True
    assert audit["recovery_audit_bundle_ready"] is True
    assert audit["production_recovery_ready"] is False
    assert audit["production_biocompute_runtime_ready"] is False
    assert audit["bic_os_phase_locked"] is True


def test_v531_write_outputs(tmp_path):
    audit = run_recovery_alerting_workflow_v531(tmp_path)

    paths = write_recovery_alerting_outputs_v531(audit, tmp_path / "out")
    assert Path(paths["summary_json"]).exists()
    assert Path(paths["alert_json"]).exists()
    assert Path(paths["failure_json"]).exists()
    assert Path(paths["recovery_probe_json"]).exists()
    assert Path(paths["events_json"]).exists()
    assert Path(paths["jobs_csv"]).exists()
    assert "Recovery Alerting" in Path(paths["markdown_report"]).read_text(encoding="utf-8")


def test_v531_runner_writes_summary(tmp_path):
    result = run(root=tmp_path, out_dir=tmp_path / "out")

    assert result["summary"]["recovery_alerting_ready"] is True
    assert (tmp_path / "out" / "V531_RECOVERY_ALERTING_SUMMARY.json").exists()