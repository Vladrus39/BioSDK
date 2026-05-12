from __future__ import annotations

from pathlib import Path

from biogpu.benchmarks.biogpu_v526_durable_scheduler_worker import run
from biogpu.beta.job_model_v43 import JobStatus
from biogpu.runtime.durable_scheduler_v526 import DurableSchedulerStoreV526, enqueue_reference_jobs_v526, run_durable_scheduler_workflow_v526, run_worker_until_idle_v526, write_durable_scheduler_outputs_v526


def test_v526_persists_v55_admitted_jobs_across_restart(tmp_path):
    db_path = tmp_path / "scheduler.sqlite3"

    enqueue = enqueue_reference_jobs_v526(db_path)
    restarted = DurableSchedulerStoreV526(db_path)
    jobs = restarted.list_jobs(JobStatus.QUEUED.value)

    assert len(jobs) == 2
    assert enqueue["submissions"]["blocked_actuation"]["admission"]["accepted"] is False
    assert {job["job_type"] for job in jobs} == {"benchmark_run", "api_readonly_validation"}


def test_v526_worker_claims_and_completes_jobs(tmp_path):
    db_path = tmp_path / "scheduler.sqlite3"
    enqueue_reference_jobs_v526(db_path)

    executions = run_worker_until_idle_v526(db_path, tmp_path / "results")
    store = DurableSchedulerStoreV526(db_path)
    jobs = store.list_jobs()

    assert [execution["status"] for execution in executions][-1] == "idle_no_queued_jobs"
    assert len([execution for execution in executions if execution["job_id"]]) == 2
    assert all(job["status"] == JobStatus.SUCCEEDED.value for job in jobs)
    assert all(job["result_bundle"] for job in jobs)
    assert len(list((tmp_path / "results").glob("*_result.json"))) == 2


def test_v526_workflow_keeps_runtime_and_bic_os_claims_blocked(tmp_path):
    audit = run_durable_scheduler_workflow_v526(tmp_path)

    assert audit["overall_status"] == "durable_scheduler_worker_proof_ready_runtime_not_claimed"
    assert audit["durable_scheduler_worker_proof_ready"] is True
    assert audit["production_scheduler_ready"] is False
    assert audit["production_biocompute_runtime_ready"] is False
    assert audit["bic_os_phase_locked"] is True
    assert audit["live_actuation_enabled"] is False


def test_v526_write_outputs(tmp_path):
    audit = run_durable_scheduler_workflow_v526(tmp_path)

    paths = write_durable_scheduler_outputs_v526(audit, tmp_path / "out")

    assert Path(paths["summary_json"]).exists()
    assert Path(paths["jobs_json"]).exists()
    assert Path(paths["jobs_csv"]).exists()
    assert Path(paths["events_json"]).exists()
    assert Path(paths["worker_executions_json"]).exists()
    assert "Durable Scheduler Worker Proof" in Path(paths["markdown_report"]).read_text(encoding="utf-8")


def test_v526_runner_writes_summary(tmp_path):
    result = run(root=tmp_path, out_dir=tmp_path / "out")

    assert result["summary"]["durable_scheduler_worker_proof_ready"] is True
    assert (tmp_path / "out" / "V526_DURABLE_SCHEDULER_WORKER_SUMMARY.json").exists()