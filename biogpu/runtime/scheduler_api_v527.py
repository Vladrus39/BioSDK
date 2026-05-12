"""Local durable scheduler API facade and lifecycle semantics, v5.27."""
from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:  # FastAPI is optional for pure workflow/tests that use the facade directly.
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
except Exception:  # pragma: no cover
    FastAPI = None  # type: ignore
    HTTPException = Exception  # type: ignore

    class BaseModel:  # type: ignore
        pass

from biogpu.beta.job_model_v43 import JobStatus, find_unsafe_fields, utc_now_iso
from biogpu.runtime.durable_scheduler_v526 import DEFAULT_DB_NAME as V526_DB_NAME
from biogpu.runtime.durable_scheduler_v526 import DurableSchedulerStoreV526, _json_dumps, _json_loads, enqueue_reference_jobs_v526, run_worker_once_v526


DEFAULT_OUT = Path("outputs/v527_scheduler_api_facade")
DEFAULT_DB_NAME = "V527_SCHEDULER_API_FACADE.sqlite3"


@dataclass(frozen=True)
class SchedulerActionV527:
    action: str
    accepted: bool
    status: str
    job_id: str | None
    related_job_id: str | None = None
    errors: tuple[str, ...] = tuple()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class CancelRequestV527(BaseModel):
    reason: str = "user_requested_cancel"


class RetryRequestV527(BaseModel):
    reason: str = "retry_requested"


class TimeoutScanRequestV527(BaseModel):
    max_running_age_seconds: int = 0


