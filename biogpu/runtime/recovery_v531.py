"""Stale-heartbeat alerting and worker recovery proof, v5.31."""
from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from biogpu.beta.job_model_v43 import JobStatus, utc_now_iso
from biogpu.runtime.durable_scheduler_v526 import enqueue_reference_jobs_v526
from biogpu.runtime.observability_v530 import run_runtime_observability_workflow_v530
from biogpu.runtime.scheduler_api_v527 import SchedulerAPIFacadeV527


DEFAULT_OUT = Path("outputs/v531_recovery_alerting")
DEFAULT_DB_NAME = "V531_RECOVERY_ALERTING.sqlite3"


@dataclass(frozen=True)
class RuntimeAlertV531:
    alert_id: str
    kind: str
    severity: str
    status: str
    accepted: bool
    runtime_id: str | None
    observed_age_seconds: float | None
    threshold_seconds: float
    details: dict[str, Any]
    production_alerting_ready: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class WorkerFailureClassificationV531:
    failure_id: str
    job_id: str | None
    kind: str
    status: str
    retryable: bool
    errors: tuple[str, ...]
    details: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def _hash_payload(prefix: str, payload: Any) -> str:
    data = json.dumps(payload, sort_keys=True, ensure_ascii=True).encode("utf-8")
    return f"{prefix}_{hashlib.sha256(data).hexdigest()[:16]}"


def build_stale_heartbeat_alert_v531(heartbeat: dict[str, Any], observed_at: str | None = None, max_age_seconds: float = 60.0) -> RuntimeAlertV531:
    observed_dt = _parse_time(observed_at) or datetime.now(timezone.utc)
    heartbeat_dt = _parse_time(str(heartbeat.get("last_heartbeat_at") or ""))
    if heartbeat_dt is None:
        age_seconds: float | None = None
        stale = True
        status = "heartbeat_timestamp_invalid"
    else:
        age_seconds = max(0.0, float((observed_dt - heartbeat_dt).total_seconds()))
        stale = age_seconds > max_age_seconds and heartbeat.get("status") == "running"
        status = "stale_heartbeat_detected" if stale else "heartbeat_fresh"
    details = {
        "heartbeat": heartbeat,
        "observed_at": observed_dt.isoformat(timespec="seconds"),
        "max_age_seconds": max_age_seconds,
        "production_alerting_ready": False,
        "live_actuation_enabled": False,
    }
    alert_id = _hash_payload("alert", {"kind": "stale_heartbeat", "status": status, "runtime_id": heartbeat.get("runtime_id"), "age_seconds": age_seconds})
    return RuntimeAlertV531(
        alert_id=alert_id,
        kind="stale_heartbeat",
        severity="critical" if stale else "info",
        status=status,
        accepted=stale,
        runtime_id=heartbeat.get("runtime_id"),
        observed_age_seconds=age_seconds,
        threshold_seconds=max_age_seconds,
        details=details,
    )


def classify_worker_failure_v531(timeout_action: dict[str, Any]) -> WorkerFailureClassificationV531:
    errors = tuple(str(item) for item in timeout_action.get("errors", []))
    job_id = timeout_action.get("job_id")
    retryable = timeout_action.get("accepted") is True and "worker_timeout_exceeded" in errors
    kind = "worker_timeout" if retryable else "worker_failure_unknown"
    status = "retryable_worker_timeout" if retryable else "not_retryable"
    failure_id = _hash_payload("failure", {"kind": kind, "job_id": job_id, "errors": errors})
    return WorkerFailureClassificationV531(
        failure_id=failure_id,
        job_id=str(job_id) if job_id else None,
        kind=kind,
        status=status,
        retryable=retryable,
        errors=errors,
        details={"timeout_action": timeout_action, "production_recovery_ready": False, "bic_os_phase_locked": True},
    )


