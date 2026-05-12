"""Private registry authentication and expiring-feed contract proof, v5.46."""
from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from biogpu.beta.job_model_v43 import utc_now_iso
from biogpu.evidence.ledger_v53 import stable_hash
from biogpu.sdk.recipient_onboarding_audit_v545 import run_recipient_onboarding_audit_workflow_v545


DEFAULT_OUT = Path("outputs/v546_private_registry_auth_feed")
AUTHORIZED_FEED_SCOPES_V546 = {"artifact_read", "provenance_read", "audit_read"}
MAX_LOCAL_FEED_TTL_MINUTES_V546 = 1440


@dataclass(frozen=True)
class PrivateRegistryAuthFeedPolicyV546:
    policy_id: str
    authorized_feed_scopes: tuple[str, ...]
    max_local_feed_ttl_minutes: int
    requires_v545_recipient_audit: bool
    requires_local_access_grant: bool
    requires_local_token_signature: bool
    requires_feed_expiry_timestamp: bool
    requires_registry_log_export_shape: bool
    live_registry_endpoint_configured: bool
    local_contract_only: bool = True
    live_private_registry_ready: bool = False
    production_distribution_ready: bool = False
    full_biosdk_ready: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AuthFeedRequestFixtureV546:
    request_id: str
    recipient_id: str
    organization_id: str
    token_scope: str
    has_v545_local_grant: bool
    local_token_signature_valid: bool
    requested_artifact_sha256: str
    feed_ttl_minutes: int
    uses_expired_feed: bool
    revoked_token: bool
    requests_live_private_registry: bool
    requests_public_registry: bool
    requests_production_distribution: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AuthFeedDecisionV546:
    request_id: str
    recipient_id: str
    token_scope: str
    authenticated_for_local_feed: bool
    reason_codes: tuple[str, ...]
    local_feed_token_id: str | None
    local_feed_url: str | None
    feed_expires_at: str | None
    registry_log_event_id: str | None
    live_private_registry_ready: bool = False
    production_distribution_ready: bool = False
    full_biosdk_ready: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def expires_at_for_minutes_v546(minutes: int) -> str | None:
    if minutes <= 0:
        return None
    expires_at = datetime.now(timezone.utc).replace(microsecond=0) + timedelta(minutes=minutes)
    return expires_at.isoformat().replace("+00:00", "Z")


def local_feed_signature_v546(payload: dict[str, Any]) -> str:
    return stable_hash({"local_signature_scope": "BIOGPU_CORE_V546_LOCAL_FEED_CONTRACT", "payload": payload})


