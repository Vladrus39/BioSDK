"""Operator acknowledgement and incident retention proof, v5.33."""
from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from biogpu.beta.job_model_v43 import utc_now_iso
from biogpu.runtime.retry_policy_v532 import build_retry_policy_audit_bundle_v532, run_bounded_retry_dead_letter_probe_v532


DEFAULT_OUT = Path("outputs/v533_operator_incident_retention")
DEFAULT_OBSERVED_AT = "2026-05-07T04:20:00+00:00"


@dataclass(frozen=True)
class IncidentRecordV533:
    incident_id: str
    kind: str
    severity: str
    status: str
    source_version: str
    created_at: str
    updated_at: str
    related_job_id: str | None
    summary: str
    details: dict[str, Any]
    acknowledged_by: str | None = None
    acknowledged_at: str | None = None
    resolved_by: str | None = None
    resolved_at: str | None = None
    production_incident_workflow_ready: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class IncidentActionV533:
    action_id: str
    incident_id: str
    action: str
    accepted: bool
    actor_id: str
    action_time: str
    status_before: str
    status_after: str
    note: str
    production_operator_workflow_ready: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class IncidentRetentionPolicyV533:
    policy_id: str = "v533_local_incident_retention_policy"
    retain_resolved_days: int = 7
    archive_before_prune: bool = True
    full_export_required: bool = True
    observed_at: str = DEFAULT_OBSERVED_AT
    production_incident_retention_ready: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _hash_payload(prefix: str, payload: Any) -> str:
    data = json.dumps(payload, sort_keys=True, ensure_ascii=True).encode("utf-8")
    return f"{prefix}_{hashlib.sha256(data).hexdigest()[:16]}"


def _parse_time(value: str | None) -> datetime:
    if not value:
        return datetime.min.replace(tzinfo=timezone.utc)
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return datetime.min.replace(tzinfo=timezone.utc)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def build_dead_letter_incident_v533(v532_audit: dict[str, Any], created_at: str | None = None) -> IncidentRecordV533:
    incident_time = created_at or utc_now_iso()
    dead_letter_job_id = v532_audit.get("dead_letter_job_id")
    dead_letter_queue = (v532_audit.get("probe", {}).get("dead_letter_queue") or [{}])
    dead_letter_entry = dead_letter_queue[0] if dead_letter_queue else {}
    incident_id = _hash_payload("incident", {"kind": "dead_lettered_job", "job_id": dead_letter_job_id, "version": "v5.33"})
    return IncidentRecordV533(
        incident_id=incident_id,
        kind="dead_lettered_job",
        severity="high",
        status="open",
        source_version="v5.32",
        created_at=incident_time,
        updated_at=incident_time,
        related_job_id=str(dead_letter_job_id) if dead_letter_job_id else None,
        summary="Dead-lettered durable scheduler job requires operator acknowledgement.",
        details={
            "dead_letter_entry": dead_letter_entry,
            "retry_job_ids": v532_audit.get("retry_job_ids", []),
            "max_retry_attempts": v532_audit.get("max_retry_attempts"),
            "production_retry_policy_ready": False,
            "production_operator_workflow_ready": False,
            "bic_os_phase_locked": True,
        },
    )


def acknowledge_incident_v533(incident: IncidentRecordV533 | dict[str, Any], operator_id: str = "operator_v533", note: str = "acknowledged_local_dead_letter_incident", action_time: str | None = None) -> dict[str, Any]:
    incident_dict = incident.to_dict() if isinstance(incident, IncidentRecordV533) else dict(incident)
    now = action_time or utc_now_iso()
    before = str(incident_dict.get("status"))
    accepted = before == "open"
    after = "acknowledged" if accepted else before
    if accepted:
        incident_dict.update({"status": after, "updated_at": now, "acknowledged_by": operator_id, "acknowledged_at": now})
    action = IncidentActionV533(
        action_id=_hash_payload("incident_action", {"incident_id": incident_dict.get("incident_id"), "action": "acknowledge", "accepted": accepted, "time": now}),
        incident_id=str(incident_dict.get("incident_id")),
        action="acknowledge",
        accepted=accepted,
        actor_id=operator_id,
        action_time=now,
        status_before=before,
        status_after=after,
        note=note,
    )
    return {"incident": incident_dict, "action": action.to_dict()}


