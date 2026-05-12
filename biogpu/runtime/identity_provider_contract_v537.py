"""Production identity-provider contract proof, v5.37."""
from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from biogpu.beta.job_model_v43 import utc_now_iso
from biogpu.evidence.ledger_v53 import stable_hash
from biogpu.runtime.dashboard_routes_v536 import build_dashboard_route_contracts_v536, run_dashboard_route_contract_workflow_v536
from biogpu.runtime.incident_permissions_v535 import authorize_incident_action_v535


DEFAULT_OUT = Path("outputs/v537_identity_provider_contract")
V537_ISSUER = "https://identity.example.invalid/biogpu"
V537_AUDIENCE = "biogpu-control-plane"
V537_CURRENT_KID = "biogpu-local-contract-key-v537-current"
V537_NEXT_KID = "biogpu-local-contract-key-v537-next"
V537_REFERENCE_NOW = 1_800_000_000


@dataclass(frozen=True)
class IdentityProviderContractV537:
    provider_id: str
    issuer: str
    audience: str
    discovery_url: str
    jwks_uri: str
    authorization_endpoint: str
    token_endpoint: str
    supported_algorithms: tuple[str, ...]
    required_claims: tuple[str, ...]
    key_rotation_required: bool = True
    local_contract_only: bool = True
    production_identity_ready: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class IdentityTokenFixtureV537:
    token_id: str
    issuer: str
    audience: str
    subject: str
    tenant_id: str
    roles: tuple[str, ...]
    scopes: tuple[str, ...]
    issued_at: int
    expires_at: int
    key_id: str
    algorithm: str = "RS256"
    local_fixture_only: bool = True
    production_token_ready: bool = False

    def to_claims(self) -> dict[str, Any]:
        return {
            "iss": self.issuer,
            "aud": self.audience,
            "sub": self.subject,
            "tenant_id": self.tenant_id,
            "roles": list(self.roles),
            "scope": " ".join(self.scopes),
            "iat": self.issued_at,
            "exp": self.expires_at,
            "kid": self.key_id,
            "alg": self.algorithm,
            "token_id": self.token_id,
            "local_fixture_only": self.local_fixture_only,
            "production_token_ready": self.production_token_ready,
        }


@dataclass(frozen=True)
class IdentityValidationDecisionV537:
    decision_id: str
    token_id: str | None
    accepted: bool
    status: str
    principal_id: str | None
    tenant_id: str | None
    role: str | None
    scopes: tuple[str, ...]
    errors: tuple[str, ...]
    production_auth_ready: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_identity_provider_contract_v537() -> IdentityProviderContractV537:
    return IdentityProviderContractV537(
        provider_id="biogpu_oidc_contract_v537",
        issuer=V537_ISSUER,
        audience=V537_AUDIENCE,
        discovery_url=f"{V537_ISSUER}/.well-known/openid-configuration",
        jwks_uri=f"{V537_ISSUER}/.well-known/jwks.json",
        authorization_endpoint=f"{V537_ISSUER}/oauth2/v1/authorize",
        token_endpoint=f"{V537_ISSUER}/oauth2/v1/token",
        supported_algorithms=("RS256",),
        required_claims=("iss", "aud", "sub", "tenant_id", "roles", "scope", "iat", "exp", "kid", "alg"),
    )


def build_oidc_discovery_contract_v537(contract: IdentityProviderContractV537 | None = None) -> dict[str, Any]:
    contract = contract or build_identity_provider_contract_v537()
    return {
        "issuer": contract.issuer,
        "authorization_endpoint": contract.authorization_endpoint,
        "token_endpoint": contract.token_endpoint,
        "jwks_uri": contract.jwks_uri,
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code", "refresh_token"],
        "id_token_signing_alg_values_supported": list(contract.supported_algorithms),
        "required_claims": list(contract.required_claims),
        "audience": contract.audience,
        "production_discovery_live": False,
        "local_contract_only": True,
        "bic_os_phase_locked": True,
    }


