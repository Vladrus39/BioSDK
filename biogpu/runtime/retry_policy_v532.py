"""Bounded retry and dead-letter queue proof, v5.32."""
from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from biogpu.beta.job_model_v43 import JobStatus, utc_now_iso
from biogpu.runtime.durable_scheduler_v526 import _json_dumps, enqueue_reference_jobs_v526
from biogpu.runtime.recovery_v531 import run_recovery_alerting_workflow_v531
from biogpu.runtime.scheduler_api_v527 import SchedulerAPIFacadeV527


DEFAULT_OUT = Path("outputs/v532_bounded_retry_dead_letter")
DEFAULT_DB_NAME = "V532_BOUNDED_RETRY_DEAD_LETTER.sqlite3"


@dataclass(frozen=True)
class RetryPolicyV532:
    policy_id: str = "v532_bounded_retry_policy"
    max_retry_attempts: int = 2
    backoff_schedule_seconds: tuple[int, ...] = (0, 30)
    retryable_errors: tuple[str, ...] = ("worker_timeout_exceeded",)
    dead_letter_on_max_attempts: bool = True
    production_retry_policy_ready: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RetryDecisionV532:
    decision_id: str
    job_id: str | None
    action: str
    accepted: bool
    status: str
    current_attempt: int
    next_attempt: int | None
    max_retry_attempts: int
    backoff_seconds: int | None
    reason: str
    errors: tuple[str, ...]
    related_job_id: str | None = None
    production_retry_policy_ready: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DeadLetterEntryV532:
    entry_id: str
    job_id: str
    retry_of: str | None
    final_attempt: int
    max_retry_attempts: int
    reason: str
    errors: tuple[str, ...]
    status: str = "dead_lettered"
    production_dead_letter_queue_ready: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _hash_payload(prefix: str, payload: Any) -> str:
    data = json.dumps(payload, sort_keys=True, ensure_ascii=True).encode("utf-8")
    return f"{prefix}_{hashlib.sha256(data).hexdigest()[:16]}"


def _retry_attempt(job: dict[str, Any]) -> int:
    metadata = job.get("metadata") or {}
    try:
        return max(0, int(metadata.get("retry_attempt", 0) or 0))
    except (TypeError, ValueError):
        return 0


def _backoff_for_attempt(policy: RetryPolicyV532, current_attempt: int) -> int:
    if not policy.backoff_schedule_seconds:
        return 0
    index = min(max(0, current_attempt), len(policy.backoff_schedule_seconds) - 1)
    return int(policy.backoff_schedule_seconds[index])


def evaluate_retry_decision_v532(job: dict[str, Any], policy: RetryPolicyV532 | None = None, reason: str = "worker_timeout") -> RetryDecisionV532:
    retry_policy = policy or RetryPolicyV532()
    errors = tuple(str(item) for item in job.get("validation_errors", []))
    current_attempt = _retry_attempt(job)
    retryable = job.get("status") == JobStatus.FAILED.value and any(error in retry_policy.retryable_errors for error in errors)
    if not retryable:
        action = "reject"
        accepted = False
        status = "not_retryable"
        next_attempt = None
        backoff_seconds = None
    elif current_attempt >= retry_policy.max_retry_attempts and retry_policy.dead_letter_on_max_attempts:
        action = "dead_letter"
        accepted = True
        status = "max_attempts_exhausted"
        next_attempt = None
        backoff_seconds = None
    else:
        action = "retry"
        accepted = True
        status = "retry_allowed"
        next_attempt = current_attempt + 1
        backoff_seconds = _backoff_for_attempt(retry_policy, current_attempt)
    decision_id = _hash_payload(
        "retry_decision",
        {
            "job_id": job.get("job_id"),
            "action": action,
            "current_attempt": current_attempt,
            "max_retry_attempts": retry_policy.max_retry_attempts,
            "errors": errors,
        },
    )
    return RetryDecisionV532(
        decision_id=decision_id,
        job_id=str(job.get("job_id")) if job.get("job_id") else None,
        action=action,
        accepted=accepted,
        status=status,
        current_attempt=current_attempt,
        next_attempt=next_attempt,
        max_retry_attempts=retry_policy.max_retry_attempts,
        backoff_seconds=backoff_seconds,
        reason=reason,
        errors=errors,
    )