def resolve_incident_v533(incident: IncidentRecordV533 | dict[str, Any], operator_id: str = "operator_v533", resolution: str = "dead_letter_reviewed_no_live_action", action_time: str | None = None) -> dict[str, Any]:
    incident_dict = incident.to_dict() if isinstance(incident, IncidentRecordV533) else dict(incident)
    now = action_time or utc_now_iso()
    before = str(incident_dict.get("status"))
    accepted = before == "acknowledged"
    after = "resolved" if accepted else before
    if accepted:
        incident_dict.update({"status": after, "updated_at": now, "resolved_by": operator_id, "resolved_at": now})
        details = dict(incident_dict.get("details") or {})
        details.update({"resolution": resolution, "live_actuation_enabled": False})
        incident_dict["details"] = details
    action = IncidentActionV533(
        action_id=_hash_payload("incident_action", {"incident_id": incident_dict.get("incident_id"), "action": "resolve", "accepted": accepted, "time": now}),
        incident_id=str(incident_dict.get("incident_id")),
        action="resolve",
        accepted=accepted,
        actor_id=operator_id,
        action_time=now,
        status_before=before,
        status_after=after,
        note=resolution,
    )
    return {"incident": incident_dict, "action": action.to_dict()}


def _legacy_resolved_incident_v533() -> dict[str, Any]:
    incident = IncidentRecordV533(
        incident_id="incident_v533_legacy_resolved_fixture",
        kind="dead_lettered_job",
        severity="medium",
        status="resolved",
        source_version="v5.32",
        created_at="2026-04-01T00:00:00+00:00",
        updated_at="2026-04-01T00:05:00+00:00",
        related_job_id="job_v533_legacy_dead_letter_fixture",
        summary="Legacy resolved incident retained for local retention policy proof.",
        details={"fixture": True, "live_actuation_enabled": False},
        acknowledged_by="operator_v533",
        acknowledged_at="2026-04-01T00:02:00+00:00",
        resolved_by="operator_v533",
        resolved_at="2026-04-01T00:05:00+00:00",
    ).to_dict()
    return incident


def build_operator_incident_timeline_v533(v532_audit: dict[str, Any]) -> dict[str, Any]:
    opened = build_dead_letter_incident_v533(v532_audit, created_at="2026-05-07T04:20:00+00:00")
    acknowledgement = acknowledge_incident_v533(opened, action_time="2026-05-07T04:21:00+00:00")
    resolution = resolve_incident_v533(acknowledgement["incident"], action_time="2026-05-07T04:22:00+00:00")
    legacy_incident = _legacy_resolved_incident_v533()
    incidents = [resolution["incident"], legacy_incident]
    actions = [acknowledgement["action"], resolution["action"]]
    state_sequence = ["open", acknowledgement["action"]["status_after"], resolution["action"]["status_after"]]
    return {
        "version": "v5.33",
        "timeline_ready": acknowledgement["action"]["accepted"] is True and resolution["action"]["accepted"] is True,
        "operator_acknowledgement_ready": acknowledgement["action"]["accepted"] is True,
        "incident_resolution_ready": resolution["action"]["accepted"] is True,
        "state_sequence": state_sequence,
        "opened_incident": opened.to_dict(),
        "acknowledgement_action": acknowledgement["action"],
        "resolution_action": resolution["action"],
        "incidents": incidents,
        "actions": actions,
        "production_operator_workflow_ready": False,
        "bic_os_phase_locked": True,
    }


