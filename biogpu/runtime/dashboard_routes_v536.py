"""Hosted dashboard route-contract proof, v5.36."""
from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from biogpu.beta.job_model_v43 import utc_now_iso
from biogpu.evidence.ledger_v53 import stable_hash
from biogpu.runtime.incident_permissions_v535 import (
    authorize_incident_action_v535,
    default_incident_principals_v535,
    run_tenant_incident_permissions_workflow_v535,
)


DEFAULT_OUT = Path("outputs/v536_dashboard_route_contract")


@dataclass(frozen=True)
class DashboardRouteContractV536:
    route_id: str
    path: str
    methods: tuple[str, ...]
    view_name: str
    action: str
    required_scope: str
    allowed_roles: tuple[str, ...]
    response_model: str
    mutating: bool = False
    local_contract_only: bool = True
    live_execution_enabled: bool = False
    production_dashboard_ready: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DashboardAccessProbeV536:
    probe_id: str
    route_id: str
    principal_id: str | None
    action: str
    accepted: bool
    expected_accepted: bool
    passed: bool
    status: str
    errors: tuple[str, ...]
    production_dashboard_ready: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_dashboard_route_contracts_v536() -> list[DashboardRouteContractV536]:
    return [
        DashboardRouteContractV536("dashboard_overview", "/v1/dashboard/overview", ("GET",), "overview", "incident_read", "incidents:read", ("operator", "viewer", "incident_admin"), "DashboardOverviewV536"),
        DashboardRouteContractV536("incident_list", "/v1/dashboard/incidents", ("GET",), "incident_list", "incident_read", "incidents:read", ("operator", "viewer", "incident_admin"), "IncidentListV536"),
        DashboardRouteContractV536("incident_detail", "/v1/dashboard/incidents/{incident_id}", ("GET",), "incident_detail", "incident_read", "incidents:read", ("operator", "viewer", "incident_admin"), "IncidentDetailV536"),
        DashboardRouteContractV536("incident_acknowledge", "/v1/dashboard/incidents/{incident_id}/acknowledge", ("POST",), "incident_action_result", "incident_acknowledge", "incidents:acknowledge", ("operator", "incident_admin"), "IncidentActionResultV536", True),
        DashboardRouteContractV536("incident_resolve", "/v1/dashboard/incidents/{incident_id}/resolve", ("POST",), "incident_action_result", "incident_resolve", "incidents:resolve", ("operator", "incident_admin"), "IncidentActionResultV536", True),
        DashboardRouteContractV536("incident_archive", "/v1/dashboard/incidents/{incident_id}/archive", ("POST",), "incident_action_result", "incident_archive", "incidents:archive", ("incident_admin",), "IncidentActionResultV536", True),
        DashboardRouteContractV536("incident_ledger", "/v1/dashboard/incident-ledger", ("GET",), "ledger_summary", "incident_ledger_read", "incident_ledger:read", ("operator", "viewer", "incident_admin", "auditor"), "IncidentLedgerSummaryV536"),
        DashboardRouteContractV536("incident_ledger_validate", "/v1/dashboard/incident-ledger/validate", ("POST",), "ledger_validation", "incident_ledger_validate", "incident_ledger:validate", ("incident_admin", "auditor"), "IncidentLedgerValidationV536", True),
        DashboardRouteContractV536("permission_matrix", "/v1/dashboard/permissions", ("GET",), "permissions_summary", "incident_ledger_validate", "incident_ledger:validate", ("incident_admin", "auditor"), "IncidentPermissionsSummaryV536"),
    ]


