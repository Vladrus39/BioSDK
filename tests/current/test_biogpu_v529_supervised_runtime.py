from __future__ import annotations

import json
from pathlib import Path

from biogpu.benchmarks.biogpu_v529_supervised_runtime import run
from biogpu.beta.job_model_v43 import JobStatus
from biogpu.runtime.local_service_v528 import V528_DEVELOPER_API_KEY, V528_WORKER_API_KEY
from biogpu.runtime.supervised_runtime_v529 import SupervisedLocalRuntimeV529, run_supervised_runtime_workflow_v529, write_supervised_runtime_outputs_v529


def test_v529_start_heartbeat_and_state_files(tmp_path):
    runtime = SupervisedLocalRuntimeV529(tmp_path)

    start = runtime.start(reset=True)
    heartbeat = runtime.heartbeat()
    state = json.loads(runtime.state_path.read_text(encoding="utf-8"))
    heartbeat_doc = json.loads(runtime.heartbeat_path.read_text(encoding="utf-8"))

    assert start.accepted is True
    assert heartbeat.accepted is True
    assert state["status"] == "running"
    assert state["process_id"] == runtime.process_id
    assert heartbeat_doc["heartbeat_index"] == state["heartbeat_index"]
    assert runtime.audit_log_path.exists()


def test_v529_worker_ticks_shutdown_and_post_shutdown_rejection(tmp_path):
    runtime = SupervisedLocalRuntimeV529(tmp_path)
    runtime.start(reset=True)

    tick_one = runtime.worker_tick(V528_WORKER_API_KEY)
    tick_two = runtime.worker_tick(V528_WORKER_API_KEY)
    idle_tick = runtime.worker_tick(V528_WORKER_API_KEY)
    shutdown = runtime.graceful_shutdown(V528_WORKER_API_KEY)
    rejected = runtime.worker_tick(V528_WORKER_API_KEY)

    assert tick_one.status == JobStatus.SUCCEEDED.value
    assert tick_two.status == JobStatus.SUCCEEDED.value
    assert idle_tick.status == "idle_no_queued_jobs"
    assert shutdown.status == "stopped"
    assert rejected.status == "runtime_not_running"
    assert runtime._load_state()["status"] == "stopped"


def test_v529_audit_export_requires_auth_and_writes_hash(tmp_path):
    runtime = SupervisedLocalRuntimeV529(tmp_path)
    runtime.start(reset=True)
    runtime.heartbeat()

    missing = runtime.export_audit_log(api_key=None)  # type: ignore[arg-type]
    exported = runtime.export_audit_log(V528_DEVELOPER_API_KEY)
    payload = exported.payload or {}

    assert missing.status == "missing_api_key"
    assert exported.accepted is True
    assert runtime.audit_export_path.exists()
    assert payload["event_count"] >= 2
    assert len(payload["audit_sha256"]) == 64


def test_v529_workflow_ready_but_not_production_runtime(tmp_path):
    audit = run_supervised_runtime_workflow_v529(tmp_path)

    assert audit["overall_status"] == "supervised_local_runtime_lifecycle_ready_runtime_not_claimed"
    assert audit["supervised_local_runtime_ready"] is True
    assert audit["start_semantics_passed"] is True
    assert audit["heartbeat_semantics_passed"] is True
    assert audit["worker_tick_semantics_passed"] is True
    assert audit["graceful_shutdown_semantics_passed"] is True
    assert audit["audit_export_semantics_passed"] is True
    assert audit["production_runtime_ready"] is False
    assert audit["production_biocompute_runtime_ready"] is False
    assert audit["bic_os_phase_locked"] is True


def test_v529_write_outputs(tmp_path):
    audit = run_supervised_runtime_workflow_v529(tmp_path)

    paths = write_supervised_runtime_outputs_v529(audit, tmp_path / "out")
    assert Path(paths["summary_json"]).exists()
    assert Path(paths["actions_json"]).exists()
    assert Path(paths["jobs_json"]).exists()
    assert Path(paths["audit_events_json"]).exists()
    assert Path(paths["jobs_csv"]).exists()
    assert "Supervised Local Runtime" in Path(paths["markdown_report"]).read_text(encoding="utf-8")


def test_v529_runner_writes_summary(tmp_path):
    result = run(root=tmp_path, out_dir=tmp_path / "out")

    assert result["summary"]["supervised_local_runtime_ready"] is True
    assert (tmp_path / "out" / "V529_SUPERVISED_RUNTIME_SUMMARY.json").exists()