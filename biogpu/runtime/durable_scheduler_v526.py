"""Durable local scheduler and worker proof, v5.26."""
from __future__ import annotations

import csv
import hashlib
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from biogpu.beta.control_plane_v55 import default_control_plane_contexts_v55, submit_agent_request_to_queue_v55
from biogpu.beta.job_model_v43 import BioGPUJobRecordV43, JobStatus, find_unsafe_fields, utc_now_iso
from biogpu.llm.agent_bridge_v54 import reference_agent_requests_v54


DEFAULT_OUT = Path("outputs/v526_durable_scheduler_worker")
DEFAULT_DB_NAME = "V526_DURABLE_SCHEDULER.sqlite3"


@dataclass(frozen=True)
class WorkerExecutionV526:
    worker_id: str
    job_id: str | None
    status: str
    result_uri: str | None
    errors: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "worker_id": self.worker_id,
            "job_id": self.job_id,
            "status": self.status,
            "result_uri": self.result_uri,
            "errors": list(self.errors),
        }


def _json_dumps(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, ensure_ascii=True)


def _json_loads(text: str | None, default: Any) -> Any:
    if not text:
        return default
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return default


class DurableSchedulerStoreV526:
    """Small SQLite-backed job store for local scheduler proof."""

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _ensure_schema(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id TEXT PRIMARY KEY,
                    workspace_id TEXT NOT NULL,
                    created_by TEXT NOT NULL,
                    job_type TEXT NOT NULL,
                    dataset_id TEXT,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    requested_result_bundle INTEGER NOT NULL,
                    manifest_json TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    validation_errors_json TEXT NOT NULL,
                    result_bundle_json TEXT
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS job_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT NOT NULL,
                    event_index INTEGER NOT NULL,
                    event_time TEXT NOT NULL,
                    event_name TEXT NOT NULL,
                    details_json TEXT NOT NULL,
                    FOREIGN KEY(job_id) REFERENCES jobs(job_id)
                )
                """
            )
            connection.execute("CREATE INDEX IF NOT EXISTS idx_jobs_status_created ON jobs(status, created_at)")

    def persist_job_record(self, record: BioGPUJobRecordV43) -> dict[str, Any]:
        payload = record.to_dict()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO jobs (
                    job_id, workspace_id, created_by, job_type, dataset_id, status, created_at, updated_at,
                    requested_result_bundle, manifest_json, metadata_json, validation_errors_json, result_bundle_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.job_id,
                    record.workspace_id,
                    record.created_by,
                    record.spec.job_type.value,
                    record.spec.dataset_id,
                    record.status.value,
                    record.created_at,
                    record.updated_at,
                    int(record.spec.requested_result_bundle),
                    _json_dumps(record.spec.manifest),
                    _json_dumps(record.spec.metadata),
                    _json_dumps(record.validation_errors),
                    _json_dumps(record.result_bundle.__dict__) if record.result_bundle else None,
                ),
            )
            connection.execute("DELETE FROM job_events WHERE job_id = ?", (record.job_id,))
            for index, event in enumerate(record.audit_events):
                connection.execute(
                    "INSERT INTO job_events (job_id, event_index, event_time, event_name, details_json) VALUES (?, ?, ?, ?, ?)",
                    (record.job_id, index, str(event.get("time")), str(event.get("event")), _json_dumps(event.get("details", {}))),
                )
        return payload

    def list_jobs(self, status: str | None = None) -> list[dict[str, Any]]:
        query = "SELECT * FROM jobs"
        args: tuple[Any, ...] = tuple()
        if status:
            query += " WHERE status = ?"
            args = (status,)
        query += " ORDER BY created_at, job_id"
        with self._connect() as connection:
            rows = connection.execute(query, args).fetchall()
        return [self._row_to_job(row) for row in rows]

    def list_events(self) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute("SELECT * FROM job_events ORDER BY job_id, event_index, event_id").fetchall()
        return [
            {
                "job_id": str(row["job_id"]),
                "event_index": int(row["event_index"]),
                "time": str(row["event_time"]),
                "event": str(row["event_name"]),
                "details": _json_loads(row["details_json"], {}),
            }
            for row in rows
        ]

    def claim_next_job(self, worker_id: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute("SELECT * FROM jobs WHERE status = ? ORDER BY created_at, job_id LIMIT 1", (JobStatus.QUEUED.value,)).fetchone()
            if row is None:
                connection.commit()
                return None
            now = utc_now_iso()
            connection.execute("UPDATE jobs SET status = ?, updated_at = ? WHERE job_id = ?", (JobStatus.RUNNING.value, now, row["job_id"]))
            event_index = self._next_event_index(connection, str(row["job_id"]))
            connection.execute(
                "INSERT INTO job_events (job_id, event_index, event_time, event_name, details_json) VALUES (?, ?, ?, ?, ?)",
                (row["job_id"], event_index, now, "worker_claimed", _json_dumps({"worker_id": worker_id})),
            )
            connection.commit()
        claimed = self.get_job(str(row["job_id"]))
        return claimed

    def complete_job(self, job_id: str, worker_id: str, result_uri: str, checksum: str) -> dict[str, Any]:
        now = utc_now_iso()
        result_bundle = {
            "bundle_id": "bundle_" + hashlib.sha256(f"{job_id}:{checksum}".encode("utf-8")).hexdigest()[:16],
            "job_id": job_id,
            "uri": result_uri,
            "created_at": now,
            "content_type": "application/json",
            "checksum": checksum,
        }
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute(
                "UPDATE jobs SET status = ?, updated_at = ?, result_bundle_json = ? WHERE job_id = ?",
                (JobStatus.SUCCEEDED.value, now, _json_dumps(result_bundle), job_id),
            )
            event_index = self._next_event_index(connection, job_id)
            connection.execute(
                "INSERT INTO job_events (job_id, event_index, event_time, event_name, details_json) VALUES (?, ?, ?, ?, ?)",
                (job_id, event_index, now, "worker_completed", _json_dumps({"worker_id": worker_id, "result_uri": result_uri, "checksum": checksum})),
            )
            connection.commit()
        return self.get_job(job_id)

    def fail_job(self, job_id: str, worker_id: str, errors: list[str]) -> dict[str, Any]:
        now = utc_now_iso()
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute("UPDATE jobs SET status = ?, updated_at = ? WHERE job_id = ?", (JobStatus.FAILED.value, now, job_id))
            event_index = self._next_event_index(connection, job_id)
            connection.execute(
                "INSERT INTO job_events (job_id, event_index, event_time, event_name, details_json) VALUES (?, ?, ?, ?, ?)",
                (job_id, event_index, now, "worker_failed", _json_dumps({"worker_id": worker_id, "errors": errors})),
            )
            connection.commit()
        return self.get_job(job_id)

    def get_job(self, job_id: str) -> dict[str, Any]:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,)).fetchone()
        if row is None:
            raise KeyError(job_id)
        return self._row_to_job(row)

    def _next_event_index(self, connection: sqlite3.Connection, job_id: str) -> int:
        row = connection.execute("SELECT COALESCE(MAX(event_index), -1) + 1 AS next_index FROM job_events WHERE job_id = ?", (job_id,)).fetchone()
        return int(row["next_index"])

    def _row_to_job(self, row: sqlite3.Row) -> dict[str, Any]:
        return {
            "job_id": str(row["job_id"]),
            "workspace_id": str(row["workspace_id"]),
            "created_by": str(row["created_by"]),
            "job_type": str(row["job_type"]),
            "dataset_id": row["dataset_id"],
            "status": str(row["status"]),
            "created_at": str(row["created_at"]),
            "updated_at": str(row["updated_at"]),
            "requested_result_bundle": bool(row["requested_result_bundle"]),
            "manifest": _json_loads(row["manifest_json"], {}),
            "metadata": _json_loads(row["metadata_json"], {}),
            "validation_errors": _json_loads(row["validation_errors_json"], []),
            "result_bundle": _json_loads(row["result_bundle_json"], None),
        }


def enqueue_reference_jobs_v526(db_path: str | Path) -> dict[str, Any]:
    contexts = default_control_plane_contexts_v55()
    requests = reference_agent_requests_v54()
    from biogpu.beta.job_model_v43 import InMemoryJobStoreV43

    memory_store = InMemoryJobStoreV43()
    submissions = {
        "safe_replay": submit_agent_request_to_queue_v55(requests["safe_replay"], contexts["researcher"], memory_store).to_dict(),
        "live_shadow_allowed": submit_agent_request_to_queue_v55(requests["live_shadow_with_approval"], contexts["enterprise_live_shadow"], memory_store).to_dict(),
        "blocked_actuation": submit_agent_request_to_queue_v55(requests["blocked_actuation"], contexts["researcher"], memory_store).to_dict(),
    }
    store = DurableSchedulerStoreV526(db_path)
    persisted = [store.persist_job_record(record) for record in memory_store.list_jobs() if record.status == JobStatus.QUEUED]
    return {"submissions": submissions, "persisted_jobs": persisted}


def run_worker_until_idle_v526(db_path: str | Path, result_dir: str | Path, worker_id: str = "local_worker_v526") -> list[dict[str, Any]]:
    store = DurableSchedulerStoreV526(db_path)
    results: list[dict[str, Any]] = []
    while True:
        execution = run_worker_once_v526(store, result_dir, worker_id)
        results.append(execution.to_dict())
        if execution.status == "idle_no_queued_jobs":
            break
    return results


def run_worker_once_v526(store: DurableSchedulerStoreV526, result_dir: str | Path, worker_id: str = "local_worker_v526") -> WorkerExecutionV526:
    job = store.claim_next_job(worker_id)
    if job is None:
        return WorkerExecutionV526(worker_id=worker_id, job_id=None, status="idle_no_queued_jobs", result_uri=None, errors=tuple())
    unsafe = find_unsafe_fields(job.get("manifest", {}))
    if unsafe:
        store.fail_job(job["job_id"], worker_id, ["unsafe_manifest_fields:" + ",".join(unsafe)])
        return WorkerExecutionV526(worker_id=worker_id, job_id=job["job_id"], status="failed_safety_scan", result_uri=None, errors=tuple(unsafe))
    result_path = Path(result_dir) / f"{job['job_id']}_result.json"
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_payload = {
        "version": "v5.26",
        "job_id": job["job_id"],
        "job_type": job["job_type"],
        "worker_id": worker_id,
        "execution_mode": "local_durable_replay_proof",
        "live_actuation_enabled": False,
        "result_status": "simulated_safe_execution_succeeded",
        "manifest_id": job.get("manifest", {}).get("manifest_id"),
        "dataset_id": job.get("dataset_id"),
        "claim_boundary": "This worker writes a local proof artifact only; it does not execute live wetware control or production runtime services.",
    }
    result_path.write_text(json.dumps(result_payload, indent=2, ensure_ascii=False), encoding="utf-8")
    checksum = hashlib.sha256(result_path.read_bytes()).hexdigest()
    completed = store.complete_job(job["job_id"], worker_id, str(result_path).replace("\\", "/"), checksum)
    return WorkerExecutionV526(
        worker_id=worker_id,
        job_id=job["job_id"],
        status="succeeded" if completed["status"] == JobStatus.SUCCEEDED.value else completed["status"],
        result_uri=str(result_path).replace("\\", "/"),
        errors=tuple(),
    )


def run_durable_scheduler_workflow_v526(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    project_root = Path(root).resolve()
    out = project_root / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    db_path = out / DEFAULT_DB_NAME
    if db_path.exists():
        db_path.unlink()
    enqueue = enqueue_reference_jobs_v526(db_path)
    restarted_store = DurableSchedulerStoreV526(db_path)
    queued_after_restart = restarted_store.list_jobs(JobStatus.QUEUED.value)
    executions = run_worker_until_idle_v526(db_path, out / "worker_results")
    final_store = DurableSchedulerStoreV526(db_path)
    final_jobs = final_store.list_jobs()
    events = final_store.list_events()
    succeeded = [job for job in final_jobs if job["status"] == JobStatus.SUCCEEDED.value]
    failed = [job for job in final_jobs if job["status"] == JobStatus.FAILED.value]
    result_bundle_count = sum(1 for job in final_jobs if job.get("result_bundle"))
    blocked_submission_count = sum(1 for submission in enqueue["submissions"].values() if not submission["admission"]["accepted"])
    proof_ready = len(queued_after_restart) >= 2 and len(succeeded) == len(final_jobs) >= 2 and not failed and result_bundle_count == len(succeeded) and blocked_submission_count >= 1
    return {
        "version": "v5.26",
        "phase": "durable_scheduler_worker_proof",
        "overall_status": "durable_scheduler_worker_proof_ready_runtime_not_claimed" if proof_ready else "durable_scheduler_worker_proof_incomplete",
        "active_phase": "biocompute_runtime_scheduler_proof",
        "bic_os_phase_locked": True,
        "durable_scheduler_worker_proof_ready": proof_ready,
        "production_scheduler_ready": False,
        "production_biocompute_runtime_ready": False,
        "full_biosdk_ready": False,
        "live_actuation_enabled": False,
        "db_path": str(db_path.relative_to(project_root)).replace("\\", "/") if db_path.is_relative_to(project_root) else str(db_path),
        "persisted_job_count": len(enqueue["persisted_jobs"]),
        "queued_after_restart_count": len(queued_after_restart),
        "worker_execution_count": len([item for item in executions if item["job_id"]]),
        "succeeded_job_count": len(succeeded),
        "failed_job_count": len(failed),
        "result_bundle_count": result_bundle_count,
        "blocked_submission_count": blocked_submission_count,
        "submissions": enqueue["submissions"],
        "jobs": final_jobs,
        "events": events,
        "worker_executions": executions,
        "remaining_runtime_blockers": [
            "multi-worker locking and retry policy beyond the local proof loop",
            "durable API server integration and auth-backed user/workspace contexts",
            "job cancellation, timeout and retention policy",
            "production result-bundle storage instead of local JSON files",
            "observability, dashboards and deployment packaging",
        ],
        "direct_answer": {
            "did_we_close_first_durable_scheduler_proof": "yes" if proof_ready else "not_yet",
            "is_production_scheduler_ready": "no",
            "is_biocompute_runtime_ready": "no",
            "is_bic_os_ready": "no",
            "next_best_build_step": "add retry/cancel/timeout semantics and a small local API facade over the durable queue" if proof_ready else "fix durable scheduler proof blockers first",
        },
        "claim_boundary": "v5.26 proves a local persisted scheduler/worker lifecycle for safe replay/read-only jobs. It does not claim production scheduling, hosted BioCompute Runtime, live API control, closed-loop wetware operation or BiC OS readiness.",
    }


def write_durable_scheduler_outputs_v526(audit: dict[str, Any], out_dir: str | Path = DEFAULT_OUT) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary_json": out / "V526_DURABLE_SCHEDULER_WORKER_SUMMARY.json",
        "submissions_json": out / "V526_DURABLE_SCHEDULER_SUBMISSIONS.json",
        "jobs_json": out / "V526_DURABLE_SCHEDULER_JOBS.json",
        "jobs_csv": out / "V526_DURABLE_SCHEDULER_JOBS.csv",
        "events_json": out / "V526_DURABLE_SCHEDULER_EVENTS.json",
        "worker_executions_json": out / "V526_DURABLE_WORKER_EXECUTIONS.json",
        "markdown_report": out / "BIOGPU_V526_DURABLE_SCHEDULER_WORKER_REPORT.md",
    }
    summary = {key: value for key, value in audit.items() if key not in {"submissions", "jobs", "events", "worker_executions"}}
    paths["summary_json"].write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["submissions_json"].write_text(json.dumps(audit["submissions"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["jobs_json"].write_text(json.dumps({"jobs": audit["jobs"]}, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["events_json"].write_text(json.dumps({"events": audit["events"]}, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["worker_executions_json"].write_text(json.dumps({"worker_executions": audit["worker_executions"]}, indent=2, ensure_ascii=False), encoding="utf-8")
    _write_jobs_csv(paths["jobs_csv"], audit["jobs"])
    paths["markdown_report"].write_text(_markdown_report(audit), encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}


def _write_jobs_csv(path: Path, jobs: list[dict[str, Any]]) -> None:
    fieldnames = ["job_id", "workspace_id", "created_by", "job_type", "dataset_id", "status", "result_bundle_uri", "validation_errors"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for job in jobs:
            bundle = job.get("result_bundle") or {}
            writer.writerow({
                "job_id": job.get("job_id"),
                "workspace_id": job.get("workspace_id"),
                "created_by": job.get("created_by"),
                "job_type": job.get("job_type"),
                "dataset_id": job.get("dataset_id"),
                "status": job.get("status"),
                "result_bundle_uri": bundle.get("uri") if isinstance(bundle, dict) else "",
                "validation_errors": " | ".join(str(item) for item in job.get("validation_errors", [])),
            })


def _markdown_report(audit: dict[str, Any]) -> str:
    answer = audit["direct_answer"]
    lines = [
        "# BioGPU-Core v5.26 Durable Scheduler Worker Proof",
        "",
        "## Direct Answer",
        "",
        f"- Durable scheduler proof closed: `{answer['did_we_close_first_durable_scheduler_proof']}`",
        f"- Production scheduler ready: `{answer['is_production_scheduler_ready']}`",
        f"- BioCompute Runtime ready: `{answer['is_biocompute_runtime_ready']}`",
        f"- BiC OS ready: `{answer['is_bic_os_ready']}`",
        f"- Next best build step: {answer['next_best_build_step']}",
        "",
        "## Summary",
        "",
        f"- Persisted jobs: `{audit['persisted_job_count']}`",
        f"- Queued after restart: `{audit['queued_after_restart_count']}`",
        f"- Worker executions: `{audit['worker_execution_count']}`",
        f"- Succeeded jobs: `{audit['succeeded_job_count']}`",
        f"- Result bundles: `{audit['result_bundle_count']}`",
        f"- Blocked submissions: `{audit['blocked_submission_count']}`",
        "",
        "## Remaining Runtime Blockers",
        "",
    ]
    for blocker in audit["remaining_runtime_blockers"]:
        lines.append(f"- {blocker}")
    lines.extend(["", "## Boundary", "", audit["claim_boundary"], ""])
    return "\n".join(lines)