def build_dashboard_view_payloads_v536(v535_audit: dict[str, Any]) -> dict[str, Any]:
    matrix = v535_audit.get("permission_matrix", {})
    incident = dict(matrix.get("incident") or {})
    decisions = list(matrix.get("decisions") or [])
    dependency = dict(v535_audit.get("v534_dependency_summary") or {})
    denied_decisions = [decision for decision in decisions if decision.get("accepted") is False]
    return {
        "overview": {
            "version": "v5.36",
            "incident_count": 1 if incident else 0,
            "open_incident_count": 1 if incident.get("status") == "open" else 0,
            "permission_decision_count": len(decisions),
            "denied_decision_count": len(denied_decisions),
            "ledger_chain_root": incident.get("ledger_chain_root") or dependency.get("chain_root"),
            "production_dashboard_ready": False,
            "bic_os_phase_locked": True,
        },
        "incident_list": {
            "version": "v5.36",
            "items": [incident] if incident else [],
            "total": 1 if incident else 0,
            "production_dashboard_ready": False,
            "bic_os_phase_locked": True,
        },
        "incident_detail": {
            "version": "v5.36",
            "incident": incident,
            "allowed_local_actions": ["incident_read", "incident_acknowledge", "incident_resolve", "incident_archive"],
            "production_dashboard_ready": False,
            "bic_os_phase_locked": True,
        },
        "incident_action_result": {
            "version": "v5.36",
            "mode": "route_contract_only",
            "writes_execute_in_dashboard": False,
            "production_dashboard_ready": False,
            "bic_os_phase_locked": True,
        },
        "ledger_summary": {
            "version": "v5.36",
            "ledger_id": incident.get("ledger_id"),
            "ledger_chain_root": incident.get("ledger_chain_root") or dependency.get("chain_root"),
            "retention_manifest_sha256": incident.get("retention_manifest_sha256"),
            "v534_dependency_ready": v535_audit.get("v534_dependency_ready") is True,
            "production_dashboard_ready": False,
            "bic_os_phase_locked": True,
        },
        "ledger_validation": {
            "version": "v5.36",
            "validation_route_contract_ready": True,
            "source_chain_valid": dependency.get("incident_ledger_chain_valid") is True,
            "production_dashboard_ready": False,
            "bic_os_phase_locked": True,
        },
        "permissions_summary": {
            "version": "v5.36",
            "decision_count": matrix.get("decision_count"),
            "passed_count": matrix.get("passed_count"),
            "denied_count": matrix.get("denied_count"),
            "tenant_isolation_passed": matrix.get("tenant_isolation_passed") is True,
            "viewer_write_denial_passed": matrix.get("viewer_write_denial_passed") is True,
            "ledger_validation_scope_passed": matrix.get("ledger_validation_scope_passed") is True,
            "production_dashboard_ready": False,
            "bic_os_phase_locked": True,
        },
    }


def validate_dashboard_contracts_v536(routes: list[DashboardRouteContractV536], view_payloads: dict[str, Any]) -> dict[str, Any]:
    route_dicts = [route.to_dict() for route in routes]
    missing_views = [route.route_id for route in routes if route.view_name not in view_payloads]
    missing_scopes = [route.route_id for route in routes if not route.required_scope]
    unsafe_live_writes = [route.route_id for route in routes if route.mutating and route.live_execution_enabled]
    production_claims = [route.route_id for route in routes if route.production_dashboard_ready]
    payload_production_claims = [name for name, payload in view_payloads.items() if isinstance(payload, dict) and payload.get("production_dashboard_ready") is True]
    methods_ok = all(route.methods and all(method in {"GET", "POST"} for method in route.methods) for route in routes)
    unique_paths = len({(route.path, route.methods) for route in routes}) == len(routes)
    required_views = {"overview", "incident_list", "incident_detail", "incident_action_result", "ledger_summary", "ledger_validation", "permissions_summary"}
    ready = (
        len(routes) >= 9
        and methods_ok
        and unique_paths
        and not missing_views
        and not missing_scopes
        and not unsafe_live_writes
        and not production_claims
        and not payload_production_claims
        and required_views.issubset(set(view_payloads))
    )
    return {
        "version": "v5.36",
        "dashboard_contract_validation_ready": ready,
        "route_count": len(routes),
        "route_contracts_have_required_scopes": not missing_scopes,
        "route_views_have_payloads": not missing_views,
        "route_methods_valid": methods_ok,
        "route_paths_unique": unique_paths,
        "mutating_routes_do_not_execute_live": not unsafe_live_writes,
        "production_dashboard_claims_absent": not production_claims and not payload_production_claims,
        "missing_views": missing_views,
        "missing_scopes": missing_scopes,
        "unsafe_live_writes": unsafe_live_writes,
        "production_claims": production_claims + payload_production_claims,
        "route_manifest": route_dicts,
        "production_dashboard_ready": False,
        "bic_os_phase_locked": True,
    }