def build_jwks_contract_v537(contract: IdentityProviderContractV537 | None = None) -> dict[str, Any]:
    contract = contract or build_identity_provider_contract_v537()
    keys = [
        {"kid": V537_CURRENT_KID, "kty": "RSA", "use": "sig", "alg": "RS256", "status": "current", "private_key_material_present": False},
        {"kid": V537_NEXT_KID, "kty": "RSA", "use": "sig", "alg": "RS256", "status": "next", "private_key_material_present": False},
    ]
    for key in keys:
        key["public_key_fingerprint"] = stable_hash({"issuer": contract.issuer, "kid": key["kid"], "alg": key["alg"], "status": key["status"]})
    return {
        "issuer": contract.issuer,
        "jwks_uri": contract.jwks_uri,
        "keys": keys,
        "key_count": len(keys),
        "rotation_pair_present": True,
        "private_key_material_absent": all(key["private_key_material_present"] is False for key in keys),
        "production_jwks_live": False,
        "local_contract_only": True,
        "bic_os_phase_locked": True,
    }


def build_identity_token_fixtures_v537() -> dict[str, IdentityTokenFixtureV537]:
    return {
        "operator_valid": IdentityTokenFixtureV537(
            "operator_valid",
            V537_ISSUER,
            V537_AUDIENCE,
            "user_operator_alpha_v537",
            "tenant_alpha",
            ("operator",),
            ("incidents:read", "incidents:acknowledge", "incidents:resolve", "incident_ledger:read"),
            V537_REFERENCE_NOW - 60,
            V537_REFERENCE_NOW + 3600,
            V537_CURRENT_KID,
        ),
        "viewer_valid": IdentityTokenFixtureV537(
            "viewer_valid",
            V537_ISSUER,
            V537_AUDIENCE,
            "user_viewer_alpha_v537",
            "tenant_alpha",
            ("viewer",),
            ("incidents:read", "incident_ledger:read"),
            V537_REFERENCE_NOW - 60,
            V537_REFERENCE_NOW + 3600,
            V537_CURRENT_KID,
        ),
        "admin_valid": IdentityTokenFixtureV537(
            "admin_valid",
            V537_ISSUER,
            V537_AUDIENCE,
            "user_admin_alpha_v537",
            "tenant_alpha",
            ("incident_admin",),
            ("incidents:read", "incidents:acknowledge", "incidents:resolve", "incidents:archive", "incident_ledger:read", "incident_ledger:validate"),
            V537_REFERENCE_NOW - 60,
            V537_REFERENCE_NOW + 3600,
            V537_CURRENT_KID,
        ),
        "auditor_valid": IdentityTokenFixtureV537(
            "auditor_valid",
            V537_ISSUER,
            V537_AUDIENCE,
            "user_auditor_v537",
            "system",
            ("auditor",),
            ("incident_ledger:read", "incident_ledger:validate"),
            V537_REFERENCE_NOW - 60,
            V537_REFERENCE_NOW + 3600,
            V537_CURRENT_KID,
        ),
        "wrong_audience": IdentityTokenFixtureV537(
            "wrong_audience",
            V537_ISSUER,
            "other-audience",
            "user_wrong_audience_v537",
            "tenant_alpha",
            ("operator",),
            ("incidents:read",),
            V537_REFERENCE_NOW - 60,
            V537_REFERENCE_NOW + 3600,
            V537_CURRENT_KID,
        ),
        "expired": IdentityTokenFixtureV537(
            "expired",
            V537_ISSUER,
            V537_AUDIENCE,
            "user_expired_v537",
            "tenant_alpha",
            ("operator",),
            ("incidents:read",),
            V537_REFERENCE_NOW - 7200,
            V537_REFERENCE_NOW - 3600,
            V537_CURRENT_KID,
        ),
        "unknown_key": IdentityTokenFixtureV537(
            "unknown_key",
            V537_ISSUER,
            V537_AUDIENCE,
            "user_unknown_key_v537",
            "tenant_alpha",
            ("operator",),
            ("incidents:read",),
            V537_REFERENCE_NOW - 60,
            V537_REFERENCE_NOW + 3600,
            "unknown-kid-v537",
        ),
        "unsupported_role": IdentityTokenFixtureV537(
            "unsupported_role",
            V537_ISSUER,
            V537_AUDIENCE,
            "user_unsupported_role_v537",
            "tenant_alpha",
            ("superuser",),
            ("incidents:read", "incident_ledger:validate"),
            V537_REFERENCE_NOW - 60,
            V537_REFERENCE_NOW + 3600,
            V537_CURRENT_KID,
        ),
    }


