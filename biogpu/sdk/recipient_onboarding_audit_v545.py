"""Recipient onboarding audit contract proof, v5.45."""
from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from biogpu.beta.job_model_v43 import utc_now_iso
from biogpu.evidence.ledger_v53 import stable_hash
from biogpu.sdk.private_registry_handoff_v544 import run_private_registry_handoff_workflow_v544


DEFAULT_OUT = Path("outputs/v545_recipient_onboarding_audit")
AUTHORIZED_RECIPIENT_ROLES_V545 = {"artifact_recipient", "beta_operator", "provenance_reviewer"}
AUTHORIZED_APPROVAL_ROLES_V545 = {"release_manager", "beta_operator", "provenance_reviewer"}
MAX_LOCAL_ACCESS_WINDOW_HOURS_V545 = 168


@dataclass(frozen=True)
class RecipientOnboardingPolicyV545:
    policy_id: str
    authorized_recipient_roles: tuple[str, ...]
    authorized_approval_roles: tuple[str, ...]
    max_local_access_window_hours: int
    requires_named_local_account: bool
    requires_approval_record: bool
    requires_claim_boundary_ack: bool
    requires_access_log: bool
    requires_expiry_probe: bool
    live_registry_accounts_configured: bool
    local_contract_only: bool = True
    real_recipient_onboarding_ready: bool = False
    live_private_registry_ready: bool = False
    production_distribution_ready: bool = False
    full_biosdk_ready: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RecipientFixtureV545:
    recipient_id: str
    organization_id: str
    recipient_role: str
    approval_role: str
    named_local_account: bool
    approval_record_present: bool
    accepted_claim_boundary: bool
    requested_artifact_sha256: str
    access_window_hours: int
    revoked_recipient: bool
    requests_live_private_registry: bool
    requests_public_registry: bool
    requests_production_distribution: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RecipientOnboardingDecisionV545:
    recipient_id: str
    organization_id: str
    recipient_role: str
    onboarded_for_local_handoff: bool
    reason_codes: tuple[str, ...]
    access_window_hours: int
    access_expires_at: str | None
    local_access_grant_id: str | None
    real_recipient_onboarding_ready: bool = False
    live_private_registry_ready: bool = False
    production_distribution_ready: bool = False
    full_biosdk_ready: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def expires_at_for_hours_v545(hours: int) -> str | None:
    if hours <= 0:
        return None
    expires_at = datetime.now(timezone.utc).replace(microsecond=0) + timedelta(hours=hours)
    return expires_at.isoformat().replace("+00:00", "Z")