def _next_event_index(connection: Any, job_id: str) -> int:
    row = connection.execute("SELECT COALESCE(MAX(event_index), -1) + 1 AS next_index FROM job_events WHERE job_id = ?", (job_id,)).fetchone()
    return int(row["next_index"])


def _annotate_job_metadata(facade: SchedulerAPIFacadeV527, job_id: str, metadata_updates: dict[str, Any], event_name: str, event_details: dict[str, Any], extra_errors: tuple[str, ...] = tuple()) -> dict[str, Any]:
    job = facade.get_job(job_id)
    metadata = dict(job.get("metadata") or {})
    metadata.update(metadata_updates)
    errors = list(job.get("validation_errors") or [])
    for error in extra_errors:
        if error not in errors:
            errors.append(error)
    now = utc_now_iso()
    with facade.store._connect() as connection:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute(
            "UPDATE jobs SET updated_at = ?, metadata_json = ?, validation_errors_json = ? WHERE job_id = ?",
            (now, _json_dumps(metadata), _json_dumps(errors), job_id),
        )
        event_index = _next_event_index(connection, job_id)
        connection.execute(
            "INSERT INTO job_events (job_id, event_index, event_time, event_name, details_json) VALUES (?, ?, ?, ?, ?)",
            (job_id, event_index, now, event_name, _json_dumps(event_details)),
        )
        connection.commit()
    return facade.get_job(job_id)


def mark_job_dead_lettered_v532(facade: SchedulerAPIFacadeV527, job_id: str, policy: RetryPolicyV532, decision: RetryDecisionV532, reason: str = "max_retry_attempts_exhausted") -> DeadLetterEntryV532:
    job = facade.get_job(job_id)
    metadata = job.get("metadata") or {}
    retry_of = metadata.get("retry_of")
    errors = tuple(str(item) for item in job.get("validation_errors", []))
    entry_id = _hash_payload("dead_letter", {"job_id": job_id, "attempt": decision.current_attempt, "errors": errors})
    entry = DeadLetterEntryV532(
        entry_id=entry_id,
        job_id=job_id,
        retry_of=str(retry_of) if retry_of else None,
        final_attempt=decision.current_attempt,
        max_retry_attempts=policy.max_retry_attempts,
        reason=reason,
        errors=errors,
    )
    _annotate_job_metadata(
        facade,
        job_id,
        {
            "dead_lettered": True,
            "dead_letter_entry_id": entry.entry_id,
            "dead_letter_reason": reason,
            "dead_lettered_at": utc_now_iso(),
            "retry_policy_id": policy.policy_id,
            "retry_policy_max_attempts": policy.max_retry_attempts,
            "final_retry_attempt": decision.current_attempt,
            "source": "v532_bounded_retry_dead_letter",
        },
        "api_dead_lettered",
        entry.to_dict(),
        extra_errors=("dead_letter_max_attempts_exhausted",),
    )
    return entry