def _known_key_ids(jwks: dict[str, Any]) -> set[str]:
    return {str(key.get("kid")) for key in jwks.get("keys", [])}


def _normalize_scopes(value: Any) -> tuple[str, ...]:
    if isinstance(value, str):
        return tuple(scope for scope in value.split(" ") if scope)
    if isinstance(value, (list, tuple)):
        return tuple(str(scope) for scope in value)
    return tuple()


def validate_identity_claims_v537(claims: dict[str, Any] | None, contract: IdentityProviderContractV537 | None = None, jwks: dict[str, Any] | None = None, now_epoch: int = V537_REFERENCE_NOW) -> IdentityValidationDecisionV537:
    contract = contract or build_identity_provider_contract_v537()
    jwks = jwks or build_jwks_contract_v537(contract)
    errors: list[str] = []
    if not claims:
        return IdentityValidationDecisionV537(_decision_id(None, "missing_claims"), None, False, "missing_claims", None, None, None, tuple(), ("missing_claims",))
    token_id = str(claims.get("token_id") or "unknown_token")
    for claim_name in contract.required_claims:
        claim_value = claims.get(claim_name)
        if claim_name not in claims or claim_value is None or claim_value == "" or claim_value == []:
            errors.append(f"missing_claim:{claim_name}")
    if claims.get("iss") != contract.issuer:
        errors.append("issuer_mismatch")
    if claims.get("aud") != contract.audience:
        errors.append("audience_mismatch")
    if claims.get("alg") not in contract.supported_algorithms:
        errors.append("unsupported_algorithm")
    if str(claims.get("kid")) not in _known_key_ids(jwks):
        errors.append("unknown_key_id")
    try:
        issued_at = int(claims.get("iat"))
        expires_at = int(claims.get("exp"))
        if issued_at > now_epoch:
            errors.append("issued_in_future")
        if expires_at <= now_epoch:
            errors.append("token_expired")
        if expires_at <= issued_at:
            errors.append("invalid_time_window")
    except (TypeError, ValueError):
        errors.append("invalid_time_claims")
    roles = tuple(str(role) for role in claims.get("roles", [])) if isinstance(claims.get("roles"), (list, tuple)) else tuple()
    role = roles[0] if roles else None
    if role not in {"operator", "viewer", "incident_admin", "auditor"}:
        errors.append("unsupported_role")
    scopes = _normalize_scopes(claims.get("scope"))
    if not scopes:
        errors.append("missing_scope_claim")
    tenant_id = str(claims.get("tenant_id")) if claims.get("tenant_id") else None
    principal_id = f"oidc_{tenant_id}_{role}_{claims.get('sub')}" if tenant_id and role else None
    accepted = not errors
    status = "validated" if accepted else "denied"
    return IdentityValidationDecisionV537(
        decision_id=_decision_id(token_id, status),
        token_id=token_id,
        accepted=accepted,
        status=status,
        principal_id=principal_id,
        tenant_id=tenant_id,
        role=role,
        scopes=scopes,
        errors=tuple(errors),
    )


def _decision_id(token_id: str | None, status: str) -> str:
    return "idp_" + stable_hash({"token_id": token_id, "status": status})[:16]


def map_identity_decision_to_principal_v537(decision: IdentityValidationDecisionV537) -> dict[str, Any] | None:
    if not decision.accepted or not decision.principal_id or not decision.tenant_id or not decision.role:
        return None
    return {
        "principal_id": decision.principal_id,
        "user_id": decision.principal_id.replace("oidc_", "", 1),
        "tenant_id": decision.tenant_id,
        "role": decision.role,
        "scopes": decision.scopes,
        "production_auth_ready": False,
        "bic_os_phase_locked": True,
    }


