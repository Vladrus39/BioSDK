"""Tenant-aware operator roles and incident permissions proof, v5.35."""
from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from biogpu.beta.job_model_v43 import utc_now_iso
from biogpu.evidence.ledger_v53 import stable_hash
from biogpu.runtime.incident_ledger_v534 import run_tamper_evident_incident_ledger_workflow_v534


DEFAULT_OUT = Path("outputs/v535_tenant_incident_permissions")


@dataclass(frozen=True)
class IncidentPrincipalV535:
    principal_id: str
    user_id: str
    tenant_id: str
    role: str
    scopes: tuple[str, ...]
    production_auth_ready: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class IncidentPermissionDecisionV535:
    decision_id: str
    action: str
    accepted: bool
    status: str
    principal_id: str | None
    tenant_id: str | None
    incident_id: str | None
    required_scope: str
    errors: tuple[str, ...]
    production_incident_permissions_ready: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


ACTION_SCOPES_V535 = {
    "incident_read": "incidents:read",
    "incident_acknowledge": "incidents:acknowledge",
    "incident_resolve": "incidents:resolve",
    "incident_archive": "incidents:archive",
    "incident_ledger_read": "incident_ledger:read",
    "incident_ledger_validate": "incident_ledger:validate",
}


def default_incident_principals_v535() -> dict[str, IncidentPrincipalV535]:
    return {
        "tenant_alpha_operator": IncidentPrincipalV535(
            "tenant_alpha_operator",
            "operator_alpha_v535",
            "tenant_alpha",
            "operator",
            ("incidents:read", "incidents:acknowledge", "incidents:resolve", "incident_ledger:read"),
        ),
        "tenant_alpha_viewer": IncidentPrincipalV535(
            "tenant_alpha_viewer",
            "viewer_alpha_v535",
            "tenant_alpha",
            "viewer",
            ("incidents:read", "incident_ledger:read"),
        ),
        "tenant_alpha_admin": IncidentPrincipalV535(
            "tenant_alpha_admin",
            "admin_alpha_v535",
            "tenant_alpha",
            "incident_admin",
            ("incidents:read", "incidents:acknowledge", "incidents:resolve", "incidents:archive", "incident_ledger:read", "incident_ledger:validate"),
        ),
        "tenant_beta_operator": IncidentPrincipalV535(
            "tenant_beta_operator",
            "operator_beta_v535",
            "tenant_beta",
            "operator",
            ("incidents:read", "incidents:acknowledge", "incidents:resolve", "incident_ledger:read"),
        ),
        "system_auditor": IncidentPrincipalV535(
            "system_auditor",
            "auditor_v535",
            "system",
            "auditor",
            ("incident_ledger:read", "incident_ledger:validate"),
        ),
    }


def _decision_id(action: str, principal_id: str | None, incident_id: str | None, status: str) -> str:
    return "perm_" + stable_hash({"action": action, "principal_id": principal_id, "incident_id": incident_id, "status": status})[:16]


def _principal_dict(principal: IncidentPrincipalV535 | dict[str, Any] | None) -> dict[str, Any] | None:
    if principal is None:
        return None
    return principal.to_dict() if isinstance(principal, IncidentPrincipalV535) else dict(principal)


def build_tenant_incident_fixture_v535(v534_audit: dict[str, Any], tenant_id: str = "tenant_alpha") -> dict[str, Any]:
    ledger = v534_audit.get("ledger", {})
    records = list(ledger.get("source_records", []))
    opened_record = next((record for record in records if record.get("record_type") == "incident_opened"), {})
    opened = dict(opened_record.get("payload") or {})
    incident_id = str(opened.get("incident_id") or v534_audit.get("v533_dependency_summary", {}).get("active_incident_id") or "incident_v535_fixture")
    return {
        "incident_id": incident_id,
        "tenant_id": tenant_id,
        "status": opened.get("status", "resolved"),
        "kind": opened.get("kind", "dead_lettered_job"),
        "severity": opened.get("severity", "high"),
        "related_job_id": opened.get("related_job_id") or v534_audit.get("v533_dependency_summary", {}).get("dead_letter_job_id"),
        "ledger_id": ledger.get("ledger_id"),
        "ledger_chain_root": ledger.get("chain_root"),
        "retention_manifest_sha256": ledger.get("retention_manifest_sha256"),
        "production_incident_permissions_ready": False,
        "bic_os_phase_locked": True,
    }