def apply_bounded_retry_policy_v532(facade: SchedulerAPIFacadeV527, job_id: str, policy: RetryPolicyV532 | None = None, reason: str = "v532_bounded_retry") -> dict[str, Any]:
    retry_policy = policy or RetryPolicyV532()
    try:
        job = facade.get_job(job_id)
    except KeyError:
        return {
            "decision": RetryDecisionV532(
                decision_id=_hash_payload("retry_decision", {"job_id": job_id, "status": "job_not_found"}),
                job_id=job_id,
                action="reject",
                accepted=False,
                status="job_not_found",
                current_attempt=0,
                next_attempt=None,
                max_retry_attempts=retry_policy.max_retry_attempts,
                backoff_seconds=None,
                reason=reason,
                errors=("job_not_found",),
            ).to_dict(),
            "retry_action": None,
            "retry_job": None,
            "dead_letter_entry": None,
        }
    decision = evaluate_retry_decision_v532(job, retry_policy, reason)
    if decision.action == "dead_letter" and decision.accepted:
        entry = mark_job_dead_lettered_v532(facade, job_id, retry_policy, decision)
        return {"decision": decision.to_dict(), "retry_action": None, "retry_job": None, "dead_letter_entry": entry.to_dict()}
    if decision.action != "retry" or not decision.accepted:
        return {"decision": decision.to_dict(), "retry_action": None, "retry_job": None, "dead_letter_entry": None}
    retry_reason = f"{reason};policy={retry_policy.policy_id};backoff_seconds={decision.backoff_seconds}"
    retry_action = facade.retry_job(job_id, reason=retry_reason)
    retry_job = None
    decision_payload = decision.to_dict()
    if retry_action.accepted and retry_action.related_job_id:
        decision_payload["related_job_id"] = retry_action.related_job_id
        retry_job = _annotate_job_metadata(
            facade,
            retry_action.related_job_id,
            {
                "retry_policy_id": retry_policy.policy_id,
                "retry_policy_max_attempts": retry_policy.max_retry_attempts,
                "retry_backoff_seconds": decision.backoff_seconds,
                "retry_decision_id": decision.decision_id,
                "retry_scheduled_by": "v532_bounded_retry_dead_letter",
                "source": "v532_bounded_retry_dead_letter",
            },
            "api_retry_policy_accepted",
            decision_payload,
        )
    return {"decision": decision_payload, "retry_action": retry_action.to_dict(), "retry_job": retry_job, "dead_letter_entry": None}


def _claim_and_timeout_next_v532(facade: SchedulerAPIFacadeV527, worker_id: str) -> dict[str, Any]:
    claimed = facade.store.claim_next_job(worker_id)
    if claimed is None:
        return {"claimed_job": None, "timeout_action": None, "failed_job": None}
    timeout_actions = facade.timeout_running_jobs(max_running_age_seconds=0)
    timeout_action = next((action.to_dict() for action in timeout_actions if action.job_id == claimed["job_id"]), None)
    return {"claimed_job": claimed, "timeout_action": timeout_action, "failed_job": facade.get_job(claimed["job_id"])}


