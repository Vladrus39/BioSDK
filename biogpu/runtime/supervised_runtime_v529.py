"""Supervised local runtime lifecycle proof, v5.29."""
from __future__ import annotations

import csv
import hashlib
import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from biogpu.beta.job_model_v43 import JobStatus, utc_now_iso
from biogpu.runtime.durable_scheduler_v526 import enqueue_reference_jobs_v526
from biogpu.runtime.local_service_v528 import AuthenticatedLocalServiceV528, LocalServicePrincipalV528, V528_DEVELOPER_API_KEY, V528_WORKER_API_KEY


DEFAULT_OUT = Path("outputs/v529_supervised_local_runtime")
DEFAULT_DB_NAME = "V529_SUPERVISED_LOCAL_RUNTIME.sqlite3"
DEFAULT_RUNTIME_ID = "biogpu_local_runtime_v529"
DEFAULT_WORKER_ID = "supervised_worker_v529"


@dataclass(frozen=True)
class RuntimeLifecycleEventV529:
    action: str
    accepted: bool
    status: str
    runtime_id: str
    process_id: int
    heartbeat_index: int
    errors: tuple[str, ...] = tuple()
    payload: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class SupervisedLocalRuntimeV529:
    """Deterministic local supervisor over the v5.28 authenticated service."""

    def __init__(self, out_dir: str | Path = DEFAULT_OUT, runtime_id: str = DEFAULT_RUNTIME_ID, worker_id: str = DEFAULT_WORKER_ID) -> None:
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.runtime_id = runtime_id
        self.worker_id = worker_id
        self.process_id = os.getpid()
        self.db_path = self.out_dir / DEFAULT_DB_NAME
        self.result_dir = self.out_dir / "supervised_worker_results"
        self.state_path = self.out_dir / "V529_RUNTIME_STATE.json"
        self.heartbeat_path = self.out_dir / "V529_RUNTIME_HEARTBEAT.json"
        self.audit_log_path = self.out_dir / "V529_RUNTIME_AUDIT_LOG.jsonl"
        self.audit_export_path = self.out_dir / "V529_RUNTIME_AUDIT_EXPORT.json"
        self._service_facade: AuthenticatedLocalServiceV528 | None = None

    @property
    def service(self) -> AuthenticatedLocalServiceV528:
        if self._service_facade is None:
            self._service_facade = AuthenticatedLocalServiceV528(self.db_path, self.result_dir)
        return self._service_facade

    def reset(self) -> None:
        for path in (self.db_path, self.state_path, self.heartbeat_path, self.audit_log_path, self.audit_export_path):
            if path.exists():
                path.unlink()
        if self.result_dir.exists():
            for child in self.result_dir.glob("*_result.json"):
                child.unlink()
        self._service_facade = None

    def start(self, api_key: str = V528_WORKER_API_KEY, reset: bool = True) -> RuntimeLifecycleEventV529:
        if reset:
            self.reset()
        self._service_facade = AuthenticatedLocalServiceV528(self.db_path, self.result_dir)
        existing = self._load_state()
        if existing.get("status") == "running":
            return self._event("runtime_start", False, "already_running", errors=("already_running",), payload=existing)
        auth_error = self._require_worker_principal(api_key, "runtime_start")
        if isinstance(auth_error, RuntimeLifecycleEventV529):
            return auth_error
        enqueue = enqueue_reference_jobs_v526(self.db_path)
        self._service_facade = AuthenticatedLocalServiceV528(self.db_path, self.result_dir)
        now = utc_now_iso()
        state = {
            "version": "v5.29",
            "runtime_id": self.runtime_id,
            "status": "running",
            "process_id": self.process_id,
            "worker_id": self.worker_id,
            "started_at": now,
            "updated_at": now,
            "stopped_at": None,
            "heartbeat_index": 0,
            "last_heartbeat_at": now,
            "graceful_shutdown_requested": False,
            "supervised_runtime_contract_ready": True,
            "production_runtime_ready": False,
            "production_service_supervision_ready": False,
            "live_actuation_enabled": False,
            "bic_os_phase_locked": True,
        }
        self._write_state(state)
        self._write_heartbeat(state, "runtime_start")
        payload = {"state": state, "persisted_job_count": len(enqueue["persisted_jobs"]), "blocked_submission_count": _blocked_submission_count(enqueue)}
        self._append_audit("runtime_started", payload)
        return self._event("runtime_start", True, "running", payload=payload)

    def heartbeat(self, api_key: str = V528_WORKER_API_KEY) -> RuntimeLifecycleEventV529:
        auth_error = self._require_worker_principal(api_key, "heartbeat")
        if isinstance(auth_error, RuntimeLifecycleEventV529):
            return auth_error
        state = self._load_state()
        if state.get("status") != "running":
            return self._event("heartbeat", False, "runtime_not_running", errors=("runtime_not_running",), payload=state)
        state = self._advance_heartbeat(state, "heartbeat")
        self._append_audit("runtime_heartbeat", {"heartbeat_index": state["heartbeat_index"], "status": state["status"]})
        return self._event("heartbeat", True, "running", payload=state)

    def worker_tick(self, api_key: str = V528_WORKER_API_KEY) -> RuntimeLifecycleEventV529:
        auth_error = self._require_worker_principal(api_key, "worker_tick")
        if isinstance(auth_error, RuntimeLifecycleEventV529):
            return auth_error
        state = self._load_state()
        if state.get("status") != "running":
            return self._event("worker_tick", False, "runtime_not_running", errors=("runtime_not_running",), payload=state)
        operation = self.service.worker_step(api_key, self.worker_id)
        state = self._advance_heartbeat(state, "worker_tick")
        accepted = operation.status in {JobStatus.SUCCEEDED.value, "idle_no_queued_jobs"}
        payload = {"operation": operation.to_dict(), "state": state}
        self._append_audit("worker_tick", payload)
        return self._event("worker_tick", accepted, operation.status, errors=operation.errors, payload=payload)

    def graceful_shutdown(self, api_key: str = V528_WORKER_API_KEY, reason: str = "requested_by_supervisor") -> RuntimeLifecycleEventV529:
        auth_error = self._require_worker_principal(api_key, "graceful_shutdown")
        if isinstance(auth_error, RuntimeLifecycleEventV529):
            return auth_error
        state = self._load_state()
        if state.get("status") != "running":
            return self._event("graceful_shutdown", False, "runtime_not_running", errors=("runtime_not_running",), payload=state)
        state = self._advance_heartbeat(state, "shutdown_requested")
        state["status"] = "stopped"
        state["graceful_shutdown_requested"] = True
        state["stopped_at"] = utc_now_iso()
        state["updated_at"] = state["stopped_at"]
        self._write_state(state)
        self._write_heartbeat(state, "runtime_stopped")
        payload = {"reason": reason, "state": state}
        self._append_audit("runtime_stopped", payload)
        return self._event("graceful_shutdown", True, "stopped", payload=payload)

    def export_audit_log(self, api_key: str = V528_DEVELOPER_API_KEY) -> RuntimeLifecycleEventV529:
        principal = self._require_principal(api_key, "audit_export")
        if isinstance(principal, RuntimeLifecycleEventV529):
            return principal
        events = self.read_audit_events()
        event_bytes = "\n".join(json.dumps(event, sort_keys=True, ensure_ascii=True) for event in events).encode("utf-8")
        audit_hash = hashlib.sha256(event_bytes).hexdigest()
        export = {
            "version": "v5.29",
            "runtime_id": self.runtime_id,
            "exported_by": principal.key_id,
            "exported_at": utc_now_iso(),
            "event_count": len(events),
            "audit_sha256": audit_hash,
            "state": self._load_state(),
            "events": events,
            "production_audit_retention_ready": False,
        }
        self.audit_export_path.write_text(json.dumps(export, indent=2, ensure_ascii=False), encoding="utf-8")
        self._append_audit("audit_exported", {"export_path": str(self.audit_export_path).replace("\\", "/"), "event_count": len(events), "audit_sha256": audit_hash})
        return self._event("audit_export", True, "audit_exported", payload=export)

    def read_audit_events(self) -> list[dict[str, Any]]:
        if not self.audit_log_path.exists():
            return []
        events: list[dict[str, Any]] = []
        for line in self.audit_log_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                events.append(json.loads(line))
        return events

    def _load_state(self) -> dict[str, Any]:
        if not self.state_path.exists():
            return {"runtime_id": self.runtime_id, "status": "not_started", "process_id": self.process_id, "heartbeat_index": -1}
        return json.loads(self.state_path.read_text(encoding="utf-8"))

    def _write_state(self, state: dict[str, Any]) -> None:
        self.state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")

    def _write_heartbeat(self, state: dict[str, Any], source: str) -> None:
        heartbeat = {
            "version": "v5.29",
            "runtime_id": self.runtime_id,
            "process_id": self.process_id,
            "worker_id": self.worker_id,
            "source": source,
            "status": state.get("status"),
            "heartbeat_index": state.get("heartbeat_index"),
            "last_heartbeat_at": state.get("last_heartbeat_at"),
            "production_runtime_ready": False,
            "bic_os_phase_locked": True,
        }
        self.heartbeat_path.write_text(json.dumps(heartbeat, indent=2, ensure_ascii=False), encoding="utf-8")

    def _advance_heartbeat(self, state: dict[str, Any], source: str) -> dict[str, Any]:
        updated = dict(state)
        updated["heartbeat_index"] = int(updated.get("heartbeat_index", -1)) + 1
        updated["last_heartbeat_at"] = utc_now_iso()
        updated["updated_at"] = updated["last_heartbeat_at"]
        self._write_state(updated)
        self._write_heartbeat(updated, source)
        return updated

    def _append_audit(self, event_name: str, details: dict[str, Any]) -> None:
        event = {
            "version": "v5.29",
            "runtime_id": self.runtime_id,
            "process_id": self.process_id,
            "time": utc_now_iso(),
            "event": event_name,
            "details": details,
            "live_actuation_enabled": False,
        }
        with self.audit_log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, sort_keys=True, ensure_ascii=False) + "\n")

    def _event(self, action: str, accepted: bool, status: str, errors: tuple[str, ...] = tuple(), payload: dict[str, Any] | None = None) -> RuntimeLifecycleEventV529:
        state = self._load_state()
        return RuntimeLifecycleEventV529(action, accepted, status, self.runtime_id, self.process_id, int(state.get("heartbeat_index", -1)), errors, payload)

    def _require_worker_principal(self, api_key: str | None, action: str) -> LocalServicePrincipalV528 | RuntimeLifecycleEventV529:
        principal = self._require_principal(api_key, action)
        if isinstance(principal, RuntimeLifecycleEventV529):
            return principal
        if "workers:step" not in principal.scopes:
            return self._event(action, False, "missing_scope", errors=("missing_scope:workers:step",), payload=principal.to_dict())
        return principal

    def _require_principal(self, api_key: str | None, action: str) -> LocalServicePrincipalV528 | RuntimeLifecycleEventV529:
        auth = self.service.authenticate(api_key)
        if not auth.accepted or auth.principal is None:
            return self._event(action, False, auth.status, errors=auth.errors, payload=auth.to_dict())
        return auth.principal