def authorize_incident_action_v535(principal: IncidentPrincipalV535 | dict[str, Any] | None, incident: dict[str, Any], action: str) -> IncidentPermissionDecisionV535:
    required_scope = ACTION_SCOPES_V535.get(action, "unknown")
    principal_dict = _principal_dict(principal)
    incident_id = str(incident.get("incident_id")) if incident.get("incident_id") else None
    errors: list[str] = []
    if required_scope == "unknown":
        errors.append("unknown_action")
    if principal_dict is None:
        errors.append("missing_principal")
        status = "missing_principal"
        accepted = False
        principal_id = None
        tenant_id = None
    else:
        principal_id = str(principal_dict.get("principal_id"))
        tenant_id = str(principal_dict.get("tenant_id"))
        scopes = tuple(str(scope) for scope in principal_dict.get("scopes", []))
        tenant_match = tenant_id == incident.get("tenant_id") or tenant_id == "system"
        if required_scope not in scopes:
            errors.append(f"missing_scope:{required_scope}")
        if not tenant_match and action != "incident_ledger_validate":
            errors.append("tenant_mismatch")
        if action == "incident_ledger_validate" and principal_dict.get("role") not in {"incident_admin", "auditor"}:
            errors.append("role_not_allowed_for_ledger_validation")
        accepted = not errors
        status = "authorized" if accepted else "denied"
    return IncidentPermissionDecisionV535(
        decision_id=_decision_id(action, principal_id if principal_dict else None, incident_id, status),
        action=action,
        accepted=accepted,
        status=status,
        principal_id=principal_id if principal_dict else None,
        tenant_id=tenant_id if principal_dict else None,
        incident_id=incident_id,
        required_scope=required_scope,
        errors=tuple(errors),
    )


def run_incident_permission_matrix_v535(v534_audit: dict[str, Any]) -> dict[str, Any]:
    principals = default_incident_principals_v535()
    incident = build_tenant_incident_fixture_v535(v534_audit)
    checks = [
        ("operator_acknowledge_allowed", principals["tenant_alpha_operator"], "incident_acknowledge", True),
        ("operator_resolve_allowed", principals["tenant_alpha_operator"], "incident_resolve", True),
        ("viewer_acknowledge_denied", principals["tenant_alpha_viewer"], "incident_acknowledge", False),
        ("viewer_read_allowed", principals["tenant_alpha_viewer"], "incident_read", True),
        ("cross_tenant_operator_denied", principals["tenant_beta_operator"], "incident_resolve", False),
        ("admin_archive_allowed", principals["tenant_alpha_admin"], "incident_archive", True),
        ("auditor_validate_ledger_allowed", principals["system_auditor"], "incident_ledger_validate", True),
        ("operator_validate_ledger_denied", principals["tenant_alpha_operator"], "incident_ledger_validate", False),
        ("missing_principal_denied", None, "incident_read", False),
    ]
    decisions: list[dict[str, Any]] = []
    for name, principal, action, expected in checks:
        decision = authorize_incident_action_v535(principal, incident, action).to_dict()
        decision["check_name"] = name
        decision["expected_accepted"] = expected
        decision["passed"] = decision["accepted"] is expected
        decisions.append(decision)
    passed_count = sum(1 for decision in decisions if decision["passed"])
    denied_count = sum(1 for decision in decisions if decision["accepted"] is False)
    return {
        "version": "v5.35",
        "permission_matrix_ready": passed_count == len(decisions) and denied_count >= 4,
        "incident": incident,
        "principals": {key: principal.to_dict() for key, principal in principals.items()},
        "decisions": decisions,
        "decision_count": len(decisions),
        "passed_count": passed_count,
        "denied_count": denied_count,
        "tenant_isolation_passed": any(decision["check_name"] == "cross_tenant_operator_denied" and decision["passed"] for decision in decisions),
        "viewer_write_denial_passed": any(decision["check_name"] == "viewer_acknowledge_denied" and decision["passed"] for decision in decisions),
        "ledger_validation_scope_passed": any(decision["check_name"] == "auditor_validate_ledger_allowed" and decision["passed"] for decision in decisions),
        "production_incident_permissions_ready": False,
        "production_auth_ready": False,
        "bic_os_phase_locked": True,
    }