def run_bounded_retry_dead_letter_probe_v532(root: str | Path, out_dir: str | Path, policy: RetryPolicyV532 | None = None) -> dict[str, Any]:
    project_root = Path(root).resolve()
    out = project_root / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    retry_policy = policy or RetryPolicyV532()
    db_path = out / DEFAULT_DB_NAME
    if db_path.exists():
        db_path.unlink()
    enqueue = enqueue_reference_jobs_v526(db_path)
    facade = SchedulerAPIFacadeV527(db_path, out / "retry_policy_worker_results")
    queued = facade.list_jobs(JobStatus.QUEUED.value)
    cancel_action = facade.cancel_job(queued[0]["job_id"], reason="v532_isolate_bounded_retry_probe") if queued else None

    attempt_0 = _claim_and_timeout_next_v532(facade, "v532_failing_worker_attempt_0")
    first_policy_action = apply_bounded_retry_policy_v532(facade, attempt_0["failed_job"]["job_id"], retry_policy, reason="v532_retry_attempt_1") if attempt_0["failed_job"] else None
    attempt_1 = _claim_and_timeout_next_v532(facade, "v532_failing_worker_attempt_1")
    second_policy_action = apply_bounded_retry_policy_v532(facade, attempt_1["failed_job"]["job_id"], retry_policy, reason="v532_retry_attempt_2") if attempt_1["failed_job"] else None
    attempt_2 = _claim_and_timeout_next_v532(facade, "v532_failing_worker_attempt_2")
    dead_letter_policy_action = apply_bounded_retry_policy_v532(facade, attempt_2["failed_job"]["job_id"], retry_policy, reason="v532_dead_letter_after_attempt_limit") if attempt_2["failed_job"] else None

    jobs = facade.list_jobs()
    events = facade.store.list_events()
    dead_letter_jobs = [job for job in jobs if (job.get("metadata") or {}).get("dead_lettered") is True]
    retry_jobs = [job for job in jobs if "retry_of" in (job.get("metadata") or {})]
    retry_attempts = [int((job.get("metadata") or {}).get("retry_attempt", 0) or 0) for job in retry_jobs]
    blocked_submission_count = sum(1 for submission in enqueue["submissions"].values() if not submission["admission"]["accepted"])
    first_decision = (first_policy_action or {}).get("decision", {})
    second_decision = (second_policy_action or {}).get("decision", {})
    final_decision = (dead_letter_policy_action or {}).get("decision", {})
    proof_ready = (
        bool(cancel_action and cancel_action.accepted)
        and first_decision.get("action") == "retry"
        and first_decision.get("accepted") is True
        and second_decision.get("action") == "retry"
        and second_decision.get("accepted") is True
        and final_decision.get("action") == "dead_letter"
        and final_decision.get("accepted") is True
        and len(dead_letter_jobs) == 1
        and max(retry_attempts or [0]) == retry_policy.max_retry_attempts
        and blocked_submission_count >= 1
    )
    return {
        "version": "v5.32",
        "bounded_retry_dead_letter_probe_ready": proof_ready,
        "db_path": str(db_path.relative_to(project_root)).replace("\\", "/") if db_path.is_relative_to(project_root) else str(db_path),
        "policy": retry_policy.to_dict(),
        "blocked_submission_count": blocked_submission_count,
        "cancel_action": cancel_action.to_dict() if cancel_action else None,
        "attempts": [attempt_0, attempt_1, attempt_2],
        "policy_actions": [item for item in [first_policy_action, second_policy_action, dead_letter_policy_action] if item is not None],
        "dead_letter_queue": [(dead_letter_policy_action or {}).get("dead_letter_entry")] if (dead_letter_policy_action or {}).get("dead_letter_entry") else [],
        "dead_letter_jobs": dead_letter_jobs,
        "jobs": jobs,
        "events": events,
        "max_attempts_enforced": max(retry_attempts or [0]) == retry_policy.max_retry_attempts and len(dead_letter_jobs) == 1,
        "retry_backoff_metadata_ready": all((job.get("metadata") or {}).get("retry_backoff_seconds") is not None for job in retry_jobs) and len(retry_jobs) == retry_policy.max_retry_attempts,
        "production_retry_policy_ready": False,
        "production_dead_letter_queue_ready": False,
        "bic_os_phase_locked": True,
    }