def apply_incident_retention_policy_v533(timeline: dict[str, Any], out_dir: str | Path, policy: IncidentRetentionPolicyV533 | None = None) -> dict[str, Any]:
    retention_policy = policy or IncidentRetentionPolicyV533()
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    observed_dt = _parse_time(retention_policy.observed_at)
    cutoff = observed_dt - timedelta(days=retention_policy.retain_resolved_days)
    incidents = list(timeline.get("incidents", []))
    actions = list(timeline.get("actions", []))
    retained: list[dict[str, Any]] = []
    archived: list[dict[str, Any]] = []
    for incident in incidents:
        resolved_at = _parse_time(str(incident.get("resolved_at") or ""))
        if incident.get("status") != "resolved" or resolved_at >= cutoff:
            retained.append(incident)
        else:
            archived.append(incident)

    full_export = {"version": "v5.33", "policy": retention_policy.to_dict(), "incidents": incidents, "actions": actions}
    full_export_path = out / "V533_INCIDENT_FULL_EXPORT.json"
    retained_path = out / "V533_INCIDENT_RETAINED.json"
    archive_path = out / "V533_INCIDENT_ARCHIVE.json"
    full_export_path.write_text(json.dumps(full_export, indent=2, ensure_ascii=False), encoding="utf-8")
    retained_path.write_text(json.dumps({"incidents": retained}, indent=2, ensure_ascii=False), encoding="utf-8")
    archive_path.write_text(json.dumps({"incidents": archived}, indent=2, ensure_ascii=False), encoding="utf-8")
    manifest = {
        "version": "v5.33",
        "policy": retention_policy.to_dict(),
        "observed_at": retention_policy.observed_at,
        "retention_cutoff": cutoff.isoformat(timespec="seconds"),
        "full_export_path": str(full_export_path).replace("\\", "/"),
        "retained_path": str(retained_path).replace("\\", "/"),
        "archive_path": str(archive_path).replace("\\", "/"),
        "source_incident_count": len(incidents),
        "retained_incident_count": len(retained),
        "archived_incident_count": len(archived),
        "pruned_from_active_count": len(archived),
        "non_destructive_full_export": full_export_path.exists() and len(incidents) == len(retained) + len(archived),
        "production_incident_retention_ready": False,
        "bic_os_phase_locked": True,
    }
    manifest_hash = hashlib.sha256(json.dumps(manifest, sort_keys=True, ensure_ascii=True).encode("utf-8")).hexdigest()
    manifest["manifest_sha256"] = manifest_hash
    manifest_path = out / "V533_INCIDENT_RETENTION_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    manifest["manifest_path"] = str(manifest_path).replace("\\", "/")
    manifest["retained_incidents"] = retained
    manifest["archived_incidents"] = archived
    return manifest