def run_worker_failure_recovery_probe_v531(root: str | Path, out_dir: str | Path) -> dict[str, Any]:
    project_root = Path(root).resolve()
    out = project_root / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    db_path = out / DEFAULT_DB_NAME
    if db_path.exists():
        db_path.unlink()
    enqueue = enqueue_reference_jobs_v526(db_path)
    facade = SchedulerAPIFacadeV527(db_path, out / "recovery_worker_results")
    queued = facade.list_jobs(JobStatus.QUEUED.value)
    cancel_action = facade.cancel_job(queued[0]["job_id"], reason="v531_isolate_recovery_probe") if queued else None
    claimed = facade.store.claim_next_job("failing_worker_v531")
    timeout_actions = facade.timeout_running_jobs(max_running_age_seconds=0)
    timeout_action = timeout_actions[0].to_dict() if timeout_actions else {"accepted": False, "job_id": claimed.get("job_id") if claimed else None, "errors": ["no_timeout_action"]}
    classification = classify_worker_failure_v531(timeout_action)
    retry_action = facade.retry_job(classification.job_id or "", reason="v531_recovery_after_worker_timeout") if classification.retryable else None
    worker_step = facade.worker_step("recovery_worker_v531") if retry_action and retry_action.accepted else {"status": "recovery_not_attempted", "job_id": None, "errors": ["retry_not_accepted"]}
    jobs = facade.list_jobs()
    events = facade.store.list_events()
    recovered_job = facade.get_job(worker_step["job_id"]) if worker_step.get("job_id") else None
    blocked_submission_count = sum(1 for submission in enqueue["submissions"].values() if not submission["admission"]["accepted"])
    recovery_ready = (
        bool(cancel_action and cancel_action.accepted)
        and classification.retryable
        and retry_action is not None
        and retry_action.accepted
        and worker_step.get("status") == JobStatus.SUCCEEDED.value
        and recovered_job is not None
        and recovered_job.get("status") == JobStatus.SUCCEEDED.value
        and blocked_submission_count >= 1
    )
    return {
        "version": "v5.31",
        "recovery_probe_ready": recovery_ready,
        "db_path": str(db_path.relative_to(project_root)).replace("\\", "/") if db_path.is_relative_to(project_root) else str(db_path),
        "blocked_submission_count": blocked_submission_count,
        "cancel_action": cancel_action.to_dict() if cancel_action else None,
        "claimed_job": claimed,
        "timeout_actions": [action.to_dict() for action in timeout_actions],
        "failure_classification": classification.to_dict(),
        "retry_action": retry_action.to_dict() if retry_action else None,
        "worker_step": worker_step,
        "recovered_job": recovered_job,
        "jobs": jobs,
        "events": events,
        "production_recovery_ready": False,
        "bic_os_phase_locked": True,
    }


def build_recovery_audit_bundle_v531(alert: RuntimeAlertV531, recovery_probe: dict[str, Any], out_dir: str | Path) -> dict[str, Any]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    bundle = {
        "version": "v5.31",
        "created_at": utc_now_iso(),
        "alert": alert.to_dict(),
        "recovery_probe": {key: value for key, value in recovery_probe.items() if key not in {"jobs", "events"}},
        "jobs": recovery_probe.get("jobs", []),
        "events": recovery_probe.get("events", []),
        "production_alerting_ready": False,
        "production_recovery_ready": False,
        "bic_os_phase_locked": True,
    }
    bundle_hash = hashlib.sha256(json.dumps(bundle, sort_keys=True, ensure_ascii=True).encode("utf-8")).hexdigest()
    bundle["bundle_sha256"] = bundle_hash
    path = out / "V531_RECOVERY_AUDIT_BUNDLE.json"
    path.write_text(json.dumps(bundle, indent=2, ensure_ascii=False), encoding="utf-8")
    return {
        "bundle_path": str(path).replace("\\", "/"),
        "bundle_sha256": bundle_hash,
        "bundle_ready": path.exists() and len(bundle_hash) == 64,
        "bundle": bundle,
    }