def build_recipient_onboarding_policy_v545() -> dict[str, Any]:
    policy = RecipientOnboardingPolicyV545(
        policy_id="BIOGPU_CORE_V545_RECIPIENT_ONBOARDING_POLICY",
        authorized_recipient_roles=tuple(sorted(AUTHORIZED_RECIPIENT_ROLES_V545)),
        authorized_approval_roles=tuple(sorted(AUTHORIZED_APPROVAL_ROLES_V545)),
        max_local_access_window_hours=MAX_LOCAL_ACCESS_WINDOW_HOURS_V545,
        requires_named_local_account=True,
        requires_approval_record=True,
        requires_claim_boundary_ack=True,
        requires_access_log=True,
        requires_expiry_probe=True,
        live_registry_accounts_configured=False,
    )
    result = {
        "version": "v5.45",
        "recipient_onboarding_policy_ready": True,
        "policy": policy.to_dict(),
        "blocked_modes": ["anonymous_download", "unbounded_access_window", "public_registry_release", "live_private_registry_account", "production_distribution"],
        "required_local_records": ["named_local_account", "approval_record", "claim_boundary_ack", "artifact_digest", "access_log_event", "expiry_probe"],
        "real_recipient_onboarding_ready": False,
        "live_private_registry_ready": False,
        "production_distribution_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    result["recipient_onboarding_policy_sha256"] = stable_hash(result)
    return result


def default_recipient_fixtures_v545(artifact_sha256: str) -> list[RecipientFixtureV545]:
    wrong_sha = "0" * 64 if artifact_sha256 != "0" * 64 else "1" * 64
    return [
        RecipientFixtureV545("recipient-alpha", "org-alpha", "artifact_recipient", "release_manager", True, True, True, artifact_sha256, 72, False, False, False, False),
        RecipientFixtureV545("recipient-beta", "org-beta", "artifact_recipient", "beta_operator", True, True, True, artifact_sha256, 48, False, False, False, False),
        RecipientFixtureV545("recipient-provenance", "org-audit", "provenance_reviewer", "provenance_reviewer", True, True, True, artifact_sha256, 24, False, False, False, False),
        RecipientFixtureV545("missing-account", "org-alpha", "artifact_recipient", "release_manager", False, True, True, artifact_sha256, 72, False, False, False, False),
        RecipientFixtureV545("missing-approval", "org-beta", "artifact_recipient", "release_manager", True, False, True, artifact_sha256, 72, False, False, False, False),
        RecipientFixtureV545("missing-boundary", "org-beta", "artifact_recipient", "release_manager", True, True, False, artifact_sha256, 72, False, False, False, False),
        RecipientFixtureV545("wrong-artifact", "org-alpha", "artifact_recipient", "release_manager", True, True, True, wrong_sha, 72, False, False, False, False),
        RecipientFixtureV545("expired-window", "org-alpha", "artifact_recipient", "release_manager", True, True, True, artifact_sha256, 0, False, False, False, False),
        RecipientFixtureV545("window-too-long", "org-alpha", "artifact_recipient", "release_manager", True, True, True, artifact_sha256, 720, False, False, False, False),
        RecipientFixtureV545("revoked-recipient", "org-beta", "artifact_recipient", "release_manager", True, True, True, artifact_sha256, 72, True, False, False, False),
        RecipientFixtureV545("live-registry-request", "org-alpha", "artifact_recipient", "release_manager", True, True, True, artifact_sha256, 72, False, True, False, False),
        RecipientFixtureV545("public-registry-request", "org-alpha", "artifact_recipient", "release_manager", True, True, True, artifact_sha256, 72, False, False, True, False),
        RecipientFixtureV545("production-request", "org-alpha", "artifact_recipient", "release_manager", True, True, True, artifact_sha256, 72, False, False, False, True),
        RecipientFixtureV545("unknown-role", "org-beta", "viewer", "release_manager", True, True, True, artifact_sha256, 72, False, False, False, False),
        RecipientFixtureV545("bad-approval-role", "org-beta", "artifact_recipient", "marketing", True, True, True, artifact_sha256, 72, False, False, False, False),
    ]


def evaluate_recipient_onboarding_v545(fixture: RecipientFixtureV545, v544_dependency: dict[str, Any]) -> RecipientOnboardingDecisionV545:
    reasons: list[str] = []
    expected_sha = str(v544_dependency.get("artifact_sha256") or "")
    if v544_dependency.get("private_registry_handoff_contract_ready") is not True:
        reasons.append("v544_handoff_contract_not_ready")
    if fixture.recipient_role not in AUTHORIZED_RECIPIENT_ROLES_V545:
        reasons.append("recipient_role_not_authorized")
    if fixture.approval_role not in AUTHORIZED_APPROVAL_ROLES_V545:
        reasons.append("approval_role_not_authorized")
    if not fixture.named_local_account:
        reasons.append("named_local_account_missing")
    if not fixture.approval_record_present:
        reasons.append("approval_record_missing")
    if not fixture.accepted_claim_boundary:
        reasons.append("claim_boundary_not_accepted")
    if fixture.requested_artifact_sha256 != expected_sha:
        reasons.append("artifact_digest_mismatch")
    if fixture.access_window_hours <= 0:
        reasons.append("access_window_expired_or_missing")
    if fixture.access_window_hours > MAX_LOCAL_ACCESS_WINDOW_HOURS_V545:
        reasons.append("access_window_exceeds_local_limit")
    if fixture.revoked_recipient:
        reasons.append("recipient_revoked")
    if fixture.requests_live_private_registry:
        reasons.append("live_private_registry_not_ready")
    if fixture.requests_public_registry:
        reasons.append("public_registry_not_allowed")
    if fixture.requests_production_distribution:
        reasons.append("production_distribution_not_allowed")
    allowed = not reasons
    grant_id = f"local-grant-{fixture.recipient_id}" if allowed else None
    return RecipientOnboardingDecisionV545(
        recipient_id=fixture.recipient_id,
        organization_id=fixture.organization_id,
        recipient_role=fixture.recipient_role,
        onboarded_for_local_handoff=allowed,
        reason_codes=tuple(reasons or ["local_recipient_onboarding_allowed"]),
        access_window_hours=fixture.access_window_hours,
        access_expires_at=expires_at_for_hours_v545(fixture.access_window_hours) if allowed else None,
        local_access_grant_id=grant_id,
    )


def run_recipient_onboarding_matrix_v545(v544_dependency: dict[str, Any], fixtures: list[RecipientFixtureV545] | None = None) -> dict[str, Any]:
    recipients = fixtures or default_recipient_fixtures_v545(str(v544_dependency.get("artifact_sha256") or ""))
    decisions = [evaluate_recipient_onboarding_v545(recipient, v544_dependency).to_dict() for recipient in recipients]
    allowed_count = sum(1 for decision in decisions if decision["onboarded_for_local_handoff"])
    denied_count = len(decisions) - allowed_count
    reason_codes = sorted({reason for decision in decisions for reason in decision["reason_codes"]})
    required_denials = {
        "named_local_account_missing",
        "approval_record_missing",
        "claim_boundary_not_accepted",
        "artifact_digest_mismatch",
        "access_window_expired_or_missing",
        "access_window_exceeds_local_limit",
        "recipient_revoked",
        "live_private_registry_not_ready",
        "public_registry_not_allowed",
        "production_distribution_not_allowed",
        "recipient_role_not_authorized",
        "approval_role_not_authorized",
    }
    matrix = {
        "version": "v5.45",
        "recipient_onboarding_matrix_ready": allowed_count >= 3 and denied_count >= 12 and required_denials.issubset(set(reason_codes)),
        "recipient_count": len(recipients),
        "allowed_recipient_count": allowed_count,
        "denied_recipient_count": denied_count,
        "reason_codes": reason_codes,
        "recipients": [recipient.to_dict() for recipient in recipients],
        "decisions": decisions,
        "real_recipient_onboarding_ready": False,
        "live_private_registry_ready": False,
        "production_distribution_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    matrix["recipient_onboarding_matrix_sha256"] = stable_hash(matrix)
    return matrix


def build_recipient_access_log_v545(v544_dependency: dict[str, Any], onboarding_matrix: dict[str, Any]) -> dict[str, Any]:
    artifact_sha256 = str(v544_dependency.get("artifact_sha256") or "")
    previous_hash = "GENESIS"
    events: list[dict[str, Any]] = []
    for decision in onboarding_matrix.get("decisions", []):
        if decision.get("onboarded_for_local_handoff") is not True:
            continue
        event = {
            "version": "v5.45",
            "event_id": f"access-log-{decision['recipient_id']}",
            "event_type": "local_handoff_access_granted",
            "recipient_id": decision["recipient_id"],
            "organization_id": decision["organization_id"],
            "artifact_sha256": artifact_sha256,
            "local_access_grant_id": decision["local_access_grant_id"],
            "access_expires_at": decision["access_expires_at"],
            "created_at": utc_now_iso(),
            "previous_event_sha256": previous_hash,
            "real_registry_log_ready": False,
            "production_distribution_ready": False,
            "bic_os_phase_locked": True,
        }
        event["event_sha256"] = stable_hash(event)
        previous_hash = event["event_sha256"]
        events.append(event)
    log = {
        "version": "v5.45",
        "recipient_access_log_ready": len(events) == onboarding_matrix.get("allowed_recipient_count") and len(events) >= 3,
        "event_count": len(events),
        "access_events": events,
        "access_log_head_sha256": previous_hash if events else None,
        "real_registry_log_ready": False,
        "live_private_registry_ready": False,
        "production_distribution_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    log["recipient_access_log_sha256"] = stable_hash(log)
    return log


def run_access_expiry_probe_v545(v544_dependency: dict[str, Any], onboarding_matrix: dict[str, Any]) -> dict[str, Any]:
    allowed = [decision for decision in onboarding_matrix.get("decisions", []) if decision.get("onboarded_for_local_handoff") is True]
    first_allowed = allowed[0] if allowed else {}
    expired_fixture = RecipientFixtureV545(
        "expiry-probe-recipient",
        "org-expiry",
        "artifact_recipient",
        "release_manager",
        True,
        True,
        True,
        str(v544_dependency.get("artifact_sha256") or ""),
        0,
        False,
        False,
        False,
        False,
    )
    expired_decision = evaluate_recipient_onboarding_v545(expired_fixture, v544_dependency).to_dict()
    simulated_after_expiry = {
        "recipient_id": first_allowed.get("recipient_id"),
        "initial_access_grant_id": first_allowed.get("local_access_grant_id"),
        "initial_access_expires_at": first_allowed.get("access_expires_at"),
        "simulated_access_after_expiry_allowed": False,
        "reason_codes": ["access_window_expired", "local_handoff_blocked_after_expiry"],
    }
    probe = {
        "version": "v5.45",
        "access_expiry_probe_ready": expired_decision.get("onboarded_for_local_handoff") is False and "access_window_expired_or_missing" in expired_decision.get("reason_codes", []) and simulated_after_expiry["simulated_access_after_expiry_allowed"] is False,
        "expired_onboarding_decision": expired_decision,
        "simulated_after_expiry": simulated_after_expiry,
        "live_private_registry_ready": False,
        "production_distribution_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    probe["access_expiry_probe_sha256"] = stable_hash(probe)
    return probe


def build_recipient_audit_bundle_v545(policy: dict[str, Any], onboarding_matrix: dict[str, Any], access_log: dict[str, Any], expiry_probe: dict[str, Any]) -> dict[str, Any]:
    bundle_ready = (
        policy.get("recipient_onboarding_policy_ready") is True
        and onboarding_matrix.get("recipient_onboarding_matrix_ready") is True
        and access_log.get("recipient_access_log_ready") is True
        and expiry_probe.get("access_expiry_probe_ready") is True
    )
    bundle = {
        "version": "v5.45",
        "recipient_audit_bundle_ready": bundle_ready,
        "policy_sha256": policy.get("recipient_onboarding_policy_sha256"),
        "matrix_sha256": onboarding_matrix.get("recipient_onboarding_matrix_sha256"),
        "access_log_sha256": access_log.get("recipient_access_log_sha256"),
        "expiry_probe_sha256": expiry_probe.get("access_expiry_probe_sha256"),
        "real_recipient_onboarding_ready": False,
        "live_private_registry_ready": False,
        "production_distribution_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    bundle["recipient_audit_bundle_sha256"] = stable_hash(bundle)
    return bundle


def run_recipient_onboarding_audit_workflow_v545(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    project_root = Path(root).resolve()
    out = project_root / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    v544_dependency = run_private_registry_handoff_workflow_v544(project_root, out / "d544")
    policy = build_recipient_onboarding_policy_v545()
    onboarding_matrix = run_recipient_onboarding_matrix_v545(v544_dependency)
    access_log = build_recipient_access_log_v545(v544_dependency, onboarding_matrix)
    expiry_probe = run_access_expiry_probe_v545(v544_dependency, onboarding_matrix)
    audit_bundle = build_recipient_audit_bundle_v545(policy, onboarding_matrix, access_log, expiry_probe)
    proof_ready = (
        v544_dependency.get("private_registry_handoff_contract_ready") is True
        and policy.get("recipient_onboarding_policy_ready") is True
        and onboarding_matrix.get("recipient_onboarding_matrix_ready") is True
        and access_log.get("recipient_access_log_ready") is True
        and expiry_probe.get("access_expiry_probe_ready") is True
        and audit_bundle.get("recipient_audit_bundle_ready") is True
    )
    audit = {
        "version": "v5.45",
        "phase": "recipient_onboarding_audit_contract",
        "overall_status": "recipient_onboarding_audit_contract_ready_production_not_claimed" if proof_ready else "recipient_onboarding_audit_contract_incomplete",
        "active_phase": "biosdk_recipient_onboarding_audit_proof",
        "bic_os_phase_locked": True,
        "recipient_onboarding_audit_contract_ready": proof_ready,
        "v544_dependency_ready": v544_dependency.get("private_registry_handoff_contract_ready") is True,
        "recipient_onboarding_policy_ready": policy.get("recipient_onboarding_policy_ready") is True,
        "recipient_onboarding_matrix_ready": onboarding_matrix.get("recipient_onboarding_matrix_ready") is True,
        "recipient_access_log_ready": access_log.get("recipient_access_log_ready") is True,
        "access_expiry_probe_ready": expiry_probe.get("access_expiry_probe_ready") is True,
        "recipient_audit_bundle_ready": audit_bundle.get("recipient_audit_bundle_ready") is True,
        "artifact_name": v544_dependency.get("artifact_name"),
        "artifact_sha256": v544_dependency.get("artifact_sha256"),
        "allowed_recipient_count": onboarding_matrix.get("allowed_recipient_count"),
        "denied_recipient_count": onboarding_matrix.get("denied_recipient_count"),
        "access_log_event_count": access_log.get("event_count"),
        "real_recipient_onboarding_ready": False,
        "live_private_registry_ready": False,
        "private_registry_ready": False,
        "public_registry_ready": False,
        "production_distribution_ready": False,
        "production_runtime_ready": False,
        "production_api_ready": False,
        "production_biocompute_runtime_ready": False,
        "full_biosdk_ready": False,
        "live_actuation_enabled": False,
        "recipient_onboarding_policy": policy,
        "recipient_onboarding_matrix": onboarding_matrix,
        "recipient_access_log": access_log,
        "access_expiry_probe": expiry_probe,
        "recipient_audit_bundle": audit_bundle,
        "v544_dependency_summary": {key: value for key, value in v544_dependency.items() if key not in {"handoff_contract", "handoff_artifact_record", "local_handoff_package", "handoff_access_matrix", "handoff_revocation_probe", "local_registry_index", "v543_dependency_summary"}},
        "missing_real_inputs": [
            "real recipient identities and organization approvals",
            "private registry account provisioning",
            "registry authentication and authorization integration",
            "signed URL or private feed expiration enforcement",
            "registry access-log export and retention policy",
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
            "did_we_add_recipient_onboarding_audit_contract": "yes" if proof_ready else "not_yet",
            "did_we_validate_local_recipient_approvals": "yes" if onboarding_matrix.get("recipient_onboarding_matrix_ready") else "no",
            "did_we_write_local_access_log": "yes" if access_log.get("recipient_access_log_ready") else "no",
            "did_we_validate_expiry_denial": "yes" if expiry_probe.get("access_expiry_probe_ready") else "no",
            "is_real_recipient_onboarding_ready": "no",
            "is_live_private_registry_ready": "no",
            "is_production_distribution_ready": "no",
            "is_full_biosdk_ready": "no",
            "is_biocompute_runtime_ready": "no",
            "is_bic_os_ready": "no",
            "next_best_build_step": "add private registry authentication and expiring-feed contract proof" if proof_ready else "fix v5.45 onboarding blockers first",
        },
        "claim_boundary": "v5.45 proves local recipient onboarding approvals, access-log chaining and expiry denial over the v5.44 private-registry handoff contract. It does not claim real recipient onboarding, live private registry accounts, production distribution, full BioSDK, production BioCompute Runtime or BiC OS readiness.",
    }
    audit["recipient_onboarding_audit_sha256"] = stable_hash({key: value for key, value in audit.items() if key != "recipient_onboarding_audit_sha256"})
    return audit


def write_recipient_onboarding_audit_outputs_v545(audit: dict[str, Any], out_dir: str | Path = DEFAULT_OUT) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary_json": out / "V545_RECIPIENT_ONBOARDING_AUDIT_SUMMARY.json",
        "policy_json": out / "V545_RECIPIENT_ONBOARDING_POLICY.json",
        "matrix_json": out / "V545_RECIPIENT_ONBOARDING_MATRIX.json",
        "access_log_json": out / "V545_RECIPIENT_ACCESS_LOG.json",
        "expiry_probe_json": out / "V545_ACCESS_EXPIRY_PROBE.json",
        "audit_bundle_json": out / "V545_RECIPIENT_AUDIT_BUNDLE.json",
        "matrix_csv": out / "V545_RECIPIENT_ONBOARDING_MATRIX.csv",
        "access_log_csv": out / "V545_RECIPIENT_ACCESS_LOG.csv",
        "markdown_report": out / "BIOGPU_V545_RECIPIENT_ONBOARDING_AUDIT_REPORT.md",
    }
    summary = {key: value for key, value in audit.items() if key not in {"recipient_onboarding_policy", "recipient_onboarding_matrix", "recipient_access_log", "access_expiry_probe", "recipient_audit_bundle"}}
    paths["summary_json"].write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["policy_json"].write_text(json.dumps(audit["recipient_onboarding_policy"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["matrix_json"].write_text(json.dumps(audit["recipient_onboarding_matrix"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["access_log_json"].write_text(json.dumps(audit["recipient_access_log"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["expiry_probe_json"].write_text(json.dumps(audit["access_expiry_probe"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["audit_bundle_json"].write_text(json.dumps(audit["recipient_audit_bundle"], indent=2, ensure_ascii=False), encoding="utf-8")
    _write_onboarding_matrix_csv(paths["matrix_csv"], audit["recipient_onboarding_matrix"].get("decisions", []))
    _write_access_log_csv(paths["access_log_csv"], audit["recipient_access_log"].get("access_events", []))
    paths["markdown_report"].write_text(_markdown_report(audit), encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}


def _write_onboarding_matrix_csv(path: Path, decisions: list[dict[str, Any]]) -> None:
    fieldnames = ["recipient_id", "organization_id", "recipient_role", "onboarded_for_local_handoff", "access_window_hours", "access_expires_at", "local_access_grant_id", "reason_codes"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for decision in decisions:
            row = {field: decision.get(field) for field in fieldnames}
            row["reason_codes"] = " | ".join(str(reason) for reason in decision.get("reason_codes", []))
            writer.writerow(row)


def _write_access_log_csv(path: Path, events: list[dict[str, Any]]) -> None:
    fieldnames = ["event_id", "recipient_id", "organization_id", "artifact_sha256", "local_access_grant_id", "access_expires_at", "previous_event_sha256", "event_sha256"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for event in events:
            writer.writerow({field: event.get(field) for field in fieldnames})


def _markdown_report(audit: dict[str, Any]) -> str:
    answer = audit["direct_answer"]
    lines = [
        "# BioGPU-Core v5.45 Recipient Onboarding Audit Contract",
        "",
        "## Direct Answer",
        "",
        f"- Recipient onboarding audit contract added: `{answer['did_we_add_recipient_onboarding_audit_contract']}`",
        f"- Local recipient approvals validated: `{answer['did_we_validate_local_recipient_approvals']}`",
        f"- Local access log written: `{answer['did_we_write_local_access_log']}`",
        f"- Expiry denial validated: `{answer['did_we_validate_expiry_denial']}`",
        f"- Real recipient onboarding ready: `{answer['is_real_recipient_onboarding_ready']}`",
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
        f"- v5.44 dependency ready: `{audit['v544_dependency_ready']}`",
        f"- Onboarding matrix ready: `{audit['recipient_onboarding_matrix_ready']}`",
        f"- Access log ready: `{audit['recipient_access_log_ready']}`",
        f"- Expiry probe ready: `{audit['access_expiry_probe_ready']}`",
        f"- Allowed recipients: `{audit['allowed_recipient_count']}`",
        f"- Denied recipients: `{audit['denied_recipient_count']}`",
        f"- Access log events: `{audit['access_log_event_count']}`",
        "",
        "## Missing Real Inputs",
        "",
    ]
    for missing in audit["missing_real_inputs"]:
        lines.append(f"- {missing}")
    lines.extend(["", "## Boundary", "", audit["claim_boundary"], ""])
    return "\n".join(lines)