def build_private_registry_auth_feed_policy_v546() -> dict[str, Any]:
    policy = PrivateRegistryAuthFeedPolicyV546(
        policy_id="BIOGPU_CORE_V546_PRIVATE_REGISTRY_AUTH_FEED_POLICY",
        authorized_feed_scopes=tuple(sorted(AUTHORIZED_FEED_SCOPES_V546)),
        max_local_feed_ttl_minutes=MAX_LOCAL_FEED_TTL_MINUTES_V546,
        requires_v545_recipient_audit=True,
        requires_local_access_grant=True,
        requires_local_token_signature=True,
        requires_feed_expiry_timestamp=True,
        requires_registry_log_export_shape=True,
        live_registry_endpoint_configured=False,
    )
    result = {
        "version": "v5.46",
        "private_registry_auth_feed_policy_ready": True,
        "policy": policy.to_dict(),
        "blocked_modes": ["anonymous_feed", "unbounded_feed", "public_registry_feed", "live_registry_endpoint", "production_distribution"],
        "required_local_records": ["v545_local_access_grant", "local_feed_token_signature", "artifact_digest", "feed_expires_at", "registry_log_event"],
        "live_private_registry_ready": False,
        "private_registry_ready": False,
        "production_distribution_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    result["private_registry_auth_feed_policy_sha256"] = stable_hash(result)
    return result


def allowed_recipient_ids_v546(v545_dependency: dict[str, Any]) -> set[str]:
    events = v545_dependency.get("recipient_access_log", {}).get("access_events", [])
    if events:
        return {str(event.get("recipient_id")) for event in events if event.get("recipient_id")}
    decisions = v545_dependency.get("recipient_onboarding_matrix", {}).get("decisions", [])
    return {str(decision.get("recipient_id")) for decision in decisions if decision.get("onboarded_for_local_handoff") is True}


def default_auth_feed_fixtures_v546(v545_dependency: dict[str, Any]) -> list[AuthFeedRequestFixtureV546]:
    artifact_sha256 = str(v545_dependency.get("artifact_sha256") or "")
    wrong_sha = "0" * 64 if artifact_sha256 != "0" * 64 else "1" * 64
    return [
        AuthFeedRequestFixtureV546("allow-alpha-artifact", "recipient-alpha", "org-alpha", "artifact_read", True, True, artifact_sha256, 60, False, False, False, False, False),
        AuthFeedRequestFixtureV546("allow-beta-artifact", "recipient-beta", "org-beta", "artifact_read", True, True, artifact_sha256, 120, False, False, False, False, False),
        AuthFeedRequestFixtureV546("allow-provenance-audit", "recipient-provenance", "org-audit", "provenance_read", True, True, artifact_sha256, 30, False, False, False, False, False),
        AuthFeedRequestFixtureV546("missing-grant", "recipient-missing", "org-alpha", "artifact_read", False, True, artifact_sha256, 60, False, False, False, False, False),
        AuthFeedRequestFixtureV546("invalid-signature", "recipient-alpha", "org-alpha", "artifact_read", True, False, artifact_sha256, 60, False, False, False, False, False),
        AuthFeedRequestFixtureV546("wrong-artifact", "recipient-alpha", "org-alpha", "artifact_read", True, True, wrong_sha, 60, False, False, False, False, False),
        AuthFeedRequestFixtureV546("expired-feed", "recipient-alpha", "org-alpha", "artifact_read", True, True, artifact_sha256, 60, True, False, False, False, False),
        AuthFeedRequestFixtureV546("ttl-too-long", "recipient-alpha", "org-alpha", "artifact_read", True, True, artifact_sha256, 10080, False, False, False, False, False),
        AuthFeedRequestFixtureV546("revoked-token", "recipient-beta", "org-beta", "artifact_read", True, True, artifact_sha256, 60, False, True, False, False, False),
        AuthFeedRequestFixtureV546("live-registry-request", "recipient-alpha", "org-alpha", "artifact_read", True, True, artifact_sha256, 60, False, False, True, False, False),
        AuthFeedRequestFixtureV546("public-registry-request", "recipient-alpha", "org-alpha", "artifact_read", True, True, artifact_sha256, 60, False, False, False, True, False),
        AuthFeedRequestFixtureV546("production-request", "recipient-alpha", "org-alpha", "artifact_read", True, True, artifact_sha256, 60, False, False, False, False, True),
        AuthFeedRequestFixtureV546("unknown-scope", "recipient-alpha", "org-alpha", "admin_write", True, True, artifact_sha256, 60, False, False, False, False, False),
    ]


def evaluate_auth_feed_request_v546(fixture: AuthFeedRequestFixtureV546, v545_dependency: dict[str, Any]) -> AuthFeedDecisionV546:
    reasons: list[str] = []
    artifact_sha256 = str(v545_dependency.get("artifact_sha256") or "")
    allowed_recipients = allowed_recipient_ids_v546(v545_dependency)
    if v545_dependency.get("recipient_onboarding_audit_contract_ready") is not True:
        reasons.append("v545_recipient_onboarding_not_ready")
    if fixture.recipient_id not in allowed_recipients or not fixture.has_v545_local_grant:
        reasons.append("recipient_local_grant_missing")
    if fixture.token_scope not in AUTHORIZED_FEED_SCOPES_V546:
        reasons.append("token_scope_not_authorized")
    if not fixture.local_token_signature_valid:
        reasons.append("local_token_signature_invalid")
    if fixture.requested_artifact_sha256 != artifact_sha256:
        reasons.append("artifact_digest_mismatch")
    if fixture.feed_ttl_minutes <= 0 or fixture.uses_expired_feed:
        reasons.append("feed_expired")
    if fixture.feed_ttl_minutes > MAX_LOCAL_FEED_TTL_MINUTES_V546:
        reasons.append("feed_ttl_exceeds_local_limit")
    if fixture.revoked_token:
        reasons.append("token_revoked")
    if fixture.requests_live_private_registry:
        reasons.append("live_private_registry_not_ready")
    if fixture.requests_public_registry:
        reasons.append("public_registry_not_allowed")
    if fixture.requests_production_distribution:
        reasons.append("production_distribution_not_allowed")
    allowed = not reasons
    token_id = f"local-feed-token-{fixture.request_id}" if allowed else None
    feed_url = f"local://biogpu/v546/private-feed/{artifact_sha256}?recipient={fixture.recipient_id}&scope={fixture.token_scope}" if allowed else None
    expires_at = expires_at_for_minutes_v546(fixture.feed_ttl_minutes) if allowed else None
    event_id = f"registry-log-{fixture.request_id}" if allowed else None
    return AuthFeedDecisionV546(
        request_id=fixture.request_id,
        recipient_id=fixture.recipient_id,
        token_scope=fixture.token_scope,
        authenticated_for_local_feed=allowed,
        reason_codes=tuple(reasons or ["local_private_feed_authenticated"]),
        local_feed_token_id=token_id,
        local_feed_url=feed_url,
        feed_expires_at=expires_at,
        registry_log_event_id=event_id,
    )


def run_auth_feed_matrix_v546(v545_dependency: dict[str, Any], fixtures: list[AuthFeedRequestFixtureV546] | None = None) -> dict[str, Any]:
    requests = fixtures or default_auth_feed_fixtures_v546(v545_dependency)
    decisions = [evaluate_auth_feed_request_v546(request, v545_dependency).to_dict() for request in requests]
    allowed_count = sum(1 for decision in decisions if decision["authenticated_for_local_feed"])
    denied_count = len(decisions) - allowed_count
    reason_codes = sorted({reason for decision in decisions for reason in decision["reason_codes"]})
    required_denials = {
        "recipient_local_grant_missing",
        "local_token_signature_invalid",
        "artifact_digest_mismatch",
        "feed_expired",
        "feed_ttl_exceeds_local_limit",
        "token_revoked",
        "live_private_registry_not_ready",
        "public_registry_not_allowed",
        "production_distribution_not_allowed",
        "token_scope_not_authorized",
    }
    matrix = {
        "version": "v5.46",
        "auth_feed_matrix_ready": allowed_count >= 3 and denied_count >= 10 and required_denials.issubset(set(reason_codes)),
        "request_count": len(requests),
        "allowed_feed_count": allowed_count,
        "denied_feed_count": denied_count,
        "reason_codes": reason_codes,
        "requests": [request.to_dict() for request in requests],
        "decisions": decisions,
        "live_private_registry_ready": False,
        "private_registry_ready": False,
        "production_distribution_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    matrix["auth_feed_matrix_sha256"] = stable_hash(matrix)
    return matrix


def build_expiring_feed_manifest_v546(v545_dependency: dict[str, Any], auth_feed_matrix: dict[str, Any]) -> dict[str, Any]:
    artifact_sha256 = str(v545_dependency.get("artifact_sha256") or "")
    feeds: list[dict[str, Any]] = []
    for decision in auth_feed_matrix.get("decisions", []):
        if decision.get("authenticated_for_local_feed") is not True:
            continue
        token_payload = {
            "token_id": decision.get("local_feed_token_id"),
            "recipient_id": decision.get("recipient_id"),
            "token_scope": decision.get("token_scope"),
            "artifact_sha256": artifact_sha256,
            "feed_expires_at": decision.get("feed_expires_at"),
        }
        feed = {
            "version": "v5.46",
            "feed_id": f"feed-{decision['request_id']}",
            "recipient_id": decision.get("recipient_id"),
            "token_scope": decision.get("token_scope"),
            "artifact_sha256": artifact_sha256,
            "local_feed_token_id": decision.get("local_feed_token_id"),
            "local_feed_url": decision.get("local_feed_url"),
            "feed_expires_at": decision.get("feed_expires_at"),
            "local_token_signature": local_feed_signature_v546(token_payload),
            "live_registry_endpoint": None,
            "production_distribution_ready": False,
            "bic_os_phase_locked": True,
        }
        feed["feed_record_sha256"] = stable_hash(feed)
        feeds.append(feed)
    manifest = {
        "version": "v5.46",
        "expiring_feed_manifest_ready": len(feeds) == auth_feed_matrix.get("allowed_feed_count") and len(feeds) >= 3,
        "artifact_sha256": artifact_sha256,
        "feed_count": len(feeds),
        "feeds": feeds,
        "live_private_registry_ready": False,
        "private_registry_ready": False,
        "production_distribution_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    manifest["expiring_feed_manifest_sha256"] = stable_hash(manifest)
    return manifest


def run_expiring_feed_probe_v546(v545_dependency: dict[str, Any], auth_feed_matrix: dict[str, Any]) -> dict[str, Any]:
    allowed = [decision for decision in auth_feed_matrix.get("decisions", []) if decision.get("authenticated_for_local_feed") is True]
    first_allowed = allowed[0] if allowed else {}
    expired_fixture = AuthFeedRequestFixtureV546(
        "expiry-probe-feed",
        str(first_allowed.get("recipient_id") or "recipient-alpha"),
        "org-expiry",
        "artifact_read",
        True,
        True,
        str(v545_dependency.get("artifact_sha256") or ""),
        0,
        True,
        False,
        False,
        False,
        False,
    )
    expired_decision = evaluate_auth_feed_request_v546(expired_fixture, v545_dependency).to_dict()
    probe = {
        "version": "v5.46",
        "expiring_feed_probe_ready": expired_decision.get("authenticated_for_local_feed") is False and "feed_expired" in expired_decision.get("reason_codes", []),
        "expired_feed_decision": expired_decision,
        "simulated_after_expiry": {
            "recipient_id": first_allowed.get("recipient_id"),
            "initial_token_id": first_allowed.get("local_feed_token_id"),
            "initial_feed_expires_at": first_allowed.get("feed_expires_at"),
            "simulated_feed_access_after_expiry_allowed": False,
            "reason_codes": ["feed_expired", "local_private_feed_blocked_after_expiry"],
        },
        "live_private_registry_ready": False,
        "production_distribution_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    probe["expiring_feed_probe_sha256"] = stable_hash(probe)
    return probe


def build_registry_log_export_contract_v546(v545_dependency: dict[str, Any], auth_feed_matrix: dict[str, Any]) -> dict[str, Any]:
    artifact_sha256 = str(v545_dependency.get("artifact_sha256") or "")
    previous_hash = "GENESIS"
    events: list[dict[str, Any]] = []
    for decision in auth_feed_matrix.get("decisions", []):
        allowed = decision.get("authenticated_for_local_feed") is True
        event = {
            "version": "v5.46",
            "event_id": f"registry-auth-{decision['request_id']}",
            "event_type": "local_private_feed_auth_allowed" if allowed else "local_private_feed_auth_denied",
            "recipient_id": decision.get("recipient_id"),
            "token_scope": decision.get("token_scope"),
            "artifact_sha256": artifact_sha256,
            "decision_allowed": allowed,
            "reason_codes": decision.get("reason_codes", []),
            "created_at": utc_now_iso(),
            "previous_event_sha256": previous_hash,
            "real_registry_log_export_ready": False,
            "production_distribution_ready": False,
            "bic_os_phase_locked": True,
        }
        event["event_sha256"] = stable_hash(event)
        previous_hash = event["event_sha256"]
        events.append(event)
    export = {
        "version": "v5.46",
        "registry_log_export_contract_ready": len(events) == auth_feed_matrix.get("request_count") and len(events) >= 13,
        "event_count": len(events),
        "allowed_event_count": sum(1 for event in events if event["decision_allowed"]),
        "denied_event_count": sum(1 for event in events if not event["decision_allowed"]),
        "registry_log_events": events,
        "registry_log_head_sha256": previous_hash if events else None,
        "real_registry_log_export_ready": False,
        "live_private_registry_ready": False,
        "production_distribution_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    export["registry_log_export_contract_sha256"] = stable_hash(export)
    return export


def build_auth_feed_audit_bundle_v546(policy: dict[str, Any], auth_feed_matrix: dict[str, Any], feed_manifest: dict[str, Any], expiry_probe: dict[str, Any], registry_log_export: dict[str, Any]) -> dict[str, Any]:
    bundle_ready = (
        policy.get("private_registry_auth_feed_policy_ready") is True
        and auth_feed_matrix.get("auth_feed_matrix_ready") is True
        and feed_manifest.get("expiring_feed_manifest_ready") is True
        and expiry_probe.get("expiring_feed_probe_ready") is True
        and registry_log_export.get("registry_log_export_contract_ready") is True
    )
    bundle = {
        "version": "v5.46",
        "auth_feed_audit_bundle_ready": bundle_ready,
        "policy_sha256": policy.get("private_registry_auth_feed_policy_sha256"),
        "auth_feed_matrix_sha256": auth_feed_matrix.get("auth_feed_matrix_sha256"),
        "expiring_feed_manifest_sha256": feed_manifest.get("expiring_feed_manifest_sha256"),
        "expiring_feed_probe_sha256": expiry_probe.get("expiring_feed_probe_sha256"),
        "registry_log_export_contract_sha256": registry_log_export.get("registry_log_export_contract_sha256"),
        "live_private_registry_ready": False,
        "private_registry_ready": False,
        "production_distribution_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    bundle["auth_feed_audit_bundle_sha256"] = stable_hash(bundle)
    return bundle


def run_private_registry_auth_feed_workflow_v546(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    project_root = Path(root).resolve()
    out = project_root / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    v545_dependency = run_recipient_onboarding_audit_workflow_v545(project_root, out / "d545")
    policy = build_private_registry_auth_feed_policy_v546()
    auth_feed_matrix = run_auth_feed_matrix_v546(v545_dependency)
    feed_manifest = build_expiring_feed_manifest_v546(v545_dependency, auth_feed_matrix)
    expiry_probe = run_expiring_feed_probe_v546(v545_dependency, auth_feed_matrix)
    registry_log_export = build_registry_log_export_contract_v546(v545_dependency, auth_feed_matrix)
    audit_bundle = build_auth_feed_audit_bundle_v546(policy, auth_feed_matrix, feed_manifest, expiry_probe, registry_log_export)
    proof_ready = (
        v545_dependency.get("recipient_onboarding_audit_contract_ready") is True
        and policy.get("private_registry_auth_feed_policy_ready") is True
        and auth_feed_matrix.get("auth_feed_matrix_ready") is True
        and feed_manifest.get("expiring_feed_manifest_ready") is True
        and expiry_probe.get("expiring_feed_probe_ready") is True
        and registry_log_export.get("registry_log_export_contract_ready") is True
        and audit_bundle.get("auth_feed_audit_bundle_ready") is True
    )
    audit = {
        "version": "v5.46",
        "phase": "private_registry_auth_expiring_feed_contract",
        "overall_status": "private_registry_auth_feed_contract_ready_production_not_claimed" if proof_ready else "private_registry_auth_feed_contract_incomplete",
        "active_phase": "biosdk_private_registry_auth_feed_proof",
        "bic_os_phase_locked": True,
        "private_registry_auth_feed_contract_ready": proof_ready,
        "v545_dependency_ready": v545_dependency.get("recipient_onboarding_audit_contract_ready") is True,
        "auth_feed_policy_ready": policy.get("private_registry_auth_feed_policy_ready") is True,
        "auth_feed_matrix_ready": auth_feed_matrix.get("auth_feed_matrix_ready") is True,
        "expiring_feed_manifest_ready": feed_manifest.get("expiring_feed_manifest_ready") is True,
        "expiring_feed_probe_ready": expiry_probe.get("expiring_feed_probe_ready") is True,
        "registry_log_export_contract_ready": registry_log_export.get("registry_log_export_contract_ready") is True,
        "auth_feed_audit_bundle_ready": audit_bundle.get("auth_feed_audit_bundle_ready") is True,
        "artifact_name": v545_dependency.get("artifact_name"),
        "artifact_sha256": v545_dependency.get("artifact_sha256"),
        "allowed_feed_count": auth_feed_matrix.get("allowed_feed_count"),
        "denied_feed_count": auth_feed_matrix.get("denied_feed_count"),
        "feed_manifest_count": feed_manifest.get("feed_count"),
        "registry_log_event_count": registry_log_export.get("event_count"),
        "real_private_registry_auth_ready": False,
        "live_private_registry_ready": False,
        "private_registry_ready": False,
        "public_registry_ready": False,
        "production_distribution_ready": False,
        "production_runtime_ready": False,
        "production_api_ready": False,
        "production_biocompute_runtime_ready": False,
        "full_biosdk_ready": False,
        "live_actuation_enabled": False,
        "auth_feed_policy": policy,
        "auth_feed_matrix": auth_feed_matrix,
        "expiring_feed_manifest": feed_manifest,
        "expiring_feed_probe": expiry_probe,
        "registry_log_export_contract": registry_log_export,
        "auth_feed_audit_bundle": audit_bundle,
        "v545_dependency_summary": {key: value for key, value in v545_dependency.items() if key not in {"recipient_onboarding_policy", "recipient_onboarding_matrix", "recipient_access_log", "access_expiry_probe", "recipient_audit_bundle", "v544_dependency_summary"}},
        "missing_real_inputs": [
            "live private registry endpoint and package feed",
            "registry authentication provider integration",
            "real account provisioning and token issuance",
            "signed URL or private feed expiry enforcement by registry",
            "registry access-log export and retention backend",
            "recipient notification and acknowledgement trail",
            "production revoke/yank authority and incident process",
        ],
        "remaining_runtime_blockers": [
            "production identity provider integration and persistent tenant membership",
            "production object storage and audit retention backend",
            "hosted dashboard server and browser session enforcement",
            "real external read-only API credentials or partner exports",
            "lab-approved live telemetry and closed-loop approval workflow",
        ],
        "direct_answer": {
            "did_we_add_private_registry_auth_feed_contract": "yes" if proof_ready else "not_yet",
            "did_we_validate_local_auth_tokens": "yes" if auth_feed_matrix.get("auth_feed_matrix_ready") else "no",
            "did_we_validate_expiring_feed_denial": "yes" if expiry_probe.get("expiring_feed_probe_ready") else "no",
            "did_we_define_registry_log_export_shape": "yes" if registry_log_export.get("registry_log_export_contract_ready") else "no",
            "is_real_private_registry_auth_ready": "no",
            "is_live_private_registry_ready": "no",
            "is_production_distribution_ready": "no",
            "is_full_biosdk_ready": "no",
            "is_biocompute_runtime_ready": "no",
            "is_bic_os_ready": "no",
            "next_best_build_step": "add registry revoke-yank and recipient notification drill contract proof" if proof_ready else "fix v5.46 auth/feed blockers first",
        },
        "claim_boundary": "v5.46 proves local private-registry auth token semantics, expiring private-feed behavior and registry log export shape over the v5.45 recipient onboarding audit contract. It does not claim real private registry authentication, live registry feed enforcement, production distribution, full BioSDK, production BioCompute Runtime or BiC OS readiness.",
    }
    audit["private_registry_auth_feed_audit_sha256"] = stable_hash({key: value for key, value in audit.items() if key != "private_registry_auth_feed_audit_sha256"})
    return audit


def write_private_registry_auth_feed_outputs_v546(audit: dict[str, Any], out_dir: str | Path = DEFAULT_OUT) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary_json": out / "V546_PRIVATE_REGISTRY_AUTH_FEED_SUMMARY.json",
        "policy_json": out / "V546_AUTH_FEED_POLICY.json",
        "matrix_json": out / "V546_AUTH_FEED_MATRIX.json",
        "feed_manifest_json": out / "V546_EXPIRING_FEED_MANIFEST.json",
        "expiry_probe_json": out / "V546_EXPIRING_FEED_PROBE.json",
        "registry_log_export_json": out / "V546_REGISTRY_LOG_EXPORT_CONTRACT.json",
        "audit_bundle_json": out / "V546_AUTH_FEED_AUDIT_BUNDLE.json",
        "matrix_csv": out / "V546_AUTH_FEED_MATRIX.csv",
        "registry_log_csv": out / "V546_REGISTRY_LOG_EXPORT.csv",
        "markdown_report": out / "BIOGPU_V546_PRIVATE_REGISTRY_AUTH_FEED_REPORT.md",
    }
    summary = {key: value for key, value in audit.items() if key not in {"auth_feed_policy", "auth_feed_matrix", "expiring_feed_manifest", "expiring_feed_probe", "registry_log_export_contract", "auth_feed_audit_bundle"}}
    paths["summary_json"].write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["policy_json"].write_text(json.dumps(audit["auth_feed_policy"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["matrix_json"].write_text(json.dumps(audit["auth_feed_matrix"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["feed_manifest_json"].write_text(json.dumps(audit["expiring_feed_manifest"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["expiry_probe_json"].write_text(json.dumps(audit["expiring_feed_probe"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["registry_log_export_json"].write_text(json.dumps(audit["registry_log_export_contract"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["audit_bundle_json"].write_text(json.dumps(audit["auth_feed_audit_bundle"], indent=2, ensure_ascii=False), encoding="utf-8")
    _write_auth_feed_matrix_csv(paths["matrix_csv"], audit["auth_feed_matrix"].get("decisions", []))
    _write_registry_log_csv(paths["registry_log_csv"], audit["registry_log_export_contract"].get("registry_log_events", []))
    paths["markdown_report"].write_text(_markdown_report(audit), encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}


def _write_auth_feed_matrix_csv(path: Path, decisions: list[dict[str, Any]]) -> None:
    fieldnames = ["request_id", "recipient_id", "token_scope", "authenticated_for_local_feed", "local_feed_token_id", "feed_expires_at", "reason_codes"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for decision in decisions:
            row = {field: decision.get(field) for field in fieldnames}
            row["reason_codes"] = " | ".join(str(reason) for reason in decision.get("reason_codes", []))
            writer.writerow(row)


def _write_registry_log_csv(path: Path, events: list[dict[str, Any]]) -> None:
    fieldnames = ["event_id", "event_type", "recipient_id", "token_scope", "artifact_sha256", "decision_allowed", "previous_event_sha256", "event_sha256"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for event in events:
            writer.writerow({field: event.get(field) for field in fieldnames})


def _markdown_report(audit: dict[str, Any]) -> str:
    answer = audit["direct_answer"]
    lines = [
        "# BioGPU-Core v5.46 Private Registry Auth Feed Contract",
        "",
        "## Direct Answer",
        "",
        f"- Private registry auth/feed contract added: `{answer['did_we_add_private_registry_auth_feed_contract']}`",
        f"- Local auth tokens validated: `{answer['did_we_validate_local_auth_tokens']}`",
        f"- Expiring feed denial validated: `{answer['did_we_validate_expiring_feed_denial']}`",
        f"- Registry log export shape defined: `{answer['did_we_define_registry_log_export_shape']}`",
        f"- Real private registry auth ready: `{answer['is_real_private_registry_auth_ready']}`",
        f"- Live private registry ready: `{answer['is_live_private_registry_ready']}`",
        f"- Production distribution ready: `{answer['is_production_distribution_ready']}`",
        f"- Full BioSDK ready: `{answer['is_full_biosdk_ready']}`",
        f"- BioCompute Runtime ready: `{answer['is_biocompute_runtime_ready']}`",
        f"- BiC OS ready: `{answer['is_bic_os_ready']}`",
        f"- Next best build step: {answer['next_best_build_step']}",
        "",
        "## Proof Summary",
        "",
        f"- Overall status: `{audit['overall_status']}`",
        f"- v5.45 dependency ready: `{audit['v545_dependency_ready']}`",
        f"- Auth/feed matrix ready: `{audit['auth_feed_matrix_ready']}`",
        f"- Expiring feed manifest ready: `{audit['expiring_feed_manifest_ready']}`",
        f"- Expiry probe ready: `{audit['expiring_feed_probe_ready']}`",
        f"- Registry log export contract ready: `{audit['registry_log_export_contract_ready']}`",
        f"- Allowed feeds: `{audit['allowed_feed_count']}`",
        f"- Denied feeds: `{audit['denied_feed_count']}`",
        f"- Registry log events: `{audit['registry_log_event_count']}`",
        "",
        "## Missing Real Inputs",
        "",
    ]
    for missing in audit["missing_real_inputs"]:
        lines.append(f"- {missing}")
    lines.extend(["", "## Boundary", "", audit["claim_boundary"], ""])
    return "\n".join(lines)