def run_identity_validation_matrix_v537(contract: IdentityProviderContractV537 | None = None, jwks: dict[str, Any] | None = None) -> dict[str, Any]:
    contract = contract or build_identity_provider_contract_v537()
    jwks = jwks or build_jwks_contract_v537(contract)
    fixtures = build_identity_token_fixtures_v537()
    expected = {
        "operator_valid": True,
        "viewer_valid": True,
        "admin_valid": True,
        "auditor_valid": True,
        "wrong_audience": False,
        "expired": False,
        "unknown_key": False,
        "unsupported_role": False,
    }
    decisions: list[dict[str, Any]] = []
    for name, fixture in fixtures.items():
        decision = validate_identity_claims_v537(fixture.to_claims(), contract, jwks).to_dict()
        decision["fixture_name"] = name
        decision["expected_accepted"] = expected[name]
        decision["passed"] = decision["accepted"] is expected[name]
        decisions.append(decision)
    passed_count = sum(1 for decision in decisions if decision["passed"])
    denied_count = sum(1 for decision in decisions if decision["accepted"] is False)
    accepted_count = sum(1 for decision in decisions if decision["accepted"] is True)
    return {
        "version": "v5.37",
        "identity_validation_matrix_ready": passed_count == len(decisions) and accepted_count >= 4 and denied_count >= 4,
        "decision_count": len(decisions),
        "passed_count": passed_count,
        "accepted_count": accepted_count,
        "denied_count": denied_count,
        "decisions": decisions,
        "production_auth_ready": False,
        "production_identity_ready": False,
        "bic_os_phase_locked": True,
    }


def run_identity_dashboard_access_probe_v537(v536_audit: dict[str, Any], validation_matrix: dict[str, Any]) -> dict[str, Any]:
    routes = {route.route_id: route for route in build_dashboard_route_contracts_v536()}
    incident = dict(v536_audit.get("dashboard_view_payloads", {}).get("incident_detail", {}).get("incident") or {})
    checks = [
        ("operator_acknowledge_allowed", "operator_valid", "incident_acknowledge", True),
        ("viewer_acknowledge_denied", "viewer_valid", "incident_acknowledge", False),
        ("admin_archive_allowed", "admin_valid", "incident_archive", True),
        ("auditor_validate_ledger_allowed", "auditor_valid", "incident_ledger_validate", True),
        ("expired_overview_denied", "expired", "dashboard_overview", False),
    ]
    decisions_by_fixture = {decision["fixture_name"]: decision for decision in validation_matrix.get("decisions", [])}
    probes: list[dict[str, Any]] = []
    for check_name, fixture_name, route_id, expected in checks:
        route = routes[route_id]
        identity_decision = decisions_by_fixture[fixture_name]
        principal = map_identity_decision_to_principal_v537(IdentityValidationDecisionV537(
            identity_decision["decision_id"],
            identity_decision.get("token_id"),
            identity_decision["accepted"],
            identity_decision["status"],
            identity_decision.get("principal_id"),
            identity_decision.get("tenant_id"),
            identity_decision.get("role"),
            tuple(identity_decision.get("scopes") or []),
            tuple(identity_decision.get("errors") or []),
        ))
        permission_decision = authorize_incident_action_v535(principal, incident, route.action)
        probe = {
            "probe_id": "idp_dash_" + stable_hash({"check_name": check_name, "fixture_name": fixture_name, "route_id": route_id})[:16],
            "check_name": check_name,
            "fixture_name": fixture_name,
            "route_id": route_id,
            "action": route.action,
            "identity_accepted": identity_decision["accepted"],
            "permission_accepted": permission_decision.accepted,
            "expected_accepted": expected,
            "passed": permission_decision.accepted is expected,
            "status": permission_decision.status,
            "errors": permission_decision.errors,
            "production_auth_ready": False,
            "production_dashboard_ready": False,
            "bic_os_phase_locked": True,
        }
        probes.append(probe)
    passed_count = sum(1 for probe in probes if probe["passed"])
    return {
        "version": "v5.37",
        "identity_dashboard_access_ready": passed_count == len(probes),
        "probe_count": len(probes),
        "passed_count": passed_count,
        "probes": probes,
        "production_auth_ready": False,
        "production_dashboard_ready": False,
        "bic_os_phase_locked": True,
    }