def build_incident_audit_bundle_v533(timeline: dict[str, Any], retention_manifest: dict[str, Any], v532_summary: dict[str, Any], out_dir: str | Path) -> dict[str, Any]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    bundle = {
        "version": "v5.33",
        "created_at": utc_now_iso(),
        "timeline": {key: value for key, value in timeline.items() if key not in {"incidents", "actions"}},
        "incidents": timeline.get("incidents", []),
        "actions": timeline.get("actions", []),
        "retention_manifest": {key: value for key, value in retention_manifest.items() if key not in {"retained_incidents", "archived_incidents"}},
        "v532_dependency_status": v532_summary.get("overall_status"),
        "production_operator_workflow_ready": False,
        "production_incident_retention_ready": False,
        "bic_os_phase_locked": True,
    }
    bundle_hash = hashlib.sha256(json.dumps(bundle, sort_keys=True, ensure_ascii=True).encode("utf-8")).hexdigest()
    bundle["bundle_sha256"] = bundle_hash
    path = out / "V533_INCIDENT_AUDIT_BUNDLE.json"
    path.write_text(json.dumps(bundle, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"bundle_path": str(path).replace("\\", "/"), "bundle_sha256": bundle_hash, "bundle_ready": path.exists() and len(bundle_hash) == 64, "bundle": bundle}


def _run_v532_dependency_for_v533(project_root: Path, out: Path) -> dict[str, Any]:
    dependency_out = out / "d532"
    probe = run_bounded_retry_dead_letter_probe_v532(project_root, dependency_out)
    bundle = build_retry_policy_audit_bundle_v532(probe, dependency_out)
    dead_letter_entry = probe["dead_letter_queue"][0] if probe.get("dead_letter_queue") else None
    proof_ready = probe.get("bounded_retry_dead_letter_probe_ready") is True and bundle.get("bundle_ready") is True
    return {
        "version": "v5.32",
        "overall_status": "bounded_retry_dead_letter_dependency_ready_runtime_not_claimed" if proof_ready else "bounded_retry_dead_letter_dependency_incomplete",
        "bounded_retry_dead_letter_ready": proof_ready,
        "bounded_retry_policy_ready": probe.get("bounded_retry_dead_letter_probe_ready") is True,
        "dead_letter_queue_ready": len(probe.get("dead_letter_queue", [])) == 1,
        "max_attempts_enforced": probe.get("max_attempts_enforced") is True,
        "retry_backoff_metadata_ready": probe.get("retry_backoff_metadata_ready") is True,
        "max_retry_attempts": probe["policy"]["max_retry_attempts"],
        "dead_letter_job_id": dead_letter_entry.get("job_id") if dead_letter_entry else None,
        "retry_job_ids": [action.get("retry_action", {}).get("related_job_id") for action in probe.get("policy_actions", []) if action.get("retry_action")],
        "production_retry_policy_ready": False,
        "production_dead_letter_queue_ready": False,
        "production_biocompute_runtime_ready": False,
        "full_biosdk_ready": False,
        "live_actuation_enabled": False,
        "probe": probe,
        "retry_policy_audit_bundle": {key: value for key, value in bundle.items() if key != "bundle"},
    }


def run_operator_incident_retention_workflow_v533(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    project_root = Path(root).resolve()
    out = project_root / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    v532_dependency = _run_v532_dependency_for_v533(project_root, out)
    timeline = build_operator_incident_timeline_v533(v532_dependency)
    retention_manifest = apply_incident_retention_policy_v533(timeline, out)
    bundle = build_incident_audit_bundle_v533(timeline, retention_manifest, v532_dependency, out)
    proof_ready = (
        v532_dependency.get("bounded_retry_dead_letter_ready") is True
        and timeline.get("operator_acknowledgement_ready") is True
        and timeline.get("incident_resolution_ready") is True
        and retention_manifest.get("non_destructive_full_export") is True
        and retention_manifest.get("archived_incident_count", 0) >= 1
        and bundle.get("bundle_ready") is True
        and v532_dependency.get("production_retry_policy_ready") is False
        and retention_manifest.get("production_incident_retention_ready") is False
    )
    return {
        "version": "v5.33",
        "phase": "operator_acknowledgement_incident_retention",
        "overall_status": "operator_incident_retention_proof_ready_runtime_not_claimed" if proof_ready else "operator_incident_retention_proof_incomplete",
        "active_phase": "biocompute_runtime_incident_workflow_proof",
        "bic_os_phase_locked": True,
        "operator_incident_retention_ready": proof_ready,
        "operator_acknowledgement_ready": timeline.get("operator_acknowledgement_ready") is True,
        "incident_resolution_ready": timeline.get("incident_resolution_ready") is True,
        "incident_retention_manifest_ready": retention_manifest.get("non_destructive_full_export") is True,
        "incident_audit_bundle_ready": bundle.get("bundle_ready") is True,
        "v532_dependency_ready": v532_dependency.get("bounded_retry_dead_letter_ready") is True,
        "incident_count": len(timeline.get("incidents", [])),
        "operator_action_count": len(timeline.get("actions", [])),
        "retained_incident_count": retention_manifest.get("retained_incident_count"),
        "archived_incident_count": retention_manifest.get("archived_incident_count"),
        "pruned_from_active_count": retention_manifest.get("pruned_from_active_count"),
        "active_incident_id": (timeline.get("incidents") or [{}])[0].get("incident_id"),
        "dead_letter_job_id": v532_dependency.get("dead_letter_job_id"),
        "production_operator_workflow_ready": False,
        "production_incident_retention_ready": False,
        "production_recovery_ready": False,
        "production_runtime_ready": False,
        "production_api_ready": False,
        "production_biocompute_runtime_ready": False,
        "full_biosdk_ready": False,
        "live_actuation_enabled": False,
        "timeline": timeline,
        "retention_manifest": {key: value for key, value in retention_manifest.items() if key not in {"retained_incidents", "archived_incidents"}},
        "incident_audit_bundle": {key: value for key, value in bundle.items() if key != "bundle"},
        "v532_dependency_summary": {key: value for key, value in v532_dependency.items() if key not in {"probe", "policy", "recovery_dependency_summary"}},
        "remaining_runtime_blockers": [
            "real background monitor loop and production alert routing",
            "tenant-aware operator roles and incident permissions",
            "tamper-evident append-only incident storage",
            "hosted incident dashboards and paging integrations",
            "production multi-worker retry orchestration with durable backoff timers",
            "process crash supervision instead of deterministic timeout fixtures",
        ],
        "direct_answer": {
            "did_we_add_operator_acknowledgement": "yes" if timeline.get("operator_acknowledgement_ready") else "not_yet",
            "did_we_add_incident_resolution": "yes" if timeline.get("incident_resolution_ready") else "not_yet",
            "did_we_add_incident_retention_manifest": "yes" if retention_manifest.get("non_destructive_full_export") else "not_yet",
            "is_production_incident_workflow_ready": "no",
            "is_biocompute_runtime_ready": "no",
            "is_bic_os_ready": "no",
            "next_best_build_step": "add tamper-evident incident ledger proof" if proof_ready else "fix v5.33 incident workflow blockers first",
        },
        "claim_boundary": "v5.33 proves local operator acknowledgement, incident resolution and non-destructive incident retention over the v5.32 dead-letter proof. It does not claim production incident management, tenant permissions, hosted dashboards, live external API control, full BioCompute Runtime or BiC OS readiness.",
    }


def write_operator_incident_retention_outputs_v533(audit: dict[str, Any], out_dir: str | Path = DEFAULT_OUT) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary_json": out / "V533_OPERATOR_INCIDENT_RETENTION_SUMMARY.json",
        "timeline_json": out / "V533_INCIDENT_TIMELINE.json",
        "acknowledgement_json": out / "V533_OPERATOR_ACKNOWLEDGEMENT.json",
        "retention_manifest_json": out / "V533_INCIDENT_RETENTION_MANIFEST_COPY.json",
        "incidents_csv": out / "V533_INCIDENTS.csv",
        "markdown_report": out / "BIOGPU_V533_OPERATOR_INCIDENT_RETENTION_REPORT.md",
    }
    summary = {key: value for key, value in audit.items() if key not in {"timeline"}}
    paths["summary_json"].write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["timeline_json"].write_text(json.dumps(audit["timeline"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["acknowledgement_json"].write_text(json.dumps({"acknowledgement_action": audit["timeline"].get("acknowledgement_action"), "resolution_action": audit["timeline"].get("resolution_action")}, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["retention_manifest_json"].write_text(json.dumps(audit["retention_manifest"], indent=2, ensure_ascii=False), encoding="utf-8")
    _write_incidents_csv(paths["incidents_csv"], audit["timeline"].get("incidents", []))
    paths["markdown_report"].write_text(_markdown_report(audit), encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}


def _write_incidents_csv(path: Path, incidents: list[dict[str, Any]]) -> None:
    fieldnames = ["incident_id", "kind", "severity", "status", "related_job_id", "acknowledged_by", "resolved_by", "resolved_at"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for incident in incidents:
            writer.writerow({field: incident.get(field) for field in fieldnames})


def _markdown_report(audit: dict[str, Any]) -> str:
    answer = audit["direct_answer"]
    lines = [
        "# BioGPU-Core v5.33 Operator Incident Retention",
        "",
        "## Direct Answer",
        "",
        f"- Operator acknowledgement: `{answer['did_we_add_operator_acknowledgement']}`",
        f"- Incident resolution: `{answer['did_we_add_incident_resolution']}`",
        f"- Incident retention manifest: `{answer['did_we_add_incident_retention_manifest']}`",
        f"- Production incident workflow ready: `{answer['is_production_incident_workflow_ready']}`",
        f"- BioCompute Runtime ready: `{answer['is_biocompute_runtime_ready']}`",
        f"- BiC OS ready: `{answer['is_bic_os_ready']}`",
        f"- Next best build step: {answer['next_best_build_step']}",
        "",
        "## Proof Summary",
        "",
        f"- Overall status: `{audit['overall_status']}`",
        f"- Operator acknowledgement ready: `{audit['operator_acknowledgement_ready']}`",
        f"- Incident resolution ready: `{audit['incident_resolution_ready']}`",
        f"- Incident retention manifest ready: `{audit['incident_retention_manifest_ready']}`",
        f"- Incident audit bundle ready: `{audit['incident_audit_bundle_ready']}`",
        f"- Active incident ID: `{audit['active_incident_id']}`",
        f"- Dead-letter job ID: `{audit['dead_letter_job_id']}`",
        "",
        "## Remaining Runtime Blockers",
        "",
    ]
    for blocker in audit["remaining_runtime_blockers"]:
        lines.append(f"- {blocker}")
    lines.extend(["", "## Boundary", "", audit["claim_boundary"], ""])
    return "\n".join(lines)