def run_dashboard_access_matrix_v536(v535_audit: dict[str, Any], routes: list[DashboardRouteContractV536]) -> dict[str, Any]:
    route_map = {route.route_id: route for route in routes}
    principals = default_incident_principals_v535()
    incident = dict(v535_audit.get("permission_matrix", {}).get("incident") or {})
    checks = [
        ("viewer_overview_allowed", "dashboard_overview", principals["tenant_alpha_viewer"], True),
        ("viewer_acknowledge_denied", "incident_acknowledge", principals["tenant_alpha_viewer"], False),
        ("operator_acknowledge_allowed", "incident_acknowledge", principals["tenant_alpha_operator"], True),
        ("cross_tenant_resolve_denied", "incident_resolve", principals["tenant_beta_operator"], False),
        ("admin_archive_allowed", "incident_archive", principals["tenant_alpha_admin"], True),
        ("auditor_validate_ledger_allowed", "incident_ledger_validate", principals["system_auditor"], True),
        ("operator_validate_ledger_denied", "incident_ledger_validate", principals["tenant_alpha_operator"], False),
        ("missing_principal_overview_denied", "dashboard_overview", None, False),
    ]
    probes: list[dict[str, Any]] = []
    for check_name, route_id, principal, expected in checks:
        route = route_map[route_id]
        decision = authorize_incident_action_v535(principal, incident, route.action)
        principal_id = decision.principal_id
        probe_id = "dash_" + stable_hash({"check_name": check_name, "route_id": route_id, "principal_id": principal_id, "expected": expected})[:16]
        probe = DashboardAccessProbeV536(
            probe_id,
            route_id,
            principal_id,
            route.action,
            decision.accepted,
            expected,
            decision.accepted is expected,
            decision.status,
            decision.errors,
        ).to_dict()
        probe["check_name"] = check_name
        probes.append(probe)
    passed_count = sum(1 for probe in probes if probe["passed"])
    denied_count = sum(1 for probe in probes if probe["accepted"] is False)
    return {
        "version": "v5.36",
        "dashboard_access_matrix_ready": passed_count == len(probes) and denied_count >= 4,
        "probe_count": len(probes),
        "passed_count": passed_count,
        "denied_count": denied_count,
        "viewer_write_denial_passed": any(probe["check_name"] == "viewer_acknowledge_denied" and probe["passed"] for probe in probes),
        "tenant_isolation_passed": any(probe["check_name"] == "cross_tenant_resolve_denied" and probe["passed"] for probe in probes),
        "ledger_validation_scope_passed": any(probe["check_name"] == "auditor_validate_ledger_allowed" and probe["passed"] for probe in probes),
        "probes": probes,
        "production_dashboard_ready": False,
        "production_auth_ready": False,
        "bic_os_phase_locked": True,
    }