def validate_identity_provider_contract_v537(contract: IdentityProviderContractV537, discovery: dict[str, Any], jwks: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if not contract.issuer.startswith("https://"):
        errors.append("issuer_not_https")
    if discovery.get("issuer") != contract.issuer:
        errors.append("discovery_issuer_mismatch")
    if discovery.get("jwks_uri") != contract.jwks_uri:
        errors.append("jwks_uri_mismatch")
    if not set(contract.required_claims).issubset(set(discovery.get("required_claims", []))):
        errors.append("required_claims_missing_from_discovery")
    if jwks.get("key_count", 0) < 2:
        errors.append("rotation_key_missing")
    if not jwks.get("private_key_material_absent"):
        errors.append("private_key_material_present")
    if discovery.get("production_discovery_live") is True or jwks.get("production_jwks_live") is True or contract.production_identity_ready:
        errors.append("production_identity_claim_present")
    ready = not errors
    return {
        "version": "v5.37",
        "identity_provider_contract_ready": ready,
        "issuer_https": contract.issuer.startswith("https://"),
        "required_claims_present": "required_claims_missing_from_discovery" not in errors,
        "jwks_rotation_contract_ready": jwks.get("key_count", 0) >= 2 and jwks.get("rotation_pair_present") is True,
        "private_key_material_absent": jwks.get("private_key_material_absent") is True,
        "production_identity_claims_absent": "production_identity_claim_present" not in errors,
        "errors": errors,
        "production_auth_ready": False,
        "production_identity_ready": False,
        "bic_os_phase_locked": True,
    }


def build_identity_audit_bundle_v537(contract_validation: dict[str, Any], validation_matrix: dict[str, Any], dashboard_probe: dict[str, Any], v536_summary: dict[str, Any], out_dir: str | Path) -> dict[str, Any]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    bundle = {
        "version": "v5.37",
        "created_at": utc_now_iso(),
        "identity_provider_contract_ready": contract_validation.get("identity_provider_contract_ready"),
        "identity_validation_matrix_ready": validation_matrix.get("identity_validation_matrix_ready"),
        "identity_dashboard_access_ready": dashboard_probe.get("identity_dashboard_access_ready"),
        "accepted_identity_fixture_count": validation_matrix.get("accepted_count"),
        "denied_identity_fixture_count": validation_matrix.get("denied_count"),
        "v536_dependency_status": v536_summary.get("overall_status"),
        "v536_dashboard_contract_ready": v536_summary.get("dashboard_route_contract_ready"),
        "production_auth_ready": False,
        "production_identity_ready": False,
        "bic_os_phase_locked": True,
    }
    bundle_hash = stable_hash(bundle)
    bundle["bundle_sha256"] = bundle_hash
    path = out / "V537_IDENTITY_PROVIDER_CONTRACT_AUDIT_BUNDLE.json"
    path.write_text(json.dumps(bundle, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"bundle_path": str(path).replace("\\", "/"), "bundle_sha256": bundle_hash, "bundle_ready": path.exists() and len(bundle_hash) == 64, "bundle": bundle}


def run_identity_provider_contract_workflow_v537(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    project_root = Path(root).resolve()
    out = project_root / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    v536_dependency = run_dashboard_route_contract_workflow_v536(project_root, out / "d536")
    contract = build_identity_provider_contract_v537()
    discovery = build_oidc_discovery_contract_v537(contract)
    jwks = build_jwks_contract_v537(contract)
    contract_validation = validate_identity_provider_contract_v537(contract, discovery, jwks)
    validation_matrix = run_identity_validation_matrix_v537(contract, jwks)
    dashboard_probe = run_identity_dashboard_access_probe_v537(v536_dependency, validation_matrix)
    bundle = build_identity_audit_bundle_v537(contract_validation, validation_matrix, dashboard_probe, v536_dependency, out)
    proof_ready = (
        v536_dependency.get("dashboard_route_contract_ready") is True
        and contract_validation.get("identity_provider_contract_ready") is True
        and validation_matrix.get("identity_validation_matrix_ready") is True
        and dashboard_probe.get("identity_dashboard_access_ready") is True
        and bundle.get("bundle_ready") is True
        and validation_matrix.get("production_auth_ready") is False
    )
    return {
        "version": "v5.37",
        "phase": "identity_provider_contract",
        "overall_status": "identity_provider_contract_proof_ready_runtime_not_claimed" if proof_ready else "identity_provider_contract_proof_incomplete",
        "active_phase": "biocompute_control_plane_identity_contract_proof",
        "bic_os_phase_locked": True,
        "identity_provider_contract_ready": proof_ready,
        "oidc_discovery_contract_ready": contract_validation.get("identity_provider_contract_ready") is True,
        "jwks_rotation_contract_ready": contract_validation.get("jwks_rotation_contract_ready") is True,
        "identity_validation_matrix_ready": validation_matrix.get("identity_validation_matrix_ready") is True,
        "identity_dashboard_access_ready": dashboard_probe.get("identity_dashboard_access_ready") is True,
        "identity_audit_bundle_ready": bundle.get("bundle_ready") is True,
        "accepted_identity_fixture_count": validation_matrix.get("accepted_count"),
        "denied_identity_fixture_count": validation_matrix.get("denied_count"),
        "v536_dependency_ready": v536_dependency.get("dashboard_route_contract_ready") is True,
        "production_identity_ready": False,
        "production_auth_ready": False,
        "production_dashboard_ready": False,
        "production_api_ready": False,
        "production_biocompute_runtime_ready": False,
        "full_biosdk_ready": False,
        "live_actuation_enabled": False,
        "identity_provider_contract": contract.to_dict(),
        "oidc_discovery_contract": discovery,
        "jwks_contract": jwks,
        "identity_validation_matrix": validation_matrix,
        "identity_dashboard_access_probe": dashboard_probe,
        "identity_audit_bundle": {key: value for key, value in bundle.items() if key != "bundle"},
        "v536_dependency_summary": {key: value for key, value in v536_dependency.items() if key not in {"dashboard_routes", "dashboard_view_payloads", "dashboard_access_matrix"}},
        "missing_real_inputs": [
            "real OIDC/OAuth discovery URL from chosen provider",
            "real JWKS endpoint with provider-owned public signing keys",
            "real token issuer and audience values for hosted deployment",
            "persistent tenant/workspace membership store",
            "enterprise SSO or IdP app registration",
            "production session/cookie policy for dashboard browser clients",
        ],
        "remaining_runtime_blockers": [
            "production identity provider integration and key rotation",
            "persistent tenant/workspace membership store",
            "hosted dashboard server and browser session enforcement",
            "production object storage and audit retention backend",
            "external notarization or remote append-only storage for incident ledger roots",
            "real external read-only API credentials or partner exports",
            "lab-approved live telemetry and closed-loop approval workflow",
        ],
        "direct_answer": {
            "did_we_find_real_identity_provider_config": "no",
            "what_we_added_instead": "local OIDC/JWKS/claims/role-mapping contract proof",
            "is_production_auth_ready": "no",
            "is_biocompute_runtime_ready": "no",
            "is_bic_os_ready": "no",
            "next_best_build_step": "add storage and retention backend contract proof" if proof_ready else "fix v5.37 identity contract blockers first",
        },
        "claim_boundary": "v5.37 proves a local identity-provider contract: OIDC discovery shape, JWKS rotation requirements, token claim validation, role/scope mapping and dashboard access probes over v5.36. It does not claim real SSO, live token verification, production auth, full BioCompute Runtime or BiC OS readiness.",
    }


def write_identity_provider_contract_outputs_v537(audit: dict[str, Any], out_dir: str | Path = DEFAULT_OUT) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary_json": out / "V537_IDENTITY_PROVIDER_CONTRACT_SUMMARY.json",
        "discovery_json": out / "V537_OIDC_DISCOVERY_CONTRACT.json",
        "jwks_json": out / "V537_JWKS_CONTRACT.json",
        "identity_decisions_json": out / "V537_IDENTITY_VALIDATION_DECISIONS.json",
        "dashboard_probe_json": out / "V537_IDENTITY_DASHBOARD_ACCESS_PROBE.json",
        "identity_decisions_csv": out / "V537_IDENTITY_VALIDATION_DECISIONS.csv",
        "markdown_report": out / "BIOGPU_V537_IDENTITY_PROVIDER_CONTRACT_REPORT.md",
    }
    summary = {key: value for key, value in audit.items() if key not in {"oidc_discovery_contract", "jwks_contract", "identity_validation_matrix", "identity_dashboard_access_probe"}}
    paths["summary_json"].write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["discovery_json"].write_text(json.dumps(audit["oidc_discovery_contract"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["jwks_json"].write_text(json.dumps(audit["jwks_contract"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["identity_decisions_json"].write_text(json.dumps(audit["identity_validation_matrix"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["dashboard_probe_json"].write_text(json.dumps(audit["identity_dashboard_access_probe"], indent=2, ensure_ascii=False), encoding="utf-8")
    _write_identity_decisions_csv(paths["identity_decisions_csv"], audit["identity_validation_matrix"].get("decisions", []))
    paths["markdown_report"].write_text(_markdown_report(audit), encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}


def _write_identity_decisions_csv(path: Path, decisions: list[dict[str, Any]]) -> None:
    fieldnames = ["fixture_name", "token_id", "accepted", "expected_accepted", "passed", "status", "principal_id", "tenant_id", "role", "scopes", "errors"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for decision in decisions:
            row = {field: decision.get(field) for field in fieldnames}
            row["scopes"] = " | ".join(str(scope) for scope in decision.get("scopes", []))
            row["errors"] = " | ".join(str(error) for error in decision.get("errors", []))
            writer.writerow(row)


def _markdown_report(audit: dict[str, Any]) -> str:
    answer = audit["direct_answer"]
    lines = [
        "# BioGPU-Core v5.37 Identity Provider Contract",
        "",
        "## Direct Answer",
        "",
        f"- Real IdP config found: `{answer['did_we_find_real_identity_provider_config']}`",
        f"- Added instead: {answer['what_we_added_instead']}",
        f"- Production auth ready: `{answer['is_production_auth_ready']}`",
        f"- BioCompute Runtime ready: `{answer['is_biocompute_runtime_ready']}`",
        f"- BiC OS ready: `{answer['is_bic_os_ready']}`",
        f"- Next best build step: {answer['next_best_build_step']}",
        "",
        "## Proof Summary",
        "",
        f"- Overall status: `{audit['overall_status']}`",
        f"- OIDC discovery contract ready: `{audit['oidc_discovery_contract_ready']}`",
        f"- JWKS rotation contract ready: `{audit['jwks_rotation_contract_ready']}`",
        f"- Identity validation matrix ready: `{audit['identity_validation_matrix_ready']}`",
        f"- Identity dashboard access ready: `{audit['identity_dashboard_access_ready']}`",
        f"- Accepted fixtures: `{audit['accepted_identity_fixture_count']}`",
        f"- Denied fixtures: `{audit['denied_identity_fixture_count']}`",
        "",
        "## Missing Real Inputs",
        "",
    ]
    for missing in audit["missing_real_inputs"]:
        lines.append(f"- {missing}")
    lines.extend(["", "## Remaining Runtime Blockers", ""])
    for blocker in audit["remaining_runtime_blockers"]:
        lines.append(f"- {blocker}")
    lines.extend(["", "## Boundary", "", audit["claim_boundary"], ""])
    return "\n".join(lines)