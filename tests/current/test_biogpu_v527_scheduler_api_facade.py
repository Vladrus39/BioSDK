from __future__ import annotations

from pathlib import Path

from biogpu.benchmarks.biogpu_v527_scheduler_api_facade import run
from biogpu.beta.job_model_v43 import JobStatus
from biogpu.runtime.durable_scheduler_v526 import enqueue_reference_jobs_v526
from biogpu.runtime.scheduler_api_v527 import SchedulerAPIFacadeV527, make_scheduler_api_app_v527, run_scheduler_api_facade_workflow_v527, scheduler_api_route_manifest_v527, write_scheduler_api_facade_outputs_v527


def test_v527_cancel_timeout_retry_and_worker_step(tmp_path):
    db_path = tmp_path / "scheduler.sqlite3"
    enqueue_reference_jobs_v526(db_path)
    facade = SchedulerAPIFacadeV527(db_path, tmp_path / "results")
    queued = facade.list_jobs(JobStatus.QUEUED.value)

    cancelled = facade.cancel_job(queued[0]["job_id"])
    running = facade.store.claim_next_job("timeout_worker")
    timeouts = facade.timeout_running_jobs(max_running_age_seconds=0)
    retry = facade.retry_job(running["job_id"])
    worker = facade.worker_step("api_worker")

    assert cancelled.accepted is True
    assert timeouts[0].accepted is True
    assert retry.accepted is True
    assert worker["status"] == "succeeded"
    final_counts = facade.health()["status_counts"]
    assert final_counts[JobStatus.CANCELLED.value] == 1
    assert final_counts[JobStatus.FAILED.value] == 1
    assert final_counts[JobStatus.SUCCEEDED.value] == 1


def test_v527_fastapi_facade_exposes_expected_routes(tmp_path):
    app = make_scheduler_api_app_v527(tmp_path / "scheduler.sqlite3", tmp_path / "results")

    routes = scheduler_api_route_manifest_v527(app)
    paths = {route["path"] for route in routes}

    assert "/health" in paths
    assert "/v1/scheduler/jobs" in paths
    assert "/v1/scheduler/jobs/{job_id}/cancel" in paths
    assert "/v1/scheduler/jobs/{job_id}/retry" in paths
    assert "/v1/scheduler/timeouts/scan" in paths
    assert "/v1/scheduler/workers/{worker_id}/step" in paths


def test_v527_workflow_ready_but_not_production_runtime(tmp_path):
    audit = run_scheduler_api_facade_workflow_v527(tmp_path)

    assert audit["overall_status"] == "scheduler_api_facade_semantics_ready_runtime_not_claimed"
    assert audit["scheduler_api_facade_ready"] is True
    assert audit["cancel_semantics_passed"] is True
    assert audit["timeout_semantics_passed"] is True
    assert audit["retry_semantics_passed"] is True
    assert audit["production_api_ready"] is False
    assert audit["production_biocompute_runtime_ready"] is False
    assert audit["bic_os_phase_locked"] is True


def test_v527_write_outputs(tmp_path):
    audit = run_scheduler_api_facade_workflow_v527(tmp_path)

    paths = write_scheduler_api_facade_outputs_v527(audit, tmp_path / "out")

    assert Path(paths["summary_json"]).exists()
    assert Path(paths["routes_json"]).exists()
    assert Path(paths["actions_json"]).exists()
    assert Path(paths["jobs_json"]).exists()
    assert Path(paths["events_json"]).exists()
    assert Path(paths["jobs_csv"]).exists()
    assert "Scheduler API Facade" in Path(paths["markdown_report"]).read_text(encoding="utf-8")


def test_v527_runner_writes_summary(tmp_path):
    result = run(root=tmp_path, out_dir=tmp_path / "out")

    assert result["summary"]["scheduler_api_facade_ready"] is True
    assert (tmp_path / "out" / "V527_SCHEDULER_API_FACADE_SUMMARY.json").exists()