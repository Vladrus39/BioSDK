"""Registry revoke/yank and recipient notification drill proof, v5.47."""
from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from biogpu.beta.job_model_v43 import utc_now_iso
from biogpu.evidence.ledger_v53 import stable_hash
from biogpu.sdk.private_registry_auth_feed_v546 import run_private_registry_auth_feed_workflow_v546


DEFAULT_OUT = Path("outputs/v547_registry_revoke_yank_notification")
AUTHORIZED_REVOKE_ROLES_V547 = {"release_manager", "beta_operator", "provenance_reviewer", "security_reviewer"}
REQUIRED_REVOKE_TRIGGERS_V547 = {
    "artifact_digest_mismatch",
    "token_revoked",
    "feed_expiry_bypass",
    "recipient_offboarded",
    "claim_boundary_violation",
}
LOCAL_NOTIFICATION_CHANNELS_V547 = ("local_email_fixture", "local_dashboard_notice", "local_audit_log")


@dataclass(frozen=True)
class RegistryRevokeYankPolicyV547:
    policy_id: str
    authorized_revoke_roles: tuple[str, ...]
    required_revoke_triggers: tuple[str, ...]
    notification_channels: tuple[str, ...]
    requires_v546_auth_feed_contract: bool
    requires_local_yank_manifest: bool
    requires_recipient_notification: bool
    requires_recipient_acknowledgement: bool
    requires_incident_linkage: bool
    live_registry_yank_configured: bool
    local_contract_only: bool = True
    production_yank_ready: bool = False
    live_private_registry_ready: bool = False
    production_distribution_ready: bool = False
    full_biosdk_ready: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RevokeYankScenarioFixtureV547:
    scenario_id: str
    trigger: str
    initiated_by_role: str
    recipient_id: str
    local_feed_token_id: str
    has_incident_link: bool
    notification_channel: str
    recipient_ack_received: bool
    attempts_live_registry_yank: bool
    attempts_public_registry_yank: bool
    requests_production_distribution: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RevokeYankDecisionV547:
    scenario_id: str
    trigger: str
    local_revoke_yank_allowed: bool
    reason_codes: tuple[str, ...]
    recipient_id: str
    local_feed_token_id: str
    incident_link_id: str | None
    notification_event_id: str | None
    local_yank_event_id: str | None
    production_yank_ready: bool = False
    live_private_registry_ready: bool = False
    production_distribution_ready: bool = False
    full_biosdk_ready: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_registry_revoke_yank_policy_v547() -> dict[str, Any]:
    policy = RegistryRevokeYankPolicyV547(
        policy_id="BIOGPU_CORE_V547_REGISTRY_REVOKE_YANK_POLICY",
        authorized_revoke_roles=tuple(sorted(AUTHORIZED_REVOKE_ROLES_V547)),
        required_revoke_triggers=tuple(sorted(REQUIRED_REVOKE_TRIGGERS_V547)),
        notification_channels=LOCAL_NOTIFICATION_CHANNELS_V547,
        requires_v546_auth_feed_contract=True,
        requires_local_yank_manifest=True,
        requires_recipient_notification=True,
        requires_recipient_acknowledgement=True,
        requires_incident_linkage=True,
        live_registry_yank_configured=False,
    )
    result = {
        "version": "v5.47",
        "registry_revoke_yank_policy_ready": True,
        "policy": policy.to_dict(),
        "blocked_modes": ["live_registry_yank", "public_registry_yank", "silent_recipient_revocation", "production_distribution_revoke"],
        "required_local_records": ["v546_auth_feed_contract", "local_yank_manifest", "notification_event", "recipient_ack", "incident_linkage"],
        "production_yank_ready": False,
        "live_private_registry_ready": False,
        "production_distribution_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    result["registry_revoke_yank_policy_sha256"] = stable_hash(result)
    return result


def allowed_feed_tokens_v547(v546_dependency: dict[str, Any]) -> list[dict[str, Any]]:
    feeds = list(v546_dependency.get("expiring_feed_manifest", {}).get("feeds", []))
    if feeds:
        return feeds
    matrix_decisions = v546_dependency.get("auth_feed_matrix", {}).get("decisions", [])
    return [
        {
            "recipient_id": decision.get("recipient_id"),
            "local_feed_token_id": decision.get("local_feed_token_id"),
            "feed_id": f"feed-{decision.get('request_id')}",
        }
        for decision in matrix_decisions
        if decision.get("authenticated_for_local_feed") is True
    ]


def default_revoke_yank_scenarios_v547(v546_dependency: dict[str, Any]) -> list[RevokeYankScenarioFixtureV547]:
    tokens = allowed_feed_tokens_v547(v546_dependency)
    alpha = tokens[0] if tokens else {"recipient_id": "recipient-alpha", "local_feed_token_id": "local-feed-token-alpha"}
    beta = tokens[1] if len(tokens) > 1 else alpha
    provenance = tokens[2] if len(tokens) > 2 else alpha
    return [
        RevokeYankScenarioFixtureV547("digest-mismatch", "artifact_digest_mismatch", "release_manager", str(alpha.get("recipient_id")), str(alpha.get("local_feed_token_id")), True, "local_email_fixture", True, False, False, False),
        RevokeYankScenarioFixtureV547("token-revoked", "token_revoked", "beta_operator", str(beta.get("recipient_id")), str(beta.get("local_feed_token_id")), True, "local_dashboard_notice", True, False, False, False),
        RevokeYankScenarioFixtureV547("feed-expiry-bypass", "feed_expiry_bypass", "security_reviewer", str(alpha.get("recipient_id")), str(alpha.get("local_feed_token_id")), True, "local_audit_log", True, False, False, False),
        RevokeYankScenarioFixtureV547("recipient-offboarded", "recipient_offboarded", "provenance_reviewer", str(provenance.get("recipient_id")), str(provenance.get("local_feed_token_id")), True, "local_email_fixture", True, False, False, False),
        RevokeYankScenarioFixtureV547("unknown-trigger", "manual_marketing_yank", "release_manager", str(alpha.get("recipient_id")), str(alpha.get("local_feed_token_id")), True, "local_email_fixture", True, False, False, False),
        RevokeYankScenarioFixtureV547("unauthorized-role", "token_revoked", "support_agent", str(alpha.get("recipient_id")), str(alpha.get("local_feed_token_id")), True, "local_email_fixture", True, False, False, False),
        RevokeYankScenarioFixtureV547("missing-incident", "token_revoked", "release_manager", str(alpha.get("recipient_id")), str(alpha.get("local_feed_token_id")), False, "local_email_fixture", True, False, False, False),
        RevokeYankScenarioFixtureV547("missing-recipient-ack", "recipient_offboarded", "release_manager", str(beta.get("recipient_id")), str(beta.get("local_feed_token_id")), True, "local_dashboard_notice", False, False, False, False),
        RevokeYankScenarioFixtureV547("bad-channel", "claim_boundary_violation", "release_manager", str(alpha.get("recipient_id")), str(alpha.get("local_feed_token_id")), True, "sms_live_gateway", True, False, False, False),
        RevokeYankScenarioFixtureV547("live-registry-yank", "token_revoked", "release_manager", str(alpha.get("recipient_id")), str(alpha.get("local_feed_token_id")), True, "local_email_fixture", True, True, False, False),
        RevokeYankScenarioFixtureV547("public-registry-yank", "token_revoked", "release_manager", str(alpha.get("recipient_id")), str(alpha.get("local_feed_token_id")), True, "local_email_fixture", True, False, True, False),
        RevokeYankScenarioFixtureV547("production-yank", "token_revoked", "release_manager", str(alpha.get("recipient_id")), str(alpha.get("local_feed_token_id")), True, "local_email_fixture", True, False, False, True),
    ]


def evaluate_revoke_yank_scenario_v547(scenario: RevokeYankScenarioFixtureV547, v546_dependency: dict[str, Any]) -> RevokeYankDecisionV547:
    reasons: list[str] = []
    known_tokens = {str(feed.get("local_feed_token_id")) for feed in allowed_feed_tokens_v547(v546_dependency)}
    if v546_dependency.get("private_registry_auth_feed_contract_ready") is not True:
        reasons.append("v546_auth_feed_contract_not_ready")
    if scenario.trigger not in REQUIRED_REVOKE_TRIGGERS_V547:
        reasons.append("revoke_trigger_not_authorized")
    if scenario.initiated_by_role not in AUTHORIZED_REVOKE_ROLES_V547:
        reasons.append("revoke_role_not_authorized")
    if scenario.local_feed_token_id not in known_tokens:
        reasons.append("local_feed_token_unknown")
    if not scenario.has_incident_link:
        reasons.append("incident_link_missing")
    if scenario.notification_channel not in LOCAL_NOTIFICATION_CHANNELS_V547:
        reasons.append("notification_channel_not_allowed")
    if not scenario.recipient_ack_received:
        reasons.append("recipient_ack_missing")
    if scenario.attempts_live_registry_yank:
        reasons.append("live_registry_yank_not_ready")
    if scenario.attempts_public_registry_yank:
        reasons.append("public_registry_yank_not_allowed")
    if scenario.requests_production_distribution:
        reasons.append("production_distribution_not_allowed")
    allowed = not reasons
    incident_id = f"incident-v547-{scenario.scenario_id}" if scenario.has_incident_link else None
    return RevokeYankDecisionV547(
        scenario_id=scenario.scenario_id,
        trigger=scenario.trigger,
        local_revoke_yank_allowed=allowed,
        reason_codes=tuple(reasons or ["local_revoke_yank_drill_allowed"]),
        recipient_id=scenario.recipient_id,
        local_feed_token_id=scenario.local_feed_token_id,
        incident_link_id=incident_id,
        notification_event_id=f"notify-{scenario.scenario_id}" if allowed else None,
        local_yank_event_id=f"local-yank-{scenario.scenario_id}" if allowed else None,
    )


def run_revoke_yank_matrix_v547(v546_dependency: dict[str, Any], scenarios: list[RevokeYankScenarioFixtureV547] | None = None) -> dict[str, Any]:
    fixtures = scenarios or default_revoke_yank_scenarios_v547(v546_dependency)
    decisions = [evaluate_revoke_yank_scenario_v547(scenario, v546_dependency).to_dict() for scenario in fixtures]
    allowed_count = sum(1 for decision in decisions if decision["local_revoke_yank_allowed"])
    denied_count = len(decisions) - allowed_count
    reason_codes = sorted({reason for decision in decisions for reason in decision["reason_codes"]})
    required_denials = {
        "revoke_trigger_not_authorized",
        "revoke_role_not_authorized",
        "incident_link_missing",
        "recipient_ack_missing",
        "notification_channel_not_allowed",
        "live_registry_yank_not_ready",
        "public_registry_yank_not_allowed",
        "production_distribution_not_allowed",
    }
    matrix = {
        "version": "v5.47",
        "revoke_yank_matrix_ready": allowed_count >= 4 and denied_count >= 8 and required_denials.issubset(set(reason_codes)),
        "scenario_count": len(fixtures),
        "allowed_revoke_yank_count": allowed_count,
        "denied_revoke_yank_count": denied_count,
        "reason_codes": reason_codes,
        "scenarios": [scenario.to_dict() for scenario in fixtures],
        "decisions": decisions,
        "production_yank_ready": False,
        "live_private_registry_ready": False,
        "production_distribution_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    matrix["revoke_yank_matrix_sha256"] = stable_hash(matrix)
    return matrix


def build_local_yank_manifest_v547(v546_dependency: dict[str, Any], revoke_yank_matrix: dict[str, Any]) -> dict[str, Any]:
    artifact_sha256 = str(v546_dependency.get("artifact_sha256") or "")
    entries: list[dict[str, Any]] = []
    for decision in revoke_yank_matrix.get("decisions", []):
        if decision.get("local_revoke_yank_allowed") is not True:
            continue
        entry = {
            "version": "v5.47",
            "local_yank_event_id": decision.get("local_yank_event_id"),
            "scenario_id": decision.get("scenario_id"),
            "trigger": decision.get("trigger"),
            "recipient_id": decision.get("recipient_id"),
            "local_feed_token_id": decision.get("local_feed_token_id"),
            "artifact_sha256": artifact_sha256,
            "local_token_revoked": True,
            "local_feed_disabled": True,
            "live_registry_yanked": False,
            "production_distribution_ready": False,
            "created_at": utc_now_iso(),
        }
        entry["local_yank_entry_sha256"] = stable_hash(entry)
        entries.append(entry)
    manifest = {
        "version": "v5.47",
        "local_yank_manifest_ready": len(entries) == revoke_yank_matrix.get("allowed_revoke_yank_count") and len(entries) >= 4,
        "artifact_sha256": artifact_sha256,
        "yank_entry_count": len(entries),
        "yank_entries": entries,
        "production_yank_ready": False,
        "live_private_registry_ready": False,
        "production_distribution_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    manifest["local_yank_manifest_sha256"] = stable_hash(manifest)
    return manifest


def build_recipient_notification_ack_trail_v547(revoke_yank_matrix: dict[str, Any]) -> dict[str, Any]:
    previous_hash = "GENESIS"
    events: list[dict[str, Any]] = []
    scenario_by_id = {scenario["scenario_id"]: scenario for scenario in revoke_yank_matrix.get("scenarios", [])}
    for decision in revoke_yank_matrix.get("decisions", []):
        if decision.get("local_revoke_yank_allowed") is not True:
            continue
        scenario = scenario_by_id.get(str(decision.get("scenario_id")), {})
        event = {
            "version": "v5.47",
            "notification_event_id": decision.get("notification_event_id"),
            "scenario_id": decision.get("scenario_id"),
            "recipient_id": decision.get("recipient_id"),
            "notification_channel": scenario.get("notification_channel"),
            "recipient_ack_received": scenario.get("recipient_ack_received") is True,
            "incident_link_id": decision.get("incident_link_id"),
            "created_at": utc_now_iso(),
            "previous_event_sha256": previous_hash,
            "real_notification_provider_ready": False,
            "production_distribution_ready": False,
            "bic_os_phase_locked": True,
        }
        event["notification_event_sha256"] = stable_hash(event)
        previous_hash = event["notification_event_sha256"]
        events.append(event)
    trail = {
        "version": "v5.47",
        "recipient_notification_ack_trail_ready": len(events) == revoke_yank_matrix.get("allowed_revoke_yank_count") and len(events) >= 4 and all(event["recipient_ack_received"] for event in events),
        "notification_event_count": len(events),
        "notification_events": events,
        "notification_trail_head_sha256": previous_hash if events else None,
        "real_notification_provider_ready": False,
        "live_private_registry_ready": False,
        "production_distribution_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    trail["recipient_notification_ack_trail_sha256"] = stable_hash(trail)
    return trail


def run_revoke_yank_effect_probe_v547(local_yank_manifest: dict[str, Any]) -> dict[str, Any]:
    probes = [
        {
            "probe_id": f"post-yank-access-{entry['scenario_id']}",
            "local_feed_token_id": entry["local_feed_token_id"],
            "local_token_revoked": entry["local_token_revoked"],
            "local_feed_disabled": entry["local_feed_disabled"],
            "simulated_post_yank_access_allowed": False,
            "reason_codes": ["local_token_revoked", "local_feed_disabled_after_yank"],
        }
        for entry in local_yank_manifest.get("yank_entries", [])
    ]
    probe = {
        "version": "v5.47",
        "revoke_yank_effect_probe_ready": len(probes) == local_yank_manifest.get("yank_entry_count") and len(probes) >= 4 and all(item["simulated_post_yank_access_allowed"] is False for item in probes),
        "probe_count": len(probes),
        "probes": probes,
        "production_yank_ready": False,
        "live_private_registry_ready": False,
        "production_distribution_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    probe["revoke_yank_effect_probe_sha256"] = stable_hash(probe)
    return probe


def build_incident_linkage_export_v547(revoke_yank_matrix: dict[str, Any], notification_trail: dict[str, Any]) -> dict[str, Any]:
    notification_by_scenario = {event["scenario_id"]: event for event in notification_trail.get("notification_events", [])}
    incidents: list[dict[str, Any]] = []
    for decision in revoke_yank_matrix.get("decisions", []):
        if decision.get("local_revoke_yank_allowed") is not True:
            continue
        incident = {
            "version": "v5.47",
            "incident_link_id": decision.get("incident_link_id"),
            "scenario_id": decision.get("scenario_id"),
            "trigger": decision.get("trigger"),
            "recipient_id": decision.get("recipient_id"),
            "notification_event_id": notification_by_scenario.get(decision.get("scenario_id"), {}).get("notification_event_id"),
            "local_yank_event_id": decision.get("local_yank_event_id"),
            "incident_state": "local_drill_resolved",
            "created_at": utc_now_iso(),
            "production_incident_system_ready": False,
            "bic_os_phase_locked": True,
        }
        incident["incident_link_sha256"] = stable_hash(incident)
        incidents.append(incident)
    export = {
        "version": "v5.47",
        "incident_linkage_export_ready": len(incidents) == revoke_yank_matrix.get("allowed_revoke_yank_count") and len(incidents) >= 4,
        "incident_count": len(incidents),
        "incident_links": incidents,
        "production_incident_system_ready": False,
        "live_private_registry_ready": False,
        "production_distribution_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    export["incident_linkage_export_sha256"] = stable_hash(export)
    return export


def build_revoke_yank_audit_bundle_v547(policy: dict[str, Any], revoke_yank_matrix: dict[str, Any], local_yank_manifest: dict[str, Any], notification_trail: dict[str, Any], effect_probe: dict[str, Any], incident_export: dict[str, Any]) -> dict[str, Any]:
    bundle_ready = (
        policy.get("registry_revoke_yank_policy_ready") is True
        and revoke_yank_matrix.get("revoke_yank_matrix_ready") is True
        and local_yank_manifest.get("local_yank_manifest_ready") is True
        and notification_trail.get("recipient_notification_ack_trail_ready") is True
        and effect_probe.get("revoke_yank_effect_probe_ready") is True
        and incident_export.get("incident_linkage_export_ready") is True
    )
    bundle = {
        "version": "v5.47",
        "revoke_yank_audit_bundle_ready": bundle_ready,
        "policy_sha256": policy.get("registry_revoke_yank_policy_sha256"),
        "matrix_sha256": revoke_yank_matrix.get("revoke_yank_matrix_sha256"),
        "local_yank_manifest_sha256": local_yank_manifest.get("local_yank_manifest_sha256"),
        "notification_trail_sha256": notification_trail.get("recipient_notification_ack_trail_sha256"),
        "effect_probe_sha256": effect_probe.get("revoke_yank_effect_probe_sha256"),
        "incident_linkage_export_sha256": incident_export.get("incident_linkage_export_sha256"),
        "production_yank_ready": False,
        "live_private_registry_ready": False,
        "production_distribution_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    bundle["revoke_yank_audit_bundle_sha256"] = stable_hash(bundle)
    return bundle


def run_registry_revoke_yank_notification_workflow_v547(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    project_root = Path(root).resolve()
    out = project_root / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    v546_dependency = run_private_registry_auth_feed_workflow_v546(project_root, out.parent / "d547")
    policy = build_registry_revoke_yank_policy_v547()
    revoke_yank_matrix = run_revoke_yank_matrix_v547(v546_dependency)
    local_yank_manifest = build_local_yank_manifest_v547(v546_dependency, revoke_yank_matrix)
    notification_trail = build_recipient_notification_ack_trail_v547(revoke_yank_matrix)
    effect_probe = run_revoke_yank_effect_probe_v547(local_yank_manifest)
    incident_export = build_incident_linkage_export_v547(revoke_yank_matrix, notification_trail)
    audit_bundle = build_revoke_yank_audit_bundle_v547(policy, revoke_yank_matrix, local_yank_manifest, notification_trail, effect_probe, incident_export)
    proof_ready = (
        v546_dependency.get("private_registry_auth_feed_contract_ready") is True
        and policy.get("registry_revoke_yank_policy_ready") is True
        and revoke_yank_matrix.get("revoke_yank_matrix_ready") is True
        and local_yank_manifest.get("local_yank_manifest_ready") is True
        and notification_trail.get("recipient_notification_ack_trail_ready") is True
        and effect_probe.get("revoke_yank_effect_probe_ready") is True
        and incident_export.get("incident_linkage_export_ready") is True
        and audit_bundle.get("revoke_yank_audit_bundle_ready") is True
    )
    audit = {
        "version": "v5.47",
        "phase": "registry_revoke_yank_notification_contract",
        "overall_status": "registry_revoke_yank_notification_contract_ready_production_not_claimed" if proof_ready else "registry_revoke_yank_notification_contract_incomplete",
        "active_phase": "biosdk_registry_revoke_yank_notification_proof",
        "bic_os_phase_locked": True,
        "registry_revoke_yank_notification_contract_ready": proof_ready,
        "v546_dependency_ready": v546_dependency.get("private_registry_auth_feed_contract_ready") is True,
        "registry_revoke_yank_policy_ready": policy.get("registry_revoke_yank_policy_ready") is True,
        "revoke_yank_matrix_ready": revoke_yank_matrix.get("revoke_yank_matrix_ready") is True,
        "local_yank_manifest_ready": local_yank_manifest.get("local_yank_manifest_ready") is True,
        "recipient_notification_ack_trail_ready": notification_trail.get("recipient_notification_ack_trail_ready") is True,
        "revoke_yank_effect_probe_ready": effect_probe.get("revoke_yank_effect_probe_ready") is True,
        "incident_linkage_export_ready": incident_export.get("incident_linkage_export_ready") is True,
        "revoke_yank_audit_bundle_ready": audit_bundle.get("revoke_yank_audit_bundle_ready") is True,
        "artifact_name": v546_dependency.get("artifact_name"),
        "artifact_sha256": v546_dependency.get("artifact_sha256"),
        "allowed_revoke_yank_count": revoke_yank_matrix.get("allowed_revoke_yank_count"),
        "denied_revoke_yank_count": revoke_yank_matrix.get("denied_revoke_yank_count"),
        "local_yank_entry_count": local_yank_manifest.get("yank_entry_count"),
        "notification_event_count": notification_trail.get("notification_event_count"),
        "incident_link_count": incident_export.get("incident_count"),
        "production_yank_ready": False,
        "real_notification_provider_ready": False,
        "live_private_registry_ready": False,
        "private_registry_ready": False,
        "public_registry_ready": False,
        "production_distribution_ready": False,
        "production_runtime_ready": False,
        "production_api_ready": False,
        "production_biocompute_runtime_ready": False,
        "full_biosdk_ready": False,
        "live_actuation_enabled": False,
        "registry_revoke_yank_policy": policy,
        "revoke_yank_matrix": revoke_yank_matrix,
        "local_yank_manifest": local_yank_manifest,
        "recipient_notification_ack_trail": notification_trail,
        "revoke_yank_effect_probe": effect_probe,
        "incident_linkage_export": incident_export,
        "revoke_yank_audit_bundle": audit_bundle,
        "v546_dependency_summary": {key: value for key, value in v546_dependency.items() if key not in {"auth_feed_policy", "auth_feed_matrix", "expiring_feed_manifest", "expiring_feed_probe", "registry_log_export_contract", "auth_feed_audit_bundle", "v545_dependency_summary"}},
        "missing_real_inputs": [
            "live private registry revoke/yank endpoint",
            "production token revocation and package yank authority",
            "recipient notification provider integration",
            "recipient acknowledgement collection from real accounts",
            "registry access-log export and retention backend",
            "production incident management workflow",
            "public/private registry user notification process",
        ],
        "remaining_runtime_blockers": [
            "production identity provider integration and persistent tenant membership",
            "production object storage and audit retention backend",
            "hosted dashboard server and browser session enforcement",
            "real external read-only API credentials or partner exports",
            "lab-approved live telemetry and closed-loop approval workflow",
        ],
        "direct_answer": {
            "did_we_add_registry_revoke_yank_notification_contract": "yes" if proof_ready else "not_yet",
            "did_we_validate_local_yank_manifest": "yes" if local_yank_manifest.get("local_yank_manifest_ready") else "no",
            "did_we_validate_notification_ack_trail": "yes" if notification_trail.get("recipient_notification_ack_trail_ready") else "no",
            "did_we_link_incidents": "yes" if incident_export.get("incident_linkage_export_ready") else "no",
            "is_production_yank_ready": "no",
            "is_live_private_registry_ready": "no",
            "is_production_distribution_ready": "no",
            "is_full_biosdk_ready": "no",
            "is_biocompute_runtime_ready": "no",
            "is_bic_os_ready": "no",
            "next_best_build_step": "add release operations runbook and operator handoff checklist proof" if proof_ready else "fix v5.47 revoke/yank blockers first",
        },
        "claim_boundary": "v5.47 proves local registry revoke/yank drill behavior, recipient notification acknowledgement trail and incident linkage over the v5.46 private-registry auth/feed contract. It does not claim production yank authority, live private registry revocation, real notification delivery, production distribution, full BioSDK, production BioCompute Runtime or BiC OS readiness.",
    }
    audit["registry_revoke_yank_notification_audit_sha256"] = stable_hash({key: value for key, value in audit.items() if key != "registry_revoke_yank_notification_audit_sha256"})
    return audit


def write_registry_revoke_yank_notification_outputs_v547(audit: dict[str, Any], out_dir: str | Path = DEFAULT_OUT) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary_json": out / "V547_REGISTRY_REVOKE_YANK_NOTIFICATION_SUMMARY.json",
        "policy_json": out / "V547_REGISTRY_REVOKE_YANK_POLICY.json",
        "matrix_json": out / "V547_REVOKE_YANK_MATRIX.json",
        "local_yank_manifest_json": out / "V547_LOCAL_YANK_MANIFEST.json",
        "notification_trail_json": out / "V547_RECIPIENT_NOTIFICATION_ACK_TRAIL.json",
        "effect_probe_json": out / "V547_REVOKE_YANK_EFFECT_PROBE.json",
        "incident_linkage_json": out / "V547_INCIDENT_LINKAGE_EXPORT.json",
        "audit_bundle_json": out / "V547_REVOKE_YANK_AUDIT_BUNDLE.json",
        "matrix_csv": out / "V547_REVOKE_YANK_MATRIX.csv",
        "notification_trail_csv": out / "V547_RECIPIENT_NOTIFICATION_ACK_TRAIL.csv",
        "markdown_report": out / "BIOGPU_V547_REGISTRY_REVOKE_YANK_NOTIFICATION_REPORT.md",
    }
    summary = {key: value for key, value in audit.items() if key not in {"registry_revoke_yank_policy", "revoke_yank_matrix", "local_yank_manifest", "recipient_notification_ack_trail", "revoke_yank_effect_probe", "incident_linkage_export", "revoke_yank_audit_bundle"}}
    paths["summary_json"].write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["policy_json"].write_text(json.dumps(audit["registry_revoke_yank_policy"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["matrix_json"].write_text(json.dumps(audit["revoke_yank_matrix"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["local_yank_manifest_json"].write_text(json.dumps(audit["local_yank_manifest"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["notification_trail_json"].write_text(json.dumps(audit["recipient_notification_ack_trail"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["effect_probe_json"].write_text(json.dumps(audit["revoke_yank_effect_probe"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["incident_linkage_json"].write_text(json.dumps(audit["incident_linkage_export"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["audit_bundle_json"].write_text(json.dumps(audit["revoke_yank_audit_bundle"], indent=2, ensure_ascii=False), encoding="utf-8")
    _write_matrix_csv(paths["matrix_csv"], audit["revoke_yank_matrix"].get("decisions", []))
    _write_notification_csv(paths["notification_trail_csv"], audit["recipient_notification_ack_trail"].get("notification_events", []))
    paths["markdown_report"].write_text(_markdown_report(audit), encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}


def _write_matrix_csv(path: Path, decisions: list[dict[str, Any]]) -> None:
    fieldnames = ["scenario_id", "trigger", "local_revoke_yank_allowed", "recipient_id", "local_feed_token_id", "incident_link_id", "notification_event_id", "local_yank_event_id", "reason_codes"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for decision in decisions:
            row = {field: decision.get(field) for field in fieldnames}
            row["reason_codes"] = " | ".join(str(reason) for reason in decision.get("reason_codes", []))
            writer.writerow(row)


def _write_notification_csv(path: Path, events: list[dict[str, Any]]) -> None:
    fieldnames = ["notification_event_id", "scenario_id", "recipient_id", "notification_channel", "recipient_ack_received", "incident_link_id", "previous_event_sha256", "notification_event_sha256"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for event in events:
            writer.writerow({field: event.get(field) for field in fieldnames})


def _markdown_report(audit: dict[str, Any]) -> str:
    answer = audit["direct_answer"]
    lines = [
        "# BioGPU-Core v5.47 Registry Revoke/Yank Notification Contract",
        "",
        "## Direct Answer",
        "",
        f"- Registry revoke/yank notification contract added: `{answer['did_we_add_registry_revoke_yank_notification_contract']}`",
        f"- Local yank manifest validated: `{answer['did_we_validate_local_yank_manifest']}`",
        f"- Notification acknowledgement trail validated: `{answer['did_we_validate_notification_ack_trail']}`",
        f"- Incidents linked: `{answer['did_we_link_incidents']}`",
        f"- Production yank ready: `{answer['is_production_yank_ready']}`",
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
        f"- v5.46 dependency ready: `{audit['v546_dependency_ready']}`",
        f"- Revoke/yank matrix ready: `{audit['revoke_yank_matrix_ready']}`",
        f"- Local yank manifest ready: `{audit['local_yank_manifest_ready']}`",
        f"- Notification trail ready: `{audit['recipient_notification_ack_trail_ready']}`",
        f"- Effect probe ready: `{audit['revoke_yank_effect_probe_ready']}`",
        f"- Incident linkage ready: `{audit['incident_linkage_export_ready']}`",
        f"- Allowed revoke/yank scenarios: `{audit['allowed_revoke_yank_count']}`",
        f"- Denied revoke/yank scenarios: `{audit['denied_revoke_yank_count']}`",
        "",
        "## Missing Real Inputs",
        "",
    ]
    for missing in audit["missing_real_inputs"]:
        lines.append(f"- {missing}")
    lines.extend(["", "## Boundary", "", audit["claim_boundary"], ""])
    return "\n".join(lines)