def build_permissions_audit_bundle_v535(matrix: dict[str, Any], v534_summary: dict[str, Any], out_dir: str | Path) -> dict[str, Any]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    bundle = {
        "version": "v5.35",
        "created_at": utc_now_iso(),
        "incident": matrix.get("incident"),
        "decision_count": matrix.get("decision_count"),
        "passed_count": matrix.get("passed_count"),
        "denied_count": matrix.get("denied_count"),
        "tenant_isolation_passed": matrix.get("tenant_isolation_passed"),
        "viewer_write_denial_passed": matrix.get("viewer_write_denial_passed"),
        "ledger_validation_scope_passed": matrix.get("ledger_validation_scope_passed"),
        "v534_dependency_status": v534_summary.get("overall_status"),
        "v534_chain_root": v534_summary.get("chain_root"),
        "production_incident_permissions_ready": False,
        "production_auth_ready": False,
        "bic_os_phase_locked": True,
    }
    bundle_hash = stable_hash(bundle)
    bundle["bundle_sha256"] = bundle_hash
    path = out / "V535_INCIDENT_PERMISSIONS_AUDIT_BUNDLE.json"
    path.write_text(json.dumps(bundle, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"bundle_path": str(path).replace("\\", "/"), "bundle_sha256": bundle_hash, "bundle_ready": path.exists() and len(bundle_hash) == 64, "bundle": bundle}


def run_tenant_incident_permissions_workflow_v535(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    project_root = Path(root).resolve()
    out = project_root / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    v534_dependency = run_tamper_evident_incident_ledger_workflow_v534(project_root, out / "d534")
    matrix = run_incident_permission_matrix_v535(v534_dependency)
    bundle = build_permissions_audit_bundle_v535(matrix, v534_dependency, out)
    proof_ready = (
        v534_dependency.get("tamper_evident_incident_ledger_ready") is True
        and matrix.get("permission_matrix_ready") is True
        and matrix.get("tenant_isolation_passed") is True
        and matrix.get("viewer_write_denial_passed") is True
        and matrix.get("ledger_validation_scope_passed") is True
        and bundle.get("bundle_ready") is True
        and matrix.get("production_incident_permissions_ready") is False
    )
    return {
        "version": "v5.35",
        "phase": "tenant_incident_permissions",
        "overall_status": "tenant_incident_permissions_proof_ready_runtime_not_claimed" if proof_ready else "tenant_incident_permissions_proof_incomplete",
        "active_phase": "biocompute_runtime_permission_proof",
        "bic_os_phase_locked": True,
        "tenant_incident_permissions_ready": proof_ready,
        "permission_matrix_ready": matrix.get("permission_matrix_ready") is True,
        "tenant_isolation_passed": matrix.get("tenant_isolation_passed") is True,
        "viewer_write_denial_passed": matrix.get("viewer_write_denial_passed") is True,
        "ledger_validation_scope_passed": matrix.get("ledger_validation_scope_passed") is True,
        "permissions_audit_bundle_ready": bundle.get("bundle_ready") is True,
        "v534_dependency_ready": v534_dependency.get("tamper_evident_incident_ledger_ready") is True,
        "decision_count": matrix.get("decision_count"),
        "passed_count": matrix.get("passed_count"),
        "denied_count": matrix.get("denied_count"),
        "production_incident_permissions_ready": False,
        "production_auth_ready": False,
        "production_incident_ledger_ready": False,
        "production_recovery_ready": False,
        "production_runtime_ready": False,
        "production_api_ready": False,
        "production_biocompute_runtime_ready": False,
        "full_biosdk_ready": False,
        "live_actuation_enabled": False,
        "permission_matrix": matrix,
        "permissions_audit_bundle": {key: value for key, value in bundle.items() if key != "bundle"},
        "v534_dependency_summary": {key: value for key, value in v534_dependency.items() if key not in {"ledger", "v533_dependency_summary"}},
        "remaining_runtime_blockers": [
            "production identity provider integration and key rotation",
            "persistent tenant/workspace membership store",
            "hosted incident dashboards and paging integrations",
            "external notarization or remote append-only storage for incident ledger roots",
            "production monitor loop and production alert routing",
            "process crash supervision instead of deterministic timeout fixtures",
        ],
        "direct_answer": {
            "is_local_only_the_right_mode_now": "yes",
            "why_local_only": "we are still proving contracts, evidence, guardrails and audit boundaries before hosted production deployment",
            "did_we_add_tenant_operator_permissions": "yes" if matrix.get("permission_matrix_ready") else "not_yet",
            "did_we_deny_viewer_write_actions": "yes" if matrix.get("viewer_write_denial_passed") else "not_yet",
            "did_we_deny_cross_tenant_operator_actions": "yes" if matrix.get("tenant_isolation_passed") else "not_yet",
            "is_production_auth_ready": "no",
            "is_biocompute_runtime_ready": "no",
            "is_bic_os_ready": "no",
            "next_best_build_step": "add hosted dashboard route-contract proof" if proof_ready else "fix v5.35 permission blockers first",
        },
        "claim_boundary": "v5.35 proves local fixture-scoped tenant roles, incident action scopes, cross-tenant denial and viewer write denial over the v5.34 incident ledger. It does not claim production identity, hosted auth, persistent tenant membership, full BioCompute Runtime or BiC OS readiness.",
    }


def write_tenant_incident_permissions_outputs_v535(audit: dict[str, Any], out_dir: str | Path = DEFAULT_OUT) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary_json": out / "V535_TENANT_INCIDENT_PERMISSIONS_SUMMARY.json",
        "principals_json": out / "V535_INCIDENT_PERMISSION_PRINCIPALS.json",
        "decisions_json": out / "V535_INCIDENT_PERMISSION_DECISIONS.json",
        "decisions_csv": out / "V535_INCIDENT_PERMISSION_DECISIONS.csv",
        "markdown_report": out / "BIOGPU_V535_TENANT_INCIDENT_PERMISSIONS_REPORT.md",
    }
    summary = {key: value for key, value in audit.items() if key not in {"permission_matrix"}}
    paths["summary_json"].write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["principals_json"].write_text(json.dumps(audit["permission_matrix"].get("principals", {}), indent=2, ensure_ascii=False), encoding="utf-8")
    paths["decisions_json"].write_text(json.dumps({"decisions": audit["permission_matrix"].get("decisions", [])}, indent=2, ensure_ascii=False), encoding="utf-8")
    _write_decisions_csv(paths["decisions_csv"], audit["permission_matrix"].get("decisions", []))
    paths["markdown_report"].write_text(_markdown_report(audit), encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}


def _write_decisions_csv(path: Path, decisions: list[dict[str, Any]]) -> None:
    fieldnames = ["check_name", "action", "principal_id", "tenant_id", "incident_id", "accepted", "expected_accepted", "passed", "status", "errors"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for decision in decisions:
            row = {field: decision.get(field) for field in fieldnames}
            row["errors"] = " | ".join(str(item) for item in decision.get("errors", []))
            writer.writerow(row)


def _markdown_report(audit: dict[str, Any]) -> str:
    answer = audit["direct_answer"]
    lines = [
        "# BioGPU-Core v5.35 Tenant Incident Permissions",
        "",
        "## Direct Answer",
        "",
        f"- Local-only mode is right now: `{answer['is_local_only_the_right_mode_now']}`",
        f"- Why: {answer['why_local_only']}",
        f"- Tenant operator permissions: `{answer['did_we_add_tenant_operator_permissions']}`",
        f"- Viewer write denial: `{answer['did_we_deny_viewer_write_actions']}`",
        f"- Cross-tenant denial: `{answer['did_we_deny_cross_tenant_operator_actions']}`",
        f"- Production auth ready: `{answer['is_production_auth_ready']}`",
        f"- BioCompute Runtime ready: `{answer['is_biocompute_runtime_ready']}`",
        f"- BiC OS ready: `{answer['is_bic_os_ready']}`",
        f"- Next best build step: {answer['next_best_build_step']}",
        "",
        "## Proof Summary",
        "",
        f"- Overall status: `{audit['overall_status']}`",
        f"- Permission matrix ready: `{audit['permission_matrix_ready']}`",
        f"- Tenant isolation passed: `{audit['tenant_isolation_passed']}`",
        f"- Viewer write denial passed: `{audit['viewer_write_denial_passed']}`",
        f"- Ledger validation scope passed: `{audit['ledger_validation_scope_passed']}`",
        f"- Decisions: `{audit['decision_count']}`",
        "",
        "## Remaining Runtime Blockers",
        "",
    ]
    for blocker in audit["remaining_runtime_blockers"]:
        lines.append(f"- {blocker}")
    lines.extend(["", "## Boundary", "", audit["claim_boundary"], ""])
    return "\n".join(lines)