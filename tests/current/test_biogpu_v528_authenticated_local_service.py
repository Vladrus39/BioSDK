from __future__ import annotations

from pathlib import Path

from biogpu.benchmarks.biogpu_v528_authenticated_local_service import run
from biogpu.beta.job_model_v43 import JobStatus
from biogpu.runtime.durable_scheduler_v526 import enqueue_reference_jobs_v526
from biogpu.runtime.local_service_v528 import (
    V528_DEVELOPER_API_KEY,
    V528_VIEWER_API_KEY,
    V528_WORKER_API_KEY,
    AuthenticatedLocalServiceV528,
    authenticated_local_service_route_manifest_v528,
    make_authenticated_local_service_app_v528,
    run_authenticated_local_service_workflow_v528,
    write_authenticated_local_service_outputs_v528,
)


def test_v528_auth_rejects_missing_invalid_and_scope_denies(tmp_path):
    db_path = tmp_path / "scheduler.sqlite3"
    enqueue_reference_jobs_v526(db_path)
    service = AuthenticatedLocalServiceV528(db_path, tmp_path / "results")

    missing = service.list_jobs(None)
    invalid = service.list_jobs("wrong-local-key")
    developer_worker_denial = service.worker_step(V528_DEVELOPER_API_KEY, "denied_worker")
    viewer_cancel_denial = service.cancel_job(V528_VIEWER_API_KEY, "missing")

    assert missing.status == "missing_api_key"
    assert invalid.status == "invalid_api_key"
    assert developer_worker_denial.status == "missing_scope"
    assert viewer_cancel_denial.status == "missing_scope"


def test_v528_worker_result_bundle_download_contract(tmp_path):
    db_path = tmp_path / "scheduler.sqlite3"
    enqueue_reference_jobs_v526(db_path)
    service = AuthenticatedLocalServiceV528(db_path, tmp_path / "results")

    worker = service.worker_step(V528_WORKER_API_KEY, "bundle_worker")
    download = service.download_result_bundle(V528_DEVELOPER_API_KEY, worker.job_id or "")

    assert worker.accepted is True
    assert worker.status == JobStatus.SUCCEEDED.value
    assert download.accepted is True
    assert download.status == "download_contract_ready"
    assert download.payload is not None
    assert download.payload["checksum_matches"] is True
    assert download.payload["payload"]["job_id"] == worker.job_id


def test_v528_routes_include_auth_and_bundle_download(tmp_path):
    app = make_authenticated_local_service_app_v528(tmp_path / "scheduler.sqlite3", tmp_path / "results")

    routes = authenticated_local_service_route_manifest_v528(app)
    paths = {route["path"] for route in routes}

    assert "/health" in paths
    assert "/v1/service/whoami" in paths
    assert "/v1/scheduler/jobs" in paths
    assert "/v1/scheduler/jobs/{job_id}/cancel" in paths
    assert "/v1/scheduler/workers/{worker_id}/step" in paths
    assert "/v1/result-bundles/{job_id}/download" in paths


def test_v528_workflow_ready_but_not_runtime_or_bic_os(tmp_path):
    audit = run_authenticated_local_service_workflow_v528(tmp_path)

    assert audit["overall_status"] == "authenticated_local_service_contract_ready_runtime_not_claimed"
    assert audit["authenticated_local_service_ready"] is True
    assert audit["missing_auth_rejected"] is True
    assert audit["invalid_auth_rejected"] is True
    assert audit["scope_denial_passed"] is True
    assert audit["result_bundle_download_contract_passed"] is True
    assert audit["production_api_ready"] is False
    assert audit["production_biocompute_runtime_ready"] is False
    assert audit["bic_os_phase_locked"] is True


def test_v528_write_outputs(tmp_path):
    audit = run_authenticated_local_service_workflow_v528(tmp_path)

    paths = write_authenticated_local_service_outputs_v528(audit, tmp_path / "out")
    assert Path(paths["summary_json"]).exists()
    assert Path(paths["routes_json"]).exists()
    assert Path(paths["actions_json"]).exists()
    assert Path(paths["download_json"]).exists()
    assert Path(paths["jobs_json"]).exists()
    assert Path(paths["events_json"]).exists()
    assert Path(paths["jobs_csv"]).exists()
    assert "Authenticated Local Service" in Path(paths["markdown_report"]).read_text(encoding="utf-8")


def test_v528_runner_writes_summary(tmp_path):
    result = run(root=tmp_path, out_dir=tmp_path / "out")

    assert result["summary"]["authenticated_local_service_ready"] is True
    assert (tmp_path / "out" / "V528_AUTHENTICATED_LOCAL_SERVICE_SUMMARY.json").exists()