def build_dashboard_audit_bundle_v536(validation: dict[str, Any], access_matrix: dict[str, Any], v535_summary: dict[str, Any], out_dir: str | Path) -> dict[str, Any]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    bundle = {
        "version": "v5.36",
        "created_at": utc_now_iso(),
        "route_count": validation.get("route_count"),
        "dashboard_contract_validation_ready": validation.get("dashboard_contract_validation_ready"),
        "dashboard_access_matrix_ready": access_matrix.get("dashboard_access_matrix_ready"),
        "viewer_write_denial_passed": access_matrix.get("viewer_write_denial_passed"),
        "tenant_isolation_passed": access_matrix.get("tenant_isolation_passed"),
        "ledger_validation_scope_passed": access_matrix.get("ledger_validation_scope_passed"),
        "v535_dependency_status": v535_summary.get("overall_status"),
        "v535_permissions_ready": v535_summary.get("tenant_incident_permissions_ready"),
        "production_dashboard_ready": False,
        "production_auth_ready": False,
        "bic_os_phase_locked": True,
    }
    bundle_hash = stable_hash(bundle)
    bundle["bundle_sha256"] = bundle_hash
    path = out / "V536_DASHBOARD_ROUTE_CONTRACT_AUDIT_BUNDLE.json"
    path.write_text(json.dumps(bundle, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"bundle_path": str(path).replace("\\", "/"), "bundle_sha256": bundle_hash, "bundle_ready": path.exists() and len(bundle_hash) == 64, "bundle": bundle}


def run_dashboard_route_contract_workflow_v536(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    project_root = Path(root).resolve()
    out = project_root / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    v535_dependency = run_tenant_incident_permissions_workflow_v535(project_root, out / "d535")
    routes = build_dashboard_route_contracts_v536()
    view_payloads = build_dashboard_view_payloads_v536(v535_dependency)
    validation = validate_dashboard_contracts_v536(routes, view_payloads)
    access_matrix = run_dashboard_access_matrix_v536(v535_dependency, routes)
    bundle = build_dashboard_audit_bundle_v536(validation, access_matrix, v535_dependency, out)
    proof_ready = (
        v535_dependency.get("tenant_incident_permissions_ready") is True
        and validation.get("dashboard_contract_validation_ready") is True
        and access_matrix.get("dashboard_access_matrix_ready") is True
        and bundle.get("bundle_ready") is True
        and validation.get("production_dashboard_claims_absent") is True
        and access_matrix.get("production_dashboard_ready") is False
    )
    return {
        "version": "v5.36",
        "phase": "dashboard_route_contract",
        "overall_status": "dashboard_route_contract_proof_ready_runtime_not_claimed" if proof_ready else "dashboard_route_contract_proof_incomplete",
        "active_phase": "biocompute_control_plane_dashboard_contract_proof",
        "bic_os_phase_locked": True,
        "dashboard_route_contract_ready": proof_ready,
        "dashboard_contract_validation_ready": validation.get("dashboard_contract_validation_ready") is True,
        "dashboard_access_matrix_ready": access_matrix.get("dashboard_access_matrix_ready") is True,
        "dashboard_audit_bundle_ready": bundle.get("bundle_ready") is True,
        "route_count": validation.get("route_count"),
        "access_probe_count": access_matrix.get("probe_count"),
        "access_passed_count": access_matrix.get("passed_count"),
        "viewer_write_denial_passed": access_matrix.get("viewer_write_denial_passed") is True,
        "tenant_isolation_passed": access_matrix.get("tenant_isolation_passed") is True,
        "ledger_validation_scope_passed": access_matrix.get("ledger_validation_scope_passed") is True,
        "v535_dependency_ready": v535_dependency.get("tenant_incident_permissions_ready") is True,
        "production_dashboard_ready": False,
        "production_auth_ready": False,
        "production_api_ready": False,
        "production_biocompute_runtime_ready": False,
        "full_biosdk_ready": False,
        "live_actuation_enabled": False,
        "dashboard_routes": validation.get("route_manifest"),
        "dashboard_view_payloads": view_payloads,
        "dashboard_access_matrix": access_matrix,
        "dashboard_audit_bundle": {key: value for key, value in bundle.items() if key != "bundle"},
        "v535_dependency_summary": {key: value for key, value in v535_dependency.items() if key not in {"permission_matrix", "v534_dependency_summary"}},
        "remaining_runtime_blockers": [
            "production identity provider integration and key rotation",
            "persistent tenant/workspace membership store",
            "hosted dashboard server and browser session enforcement",
            "production object storage and audit retention backend",
            "external notarization or remote append-only storage for incident ledger roots",
            "real external read-only API credentials or partner exports",
            "lab-approved live telemetry and closed-loop approval workflow",
        ],
        "real_data_or_api_requirements": [
            "repeatable raw neural recordings with stimulus/event metadata from Zenodo/MCS or equivalent HDF5 exports",
            "validated public NWB/DANDI assets with units, trials and stimulus/task metadata",
            "Allen visual-coding style public benchmark assets for cross-dataset orientation/readout checks",
            "one or more safe vendor/user exports for private beta upload/import validation",
            "non-mock read-only external API token or export from a neural compute provider",
            "OIDC/OAuth or enterprise SSO provider for production identity",
            "object storage API for result bundles, retention manifests and audit artifacts",
            "append-only/notarization API or remote immutable storage for ledger roots",
            "monitoring/paging API for production incident routing",
            "lab approval API or signed manual approval workflow before any live closed-loop module",
        ],
        "direct_answer": {
            "are_we_configured_to_move_to_model_plus_os_after_real_proof": "yes_gradually",
            "when_estimate": "milestone_based_not_calendar_based",
            "earliest_responsible_next_state": "local OS-like control-plane prototype after dashboard, identity-contract, storage-contract and package gates pass",
            "full_model_plus_os_requires": "real external data/API evidence, production identity, hosted runtime, immutable audit storage, monitoring, lab approval and safety-supervisor gates",
            "is_production_dashboard_ready": "no",
            "is_production_auth_ready": "no",
            "is_biocompute_runtime_ready": "no",
            "is_bic_os_ready": "no",
            "next_best_build_step": "add production identity-provider contract proof" if proof_ready else "fix v5.36 dashboard route contract blockers first",
        },
        "claim_boundary": "v5.36 proves local dashboard route contracts, DTO/view payloads and role/scope access probes over the v5.35 tenant incident permissions layer. It does not claim a hosted dashboard, browser session security, production identity, full BioCompute Runtime or BiC OS readiness.",
    }


def write_dashboard_route_contract_outputs_v536(audit: dict[str, Any], out_dir: str | Path = DEFAULT_OUT) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary_json": out / "V536_DASHBOARD_ROUTE_CONTRACT_SUMMARY.json",
        "routes_json": out / "V536_DASHBOARD_ROUTES.json",
        "views_json": out / "V536_DASHBOARD_VIEW_PAYLOADS.json",
        "access_json": out / "V536_DASHBOARD_ACCESS_MATRIX.json",
        "routes_csv": out / "V536_DASHBOARD_ROUTES.csv",
        "markdown_report": out / "BIOGPU_V536_DASHBOARD_ROUTE_CONTRACT_REPORT.md",
    }
    summary = {key: value for key, value in audit.items() if key not in {"dashboard_routes", "dashboard_view_payloads", "dashboard_access_matrix"}}
    paths["summary_json"].write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["routes_json"].write_text(json.dumps({"routes": audit["dashboard_routes"]}, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["views_json"].write_text(json.dumps(audit["dashboard_view_payloads"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["access_json"].write_text(json.dumps(audit["dashboard_access_matrix"], indent=2, ensure_ascii=False), encoding="utf-8")
    _write_routes_csv(paths["routes_csv"], audit["dashboard_routes"])
    paths["markdown_report"].write_text(_markdown_report(audit), encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}


def _write_routes_csv(path: Path, routes: list[dict[str, Any]]) -> None:
    fieldnames = ["route_id", "path", "methods", "view_name", "action", "required_scope", "allowed_roles", "mutating", "local_contract_only", "production_dashboard_ready"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for route in routes:
            row = {field: route.get(field) for field in fieldnames}
            row["methods"] = " | ".join(str(item) for item in route.get("methods", []))
            row["allowed_roles"] = " | ".join(str(item) for item in route.get("allowed_roles", []))
            writer.writerow(row)


def _markdown_report(audit: dict[str, Any]) -> str:
    answer = audit["direct_answer"]
    lines = [
        "# BioGPU-Core v5.36 Dashboard Route Contract",
        "",
        "## Direct Answer",
        "",
        f"- Configured to move to model plus OS after real proof: `{answer['are_we_configured_to_move_to_model_plus_os_after_real_proof']}`",
        f"- Timing basis: `{answer['when_estimate']}`",
        f"- Earliest responsible next state: {answer['earliest_responsible_next_state']}",
        f"- Full model plus OS requires: {answer['full_model_plus_os_requires']}",
        f"- Production dashboard ready: `{answer['is_production_dashboard_ready']}`",
        f"- Production auth ready: `{answer['is_production_auth_ready']}`",
        f"- BioCompute Runtime ready: `{answer['is_biocompute_runtime_ready']}`",
        f"- BiC OS ready: `{answer['is_bic_os_ready']}`",
        f"- Next best build step: {answer['next_best_build_step']}",
        "",
        "## Proof Summary",
        "",
        f"- Overall status: `{audit['overall_status']}`",
        f"- Route count: `{audit['route_count']}`",
        f"- Dashboard contract validation ready: `{audit['dashboard_contract_validation_ready']}`",
        f"- Dashboard access matrix ready: `{audit['dashboard_access_matrix_ready']}`",
        f"- Viewer write denial passed: `{audit['viewer_write_denial_passed']}`",
        f"- Tenant isolation passed: `{audit['tenant_isolation_passed']}`",
        f"- Ledger validation scope passed: `{audit['ledger_validation_scope_passed']}`",
        "",
        "## Real Data Or API Requirements",
        "",
    ]
    for requirement in audit["real_data_or_api_requirements"]:
        lines.append(f"- {requirement}")
    lines.extend(["", "## Remaining Runtime Blockers", ""])
    for blocker in audit["remaining_runtime_blockers"]:
        lines.append(f"- {blocker}")
    lines.extend(["", "## Boundary", "", audit["claim_boundary"], ""])
    return "\n".join(lines)