def _blocked_submission_count(enqueue: dict[str, Any]) -> int:
    return sum(1 for submission in enqueue["submissions"].values() if not submission["admission"]["accepted"])


def run_supervised_runtime_workflow_v529(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    project_root = Path(root).resolve()
    out = project_root / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    runtime = SupervisedLocalRuntimeV529(out)
    start = runtime.start(reset=True)
    heartbeat = runtime.heartbeat()
    tick_one = runtime.worker_tick()
    tick_two = runtime.worker_tick()
    idle_tick = runtime.worker_tick()
    jobs_before_shutdown = runtime.service.scheduler.list_jobs()
    succeeded_jobs = [job for job in jobs_before_shutdown if job["status"] == JobStatus.SUCCEEDED.value]
    download = runtime.service.download_result_bundle(V528_DEVELOPER_API_KEY, succeeded_jobs[0]["job_id"], include_payload=False) if succeeded_jobs else None
    shutdown = runtime.graceful_shutdown(reason="v529_graceful_shutdown_probe")
    post_shutdown_tick = runtime.worker_tick()
    audit_export = runtime.export_audit_log()
    final_state = runtime._load_state()
    audit_events = runtime.read_audit_events()
    heartbeat_doc = json.loads(runtime.heartbeat_path.read_text(encoding="utf-8"))
    final_jobs = runtime.service.scheduler.list_jobs()
    event_names = [event["event"] for event in audit_events]
    worker_succeeded_count = sum(1 for event in (tick_one, tick_two) if event.status == JobStatus.SUCCEEDED.value)
    proof_ready = (
        start.accepted
        and heartbeat.accepted
        and worker_succeeded_count >= 2
        and idle_tick.status == "idle_no_queued_jobs"
        and bool(download and download.accepted and download.payload and download.payload.get("checksum_matches"))
        and shutdown.accepted
        and final_state.get("status") == "stopped"
        and post_shutdown_tick.status == "runtime_not_running"
        and audit_export.accepted
        and runtime.audit_export_path.exists()
        and heartbeat_doc.get("status") == "stopped"
        and final_state.get("heartbeat_index", -1) >= 4
        and {"runtime_started", "runtime_heartbeat", "worker_tick", "runtime_stopped", "audit_exported"}.issubset(set(event_names))
    )
    actions = {
        "start": start.to_dict(),
        "heartbeat": heartbeat.to_dict(),
        "worker_tick_one": tick_one.to_dict(),
        "worker_tick_two": tick_two.to_dict(),
        "idle_tick": idle_tick.to_dict(),
        "download_check": download.to_dict() if download else None,
        "shutdown": shutdown.to_dict(),
        "post_shutdown_tick": post_shutdown_tick.to_dict(),
        "audit_export": audit_export.to_dict(),
    }
    return {
        "version": "v5.29",
        "phase": "supervised_local_runtime_lifecycle",
        "overall_status": "supervised_local_runtime_lifecycle_ready_runtime_not_claimed" if proof_ready else "supervised_local_runtime_lifecycle_incomplete",
        "active_phase": "biocompute_runtime_supervised_process_proof",
        "bic_os_phase_locked": True,
        "supervised_local_runtime_ready": proof_ready,
        "runtime_state_file_ready": runtime.state_path.exists(),
        "heartbeat_file_ready": runtime.heartbeat_path.exists(),
        "audit_log_ready": runtime.audit_log_path.exists(),
        "audit_export_ready": runtime.audit_export_path.exists(),
        "start_semantics_passed": start.accepted,
        "heartbeat_semantics_passed": heartbeat.accepted and final_state.get("heartbeat_index", -1) >= 4,
        "worker_tick_semantics_passed": worker_succeeded_count >= 2 and idle_tick.status == "idle_no_queued_jobs",
        "graceful_shutdown_semantics_passed": shutdown.accepted and final_state.get("status") == "stopped" and post_shutdown_tick.status == "runtime_not_running",
        "audit_export_semantics_passed": audit_export.accepted and runtime.audit_export_path.exists(),
        "result_bundle_download_contract_passed": bool(download and download.accepted and download.payload and download.payload.get("checksum_matches")),
        "process_id": runtime.process_id,
        "runtime_id": runtime.runtime_id,
        "worker_id": runtime.worker_id,
        "heartbeat_index": final_state.get("heartbeat_index"),
        "audit_event_count": len(audit_events),
        "succeeded_job_count": len([job for job in final_jobs if job["status"] == JobStatus.SUCCEEDED.value]),
        "production_runtime_ready": False,
        "production_api_ready": False,
        "production_scheduler_ready": False,
        "production_biocompute_runtime_ready": False,
        "full_biosdk_ready": False,
        "live_actuation_enabled": False,
        "db_path": str(runtime.db_path.relative_to(project_root)).replace("\\", "/") if runtime.db_path.is_relative_to(project_root) else str(runtime.db_path),
        "state_path": str(runtime.state_path.relative_to(project_root)).replace("\\", "/") if runtime.state_path.is_relative_to(project_root) else str(runtime.state_path),
        "heartbeat_path": str(runtime.heartbeat_path.relative_to(project_root)).replace("\\", "/") if runtime.heartbeat_path.is_relative_to(project_root) else str(runtime.heartbeat_path),
        "audit_log_path": str(runtime.audit_log_path.relative_to(project_root)).replace("\\", "/") if runtime.audit_log_path.is_relative_to(project_root) else str(runtime.audit_log_path),
        "audit_export_path": str(runtime.audit_export_path.relative_to(project_root)).replace("\\", "/") if runtime.audit_export_path.is_relative_to(project_root) else str(runtime.audit_export_path),
        "final_state": final_state,
        "heartbeat": heartbeat_doc,
        "actions": actions,
        "jobs": final_jobs,
        "audit_events": audit_events,
        "remaining_runtime_blockers": [
            "real process manager integration instead of in-process deterministic supervisor proof",
            "OS service installation and restart policy",
            "multi-worker concurrency and cancellation propagation",
            "production metrics, log retention and tenant-isolated audit storage",
            "TLS/authenticated hosted API deployment",
            "production object storage and signed result-bundle URLs",
        ],
        "direct_answer": {
            "did_we_add_supervised_local_runtime_lifecycle": "yes" if proof_ready else "not_yet",
            "did_we_add_graceful_shutdown_contract": "yes" if shutdown.accepted else "not_yet",
            "did_we_add_audit_export_contract": "yes" if audit_export.accepted else "not_yet",
            "is_production_runtime_ready": "no",
            "is_biocompute_runtime_ready": "no",
            "is_bic_os_ready": "no",
            "next_best_build_step": "add local metrics and retention policy proof for runtime observability" if proof_ready else "fix v5.29 supervisor lifecycle blockers first",
        },
        "claim_boundary": "v5.29 proves a deterministic local supervisor lifecycle contract with state, heartbeat, worker ticks, graceful shutdown and audit export. It does not claim a production daemon, hosted BioCompute Runtime, live external API control, closed-loop wetware operation, full BioSDK or BiC OS readiness.",
    }


def write_supervised_runtime_outputs_v529(audit: dict[str, Any], out_dir: str | Path = DEFAULT_OUT) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary_json": out / "V529_SUPERVISED_RUNTIME_SUMMARY.json",
        "actions_json": out / "V529_SUPERVISED_RUNTIME_ACTIONS.json",
        "jobs_json": out / "V529_SUPERVISED_RUNTIME_JOBS.json",
        "audit_events_json": out / "V529_SUPERVISED_RUNTIME_AUDIT_EVENTS.json",
        "jobs_csv": out / "V529_SUPERVISED_RUNTIME_JOBS.csv",
        "markdown_report": out / "BIOGPU_V529_SUPERVISED_RUNTIME_REPORT.md",
    }
    summary = {key: value for key, value in audit.items() if key not in {"actions", "jobs", "audit_events"}}
    paths["summary_json"].write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["actions_json"].write_text(json.dumps(audit["actions"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["jobs_json"].write_text(json.dumps({"jobs": audit["jobs"]}, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["audit_events_json"].write_text(json.dumps({"events": audit["audit_events"]}, indent=2, ensure_ascii=False), encoding="utf-8")
    _write_jobs_csv(paths["jobs_csv"], audit["jobs"])
    paths["markdown_report"].write_text(_markdown_report(audit), encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}


def _write_jobs_csv(path: Path, jobs: list[dict[str, Any]]) -> None:
    fieldnames = ["job_id", "job_type", "dataset_id", "status", "result_bundle_ready", "validation_errors"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for job in jobs:
            writer.writerow({
                "job_id": job.get("job_id"),
                "job_type": job.get("job_type"),
                "dataset_id": job.get("dataset_id"),
                "status": job.get("status"),
                "result_bundle_ready": bool(job.get("result_bundle")),
                "validation_errors": " | ".join(str(item) for item in job.get("validation_errors", [])),
            })


def _markdown_report(audit: dict[str, Any]) -> str:
    answer = audit["direct_answer"]
    lines = [
        "# BioGPU-Core v5.29 Supervised Local Runtime",
        "",
        "## Direct Answer",
        "",
        f"- Supervised local runtime lifecycle: `{answer['did_we_add_supervised_local_runtime_lifecycle']}`",
        f"- Graceful shutdown contract: `{answer['did_we_add_graceful_shutdown_contract']}`",
        f"- Audit export contract: `{answer['did_we_add_audit_export_contract']}`",
        f"- Production runtime ready: `{answer['is_production_runtime_ready']}`",
        f"- BioCompute Runtime ready: `{answer['is_biocompute_runtime_ready']}`",
        f"- BiC OS ready: `{answer['is_bic_os_ready']}`",
        f"- Next best build step: {answer['next_best_build_step']}",
        "",
        "## Proof Summary",
        "",
        f"- Start semantics passed: `{audit['start_semantics_passed']}`",
        f"- Heartbeat semantics passed: `{audit['heartbeat_semantics_passed']}`",
        f"- Worker tick semantics passed: `{audit['worker_tick_semantics_passed']}`",
        f"- Graceful shutdown semantics passed: `{audit['graceful_shutdown_semantics_passed']}`",
        f"- Audit export semantics passed: `{audit['audit_export_semantics_passed']}`",
        f"- Heartbeat index: `{audit['heartbeat_index']}`",
        f"- Audit events: `{audit['audit_event_count']}`",
        "",
        "## Remaining Runtime Blockers",
        "",
    ]
    for blocker in audit["remaining_runtime_blockers"]:
        lines.append(f"- {blocker}")
    lines.extend(["", "## Boundary", "", audit["claim_boundary"], ""])
    return "\n".join(lines)