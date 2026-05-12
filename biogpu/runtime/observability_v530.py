"""Local runtime metrics and retention policy proof, v5.30."""
from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from biogpu.beta.job_model_v43 import JobStatus, utc_now_iso
from biogpu.runtime.supervised_runtime_v529 import run_supervised_runtime_workflow_v529


DEFAULT_OUT = Path("outputs/v530_runtime_observability")


@dataclass(frozen=True)
class RuntimeRetentionPolicyV530:
    max_retained_events: int = 5
    export_before_prune: bool = True
    non_destructive_prune: bool = True
    policy_name: str = "local_recent_events_with_full_export"

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


def _seconds_between(start: str | None, end: str | None) -> float | None:
    start_dt = _parse_time(start)
    end_dt = _parse_time(end)
    if start_dt is None or end_dt is None:
        return None
    return max(0.0, float((end_dt - start_dt).total_seconds()))


def _canonical_hash(payload: Any) -> str:
    data = json.dumps(payload, sort_keys=True, ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def build_runtime_metrics_snapshot_v530(supervisor_audit: dict[str, Any]) -> dict[str, Any]:
    state = supervisor_audit.get("final_state", {})
    heartbeat = supervisor_audit.get("heartbeat", {})
    events = list(supervisor_audit.get("audit_events", []))
    jobs = list(supervisor_audit.get("jobs", []))
    event_counts: dict[str, int] = {}
    for event in events:
        event_name = str(event.get("event", "unknown"))
        event_counts[event_name] = event_counts.get(event_name, 0) + 1
    job_status_counts: dict[str, int] = {}
    result_bundle_count = 0
    result_artifact_bytes = 0
    for job in jobs:
        status = str(job.get("status", "unknown"))
        job_status_counts[status] = job_status_counts.get(status, 0) + 1
        bundle = job.get("result_bundle") if isinstance(job, dict) else None
        if isinstance(bundle, dict) and bundle:
            result_bundle_count += 1
            uri = bundle.get("uri")
            if uri and Path(str(uri)).exists():
                result_artifact_bytes += Path(str(uri)).stat().st_size
    runtime_elapsed = _seconds_between(state.get("started_at"), state.get("stopped_at"))
    heartbeat_lag = _seconds_between(heartbeat.get("last_heartbeat_at"), state.get("stopped_at"))
    metrics_ready = (
        state.get("status") == "stopped"
        and int(state.get("heartbeat_index", -1)) >= 5
        and event_counts.get("worker_tick", 0) >= 3
        and job_status_counts.get(JobStatus.SUCCEEDED.value, 0) >= 2
        and result_bundle_count >= 2
        and state.get("bic_os_phase_locked") is True
        and state.get("live_actuation_enabled") is False
    )
    return {
        "version": "v5.30",
        "snapshot_time": utc_now_iso(),
        "runtime_id": state.get("runtime_id"),
        "process_id": state.get("process_id"),
        "worker_id": state.get("worker_id"),
        "runtime_status": state.get("status"),
        "heartbeat_index": state.get("heartbeat_index"),
        "runtime_elapsed_seconds": runtime_elapsed,
        "heartbeat_lag_seconds_at_shutdown": heartbeat_lag,
        "audit_event_count": len(events),
        "event_counts": dict(sorted(event_counts.items())),
        "job_status_counts": dict(sorted(job_status_counts.items())),
        "result_bundle_count": result_bundle_count,
        "result_artifact_bytes": result_artifact_bytes,
        "local_metrics_snapshot_ready": metrics_ready,
        "production_metrics_ready": False,
        "live_actuation_enabled": False,
        "bic_os_phase_locked": True,
    }


def build_runtime_status_snapshots_v530(supervisor_audit: dict[str, Any]) -> list[dict[str, Any]]:
    snapshots: list[dict[str, Any]] = []
    for name, action in supervisor_audit.get("actions", {}).items():
        if not isinstance(action, dict):
            continue
        payload = action.get("payload") if isinstance(action.get("payload"), dict) else {}
        state = payload.get("state") if isinstance(payload.get("state"), dict) else payload
        operation = payload.get("operation") if isinstance(payload.get("operation"), dict) else None
        if not isinstance(state, dict):
            state = {}
        snapshots.append({
            "action": name,
            "accepted": bool(action.get("accepted")),
            "status": action.get("status"),
            "runtime_status": state.get("status"),
            "heartbeat_index": state.get("heartbeat_index", action.get("heartbeat_index")),
            "operation_status": operation.get("status") if isinstance(operation, dict) else None,
            "job_id": operation.get("job_id") if isinstance(operation, dict) else action.get("job_id"),
            "production_runtime_ready": False,
            "bic_os_phase_locked": True,
        })
    return snapshots


def apply_audit_retention_policy_v530(events: list[dict[str, Any]], out_dir: str | Path, policy: RuntimeRetentionPolicyV530 | None = None) -> dict[str, Any]:
    policy = policy or RuntimeRetentionPolicyV530()
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    full_export_path = out / "V530_AUDIT_RETENTION_FULL_EXPORT.json"
    retained_path = out / "V530_AUDIT_RETENTION_RETAINED_EVENTS.json"
    max_events = max(1, int(policy.max_retained_events))
    retained_events = events[-max_events:]
    pruned_events = events[:-max_events]
    full_payload = {
        "version": "v5.30",
        "exported_at": utc_now_iso(),
        "event_count": len(events),
        "events": events,
        "production_audit_retention_ready": False,
    }
    retained_payload = {
        "version": "v5.30",
        "retained_at": utc_now_iso(),
        "policy": policy.to_dict(),
        "event_count": len(retained_events),
        "events": retained_events,
        "non_destructive_prune": policy.non_destructive_prune,
        "production_audit_retention_ready": False,
    }
    full_export_path.write_text(json.dumps(full_payload, indent=2, ensure_ascii=False), encoding="utf-8")
    retained_path.write_text(json.dumps(retained_payload, indent=2, ensure_ascii=False), encoding="utf-8")
    full_hash = _canonical_hash(full_payload)
    retained_hash = _canonical_hash(retained_payload)
    pruned_hashes = [_canonical_hash(event) for event in pruned_events]
    retention_ready = (
        policy.export_before_prune
        and policy.non_destructive_prune
        and len(events) > len(retained_events)
        and len(retained_events) <= max_events
        and len(full_hash) == 64
        and len(retained_hash) == 64
        and full_export_path.exists()
        and retained_path.exists()
    )
    return {
        "version": "v5.30",
        "policy": policy.to_dict(),
        "source_event_count": len(events),
        "retained_event_count": len(retained_events),
        "pruned_event_count": len(pruned_events),
        "full_export_path": str(full_export_path).replace("\\", "/"),
        "retained_events_path": str(retained_path).replace("\\", "/"),
        "full_export_sha256": full_hash,
        "retained_events_sha256": retained_hash,
        "pruned_event_hashes": pruned_hashes,
        "retention_policy_contract_ready": retention_ready,
        "retention_pruning_non_destructive": policy.non_destructive_prune,
        "production_audit_retention_ready": False,
        "claim_boundary": "v5.30 applies a local non-destructive retention policy after writing a full audit export. It does not claim production audit retention or tenant-isolated storage.",
    }


def run_runtime_observability_workflow_v530(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    project_root = Path(root).resolve()
    out = project_root / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    supervisor_audit = run_supervised_runtime_workflow_v529(project_root, out)
    metrics = build_runtime_metrics_snapshot_v530(supervisor_audit)
    status_snapshots = build_runtime_status_snapshots_v530(supervisor_audit)
    retention = apply_audit_retention_policy_v530(list(supervisor_audit.get("audit_events", [])), out)
    proof_ready = (
        supervisor_audit.get("supervised_local_runtime_ready") is True
        and metrics.get("local_metrics_snapshot_ready") is True
        and len(status_snapshots) >= 7
        and retention.get("retention_policy_contract_ready") is True
        and supervisor_audit.get("production_runtime_ready") is False
        and supervisor_audit.get("bic_os_phase_locked") is True
    )
    return {
        "version": "v5.30",
        "phase": "runtime_metrics_retention_observability",
        "overall_status": "runtime_observability_retention_ready_runtime_not_claimed" if proof_ready else "runtime_observability_retention_incomplete",
        "active_phase": "biocompute_runtime_observability_proof",
        "bic_os_phase_locked": True,
        "runtime_observability_ready": proof_ready,
        "local_metrics_snapshot_ready": metrics["local_metrics_snapshot_ready"],
        "status_snapshot_count": len(status_snapshots),
        "retention_policy_contract_ready": retention["retention_policy_contract_ready"],
        "retention_pruning_non_destructive": retention["retention_pruning_non_destructive"],
        "source_audit_event_count": retention["source_event_count"],
        "retained_audit_event_count": retention["retained_event_count"],
        "pruned_audit_event_count": retention["pruned_event_count"],
        "metrics_event_count": metrics["audit_event_count"],
        "metrics_worker_tick_count": metrics["event_counts"].get("worker_tick", 0),
        "metrics_succeeded_job_count": metrics["job_status_counts"].get(JobStatus.SUCCEEDED.value, 0),
        "result_bundle_count": metrics["result_bundle_count"],
        "heartbeat_index": metrics["heartbeat_index"],
        "production_metrics_ready": False,
        "production_audit_retention_ready": False,
        "production_runtime_ready": False,
        "production_api_ready": False,
        "production_biocompute_runtime_ready": False,
        "full_biosdk_ready": False,
        "live_actuation_enabled": False,
        "metrics": metrics,
        "status_snapshots": status_snapshots,
        "retention_manifest": retention,
        "supervisor_summary": {key: value for key, value in supervisor_audit.items() if key not in {"actions", "jobs", "audit_events"}},
        "remaining_runtime_blockers": [
            "production metrics backend and scrape/export endpoint",
            "retention policy tied to tenant, workspace and compliance requirements",
            "tamper-evident append-only audit storage",
            "alerting for stale heartbeats and failed workers",
            "hosted deployment observability and dashboards",
            "production object storage retention for result bundles",
        ],
        "direct_answer": {
            "did_we_add_local_runtime_metrics": "yes" if metrics["local_metrics_snapshot_ready"] else "not_yet",
            "did_we_add_retention_policy_contract": "yes" if retention["retention_policy_contract_ready"] else "not_yet",
            "is_production_observability_ready": "no",
            "is_biocompute_runtime_ready": "no",
            "is_bic_os_ready": "no",
            "next_best_build_step": "add stale-heartbeat alerting and worker failure recovery proof" if proof_ready else "fix v5.30 observability blockers first",
        },
        "claim_boundary": "v5.30 proves local runtime metrics snapshots and a non-destructive audit retention policy over the v5.29 supervisor proof. It does not claim production observability, hosted BioCompute Runtime, production audit retention, full BioSDK or BiC OS readiness.",
    }


def write_runtime_observability_outputs_v530(audit: dict[str, Any], out_dir: str | Path = DEFAULT_OUT) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary_json": out / "V530_RUNTIME_OBSERVABILITY_SUMMARY.json",
        "metrics_json": out / "V530_RUNTIME_METRICS_SNAPSHOT.json",
        "status_snapshots_json": out / "V530_RUNTIME_STATUS_SNAPSHOTS.json",
        "retention_manifest_json": out / "V530_AUDIT_RETENTION_MANIFEST.json",
        "metrics_csv": out / "V530_RUNTIME_METRICS.csv",
        "markdown_report": out / "BIOGPU_V530_RUNTIME_OBSERVABILITY_REPORT.md",
    }
    summary = {key: value for key, value in audit.items() if key not in {"metrics", "status_snapshots", "retention_manifest"}}
    paths["summary_json"].write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["metrics_json"].write_text(json.dumps(audit["metrics"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["status_snapshots_json"].write_text(json.dumps({"snapshots": audit["status_snapshots"]}, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["retention_manifest_json"].write_text(json.dumps(audit["retention_manifest"], indent=2, ensure_ascii=False), encoding="utf-8")
    _write_metrics_csv(paths["metrics_csv"], audit["metrics"])
    paths["markdown_report"].write_text(_markdown_report(audit), encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}


def _write_metrics_csv(path: Path, metrics: dict[str, Any]) -> None:
    rows = [
        ("runtime_status", metrics.get("runtime_status")),
        ("heartbeat_index", metrics.get("heartbeat_index")),
        ("audit_event_count", metrics.get("audit_event_count")),
        ("worker_tick_count", metrics.get("event_counts", {}).get("worker_tick", 0)),
        ("succeeded_job_count", metrics.get("job_status_counts", {}).get(JobStatus.SUCCEEDED.value, 0)),
        ("result_bundle_count", metrics.get("result_bundle_count")),
        ("result_artifact_bytes", metrics.get("result_artifact_bytes")),
        ("local_metrics_snapshot_ready", metrics.get("local_metrics_snapshot_ready")),
        ("production_metrics_ready", metrics.get("production_metrics_ready")),
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["metric", "value"])
        writer.writerows(rows)


def _markdown_report(audit: dict[str, Any]) -> str:
    answer = audit["direct_answer"]
    lines = [
        "# BioGPU-Core v5.30 Runtime Observability",
        "",
        "## Direct Answer",
        "",
        f"- Local runtime metrics: `{answer['did_we_add_local_runtime_metrics']}`",
        f"- Retention policy contract: `{answer['did_we_add_retention_policy_contract']}`",
        f"- Production observability ready: `{answer['is_production_observability_ready']}`",
        f"- BioCompute Runtime ready: `{answer['is_biocompute_runtime_ready']}`",
        f"- BiC OS ready: `{answer['is_bic_os_ready']}`",
        f"- Next best build step: {answer['next_best_build_step']}",
        "",
        "## Proof Summary",
        "",
        f"- Metrics ready: `{audit['local_metrics_snapshot_ready']}`",
        f"- Status snapshots: `{audit['status_snapshot_count']}`",
        f"- Retention policy ready: `{audit['retention_policy_contract_ready']}`",
        f"- Source audit events: `{audit['source_audit_event_count']}`",
        f"- Retained audit events: `{audit['retained_audit_event_count']}`",
        f"- Pruned audit events: `{audit['pruned_audit_event_count']}`",
        f"- Worker ticks: `{audit['metrics_worker_tick_count']}`",
        f"- Succeeded jobs: `{audit['metrics_succeeded_job_count']}`",
        "",
        "## Remaining Runtime Blockers",
        "",
    ]
    for blocker in audit["remaining_runtime_blockers"]:
        lines.append(f"- {blocker}")
    lines.extend(["", "## Boundary", "", audit["claim_boundary"], ""])
    return "\n".join(lines)