def _parse_time(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return datetime.min.replace(tzinfo=timezone.utc)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


class SchedulerAPIFacadeV527:
    """Small local API facade over the v5.26 SQLite scheduler store."""

    def __init__(self, db_path: str | Path, result_dir: str | Path | None = None) -> None:
        self.store = DurableSchedulerStoreV526(db_path)
        self.result_dir = Path(result_dir) if result_dir is not None else Path(db_path).parent / "api_worker_results"

    def health(self) -> dict[str, Any]:
        jobs = self.store.list_jobs()
        status_counts: dict[str, int] = {}
        for job in jobs:
            status_counts[job["status"]] = status_counts.get(job["status"], 0) + 1
        return {
            "status": "ok",
            "version": "v5.27",
            "job_count": len(jobs),
            "status_counts": dict(sorted(status_counts.items())),
            "local_api_facade_ready": True,
            "production_api_ready": False,
            "production_scheduler_ready": False,
            "live_actuation_enabled": False,
            "bic_os_phase_locked": True,
        }

    def list_jobs(self, status: str | None = None) -> list[dict[str, Any]]:
        return self.store.list_jobs(status)

    def get_job(self, job_id: str) -> dict[str, Any]:
        return self.store.get_job(job_id)

    def cancel_job(self, job_id: str, reason: str = "user_requested_cancel") -> SchedulerActionV527:
        try:
            job = self.store.get_job(job_id)
        except KeyError:
            return SchedulerActionV527("cancel", False, "job_not_found", job_id, errors=("job_not_found",))
        if job["status"] not in {JobStatus.QUEUED.value, JobStatus.RUNNING.value}:
            return SchedulerActionV527("cancel", False, "terminal_status_not_cancellable", job_id, errors=(f"status:{job['status']}",))
        now = utc_now_iso()
        with self.store._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute("UPDATE jobs SET status = ?, updated_at = ? WHERE job_id = ?", (JobStatus.CANCELLED.value, now, job_id))
            event_index = self.store._next_event_index(connection, job_id)
            connection.execute(
                "INSERT INTO job_events (job_id, event_index, event_time, event_name, details_json) VALUES (?, ?, ?, ?, ?)",
                (job_id, event_index, now, "api_cancelled", _json_dumps({"reason": reason})),
            )
            connection.commit()
        return SchedulerActionV527("cancel", True, JobStatus.CANCELLED.value, job_id)

    def timeout_running_jobs(self, max_running_age_seconds: int = 0) -> list[SchedulerActionV527]:
        running = self.store.list_jobs(JobStatus.RUNNING.value)
        now_dt = datetime.now(timezone.utc)
        actions: list[SchedulerActionV527] = []
        for job in running:
            age_seconds = (now_dt - _parse_time(job["updated_at"])).total_seconds()
            if max_running_age_seconds > 0 and age_seconds < max_running_age_seconds:
                actions.append(SchedulerActionV527("timeout_scan", False, "running_but_not_expired", job["job_id"]))
                continue
            errors = list(job.get("validation_errors", []))
            if "worker_timeout_exceeded" not in errors:
                errors.append("worker_timeout_exceeded")
            now = utc_now_iso()
            with self.store._connect() as connection:
                connection.execute("BEGIN IMMEDIATE")
                connection.execute(
                    "UPDATE jobs SET status = ?, updated_at = ?, validation_errors_json = ? WHERE job_id = ?",
                    (JobStatus.FAILED.value, now, _json_dumps(errors), job["job_id"]),
                )
                event_index = self.store._next_event_index(connection, job["job_id"])
                connection.execute(
                    "INSERT INTO job_events (job_id, event_index, event_time, event_name, details_json) VALUES (?, ?, ?, ?, ?)",
                    (job["job_id"], event_index, now, "api_timed_out", _json_dumps({"max_running_age_seconds": max_running_age_seconds, "observed_age_seconds": age_seconds})),
                )
                connection.commit()
            actions.append(SchedulerActionV527("timeout", True, JobStatus.FAILED.value, job["job_id"], errors=("worker_timeout_exceeded",)))
        return actions

    def retry_job(self, job_id: str, reason: str = "retry_requested") -> SchedulerActionV527:
        try:
            job = self.store.get_job(job_id)
        except KeyError:
            return SchedulerActionV527("retry", False, "job_not_found", job_id, errors=("job_not_found",))
        if job["status"] not in {JobStatus.FAILED.value, JobStatus.CANCELLED.value}:
            return SchedulerActionV527("retry", False, "status_not_retryable", job_id, errors=(f"status:{job['status']}",))
        unsafe = find_unsafe_fields(job.get("manifest", {}))
        if unsafe:
            return SchedulerActionV527("retry", False, "unsafe_manifest_not_retryable", job_id, errors=tuple(unsafe))
        metadata = dict(job.get("metadata") or {})
        attempt = int(metadata.get("retry_attempt", 0) or 0) + 1
        metadata.update({"retry_of": job_id, "retry_attempt": attempt, "retry_reason": reason, "source": "v527_scheduler_api_facade"})
        new_job_id = f"{job_id}_retry_{attempt}"
        with self.store._connect() as connection:
            while connection.execute("SELECT 1 FROM jobs WHERE job_id = ?", (new_job_id,)).fetchone() is not None:
                attempt += 1
                metadata["retry_attempt"] = attempt
                new_job_id = f"{job_id}_retry_{attempt}"
            now = utc_now_iso()
            connection.execute("BEGIN IMMEDIATE")
            connection.execute(
                """
                INSERT INTO jobs (
                    job_id, workspace_id, created_by, job_type, dataset_id, status, created_at, updated_at,
                    requested_result_bundle, manifest_json, metadata_json, validation_errors_json, result_bundle_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    new_job_id,
                    job["workspace_id"],
                    job["created_by"],
                    job["job_type"],
                    job.get("dataset_id"),
                    JobStatus.QUEUED.value,
                    now,
                    now,
                    int(bool(job.get("requested_result_bundle", True))),
                    _json_dumps(job.get("manifest", {})),
                    _json_dumps(metadata),
                    _json_dumps([]),
                    None,
                ),
            )
            old_event_index = self.store._next_event_index(connection, job_id)
            connection.execute(
                "INSERT INTO job_events (job_id, event_index, event_time, event_name, details_json) VALUES (?, ?, ?, ?, ?)",
                (job_id, old_event_index, now, "api_retry_requested", _json_dumps({"retry_job_id": new_job_id, "reason": reason})),
            )
            connection.execute(
                "INSERT INTO job_events (job_id, event_index, event_time, event_name, details_json) VALUES (?, ?, ?, ?, ?)",
                (new_job_id, 0, now, "api_retry_queued", _json_dumps({"retry_of": job_id, "reason": reason})),
            )
            connection.commit()
        return SchedulerActionV527("retry", True, JobStatus.QUEUED.value, job_id, related_job_id=new_job_id)

    def worker_step(self, worker_id: str = "api_worker_v527") -> dict[str, Any]:
        return run_worker_once_v526(self.store, self.result_dir, worker_id).to_dict()


def make_scheduler_api_app_v527(db_path: str | Path, result_dir: str | Path | None = None):
    if FastAPI is None:  # pragma: no cover
        raise RuntimeError("FastAPI is not installed")
    facade = SchedulerAPIFacadeV527(db_path, result_dir)
    app = FastAPI(title="BioGPU-Core Local Scheduler API Facade", version="5.27.0")

    @app.get("/health")
    def health() -> dict[str, Any]:
        return facade.health()

    @app.get("/v1/scheduler/jobs")
    def list_jobs(status: str | None = None) -> dict[str, Any]:
        return {"jobs": facade.list_jobs(status)}

    @app.get("/v1/scheduler/jobs/{job_id}")
    def get_job(job_id: str) -> dict[str, Any]:
        try:
            return facade.get_job(job_id)
        except KeyError:
            raise HTTPException(status_code=404, detail="job_not_found")

    @app.post("/v1/scheduler/jobs/{job_id}/cancel")
    def cancel_job(job_id: str, req: CancelRequestV527 | None = None) -> dict[str, Any]:
        return facade.cancel_job(job_id, reason=(req.reason if req else "user_requested_cancel")).to_dict()

    @app.post("/v1/scheduler/jobs/{job_id}/retry")
    def retry_job(job_id: str, req: RetryRequestV527 | None = None) -> dict[str, Any]:
        return facade.retry_job(job_id, reason=(req.reason if req else "retry_requested")).to_dict()

    @app.post("/v1/scheduler/timeouts/scan")
    def timeout_scan(req: TimeoutScanRequestV527 | None = None) -> dict[str, Any]:
        max_age = req.max_running_age_seconds if req else 0
        return {"actions": [action.to_dict() for action in facade.timeout_running_jobs(max_age)]}

    @app.post("/v1/scheduler/workers/{worker_id}/step")
    def worker_step(worker_id: str) -> dict[str, Any]:
        return facade.worker_step(worker_id)

    return app


def scheduler_api_route_manifest_v527(app: Any) -> list[dict[str, Any]]:
    routes: list[dict[str, Any]] = []
    for route in getattr(app, "routes", []):
        path = getattr(route, "path", "")
        methods = sorted(str(method) for method in getattr(route, "methods", set()) if method not in {"HEAD", "OPTIONS"})
        if path and methods:
            routes.append({"path": path, "methods": methods})
    return sorted(routes, key=lambda item: item["path"])


def run_scheduler_api_facade_workflow_v527(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    project_root = Path(root).resolve()
    out = project_root / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    db_path = out / DEFAULT_DB_NAME
    if db_path.exists():
        db_path.unlink()
    enqueue = enqueue_reference_jobs_v526(db_path)
    facade = SchedulerAPIFacadeV527(db_path, out / "api_worker_results")
    app = make_scheduler_api_app_v527(db_path, out / "api_worker_results")
    route_manifest = scheduler_api_route_manifest_v527(app)
    health_before = facade.health()
    queued = facade.list_jobs(JobStatus.QUEUED.value)
    cancel_action = facade.cancel_job(queued[0]["job_id"], reason="v527_cancel_semantics_probe") if queued else SchedulerActionV527("cancel", False, "no_queued_job", None)
    remaining = facade.store.claim_next_job("v527_timeout_probe_worker")
    timeout_actions = facade.timeout_running_jobs(max_running_age_seconds=0)
    timed_out_job_id = timeout_actions[0].job_id if timeout_actions else (remaining["job_id"] if remaining else None)
    retry_action = facade.retry_job(timed_out_job_id, reason="v527_retry_after_timeout_probe") if timed_out_job_id else SchedulerActionV527("retry", False, "no_timed_out_job", None)
    worker_actions: list[dict[str, Any]] = []
    while True:
        action = facade.worker_step("api_worker_v527")
        worker_actions.append(action)
        if action["status"] == "idle_no_queued_jobs":
            break
    jobs = facade.list_jobs()
    events = facade.store.list_events()
    health_after = facade.health()
    status_counts = health_after["status_counts"]
    timed_out_count = sum(1 for event in events if event["event"] == "api_timed_out")
    retry_count = sum(1 for event in events if event["event"] == "api_retry_queued")
    blocked_submission_count = sum(1 for submission in enqueue["submissions"].values() if not submission["admission"]["accepted"])
    worker_succeeded_count = sum(1 for action in worker_actions if action.get("status") == "succeeded")
    proof_ready = (
        len(route_manifest) >= 7
        and cancel_action.accepted
        and timed_out_count >= 1
        and retry_action.accepted
        and worker_succeeded_count >= 1
        and int(status_counts.get(JobStatus.CANCELLED.value, 0)) >= 1
        and int(status_counts.get(JobStatus.SUCCEEDED.value, 0)) >= 1
        and blocked_submission_count >= 1
    )
    return {
        "version": "v5.27",
        "phase": "scheduler_api_facade_retry_cancel_timeout",
        "overall_status": "scheduler_api_facade_semantics_ready_runtime_not_claimed" if proof_ready else "scheduler_api_facade_semantics_incomplete",
        "active_phase": "biocompute_runtime_scheduler_api_proof",
        "bic_os_phase_locked": True,
        "scheduler_api_facade_ready": proof_ready,
        "production_api_ready": False,
        "production_scheduler_ready": False,
        "production_biocompute_runtime_ready": False,
        "full_biosdk_ready": False,
        "live_actuation_enabled": False,
        "db_path": str(db_path.relative_to(project_root)).replace("\\", "/") if db_path.is_relative_to(project_root) else str(db_path),
        "api_route_count": len(route_manifest),
        "persisted_job_count": len(enqueue["persisted_jobs"]),
        "blocked_submission_count": blocked_submission_count,
        "cancel_semantics_passed": cancel_action.accepted,
        "timeout_semantics_passed": timed_out_count >= 1,
        "retry_semantics_passed": retry_action.accepted,
        "worker_step_semantics_passed": worker_succeeded_count >= 1,
        "final_status_counts": status_counts,
        "health_before": health_before,
        "health_after": health_after,
        "route_manifest": route_manifest,
        "actions": {
            "cancel": cancel_action.to_dict(),
            "timeout": [action.to_dict() for action in timeout_actions],
            "retry": retry_action.to_dict(),
            "worker_steps": worker_actions,
        },
        "jobs": jobs,
        "events": events,
        "remaining_api_blockers": [
            "authenticated HTTP service process and deployment configuration",
            "multi-worker concurrency policy with retry backoff and dead-letter queue",
            "job cancellation propagation into long-running workers",
            "timeout policy tied to tier quotas instead of a local proof threshold",
            "production object storage for result bundles and audit retention",
        ],
        "direct_answer": {
            "did_we_close_retry_cancel_timeout_proof": "yes" if proof_ready else "not_yet",
            "is_production_api_ready": "no",
            "is_biocompute_runtime_ready": "no",
            "is_bic_os_ready": "no",
            "next_best_build_step": "add authenticated local service process plus result-bundle download contract" if proof_ready else "fix scheduler API facade proof blockers first",
        },
        "claim_boundary": "v5.27 proves local scheduler API semantics for list/get/cancel/retry/timeout/worker-step over the durable queue. It does not claim a production API server, hosted BioCompute Runtime, live external API control, closed-loop wetware operation or BiC OS readiness.",
    }


def write_scheduler_api_facade_outputs_v527(audit: dict[str, Any], out_dir: str | Path = DEFAULT_OUT) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary_json": out / "V527_SCHEDULER_API_FACADE_SUMMARY.json",
        "routes_json": out / "V527_SCHEDULER_API_ROUTES.json",
        "actions_json": out / "V527_SCHEDULER_API_ACTIONS.json",
        "jobs_json": out / "V527_SCHEDULER_API_JOBS.json",
        "events_json": out / "V527_SCHEDULER_API_EVENTS.json",
        "jobs_csv": out / "V527_SCHEDULER_API_JOBS.csv",
        "markdown_report": out / "BIOGPU_V527_SCHEDULER_API_FACADE_REPORT.md",
    }
    summary = {key: value for key, value in audit.items() if key not in {"route_manifest", "actions", "jobs", "events"}}
    paths["summary_json"].write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["routes_json"].write_text(json.dumps({"routes": audit["route_manifest"]}, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["actions_json"].write_text(json.dumps(audit["actions"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["jobs_json"].write_text(json.dumps({"jobs": audit["jobs"]}, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["events_json"].write_text(json.dumps({"events": audit["events"]}, indent=2, ensure_ascii=False), encoding="utf-8")
    _write_jobs_csv(paths["jobs_csv"], audit["jobs"])
    paths["markdown_report"].write_text(_markdown_report(audit), encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}


def _write_jobs_csv(path: Path, jobs: list[dict[str, Any]]) -> None:
    fieldnames = ["job_id", "job_type", "dataset_id", "status", "retry_of", "retry_attempt", "validation_errors"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for job in jobs:
            metadata = job.get("metadata") or {}
            writer.writerow({
                "job_id": job.get("job_id"),
                "job_type": job.get("job_type"),
                "dataset_id": job.get("dataset_id"),
                "status": job.get("status"),
                "retry_of": metadata.get("retry_of") if isinstance(metadata, dict) else "",
                "retry_attempt": metadata.get("retry_attempt") if isinstance(metadata, dict) else "",
                "validation_errors": " | ".join(str(item) for item in job.get("validation_errors", [])),
            })


def _markdown_report(audit: dict[str, Any]) -> str:
    answer = audit["direct_answer"]
    lines = [
        "# BioGPU-Core v5.27 Scheduler API Facade",
        "",
        "## Direct Answer",
        "",
        f"- Retry/cancel/timeout proof closed: `{answer['did_we_close_retry_cancel_timeout_proof']}`",
        f"- Production API ready: `{answer['is_production_api_ready']}`",
        f"- BioCompute Runtime ready: `{answer['is_biocompute_runtime_ready']}`",
        f"- BiC OS ready: `{answer['is_bic_os_ready']}`",
        f"- Next best build step: {answer['next_best_build_step']}",
        "",
        "## Summary",
        "",
        f"- API routes: `{audit['api_route_count']}`",
        f"- Cancel semantics passed: `{audit['cancel_semantics_passed']}`",
        f"- Timeout semantics passed: `{audit['timeout_semantics_passed']}`",
        f"- Retry semantics passed: `{audit['retry_semantics_passed']}`",
        f"- Worker step semantics passed: `{audit['worker_step_semantics_passed']}`",
        f"- Final status counts: `{audit['final_status_counts']}`",
        "",
        "## Remaining API Blockers",
        "",
    ]
    for blocker in audit["remaining_api_blockers"]:
        lines.append(f"- {blocker}")
    lines.extend(["", "## Boundary", "", audit["claim_boundary"], ""])
    return "\n".join(lines)