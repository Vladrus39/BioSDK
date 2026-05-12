"""Release operations runbook and operator handoff checklist proof, v5.48."""
from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from biogpu.beta.job_model_v43 import utc_now_iso
from biogpu.evidence.ledger_v53 import stable_hash
from biogpu.sdk.registry_revoke_yank_notification_v547 import run_registry_revoke_yank_notification_workflow_v547


DEFAULT_OUT = Path("outputs/v548_release_operations_handoff")
AUTHORIZED_OPERATOR_ROLES_V548 = {"release_manager", "beta_operator", "support_lead", "incident_commander", "security_reviewer"}
REQUIRED_RUNBOOK_SECTIONS_V548 = {
    "evidence_bundle_review",
    "clean_room_install_review",
    "private_registry_handoff_review",
    "auth_feed_review",
    "revoke_yank_notification_review",
    "support_escalation_path",
    "rollback_boundary",
    "claim_boundary_guardrail",
}


@dataclass(frozen=True)
class ReleaseOperationsHandoffPolicyV548:
    policy_id: str
    authorized_operator_roles: tuple[str, ...]
    required_runbook_sections: tuple[str, ...]
    requires_v547_revoke_yank_contract: bool
    requires_operator_handoff_packet: bool
    requires_support_window: bool
    requires_rollback_contact: bool
    requires_incident_commander: bool
    requires_claim_boundary_ack: bool
    live_operator_handoff_configured: bool
    local_contract_only: bool = True
    production_release_ready: bool = False
    production_operations_ready: bool = False
    full_biosdk_ready: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class OperatorHandoffFixtureV548:
    handoff_id: str
    operator_role: str
    has_v547_evidence: bool
    confirmed_runbook_sections: tuple[str, ...]
    handoff_packet_signed_local: bool
    support_window_defined: bool
    rollback_contact_defined: bool
    incident_commander_assigned: bool
    recipient_notice_template_ready: bool
    claim_boundary_acknowledged: bool
    attempts_live_operator_handoff: bool
    requests_production_release: bool
    requests_bic_os_unlocked: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class OperatorHandoffDecisionV548:
    handoff_id: str
    operator_role: str
    accepted_for_local_release_ops: bool
    reason_codes: tuple[str, ...]
    missing_runbook_sections: tuple[str, ...]
    handoff_packet_id: str | None
    local_operator_signature_id: str | None
    support_window_id: str | None
    production_release_ready: bool = False
    production_operations_ready: bool = False
    full_biosdk_ready: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_release_operations_handoff_policy_v548() -> dict[str, Any]:
    policy = ReleaseOperationsHandoffPolicyV548(
        policy_id="BIOGPU_CORE_V548_RELEASE_OPERATIONS_HANDOFF_POLICY",
        authorized_operator_roles=tuple(sorted(AUTHORIZED_OPERATOR_ROLES_V548)),
        required_runbook_sections=tuple(sorted(REQUIRED_RUNBOOK_SECTIONS_V548)),
        requires_v547_revoke_yank_contract=True,
        requires_operator_handoff_packet=True,
        requires_support_window=True,
        requires_rollback_contact=True,
        requires_incident_commander=True,
        requires_claim_boundary_ack=True,
        live_operator_handoff_configured=False,
    )
    result = {
        "version": "v5.48",
        "release_operations_handoff_policy_ready": True,
        "policy": policy.to_dict(),
        "blocked_modes": ["production_release", "live_operator_handoff", "unchecked_runbook_handoff", "bic_os_unlock"],
        "required_local_records": ["v547_revoke_yank_contract", "runbook_sections", "operator_handoff_packet", "support_window", "rollback_contact", "claim_boundary_ack"],
        "production_release_ready": False,
        "production_operations_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    result["release_operations_handoff_policy_sha256"] = stable_hash(result)
    return result


def build_release_operations_runbook_v548(v547_dependency: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    sections: list[dict[str, Any]] = []
    for section_id in sorted(REQUIRED_RUNBOOK_SECTIONS_V548):
        section = {
            "version": "v5.48",
            "section_id": section_id,
            "requires_operator_checkoff": True,
            "local_evidence_anchor": v547_dependency.get("registry_revoke_yank_notification_audit_sha256"),
            "artifact_sha256": v547_dependency.get("artifact_sha256"),
            "local_only": True,
            "production_release_ready": False,
            "bic_os_phase_locked": True,
        }
        section["runbook_section_sha256"] = stable_hash(section)
        sections.append(section)
    runbook = {
        "version": "v5.48",
        "release_operations_runbook_ready": policy.get("release_operations_handoff_policy_ready") is True and v547_dependency.get("registry_revoke_yank_notification_contract_ready") is True and len(sections) == len(REQUIRED_RUNBOOK_SECTIONS_V548),
        "runbook_id": "BIOGPU_CORE_V548_LOCAL_RELEASE_OPERATIONS_RUNBOOK",
        "section_count": len(sections),
        "sections": sections,
        "v547_dependency_sha256": v547_dependency.get("registry_revoke_yank_notification_audit_sha256"),
        "local_contract_only": True,
        "production_release_ready": False,
        "production_operations_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    runbook["release_operations_runbook_sha256"] = stable_hash(runbook)
    return runbook


def default_operator_handoff_fixtures_v548() -> list[OperatorHandoffFixtureV548]:
    all_sections = tuple(sorted(REQUIRED_RUNBOOK_SECTIONS_V548))
    missing_section_set = tuple(section for section in all_sections if section != "rollback_boundary")
    return [
        OperatorHandoffFixtureV548("release-manager-ready", "release_manager", True, all_sections, True, True, True, True, True, True, False, False, False),
        OperatorHandoffFixtureV548("beta-operator-ready", "beta_operator", True, all_sections, True, True, True, True, True, True, False, False, False),
        OperatorHandoffFixtureV548("support-lead-ready", "support_lead", True, all_sections, True, True, True, True, True, True, False, False, False),
        OperatorHandoffFixtureV548("incident-commander-ready", "incident_commander", True, all_sections, True, True, True, True, True, True, False, False, False),
        OperatorHandoffFixtureV548("missing-v547-evidence", "release_manager", False, all_sections, True, True, True, True, True, True, False, False, False),
        OperatorHandoffFixtureV548("missing-runbook-section", "release_manager", True, missing_section_set, True, True, True, True, True, True, False, False, False),
        OperatorHandoffFixtureV548("unsigned-packet", "release_manager", True, all_sections, False, True, True, True, True, True, False, False, False),
        OperatorHandoffFixtureV548("missing-support-window", "support_lead", True, all_sections, True, False, True, True, True, True, False, False, False),
        OperatorHandoffFixtureV548("missing-rollback-contact", "release_manager", True, all_sections, True, True, False, True, True, True, False, False, False),
        OperatorHandoffFixtureV548("missing-incident-commander", "beta_operator", True, all_sections, True, True, True, False, True, True, False, False, False),
        OperatorHandoffFixtureV548("missing-recipient-notice-template", "support_lead", True, all_sections, True, True, True, True, False, True, False, False, False),
        OperatorHandoffFixtureV548("missing-claim-boundary", "release_manager", True, all_sections, True, True, True, True, True, False, False, False, False),
        OperatorHandoffFixtureV548("unauthorized-operator", "marketing_owner", True, all_sections, True, True, True, True, True, True, False, False, False),
        OperatorHandoffFixtureV548("live-operator-handoff", "release_manager", True, all_sections, True, True, True, True, True, True, True, False, False),
        OperatorHandoffFixtureV548("production-release-request", "release_manager", True, all_sections, True, True, True, True, True, True, False, True, False),
        OperatorHandoffFixtureV548("bic-os-unlock-request", "release_manager", True, all_sections, True, True, True, True, True, True, False, False, True),
    ]


def evaluate_operator_handoff_v548(fixture: OperatorHandoffFixtureV548, v547_dependency: dict[str, Any]) -> OperatorHandoffDecisionV548:
    reasons: list[str] = []
    missing_sections = tuple(sorted(REQUIRED_RUNBOOK_SECTIONS_V548.difference(set(fixture.confirmed_runbook_sections))))
    if v547_dependency.get("registry_revoke_yank_notification_contract_ready") is not True or not fixture.has_v547_evidence:
        reasons.append("v547_revoke_yank_evidence_missing")
    if fixture.operator_role not in AUTHORIZED_OPERATOR_ROLES_V548:
        reasons.append("operator_role_not_authorized")
    if missing_sections:
        reasons.append("runbook_section_missing")
    if not fixture.handoff_packet_signed_local:
        reasons.append("local_handoff_signature_missing")
    if not fixture.support_window_defined:
        reasons.append("support_window_missing")
    if not fixture.rollback_contact_defined:
        reasons.append("rollback_contact_missing")
    if not fixture.incident_commander_assigned:
        reasons.append("incident_commander_missing")
    if not fixture.recipient_notice_template_ready:
        reasons.append("recipient_notice_template_missing")
    if not fixture.claim_boundary_acknowledged:
        reasons.append("claim_boundary_ack_missing")
    if fixture.attempts_live_operator_handoff:
        reasons.append("live_operator_handoff_not_ready")
    if fixture.requests_production_release:
        reasons.append("production_release_not_allowed")
    if fixture.requests_bic_os_unlocked:
        reasons.append("bic_os_unlock_not_allowed")
    accepted = not reasons
    return OperatorHandoffDecisionV548(
        handoff_id=fixture.handoff_id,
        operator_role=fixture.operator_role,
        accepted_for_local_release_ops=accepted,
        reason_codes=tuple(reasons or ["local_release_operations_handoff_accepted"]),
        missing_runbook_sections=missing_sections,
        handoff_packet_id=f"handoff-packet-{fixture.handoff_id}" if accepted else None,
        local_operator_signature_id=f"local-operator-sig-{fixture.handoff_id}" if accepted else None,
        support_window_id=f"support-window-{fixture.handoff_id}" if accepted else None,
    )


def run_operator_handoff_matrix_v548(v547_dependency: dict[str, Any], fixtures: list[OperatorHandoffFixtureV548] | None = None) -> dict[str, Any]:
    handoffs = fixtures or default_operator_handoff_fixtures_v548()
    decisions = [evaluate_operator_handoff_v548(handoff, v547_dependency).to_dict() for handoff in handoffs]
    accepted_count = sum(1 for decision in decisions if decision["accepted_for_local_release_ops"])
    denied_count = len(decisions) - accepted_count
    reason_codes = sorted({reason for decision in decisions for reason in decision["reason_codes"]})
    required_denials = {
        "v547_revoke_yank_evidence_missing",
        "runbook_section_missing",
        "local_handoff_signature_missing",
        "support_window_missing",
        "rollback_contact_missing",
        "incident_commander_missing",
        "recipient_notice_template_missing",
        "claim_boundary_ack_missing",
        "operator_role_not_authorized",
        "live_operator_handoff_not_ready",
        "production_release_not_allowed",
        "bic_os_unlock_not_allowed",
    }
    matrix = {
        "version": "v5.48",
        "operator_handoff_matrix_ready": accepted_count >= 4 and denied_count >= 12 and required_denials.issubset(set(reason_codes)),
        "handoff_count": len(handoffs),
        "accepted_operator_handoff_count": accepted_count,
        "denied_operator_handoff_count": denied_count,
        "reason_codes": reason_codes,
        "handoffs": [handoff.to_dict() for handoff in handoffs],
        "decisions": decisions,
        "production_release_ready": False,
        "production_operations_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    matrix["operator_handoff_matrix_sha256"] = stable_hash(matrix)
    return matrix


def build_operator_handoff_packet_v548(v547_dependency: dict[str, Any], runbook: dict[str, Any], handoff_matrix: dict[str, Any]) -> dict[str, Any]:
    packets: list[dict[str, Any]] = []
    for decision in handoff_matrix.get("decisions", []):
        if decision.get("accepted_for_local_release_ops") is not True:
            continue
        packet = {
            "version": "v5.48",
            "handoff_packet_id": decision.get("handoff_packet_id"),
            "operator_role": decision.get("operator_role"),
            "artifact_sha256": v547_dependency.get("artifact_sha256"),
            "runbook_sha256": runbook.get("release_operations_runbook_sha256"),
            "v547_dependency_sha256": v547_dependency.get("registry_revoke_yank_notification_audit_sha256"),
            "local_operator_signature_id": decision.get("local_operator_signature_id"),
            "support_window_id": decision.get("support_window_id"),
            "rollback_contact": "local-release-manager-contact",
            "incident_commander": "local-incident-commander-fixture",
            "recipient_notice_template": "local-recipient-notice-template-v548",
            "created_at": utc_now_iso(),
            "production_release_ready": False,
            "production_operations_ready": False,
            "bic_os_phase_locked": True,
        }
        packet["handoff_packet_sha256"] = stable_hash(packet)
        packets.append(packet)
    handoff_packet = {
        "version": "v5.48",
        "operator_handoff_packet_ready": len(packets) == handoff_matrix.get("accepted_operator_handoff_count") and len(packets) >= 4,
        "packet_count": len(packets),
        "packets": packets,
        "production_release_ready": False,
        "production_operations_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    handoff_packet["operator_handoff_packet_sha256"] = stable_hash(handoff_packet)
    return handoff_packet


def build_claim_boundary_attestation_v548(handoff_packet: dict[str, Any]) -> dict[str, Any]:
    attestations: list[dict[str, Any]] = []
    for packet in handoff_packet.get("packets", []):
        attestation = {
            "version": "v5.48",
            "attestation_id": f"claim-boundary-{packet['handoff_packet_id']}",
            "handoff_packet_id": packet.get("handoff_packet_id"),
            "operator_role": packet.get("operator_role"),
            "acknowledged_claim_boundary": True,
            "production_release_ready": False,
            "production_operations_ready": False,
            "full_biosdk_ready": False,
            "bic_os_ready": False,
            "created_at": utc_now_iso(),
        }
        attestation["claim_boundary_attestation_sha256"] = stable_hash(attestation)
        attestations.append(attestation)
    result = {
        "version": "v5.48",
        "claim_boundary_attestation_ready": len(attestations) == handoff_packet.get("packet_count") and len(attestations) >= 4,
        "attestation_count": len(attestations),
        "attestations": attestations,
        "production_release_ready": False,
        "production_operations_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    result["claim_boundary_attestation_sha256"] = stable_hash(result)
    return result


def build_release_operations_audit_bundle_v548(policy: dict[str, Any], runbook: dict[str, Any], handoff_matrix: dict[str, Any], handoff_packet: dict[str, Any], claim_boundary: dict[str, Any]) -> dict[str, Any]:
    bundle_ready = (
        policy.get("release_operations_handoff_policy_ready") is True
        and runbook.get("release_operations_runbook_ready") is True
        and handoff_matrix.get("operator_handoff_matrix_ready") is True
        and handoff_packet.get("operator_handoff_packet_ready") is True
        and claim_boundary.get("claim_boundary_attestation_ready") is True
    )
    bundle = {
        "version": "v5.48",
        "release_operations_audit_bundle_ready": bundle_ready,
        "policy_sha256": policy.get("release_operations_handoff_policy_sha256"),
        "runbook_sha256": runbook.get("release_operations_runbook_sha256"),
        "operator_handoff_matrix_sha256": handoff_matrix.get("operator_handoff_matrix_sha256"),
        "operator_handoff_packet_sha256": handoff_packet.get("operator_handoff_packet_sha256"),
        "claim_boundary_attestation_sha256": claim_boundary.get("claim_boundary_attestation_sha256"),
        "production_release_ready": False,
        "production_operations_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    bundle["release_operations_audit_bundle_sha256"] = stable_hash(bundle)
    return bundle


def run_release_operations_handoff_workflow_v548(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    project_root = Path(root).resolve()
    out = project_root / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    v547_dependency = run_registry_revoke_yank_notification_workflow_v547(project_root, out.parent / "d548")
    policy = build_release_operations_handoff_policy_v548()
    runbook = build_release_operations_runbook_v548(v547_dependency, policy)
    handoff_matrix = run_operator_handoff_matrix_v548(v547_dependency)
    handoff_packet = build_operator_handoff_packet_v548(v547_dependency, runbook, handoff_matrix)
    claim_boundary = build_claim_boundary_attestation_v548(handoff_packet)
    audit_bundle = build_release_operations_audit_bundle_v548(policy, runbook, handoff_matrix, handoff_packet, claim_boundary)
    proof_ready = (
        v547_dependency.get("registry_revoke_yank_notification_contract_ready") is True
        and policy.get("release_operations_handoff_policy_ready") is True
        and runbook.get("release_operations_runbook_ready") is True
        and handoff_matrix.get("operator_handoff_matrix_ready") is True
        and handoff_packet.get("operator_handoff_packet_ready") is True
        and claim_boundary.get("claim_boundary_attestation_ready") is True
        and audit_bundle.get("release_operations_audit_bundle_ready") is True
    )
    audit = {
        "version": "v5.48",
        "phase": "release_operations_handoff_contract",
        "overall_status": "release_operations_handoff_contract_ready_production_not_claimed" if proof_ready else "release_operations_handoff_contract_incomplete",
        "active_phase": "biosdk_release_operations_handoff_proof",
        "bic_os_phase_locked": True,
        "release_operations_handoff_contract_ready": proof_ready,
        "v547_dependency_ready": v547_dependency.get("registry_revoke_yank_notification_contract_ready") is True,
        "release_operations_handoff_policy_ready": policy.get("release_operations_handoff_policy_ready") is True,
        "release_operations_runbook_ready": runbook.get("release_operations_runbook_ready") is True,
        "operator_handoff_matrix_ready": handoff_matrix.get("operator_handoff_matrix_ready") is True,
        "operator_handoff_packet_ready": handoff_packet.get("operator_handoff_packet_ready") is True,
        "claim_boundary_attestation_ready": claim_boundary.get("claim_boundary_attestation_ready") is True,
        "release_operations_audit_bundle_ready": audit_bundle.get("release_operations_audit_bundle_ready") is True,
        "artifact_name": v547_dependency.get("artifact_name"),
        "artifact_sha256": v547_dependency.get("artifact_sha256"),
        "runbook_section_count": runbook.get("section_count"),
        "accepted_operator_handoff_count": handoff_matrix.get("accepted_operator_handoff_count"),
        "denied_operator_handoff_count": handoff_matrix.get("denied_operator_handoff_count"),
        "handoff_packet_count": handoff_packet.get("packet_count"),
        "claim_boundary_attestation_count": claim_boundary.get("attestation_count"),
        "production_release_ready": False,
        "production_operations_ready": False,
        "live_operator_handoff_ready": False,
        "live_private_registry_ready": False,
        "private_registry_ready": False,
        "public_registry_ready": False,
        "production_distribution_ready": False,
        "production_runtime_ready": False,
        "production_api_ready": False,
        "production_biocompute_runtime_ready": False,
        "full_biosdk_ready": False,
        "live_actuation_enabled": False,
        "release_operations_handoff_policy": policy,
        "release_operations_runbook": runbook,
        "operator_handoff_matrix": handoff_matrix,
        "operator_handoff_packet": handoff_packet,
        "claim_boundary_attestation": claim_boundary,
        "release_operations_audit_bundle": audit_bundle,
        "v547_dependency_summary": {key: value for key, value in v547_dependency.items() if key not in {"registry_revoke_yank_policy", "revoke_yank_matrix", "local_yank_manifest", "recipient_notification_ack_trail", "revoke_yank_effect_probe", "incident_linkage_export", "revoke_yank_audit_bundle", "v546_dependency_summary"}},
        "missing_real_inputs": [
            "real release operator identities and approvals",
            "production release operations runbook signoff",
            "live private registry administrative credentials",
            "production token revocation and package yank authority",
            "recipient notification provider integration",
            "production support and incident management systems",
            "production CI/CD and deployment gates",
            "legal, compliance and external beta acceptance records",
        ],
        "remaining_runtime_blockers": [
            "production identity provider integration and persistent tenant membership",
            "production object storage and audit retention backend",
            "hosted dashboard server and browser session enforcement",
            "real external read-only API credentials or partner exports",
            "lab-approved live telemetry and closed-loop approval workflow",
            "durable BioCompute Runtime daemon and OS service supervision",
        ],
        "direct_answer": {
            "did_we_add_release_operations_handoff_contract": "yes" if proof_ready else "not_yet",
            "did_we_validate_release_runbook": "yes" if runbook.get("release_operations_runbook_ready") else "no",
            "did_we_validate_operator_handoff_checklist": "yes" if handoff_matrix.get("operator_handoff_matrix_ready") else "no",
            "do_we_still_need_many_layers_before_production_and_os": "yes",
            "is_production_release_ready": "no",
            "is_production_operations_ready": "no",
            "is_full_biosdk_ready": "no",
            "is_biocompute_runtime_ready": "no",
            "is_bic_os_ready": "no",
            "next_best_build_step": "add production readiness gap matrix and staged pilot acceptance proof" if proof_ready else "fix v5.48 handoff blockers first",
        },
        "claim_boundary": "v5.48 proves a local release operations runbook and operator handoff checklist over the v5.47 revoke/yank notification drill. It does not claim production release operations, live operator handoff, production distribution, full BioSDK, production BioCompute Runtime or BiC OS readiness. Many additional proof layers remain before any production or OS claim.",
    }
    audit["release_operations_handoff_audit_sha256"] = stable_hash({key: value for key, value in audit.items() if key != "release_operations_handoff_audit_sha256"})
    return audit


def write_release_operations_handoff_outputs_v548(audit: dict[str, Any], out_dir: str | Path = DEFAULT_OUT) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary_json": out / "V548_RELEASE_OPERATIONS_HANDOFF_SUMMARY.json",
        "policy_json": out / "V548_RELEASE_OPERATIONS_HANDOFF_POLICY.json",
        "runbook_json": out / "V548_RELEASE_OPERATIONS_RUNBOOK.json",
        "handoff_matrix_json": out / "V548_OPERATOR_HANDOFF_MATRIX.json",
        "handoff_packet_json": out / "V548_OPERATOR_HANDOFF_PACKET.json",
        "claim_boundary_json": out / "V548_CLAIM_BOUNDARY_ATTESTATION.json",
        "audit_bundle_json": out / "V548_RELEASE_OPERATIONS_AUDIT_BUNDLE.json",
        "handoff_matrix_csv": out / "V548_OPERATOR_HANDOFF_MATRIX.csv",
        "handoff_packet_csv": out / "V548_OPERATOR_HANDOFF_PACKET.csv",
        "markdown_report": out / "BIOGPU_V548_RELEASE_OPERATIONS_HANDOFF_REPORT.md",
    }
    summary = {key: value for key, value in audit.items() if key not in {"release_operations_handoff_policy", "release_operations_runbook", "operator_handoff_matrix", "operator_handoff_packet", "claim_boundary_attestation", "release_operations_audit_bundle"}}
    paths["summary_json"].write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["policy_json"].write_text(json.dumps(audit["release_operations_handoff_policy"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["runbook_json"].write_text(json.dumps(audit["release_operations_runbook"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["handoff_matrix_json"].write_text(json.dumps(audit["operator_handoff_matrix"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["handoff_packet_json"].write_text(json.dumps(audit["operator_handoff_packet"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["claim_boundary_json"].write_text(json.dumps(audit["claim_boundary_attestation"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["audit_bundle_json"].write_text(json.dumps(audit["release_operations_audit_bundle"], indent=2, ensure_ascii=False), encoding="utf-8")
    _write_handoff_matrix_csv(paths["handoff_matrix_csv"], audit["operator_handoff_matrix"].get("decisions", []))
    _write_handoff_packet_csv(paths["handoff_packet_csv"], audit["operator_handoff_packet"].get("packets", []))
    paths["markdown_report"].write_text(_markdown_report(audit), encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}


def _write_handoff_matrix_csv(path: Path, decisions: list[dict[str, Any]]) -> None:
    fieldnames = ["handoff_id", "operator_role", "accepted_for_local_release_ops", "handoff_packet_id", "local_operator_signature_id", "support_window_id", "missing_runbook_sections", "reason_codes"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for decision in decisions:
            row = {field: decision.get(field) for field in fieldnames}
            row["missing_runbook_sections"] = " | ".join(str(section) for section in decision.get("missing_runbook_sections", []))
            row["reason_codes"] = " | ".join(str(reason) for reason in decision.get("reason_codes", []))
            writer.writerow(row)


def _write_handoff_packet_csv(path: Path, packets: list[dict[str, Any]]) -> None:
    fieldnames = ["handoff_packet_id", "operator_role", "artifact_sha256", "runbook_sha256", "local_operator_signature_id", "support_window_id", "handoff_packet_sha256"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for packet in packets:
            writer.writerow({field: packet.get(field) for field in fieldnames})


def _markdown_report(audit: dict[str, Any]) -> str:
    answer = audit["direct_answer"]
    lines = [
        "# BioGPU-Core v5.48 Release Operations Handoff Contract",
        "",
        "## Direct Answer",
        "",
        f"- Release operations handoff contract added: `{answer['did_we_add_release_operations_handoff_contract']}`",
        f"- Release runbook validated: `{answer['did_we_validate_release_runbook']}`",
        f"- Operator handoff checklist validated: `{answer['did_we_validate_operator_handoff_checklist']}`",
        f"- More layers needed before production and OS: `{answer['do_we_still_need_many_layers_before_production_and_os']}`",
        f"- Production release ready: `{answer['is_production_release_ready']}`",
        f"- Production operations ready: `{answer['is_production_operations_ready']}`",
        f"- Full BioSDK ready: `{answer['is_full_biosdk_ready']}`",
        f"- BioCompute Runtime ready: `{answer['is_biocompute_runtime_ready']}`",
        f"- BiC OS ready: `{answer['is_bic_os_ready']}`",
        f"- Next best build step: {answer['next_best_build_step']}",
        "",
        "## Proof Summary",
        "",
        f"- Overall status: `{audit['overall_status']}`",
        f"- v5.47 dependency ready: `{audit['v547_dependency_ready']}`",
        f"- Release operations runbook ready: `{audit['release_operations_runbook_ready']}`",
        f"- Operator handoff matrix ready: `{audit['operator_handoff_matrix_ready']}`",
        f"- Operator handoff packet ready: `{audit['operator_handoff_packet_ready']}`",
        f"- Claim boundary attestation ready: `{audit['claim_boundary_attestation_ready']}`",
        f"- Accepted operator handoffs: `{audit['accepted_operator_handoff_count']}`",
        f"- Denied operator handoffs: `{audit['denied_operator_handoff_count']}`",
        "",
        "## Missing Real Inputs",
        "",
    ]
    for missing in audit["missing_real_inputs"]:
        lines.append(f"- {missing}")
    lines.extend(["", "## Boundary", "", audit["claim_boundary"], ""])
    return "\n".join(lines)