def run_recovery_alerting_workflow_v531(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    project_root = Path(root).resolve()
    out = project_root / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    observability = run_runtime_observability_workflow_v530(project_root, out / "v530_observability_dependency")
    healthy_heartbeat = dict(observability.get("supervisor_summary", {}).get("heartbeat", {}))
    stale_heartbeat = dict(healthy_heartbeat)
    stale_heartbeat.update({"status": "running", "last_heartbeat_at": "1970-01-01T00:00:00+00:00", "source": "v531_stale_probe"})
    alert = build_stale_heartbeat_alert_v531(stale_heartbeat, observed_at="2026-05-07T04:10:00+00:00", max_age_seconds=60.0)
    recovery_probe = run_worker_failure_recovery_probe_v531(project_root, out)
    bundle = build_recovery_audit_bundle_v531(alert, recovery_probe, out)
    failure = recovery_probe["failure_classification"]
    proof_ready = (
        observability.get("runtime_observability_ready") is True
        and alert.accepted
        and alert.status == "stale_heartbeat_detected"
        and failure.get("retryable") is True
        and recovery_probe.get("recovery_probe_ready") is True
        and bundle.get("bundle_ready") is True
        and observability.get("production_metrics_ready") is False
        and recovery_probe.get("production_recovery_ready") is False
    )
    return {
        "version": "v5.31",
        "phase": "stale_heartbeat_alerting_worker_failure_recovery",
        "overall_status": "recovery_alerting_proof_ready_runtime_not_claimed" if proof_ready else "recovery_alerting_proof_incomplete",
        "active_phase": "biocompute_runtime_recovery_observability_proof",
        "bic_os_phase_locked": True,
        "recovery_alerting_ready": proof_ready,
        "stale_heartbeat_alert_passed": alert.accepted and alert.status == "stale_heartbeat_detected",
        "failure_classification_passed": failure.get("retryable") is True and failure.get("kind") == "worker_timeout",
        "worker_recovery_passed": recovery_probe.get("recovery_probe_ready") is True,
        "recovery_audit_bundle_ready": bundle.get("bundle_ready") is True,
        "observability_dependency_ready": observability.get("runtime_observability_ready") is True,
        "alert_count": 1,
        "recovered_job_id": (recovery_probe.get("recovered_job") or {}).get("job_id"),
        "failed_job_id": failure.get("job_id"),
        "retry_job_id": (recovery_probe.get("retry_action") or {}).get("related_job_id"),
        "production_alerting_ready": False,
        "production_recovery_ready": False,
        "production_runtime_ready": False,
        "production_api_ready": False,
        "production_biocompute_runtime_ready": False,
        "full_biosdk_ready": False,
        "live_actuation_enabled": False,
        "alert": alert.to_dict(),
        "failure_classification": failure,
        "recovery_probe": recovery_probe,
        "recovery_audit_bundle": {key: value for key, value in bundle.items() if key != "bundle"},
        "observability_summary": {key: value for key, value in observability.items() if key not in {"metrics", "status_snapshots", "retention_manifest", "supervisor_summary"}},
        "remaining_runtime_blockers": [
            "real background monitor loop and production alert routing",
            "worker crash detection from process supervision instead of deterministic timeout probe",
            "retry backoff, dead-letter queues and bounded retry policy",
            "operator acknowledgement workflow",
            "tenant-aware incident retention and tamper-evident alert storage",
            "hosted deployment alert dashboards and paging integrations",
        ],
        "direct_answer": {
            "did_we_add_stale_heartbeat_alerting": "yes" if alert.accepted else "not_yet",
            "did_we_add_worker_failure_recovery": "yes" if recovery_probe.get("recovery_probe_ready") else "not_yet",
            "did_we_add_recovery_audit_bundle": "yes" if bundle.get("bundle_ready") else "not_yet",
            "is_production_recovery_ready": "no",
            "is_biocompute_runtime_ready": "no",
            "is_bic_os_ready": "no",
            "next_best_build_step": "add bounded retry and dead-letter queue proof" if proof_ready else "fix v5.31 recovery alerting blockers first",
        },
        "claim_boundary": "v5.31 proves local stale-heartbeat alert classification and worker timeout recovery through retry/worker-step semantics. It does not claim production monitoring, hosted recovery orchestration, live external API control, closed-loop wetware operation, full BioCompute Runtime or BiC OS readiness.",
    }


def write_recovery_alerting_outputs_v531(audit: dict[str, Any], out_dir: str | Path = DEFAULT_OUT) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary_json": out / "V531_RECOVERY_ALERTING_SUMMARY.json",
        "alert_json": out / "V531_STALE_HEARTBEAT_ALERT.json",
        "failure_json": out / "V531_WORKER_FAILURE_CLASSIFICATION.json",
        "recovery_probe_json": out / "V531_WORKER_RECOVERY_PROBE.json",
        "events_json": out / "V531_RECOVERY_EVENTS.json",
        "jobs_csv": out / "V531_RECOVERY_JOBS.csv",
        "markdown_report": out / "BIOGPU_V531_RECOVERY_ALERTING_REPORT.md",
    }
    summary = {key: value for key, value in audit.items() if key not in {"alert", "failure_classification", "recovery_probe"}}
    paths["summary_json"].write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["alert_json"].write_text(json.dumps(audit["alert"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["failure_json"].write_text(json.dumps(audit["failure_classification"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["recovery_probe_json"].write_text(json.dumps(audit["recovery_probe"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["events_json"].write_text(json.dumps({"events": audit["recovery_probe"].get("events", [])}, indent=2, ensure_ascii=False), encoding="utf-8")
    _write_jobs_csv(paths["jobs_csv"], audit["recovery_probe"].get("jobs", []))
    paths["markdown_report"].write_text(_markdown_report(audit), encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}


def _write_jobs_csv(path: Path, jobs: list[dict[str, Any]]) -> None:
    fieldnames = ["job_id", "job_type", "dataset_id", "status", "retry_of", "result_bundle_ready", "validation_errors"]
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
                "result_bundle_ready": bool(job.get("result_bundle")),
                "validation_errors": " | ".join(str(item) for item in job.get("validation_errors", [])),
            })


def _markdown_report(audit: dict[str, Any]) -> str:
    answer = audit["direct_answer"]
    lines = [
        "# BioGPU-Core v5.31 Recovery Alerting",
        "",
        "## Direct Answer",
        "",
        f"- Stale-heartbeat alerting: `{answer['did_we_add_stale_heartbeat_alerting']}`",
        f"- Worker failure recovery: `{answer['did_we_add_worker_failure_recovery']}`",
        f"- Recovery audit bundle: `{answer['did_we_add_recovery_audit_bundle']}`",
        f"- Production recovery ready: `{answer['is_production_recovery_ready']}`",
        f"- BioCompute Runtime ready: `{answer['is_biocompute_runtime_ready']}`",
        f"- BiC OS ready: `{answer['is_bic_os_ready']}`",
        f"- Next best build step: {answer['next_best_build_step']}",
        "",
        "## Proof Summary",
        "",
        f"- Stale heartbeat alert passed: `{audit['stale_heartbeat_alert_passed']}`",
        f"- Failure classification passed: `{audit['failure_classification_passed']}`",
        f"- Worker recovery passed: `{audit['worker_recovery_passed']}`",
        f"- Recovery audit bundle ready: `{audit['recovery_audit_bundle_ready']}`",
        f"- Failed job ID: `{audit['failed_job_id']}`",
        f"- Retry job ID: `{audit['retry_job_id']}`",
        f"- Recovered job ID: `{audit['recovered_job_id']}`",
        "",
        "## Remaining Runtime Blockers",
        "",
    ]
    for blocker in audit["remaining_runtime_blockers"]:
        lines.append(f"- {blocker}")
    lines.extend(["", "## Boundary", "", audit["claim_boundary"], ""])
    return "\n".join(lines)