def build_retry_policy_audit_bundle_v532(probe: dict[str, Any], out_dir: str | Path) -> dict[str, Any]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    bundle = {
        "version": "v5.32",
        "created_at": utc_now_iso(),
        "policy": probe["policy"],
        "policy_actions": probe.get("policy_actions", []),
        "dead_letter_queue": probe.get("dead_letter_queue", []),
        "dead_letter_jobs": probe.get("dead_letter_jobs", []),
        "max_attempts_enforced": probe.get("max_attempts_enforced"),
        "retry_backoff_metadata_ready": probe.get("retry_backoff_metadata_ready"),
        "production_retry_policy_ready": False,
        "production_dead_letter_queue_ready": False,
        "bic_os_phase_locked": True,
    }
    bundle_hash = hashlib.sha256(json.dumps(bundle, sort_keys=True, ensure_ascii=True).encode("utf-8")).hexdigest()
    bundle["bundle_sha256"] = bundle_hash
    path = out / "V532_RETRY_POLICY_AUDIT_BUNDLE.json"
    path.write_text(json.dumps(bundle, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"bundle_path": str(path).replace("\\", "/"), "bundle_sha256": bundle_hash, "bundle_ready": path.exists() and len(bundle_hash) == 64, "bundle": bundle}


def run_bounded_retry_dead_letter_workflow_v532(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    project_root = Path(root).resolve()
    out = project_root / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    recovery_dependency = run_recovery_alerting_workflow_v531(project_root, out / "v531_recovery_dependency")
    probe = run_bounded_retry_dead_letter_probe_v532(project_root, out)
    bundle = build_retry_policy_audit_bundle_v532(probe, out)
    dead_letter_entry = probe["dead_letter_queue"][0] if probe.get("dead_letter_queue") else None
    proof_ready = (
        recovery_dependency.get("recovery_alerting_ready") is True
        and probe.get("bounded_retry_dead_letter_probe_ready") is True
        and probe.get("max_attempts_enforced") is True
        and probe.get("retry_backoff_metadata_ready") is True
        and bundle.get("bundle_ready") is True
        and probe.get("production_retry_policy_ready") is False
        and probe.get("production_dead_letter_queue_ready") is False
    )
    return {
        "version": "v5.32",
        "phase": "bounded_retry_dead_letter_queue",
        "overall_status": "bounded_retry_dead_letter_proof_ready_runtime_not_claimed" if proof_ready else "bounded_retry_dead_letter_proof_incomplete",
        "active_phase": "biocompute_runtime_recovery_policy_proof",
        "bic_os_phase_locked": True,
        "bounded_retry_dead_letter_ready": proof_ready,
        "bounded_retry_policy_ready": probe.get("bounded_retry_dead_letter_probe_ready") is True,
        "dead_letter_queue_ready": len(probe.get("dead_letter_queue", [])) == 1,
        "max_attempts_enforced": probe.get("max_attempts_enforced") is True,
        "retry_backoff_metadata_ready": probe.get("retry_backoff_metadata_ready") is True,
        "recovery_dependency_ready": recovery_dependency.get("recovery_alerting_ready") is True,
        "retry_policy_audit_bundle_ready": bundle.get("bundle_ready") is True,
        "max_retry_attempts": probe["policy"]["max_retry_attempts"],
        "dead_letter_job_id": dead_letter_entry.get("job_id") if dead_letter_entry else None,
        "retry_job_ids": [action.get("retry_action", {}).get("related_job_id") for action in probe.get("policy_actions", []) if action.get("retry_action")],
        "production_retry_policy_ready": False,
        "production_dead_letter_queue_ready": False,
        "production_recovery_ready": False,
        "production_runtime_ready": False,
        "production_api_ready": False,
        "production_biocompute_runtime_ready": False,
        "full_biosdk_ready": False,
        "live_actuation_enabled": False,
        "policy": probe["policy"],
        "probe": probe,
        "retry_policy_audit_bundle": {key: value for key, value in bundle.items() if key != "bundle"},
        "recovery_dependency_summary": {key: value for key, value in recovery_dependency.items() if key not in {"alert", "failure_classification", "recovery_probe", "observability_summary"}},
        "remaining_runtime_blockers": [
            "real background monitor loop and production alert routing",
            "worker crash detection from process supervision instead of deterministic timeout probe",
            "operator acknowledgement workflow and incident state transitions",
            "tenant-aware incident retention and tamper-evident alert storage",
            "hosted deployment alert dashboards and paging integrations",
            "production multi-worker retry orchestration with durable backoff timers",
        ],
        "direct_answer": {
            "did_we_add_bounded_retry_policy": "yes" if probe.get("max_attempts_enforced") else "not_yet",
            "did_we_add_dead_letter_queue_proof": "yes" if len(probe.get("dead_letter_queue", [])) == 1 else "not_yet",
            "did_we_add_retry_backoff_metadata": "yes" if probe.get("retry_backoff_metadata_ready") else "not_yet",
            "is_production_retry_policy_ready": "no",
            "is_biocompute_runtime_ready": "no",
            "is_bic_os_ready": "no",
            "next_best_build_step": "add operator acknowledgement and incident retention proof" if proof_ready else "fix v5.32 retry policy blockers first",
        },
        "claim_boundary": "v5.32 proves a local bounded retry policy, deterministic retry backoff metadata and terminal dead-letter audit entries over the v5.27 durable scheduler facade. It does not claim production retry orchestration, hosted queues, live external API control, full BioCompute Runtime or BiC OS readiness.",
    }


def write_bounded_retry_dead_letter_outputs_v532(audit: dict[str, Any], out_dir: str | Path = DEFAULT_OUT) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary_json": out / "V532_BOUNDED_RETRY_DEAD_LETTER_SUMMARY.json",
        "policy_json": out / "V532_RETRY_POLICY.json",
        "policy_actions_json": out / "V532_RETRY_POLICY_ACTIONS.json",
        "dead_letter_queue_json": out / "V532_DEAD_LETTER_QUEUE.json",
        "events_json": out / "V532_RETRY_POLICY_EVENTS.json",
        "jobs_csv": out / "V532_RETRY_POLICY_JOBS.csv",
        "markdown_report": out / "BIOGPU_V532_BOUNDED_RETRY_DEAD_LETTER_REPORT.md",
    }
    summary = {key: value for key, value in audit.items() if key not in {"probe", "policy"}}
    paths["summary_json"].write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["policy_json"].write_text(json.dumps(audit["policy"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["policy_actions_json"].write_text(json.dumps({"policy_actions": audit["probe"].get("policy_actions", [])}, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["dead_letter_queue_json"].write_text(json.dumps({"dead_letter_queue": audit["probe"].get("dead_letter_queue", []), "dead_letter_jobs": audit["probe"].get("dead_letter_jobs", [])}, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["events_json"].write_text(json.dumps({"events": audit["probe"].get("events", [])}, indent=2, ensure_ascii=False), encoding="utf-8")
    _write_jobs_csv(paths["jobs_csv"], audit["probe"].get("jobs", []))
    paths["markdown_report"].write_text(_markdown_report(audit), encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}


def _write_jobs_csv(path: Path, jobs: list[dict[str, Any]]) -> None:
    fieldnames = ["job_id", "status", "retry_of", "retry_attempt", "retry_backoff_seconds", "dead_lettered", "validation_errors"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for job in jobs:
            metadata = job.get("metadata") or {}
            writer.writerow(
                {
                    "job_id": job.get("job_id"),
                    "status": job.get("status"),
                    "retry_of": metadata.get("retry_of"),
                    "retry_attempt": metadata.get("retry_attempt", 0),
                    "retry_backoff_seconds": metadata.get("retry_backoff_seconds"),
                    "dead_lettered": bool(metadata.get("dead_lettered")),
                    "validation_errors": " | ".join(str(item) for item in job.get("validation_errors", [])),
                }
            )


def _markdown_report(audit: dict[str, Any]) -> str:
    answer = audit["direct_answer"]
    lines = [
        "# BioGPU-Core v5.32 Bounded Retry and Dead Letter Queue",
        "",
        "## Direct Answer",
        "",
        f"- Bounded retry policy: `{answer['did_we_add_bounded_retry_policy']}`",
        f"- Dead-letter queue proof: `{answer['did_we_add_dead_letter_queue_proof']}`",
        f"- Retry backoff metadata: `{answer['did_we_add_retry_backoff_metadata']}`",
        f"- Production retry policy ready: `{answer['is_production_retry_policy_ready']}`",
        f"- BioCompute Runtime ready: `{answer['is_biocompute_runtime_ready']}`",
        f"- BiC OS ready: `{answer['is_bic_os_ready']}`",
        f"- Next best build step: {answer['next_best_build_step']}",
        "",
        "## Proof Summary",
        "",
        f"- Overall status: `{audit['overall_status']}`",
        f"- Max retry attempts: `{audit['max_retry_attempts']}`",
        f"- Max attempts enforced: `{audit['max_attempts_enforced']}`",
        f"- Retry backoff metadata ready: `{audit['retry_backoff_metadata_ready']}`",
        f"- Dead-letter job ID: `{audit['dead_letter_job_id']}`",
        f"- Retry job IDs: `{', '.join(str(item) for item in audit['retry_job_ids'])}`",
        "",
        "## Remaining Runtime Blockers",
        "",
    ]
    for blocker in audit["remaining_runtime_blockers"]:
        lines.append(f"- {blocker}")
    lines.extend(["", "## Boundary", "", audit["claim_boundary"], ""])
    return "\n".join(lines)