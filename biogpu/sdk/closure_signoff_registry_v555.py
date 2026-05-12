"""Closure attestation audit trail and external reviewer signoff registry proof, v5.55."""
from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from biogpu.beta.job_model_v43 import utc_now_iso
from biogpu.evidence.ledger_v53 import stable_hash
from biogpu.sdk.remediation_evidence_closure_v554 import run_remediation_evidence_closure_workflow_v554


DEFAULT_OUT = Path("outputs/v555_closure_signoff_registry")
SIGNOFF_REGISTRY_RECORD_TYPES_V555 = (
    "closure_attestation_record",
    "external_reviewer_identity_record",
    "external_reviewer_recheck_record",
    "external_reviewer_signoff_manifest",
    "remediation_owner_attestation_record",
    "closure_signature_manifest",
    "immutable_closure_transcript_anchor",
    "partner_dataroom_access_anchor",
    "external_security_signoff_anchor",
    "claim_boundary_attestation_anchor",
)
SIGNOFF_AUDIT_EVENT_TYPES_V555 = (
    "registry_record_created",
    "dependency_anchor_verified",
    "reviewer_identity_checked",
    "reviewer_recheck_required",
    "owner_attestation_required",
    "closure_signature_required",
    "claim_boundary_confirmed",
    "real_signoff_denied",
)
LOCAL_SIGNOFF_STAGES_V555 = ("audit_trail_assembly", "signoff_registry_packet", "signoff_registry_preflight")


@dataclass(frozen=True)
class ClosureSignoffRegistryPolicyV555:
    policy_id: str
    signoff_registry_record_types: tuple[str, ...]
    signoff_audit_event_types: tuple[str, ...]
    local_signoff_stages: tuple[str, ...]
    requires_v554_closure_attestation: bool
    requires_signoff_registry_matrix: bool
    requires_closure_signoff_audit_trail: bool
    requires_external_reviewer_identity: bool
    requires_external_reviewer_signoff: bool
    requires_immutable_closure_transcript: bool
    local_contract_only: bool = True
    real_external_reviewer_signoff_ready: bool = False
    real_closure_signoff_ready: bool = False
    real_review_finding_closure_ready: bool = False
    real_external_review_ready: bool = False
    real_external_pilot_ready: bool = False
    production_ready: bool = False
    full_biosdk_ready: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SignoffRegistryRecordFixtureV555:
    record_id: str
    record_type: str
    signoff_domain: str
    has_v554_anchor: bool
    has_local_registry_reference: bool
    has_audit_event_chain: bool
    has_claim_boundary_ack: bool
    has_external_reviewer_identity: bool
    has_external_reviewer_recheck: bool
    has_external_reviewer_signoff: bool
    has_immutable_closure_transcript: bool
    requests_external_reviewer_signoff: bool
    requests_review_finding_closure: bool
    requests_external_review_completion: bool
    requests_real_external_pilot: bool
    requests_production_release: bool
    requests_bic_os_unlock: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SignoffRegistryRecordDecisionV555:
    record_id: str
    record_type: str
    signoff_domain: str
    local_signoff_registry_record_ready: bool
    local_audit_trail_ready: bool
    real_external_reviewer_signoff_ready: bool
    real_closure_signoff_ready: bool
    review_finding_closed: bool
    reason_codes: tuple[str, ...]
    local_anchor: str | None
    real_review_finding_closure_ready: bool = False
    real_external_review_ready: bool = False
    real_external_pilot_ready: bool = False
    production_ready: bool = False
    full_biosdk_ready: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SignoffRegistryGateFixtureV555:
    gate_id: str
    has_v554_closure_attestation: bool
    has_signoff_registry_matrix: bool
    has_closure_signoff_audit_trail: bool
    has_signoff_packet: bool
    has_claim_boundary_ack: bool
    has_external_reviewer_identity: bool
    has_external_reviewer_recheck: bool
    has_external_reviewer_signoff: bool
    has_immutable_closure_transcript: bool
    requests_external_reviewer_signoff: bool
    requests_review_finding_closure: bool
    requests_external_review_completion: bool
    requests_real_external_pilot: bool
    requests_production_release: bool
    requests_bic_os_unlock: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SignoffRegistryGateDecisionV555:
    gate_id: str
    accepted_for_local_signoff_stage: bool
    reason_codes: tuple[str, ...]
    local_signoff_record_id: str | None
    real_external_reviewer_signoff_ready: bool = False
    real_closure_signoff_ready: bool = False
    real_review_finding_closure_ready: bool = False
    real_external_review_ready: bool = False
    real_external_pilot_ready: bool = False
    production_release_ready: bool = False
    full_biosdk_ready: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_closure_signoff_registry_policy_v555() -> dict[str, Any]:
    policy = ClosureSignoffRegistryPolicyV555(
        policy_id="BIOGPU_CORE_V555_CLOSURE_SIGNOFF_REGISTRY_POLICY",
        signoff_registry_record_types=SIGNOFF_REGISTRY_RECORD_TYPES_V555,
        signoff_audit_event_types=SIGNOFF_AUDIT_EVENT_TYPES_V555,
        local_signoff_stages=LOCAL_SIGNOFF_STAGES_V555,
        requires_v554_closure_attestation=True,
        requires_signoff_registry_matrix=True,
        requires_closure_signoff_audit_trail=True,
        requires_external_reviewer_identity=True,
        requires_external_reviewer_signoff=True,
        requires_immutable_closure_transcript=True,
    )
    result = {
        "version": "v5.55",
        "closure_signoff_registry_policy_ready": True,
        "policy": policy.to_dict(),
        "blocked_modes": ["real_external_reviewer_signoff", "real_closure_signoff", "real_review_finding_closure", "real_external_review", "real_external_pilot", "production_release", "production_ready_claim", "bic_os_unlock"],
        "required_real_records": ["external_reviewer_identity", "external_reviewer_recheck", "external_reviewer_signoff", "immutable_closure_transcript", "signed_closure_timestamp"],
        "real_external_reviewer_signoff_ready": False,
        "real_closure_signoff_ready": False,
        "real_review_finding_closure_ready": False,
        "real_external_review_ready": False,
        "real_external_pilot_ready": False,
        "production_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    result["closure_signoff_registry_policy_sha256"] = stable_hash(result)
    return result


def default_signoff_registry_record_fixtures_v555() -> list[SignoffRegistryRecordFixtureV555]:
    domain_by_type = {
        "closure_attestation_record": "closure_attestation",
        "external_reviewer_identity_record": "reviewer_identity",
        "external_reviewer_recheck_record": "reviewer_recheck",
        "external_reviewer_signoff_manifest": "reviewer_signoff",
        "remediation_owner_attestation_record": "owner_attestation",
        "closure_signature_manifest": "closure_signature",
        "immutable_closure_transcript_anchor": "closure_transcript",
        "partner_dataroom_access_anchor": "partner_dataroom",
        "external_security_signoff_anchor": "security_signoff",
        "claim_boundary_attestation_anchor": "claim_boundary",
    }
    return [
        SignoffRegistryRecordFixtureV555(
            record_id=f"signoff-registry-{record_type}",
            record_type=record_type,
            signoff_domain=domain_by_type[record_type],
            has_v554_anchor=True,
            has_local_registry_reference=True,
            has_audit_event_chain=True,
            has_claim_boundary_ack=True,
            has_external_reviewer_identity=False,
            has_external_reviewer_recheck=False,
            has_external_reviewer_signoff=False,
            has_immutable_closure_transcript=False,
            requests_external_reviewer_signoff=record_type == "external_reviewer_signoff_manifest",
            requests_review_finding_closure=record_type == "closure_signature_manifest",
            requests_external_review_completion=record_type == "external_security_signoff_anchor",
            requests_real_external_pilot=record_type == "external_reviewer_recheck_record",
            requests_production_release=record_type == "partner_dataroom_access_anchor",
            requests_bic_os_unlock=record_type == "claim_boundary_attestation_anchor",
        )
        for record_type in SIGNOFF_REGISTRY_RECORD_TYPES_V555
    ]


def evaluate_signoff_registry_record_v555(fixture: SignoffRegistryRecordFixtureV555, v554_dependency: dict[str, Any]) -> SignoffRegistryRecordDecisionV555:
    reasons: list[str] = []
    if v554_dependency.get("remediation_evidence_closure_contract_ready") is not True or not fixture.has_v554_anchor:
        reasons.append("v554_closure_attestation_missing")
    if fixture.record_type not in SIGNOFF_REGISTRY_RECORD_TYPES_V555:
        reasons.append("signoff_registry_record_type_not_allowed")
    if not fixture.has_local_registry_reference:
        reasons.append("local_registry_reference_missing")
    if not fixture.has_audit_event_chain:
        reasons.append("audit_event_chain_missing")
    if not fixture.has_claim_boundary_ack:
        reasons.append("claim_boundary_ack_missing")
    local_ready = not any(reason in reasons for reason in {"v554_closure_attestation_missing", "signoff_registry_record_type_not_allowed", "local_registry_reference_missing", "audit_event_chain_missing", "claim_boundary_ack_missing"})
    if not fixture.has_external_reviewer_identity:
        reasons.append("external_reviewer_identity_missing")
    if not fixture.has_external_reviewer_recheck:
        reasons.append("external_reviewer_recheck_missing")
    if not fixture.has_external_reviewer_signoff:
        reasons.append("external_reviewer_signoff_missing")
    if not fixture.has_immutable_closure_transcript:
        reasons.append("immutable_closure_transcript_missing")
    if fixture.requests_external_reviewer_signoff:
        reasons.append("real_external_reviewer_signoff_not_ready")
    if fixture.requests_review_finding_closure:
        reasons.append("real_closure_signoff_not_ready")
        reasons.append("real_review_finding_closure_not_ready")
    if fixture.requests_external_review_completion:
        reasons.append("real_external_review_not_ready")
    if fixture.requests_real_external_pilot:
        reasons.append("real_external_pilot_not_ready")
    if fixture.requests_production_release:
        reasons.append("production_release_not_allowed")
    if fixture.requests_bic_os_unlock:
        reasons.append("bic_os_unlock_not_allowed")
    return SignoffRegistryRecordDecisionV555(
        record_id=fixture.record_id,
        record_type=fixture.record_type,
        signoff_domain=fixture.signoff_domain,
        local_signoff_registry_record_ready=local_ready,
        local_audit_trail_ready=local_ready and fixture.has_audit_event_chain,
        real_external_reviewer_signoff_ready=False,
        real_closure_signoff_ready=False,
        review_finding_closed=False,
        reason_codes=tuple(reasons or ["review_finding_closed"]),
        local_anchor=str(v554_dependency.get("remediation_evidence_closure_audit_sha256") or "") or None,
    )


def build_signoff_registry_matrix_v555(v554_dependency: dict[str, Any], fixtures: list[SignoffRegistryRecordFixtureV555] | None = None) -> dict[str, Any]:
    registry_fixtures = fixtures or default_signoff_registry_record_fixtures_v555()
    decisions = [evaluate_signoff_registry_record_v555(fixture, v554_dependency).to_dict() for fixture in registry_fixtures]
    reason_codes = sorted({reason for decision in decisions for reason in decision["reason_codes"]})
    required_reasons = {
        "external_reviewer_identity_missing",
        "external_reviewer_recheck_missing",
        "external_reviewer_signoff_missing",
        "immutable_closure_transcript_missing",
        "real_external_reviewer_signoff_not_ready",
        "real_closure_signoff_not_ready",
        "real_review_finding_closure_not_ready",
        "real_external_review_not_ready",
        "real_external_pilot_not_ready",
        "production_release_not_allowed",
        "bic_os_unlock_not_allowed",
    }
    local_ready_count = sum(1 for decision in decisions if decision["local_signoff_registry_record_ready"])
    audit_ready_count = sum(1 for decision in decisions if decision["local_audit_trail_ready"])
    matrix = {
        "version": "v5.55",
        "signoff_registry_matrix_ready": local_ready_count == len(SIGNOFF_REGISTRY_RECORD_TYPES_V555) and audit_ready_count == len(SIGNOFF_REGISTRY_RECORD_TYPES_V555) and required_reasons.issubset(set(reason_codes)),
        "signoff_registry_record_count": len(decisions),
        "local_signoff_registry_record_ready_count": local_ready_count,
        "local_audit_trail_ready_count": audit_ready_count,
        "real_external_reviewer_signoff_ready_count": sum(1 for decision in decisions if decision["real_external_reviewer_signoff_ready"]),
        "real_closure_signoff_ready_count": sum(1 for decision in decisions if decision["real_closure_signoff_ready"]),
        "review_finding_closed_count": sum(1 for decision in decisions if decision["review_finding_closed"]),
        "record_types": sorted({decision["record_type"] for decision in decisions}),
        "reason_codes": reason_codes,
        "fixtures": [fixture.to_dict() for fixture in registry_fixtures],
        "decisions": decisions,
        "real_external_reviewer_signoff_ready": False,
        "real_closure_signoff_ready": False,
        "real_review_finding_closure_ready": False,
        "real_external_review_ready": False,
        "real_external_pilot_ready": False,
        "production_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    matrix["signoff_registry_matrix_sha256"] = stable_hash(matrix)
    return matrix


def build_closure_signoff_audit_trail_v555(v554_dependency: dict[str, Any], registry_matrix: dict[str, Any]) -> dict[str, Any]:
    events: list[dict[str, Any]] = []
    for decision in registry_matrix.get("decisions", []):
        if decision.get("local_audit_trail_ready") is not True:
            continue
        for event_type in SIGNOFF_AUDIT_EVENT_TYPES_V555:
            event = {
                "version": "v5.55",
                "event_id": f"audit-{decision['record_id']}-{event_type}",
                "event_type": event_type,
                "record_id": decision.get("record_id"),
                "record_type": decision.get("record_type"),
                "v554_closure_anchor": v554_dependency.get("remediation_evidence_closure_audit_sha256"),
                "signoff_registry_anchor": registry_matrix.get("signoff_registry_matrix_sha256"),
                "local_audit_event_ready": True,
                "real_external_reviewer_signoff_present": False,
                "real_closure_signoff_present": False,
                "created_at": utc_now_iso(),
            }
            event["audit_event_sha256"] = stable_hash(event)
            events.append(event)
    trail = {
        "version": "v5.55",
        "closure_signoff_audit_trail_ready": len(events) == len(SIGNOFF_REGISTRY_RECORD_TYPES_V555) * len(SIGNOFF_AUDIT_EVENT_TYPES_V555) and registry_matrix.get("signoff_registry_matrix_ready") is True,
        "audit_event_count": len(events),
        "audit_event_type_count": len(SIGNOFF_AUDIT_EVENT_TYPES_V555),
        "local_audit_event_ready_count": sum(1 for event in events if event["local_audit_event_ready"]),
        "real_external_reviewer_signoff_count": sum(1 for event in events if event["real_external_reviewer_signoff_present"]),
        "real_closure_signoff_count": sum(1 for event in events if event["real_closure_signoff_present"]),
        "events": events,
        "real_external_reviewer_signoff_ready": False,
        "real_closure_signoff_ready": False,
        "real_review_finding_closure_ready": False,
        "real_external_review_ready": False,
        "real_external_pilot_ready": False,
        "production_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    trail["closure_signoff_audit_trail_sha256"] = stable_hash(trail)
    return trail


def build_external_reviewer_signoff_packet_v555(v554_dependency: dict[str, Any], registry_matrix: dict[str, Any], audit_trail: dict[str, Any]) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for decision in registry_matrix.get("decisions", []):
        if decision.get("local_signoff_registry_record_ready") is not True:
            continue
        record = {
            "version": "v5.55",
            "signoff_packet_record_id": f"signoff-packet-{decision['record_id']}",
            "record_type": decision.get("record_type"),
            "signoff_domain": decision.get("signoff_domain"),
            "v554_closure_anchor": v554_dependency.get("remediation_evidence_closure_audit_sha256"),
            "registry_matrix_anchor": registry_matrix.get("signoff_registry_matrix_sha256"),
            "audit_trail_anchor": audit_trail.get("closure_signoff_audit_trail_sha256"),
            "local_signoff_packet_record_ready": True,
            "external_reviewer_identity_present": False,
            "external_reviewer_recheck_present": False,
            "external_reviewer_signoff_present": False,
            "immutable_closure_transcript_present": False,
            "real_external_reviewer_signoff_ready": False,
            "real_closure_signoff_ready": False,
            "review_finding_closed": False,
            "real_external_review_ready": False,
            "real_external_pilot_ready": False,
            "production_ready": False,
            "created_at": utc_now_iso(),
        }
        record["signoff_packet_record_sha256"] = stable_hash(record)
        records.append(record)
    packet = {
        "version": "v5.55",
        "external_reviewer_signoff_packet_ready": len(records) == len(SIGNOFF_REGISTRY_RECORD_TYPES_V555) and audit_trail.get("closure_signoff_audit_trail_ready") is True,
        "signoff_packet_record_count": len(records),
        "local_signoff_packet_record_ready_count": sum(1 for record in records if record["local_signoff_packet_record_ready"]),
        "real_external_reviewer_signoff_ready_count": sum(1 for record in records if record["real_external_reviewer_signoff_ready"]),
        "real_closure_signoff_ready_count": sum(1 for record in records if record["real_closure_signoff_ready"]),
        "review_finding_closed_count": sum(1 for record in records if record["review_finding_closed"]),
        "signoff_packet_records": records,
        "real_external_reviewer_signoff_ready": False,
        "real_closure_signoff_ready": False,
        "real_review_finding_closure_ready": False,
        "real_external_review_ready": False,
        "real_external_pilot_ready": False,
        "production_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    packet["external_reviewer_signoff_packet_sha256"] = stable_hash(packet)
    return packet


def default_signoff_registry_gate_fixtures_v555() -> list[SignoffRegistryGateFixtureV555]:
    return [
        SignoffRegistryGateFixtureV555("audit-trail-assembly", True, True, True, True, True, True, True, True, True, False, False, False, False, False, False),
        SignoffRegistryGateFixtureV555("signoff-registry-packet", True, True, True, True, True, True, True, True, True, False, False, False, False, False, False),
        SignoffRegistryGateFixtureV555("signoff-registry-preflight", True, True, True, True, True, True, True, True, True, False, False, False, False, False, False),
        SignoffRegistryGateFixtureV555("missing-v554-contract", False, True, True, True, True, True, True, True, True, False, False, False, False, False, False),
        SignoffRegistryGateFixtureV555("missing-registry-matrix", True, False, True, True, True, True, True, True, True, False, False, False, False, False, False),
        SignoffRegistryGateFixtureV555("missing-audit-trail", True, True, False, True, True, True, True, True, True, False, False, False, False, False, False),
        SignoffRegistryGateFixtureV555("missing-signoff-packet", True, True, True, False, True, True, True, True, True, False, False, False, False, False, False),
        SignoffRegistryGateFixtureV555("missing-claim-boundary", True, True, True, True, False, True, True, True, True, False, False, False, False, False, False),
        SignoffRegistryGateFixtureV555("missing-real-signoff", True, True, True, True, True, False, False, False, False, True, True, False, False, False, False),
        SignoffRegistryGateFixtureV555("external-review-completion-request", True, True, True, True, True, True, True, True, True, False, False, True, False, False, False),
        SignoffRegistryGateFixtureV555("real-pilot-request", True, True, True, True, True, True, True, True, True, False, False, False, True, False, False),
        SignoffRegistryGateFixtureV555("production-release-request", True, True, True, True, True, True, True, True, True, False, False, False, False, True, False),
        SignoffRegistryGateFixtureV555("bic-os-unlock-request", True, True, True, True, True, True, True, True, True, False, False, False, False, False, True),
    ]


def evaluate_signoff_registry_gate_v555(fixture: SignoffRegistryGateFixtureV555, v554_dependency: dict[str, Any], registry_matrix: dict[str, Any], audit_trail: dict[str, Any], signoff_packet: dict[str, Any]) -> SignoffRegistryGateDecisionV555:
    reasons: list[str] = []
    if v554_dependency.get("remediation_evidence_closure_contract_ready") is not True or not fixture.has_v554_closure_attestation:
        reasons.append("v554_closure_attestation_missing")
    if registry_matrix.get("signoff_registry_matrix_ready") is not True or not fixture.has_signoff_registry_matrix:
        reasons.append("signoff_registry_matrix_missing")
    if audit_trail.get("closure_signoff_audit_trail_ready") is not True or not fixture.has_closure_signoff_audit_trail:
        reasons.append("closure_signoff_audit_trail_missing")
    if signoff_packet.get("external_reviewer_signoff_packet_ready") is not True or not fixture.has_signoff_packet:
        reasons.append("external_reviewer_signoff_packet_missing")
    if not fixture.has_claim_boundary_ack:
        reasons.append("claim_boundary_ack_missing")
    if fixture.requests_external_reviewer_signoff or fixture.requests_review_finding_closure:
        if not fixture.has_external_reviewer_identity:
            reasons.append("external_reviewer_identity_missing")
        if not fixture.has_external_reviewer_recheck:
            reasons.append("external_reviewer_recheck_missing")
        if not fixture.has_external_reviewer_signoff:
            reasons.append("external_reviewer_signoff_missing")
        if not fixture.has_immutable_closure_transcript:
            reasons.append("immutable_closure_transcript_missing")
        reasons.append("real_external_reviewer_signoff_not_ready")
    if fixture.requests_review_finding_closure:
        reasons.append("real_closure_signoff_not_ready")
        reasons.append("real_review_finding_closure_not_ready")
    if fixture.requests_external_review_completion:
        reasons.append("real_external_review_not_ready")
    if fixture.requests_real_external_pilot:
        reasons.append("real_external_pilot_not_ready")
    if fixture.requests_production_release:
        reasons.append("production_release_not_allowed")
    if fixture.requests_bic_os_unlock:
        reasons.append("bic_os_unlock_not_allowed")
    accepted = not reasons
    return SignoffRegistryGateDecisionV555(fixture.gate_id, accepted, tuple(reasons or ["local_signoff_stage_accepted"]), f"local-signoff-{fixture.gate_id}" if accepted else None)


def run_signoff_registry_gate_v555(v554_dependency: dict[str, Any], registry_matrix: dict[str, Any], audit_trail: dict[str, Any], signoff_packet: dict[str, Any], fixtures: list[SignoffRegistryGateFixtureV555] | None = None) -> dict[str, Any]:
    gate_fixtures = fixtures or default_signoff_registry_gate_fixtures_v555()
    decisions = [evaluate_signoff_registry_gate_v555(fixture, v554_dependency, registry_matrix, audit_trail, signoff_packet).to_dict() for fixture in gate_fixtures]
    reason_codes = sorted({reason for decision in decisions for reason in decision["reason_codes"]})
    required_denials = {
        "v554_closure_attestation_missing",
        "signoff_registry_matrix_missing",
        "closure_signoff_audit_trail_missing",
        "external_reviewer_signoff_packet_missing",
        "claim_boundary_ack_missing",
        "external_reviewer_identity_missing",
        "external_reviewer_recheck_missing",
        "external_reviewer_signoff_missing",
        "immutable_closure_transcript_missing",
        "real_external_reviewer_signoff_not_ready",
        "real_closure_signoff_not_ready",
        "real_review_finding_closure_not_ready",
        "real_external_review_not_ready",
        "real_external_pilot_not_ready",
        "production_release_not_allowed",
        "bic_os_unlock_not_allowed",
    }
    accepted_count = sum(1 for decision in decisions if decision["accepted_for_local_signoff_stage"])
    denied_count = len(decisions) - accepted_count
    gate = {
        "version": "v5.55",
        "signoff_registry_gate_ready": accepted_count == len(LOCAL_SIGNOFF_STAGES_V555) and denied_count == 10 and required_denials.issubset(set(reason_codes)),
        "gate_fixture_count": len(gate_fixtures),
        "accepted_local_signoff_stage_count": accepted_count,
        "denied_signoff_registry_gate_count": denied_count,
        "reason_codes": reason_codes,
        "fixtures": [fixture.to_dict() for fixture in gate_fixtures],
        "decisions": decisions,
        "real_external_reviewer_signoff_ready": False,
        "real_closure_signoff_ready": False,
        "real_review_finding_closure_ready": False,
        "real_external_review_ready": False,
        "real_external_pilot_ready": False,
        "production_release_ready": False,
        "production_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    gate["signoff_registry_gate_sha256"] = stable_hash(gate)
    return gate


def build_signoff_registry_blocker_register_v555(registry_matrix: dict[str, Any], signoff_gate: dict[str, Any]) -> dict[str, Any]:
    blockers: list[dict[str, Any]] = []
    for decision in registry_matrix.get("decisions", []):
        if decision.get("review_finding_closed") is not True:
            blockers.append({"version": "v5.55", "blocker_id": f"signoff-registry-blocker-{decision['record_id']}", "source": "signoff_registry_matrix", "record_id": decision.get("record_id"), "reason_codes": decision.get("reason_codes", []), "must_be_resolved_before_external_reviewer_signoff": True, "must_be_resolved_before_closure_signoff": True, "must_be_resolved_before_review_closure": True, "must_be_resolved_before_external_review": True, "must_be_resolved_before_real_pilot": True, "must_be_resolved_before_production": True, "must_be_resolved_before_bic_os": True})
    for decision in signoff_gate.get("decisions", []):
        if decision.get("accepted_for_local_signoff_stage") is not True:
            blockers.append({"version": "v5.55", "blocker_id": f"signoff-gate-blocker-{decision['gate_id']}", "source": "signoff_registry_gate", "record_id": decision.get("gate_id"), "reason_codes": decision.get("reason_codes", []), "must_be_resolved_before_external_reviewer_signoff": True, "must_be_resolved_before_closure_signoff": True, "must_be_resolved_before_review_closure": True, "must_be_resolved_before_external_review": True, "must_be_resolved_before_real_pilot": True, "must_be_resolved_before_production": True, "must_be_resolved_before_bic_os": True})
    for blocker in blockers:
        blocker["blocker_sha256"] = stable_hash(blocker)
    register = {
        "version": "v5.55",
        "signoff_registry_blocker_register_ready": len(blockers) == len(SIGNOFF_REGISTRY_RECORD_TYPES_V555) + 10,
        "blocker_count": len(blockers),
        "blockers": blockers,
        "real_external_reviewer_signoff_ready": False,
        "real_closure_signoff_ready": False,
        "real_review_finding_closure_ready": False,
        "real_external_review_ready": False,
        "real_external_pilot_ready": False,
        "production_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    register["signoff_registry_blocker_register_sha256"] = stable_hash(register)
    return register


def build_closure_signoff_registry_audit_bundle_v555(policy: dict[str, Any], registry_matrix: dict[str, Any], audit_trail: dict[str, Any], signoff_packet: dict[str, Any], signoff_gate: dict[str, Any], blocker_register: dict[str, Any]) -> dict[str, Any]:
    bundle_ready = policy.get("closure_signoff_registry_policy_ready") is True and registry_matrix.get("signoff_registry_matrix_ready") is True and audit_trail.get("closure_signoff_audit_trail_ready") is True and signoff_packet.get("external_reviewer_signoff_packet_ready") is True and signoff_gate.get("signoff_registry_gate_ready") is True and blocker_register.get("signoff_registry_blocker_register_ready") is True
    bundle = {
        "version": "v5.55",
        "closure_signoff_registry_audit_bundle_ready": bundle_ready,
        "policy_sha256": policy.get("closure_signoff_registry_policy_sha256"),
        "registry_matrix_sha256": registry_matrix.get("signoff_registry_matrix_sha256"),
        "audit_trail_sha256": audit_trail.get("closure_signoff_audit_trail_sha256"),
        "signoff_packet_sha256": signoff_packet.get("external_reviewer_signoff_packet_sha256"),
        "signoff_gate_sha256": signoff_gate.get("signoff_registry_gate_sha256"),
        "blocker_register_sha256": blocker_register.get("signoff_registry_blocker_register_sha256"),
        "real_external_reviewer_signoff_ready": False,
        "real_closure_signoff_ready": False,
        "real_review_finding_closure_ready": False,
        "real_external_review_ready": False,
        "real_external_pilot_ready": False,
        "production_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    bundle["closure_signoff_registry_audit_bundle_sha256"] = stable_hash(bundle)
    return bundle


def run_closure_signoff_registry_workflow_v555(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    project_root = Path(root).resolve()
    out = project_root / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    v554_dependency = run_remediation_evidence_closure_workflow_v554(project_root, out.parent / "d555")
    policy = build_closure_signoff_registry_policy_v555()
    registry_matrix = build_signoff_registry_matrix_v555(v554_dependency)
    audit_trail = build_closure_signoff_audit_trail_v555(v554_dependency, registry_matrix)
    signoff_packet = build_external_reviewer_signoff_packet_v555(v554_dependency, registry_matrix, audit_trail)
    signoff_gate = run_signoff_registry_gate_v555(v554_dependency, registry_matrix, audit_trail, signoff_packet)
    blocker_register = build_signoff_registry_blocker_register_v555(registry_matrix, signoff_gate)
    audit_bundle = build_closure_signoff_registry_audit_bundle_v555(policy, registry_matrix, audit_trail, signoff_packet, signoff_gate, blocker_register)
    proof_ready = v554_dependency.get("remediation_evidence_closure_contract_ready") is True and policy.get("closure_signoff_registry_policy_ready") is True and registry_matrix.get("signoff_registry_matrix_ready") is True and audit_trail.get("closure_signoff_audit_trail_ready") is True and signoff_packet.get("external_reviewer_signoff_packet_ready") is True and signoff_gate.get("signoff_registry_gate_ready") is True and blocker_register.get("signoff_registry_blocker_register_ready") is True and audit_bundle.get("closure_signoff_registry_audit_bundle_ready") is True
    audit = {
        "version": "v5.55",
        "phase": "closure_attestation_audit_trail_external_reviewer_signoff_registry_contract",
        "overall_status": "closure_signoff_registry_contract_ready_signoff_not_claimed" if proof_ready else "closure_signoff_registry_contract_incomplete",
        "active_phase": "biosdk_closure_signoff_registry_proof",
        "bic_os_phase_locked": True,
        "closure_signoff_registry_contract_ready": proof_ready,
        "v554_dependency_ready": v554_dependency.get("remediation_evidence_closure_contract_ready") is True,
        "closure_signoff_registry_policy_ready": policy.get("closure_signoff_registry_policy_ready") is True,
        "signoff_registry_matrix_ready": registry_matrix.get("signoff_registry_matrix_ready") is True,
        "closure_signoff_audit_trail_ready": audit_trail.get("closure_signoff_audit_trail_ready") is True,
        "external_reviewer_signoff_packet_ready": signoff_packet.get("external_reviewer_signoff_packet_ready") is True,
        "signoff_registry_gate_ready": signoff_gate.get("signoff_registry_gate_ready") is True,
        "signoff_registry_blocker_register_ready": blocker_register.get("signoff_registry_blocker_register_ready") is True,
        "closure_signoff_registry_audit_bundle_ready": audit_bundle.get("closure_signoff_registry_audit_bundle_ready") is True,
        "artifact_name": v554_dependency.get("artifact_name"),
        "artifact_sha256": v554_dependency.get("artifact_sha256"),
        "signoff_registry_record_count": registry_matrix.get("signoff_registry_record_count"),
        "local_signoff_registry_record_ready_count": registry_matrix.get("local_signoff_registry_record_ready_count"),
        "local_audit_trail_ready_count": registry_matrix.get("local_audit_trail_ready_count"),
        "audit_event_count": audit_trail.get("audit_event_count"),
        "signoff_packet_record_count": signoff_packet.get("signoff_packet_record_count"),
        "real_external_reviewer_signoff_ready_count": registry_matrix.get("real_external_reviewer_signoff_ready_count"),
        "real_closure_signoff_ready_count": registry_matrix.get("real_closure_signoff_ready_count"),
        "review_finding_closed_count": registry_matrix.get("review_finding_closed_count"),
        "accepted_local_signoff_stage_count": signoff_gate.get("accepted_local_signoff_stage_count"),
        "denied_signoff_registry_gate_count": signoff_gate.get("denied_signoff_registry_gate_count"),
        "signoff_registry_blocker_count": blocker_register.get("blocker_count"),
        "real_external_reviewer_signoff_ready": False,
        "real_closure_signoff_ready": False,
        "real_review_finding_closure_ready": False,
        "real_external_review_ready": False,
        "real_external_pilot_ready": False,
        "production_ready": False,
        "production_release_ready": False,
        "production_operations_ready": False,
        "live_private_registry_ready": False,
        "private_registry_ready": False,
        "public_registry_ready": False,
        "production_distribution_ready": False,
        "production_runtime_ready": False,
        "production_api_ready": False,
        "production_biocompute_runtime_ready": False,
        "full_biosdk_ready": False,
        "live_actuation_enabled": False,
        "closure_signoff_registry_policy": policy,
        "signoff_registry_matrix": registry_matrix,
        "closure_signoff_audit_trail": audit_trail,
        "external_reviewer_signoff_packet": signoff_packet,
        "signoff_registry_gate": signoff_gate,
        "signoff_registry_blocker_register": blocker_register,
        "closure_signoff_registry_audit_bundle": audit_bundle,
        "v554_dependency_summary": {key: value for key, value in v554_dependency.items() if key not in {"remediation_evidence_closure_policy", "remediation_evidence_matrix", "closure_attestation_packet", "closure_attestation_gate", "closure_attestation_blocker_register", "remediation_evidence_closure_audit_bundle", "v553_dependency_summary"}},
        "missing_real_inputs": ["real external reviewer identity record", "real external reviewer recheck record", "external reviewer signed signoff manifest", "immutable closure transcript", "signed closure timestamp and owner attestation", "real partner data-room access logs", "signed partner data-use approval", "external security review signoff", "production identity-provider approval", "live registry administrative approval", "trusted signing authority approval", "production CI/CD and rollback/yank acceptance"],
        "remaining_runtime_blockers": ["production identity provider integration and persistent tenant membership", "production object storage and audit retention backend", "hosted dashboard server and browser session enforcement", "real external read-only API credentials or partner exports", "lab-approved live telemetry and closed-loop approval workflow", "durable BioCompute Runtime daemon and OS service supervision"],
        "production_distance_assessment": {"distance": "far", "reason": "the proof ladder has validated local contracts and artifacts, but production still needs real external reviewer signoff, pilot acceptance, production identity/storage/registry/CI services, hosted API/dashboard enforcement and operational runtime supervision", "minimum_missing_evidence_families": 6},
        "bic_os_distance_assessment": {"distance": "very_far", "reason": "BiC OS remains after full BioSDK, production BioCompute Runtime, NSI/control-plane maturity, durable daemon scheduling, permissions, service supervision and real-world validation", "bic_os_phase_locked": True},
        "direct_answer": {"did_we_add_closure_signoff_audit_trail": "yes" if audit_trail.get("closure_signoff_audit_trail_ready") else "no", "did_we_add_external_reviewer_signoff_registry": "yes" if registry_matrix.get("signoff_registry_matrix_ready") else "no", "are_real_external_reviewer_signoffs_ready": "no", "are_real_closure_signoffs_ready": "no", "are_real_review_findings_closed": "no", "is_real_external_review_ready": "no", "is_real_external_pilot_ready": "no", "is_production_ready": "no_far", "is_full_biosdk_ready": "no", "is_biocompute_runtime_ready": "no", "is_bic_os_ready": "no_very_far", "next_best_build_step": "add real external signoff intake contract and signed closure transcript acceptance gate" if proof_ready else "fix v5.55 signoff-registry blockers first"},
        "claim_boundary": "v5.55 proves a local closure attestation audit trail, external reviewer signoff registry matrix, signoff packet shape and signoff-registry preflight gate over the v5.54 remediation evidence closure contract. It does not claim real external reviewer signoff, real closure signoff, real finding closure, completed external review, real external pilot readiness, production readiness, full BioSDK, production BioCompute Runtime or BiC OS readiness.",
    }
    audit["closure_signoff_registry_audit_sha256"] = stable_hash({key: value for key, value in audit.items() if key != "closure_signoff_registry_audit_sha256"})
    return audit


def write_closure_signoff_registry_outputs_v555(audit: dict[str, Any], out_dir: str | Path = DEFAULT_OUT) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary_json": out / "V555_CLOSURE_SIGNOFF_REGISTRY_SUMMARY.json",
        "policy_json": out / "V555_CLOSURE_SIGNOFF_REGISTRY_POLICY.json",
        "registry_matrix_json": out / "V555_SIGNOFF_REGISTRY_MATRIX.json",
        "audit_trail_json": out / "V555_CLOSURE_SIGNOFF_AUDIT_TRAIL.json",
        "signoff_packet_json": out / "V555_EXTERNAL_REVIEWER_SIGNOFF_PACKET.json",
        "signoff_gate_json": out / "V555_SIGNOFF_REGISTRY_GATE.json",
        "blocker_register_json": out / "V555_SIGNOFF_REGISTRY_BLOCKER_REGISTER.json",
        "audit_bundle_json": out / "V555_CLOSURE_SIGNOFF_REGISTRY_AUDIT_BUNDLE.json",
        "registry_matrix_csv": out / "V555_SIGNOFF_REGISTRY_MATRIX.csv",
        "signoff_gate_csv": out / "V555_SIGNOFF_REGISTRY_GATE.csv",
        "markdown_report": out / "BIOGPU_V555_CLOSURE_SIGNOFF_REGISTRY_REPORT.md",
    }
    summary = {key: value for key, value in audit.items() if key not in {"closure_signoff_registry_policy", "signoff_registry_matrix", "closure_signoff_audit_trail", "external_reviewer_signoff_packet", "signoff_registry_gate", "signoff_registry_blocker_register", "closure_signoff_registry_audit_bundle"}}
    paths["summary_json"].write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["policy_json"].write_text(json.dumps(audit["closure_signoff_registry_policy"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["registry_matrix_json"].write_text(json.dumps(audit["signoff_registry_matrix"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["audit_trail_json"].write_text(json.dumps(audit["closure_signoff_audit_trail"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["signoff_packet_json"].write_text(json.dumps(audit["external_reviewer_signoff_packet"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["signoff_gate_json"].write_text(json.dumps(audit["signoff_registry_gate"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["blocker_register_json"].write_text(json.dumps(audit["signoff_registry_blocker_register"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["audit_bundle_json"].write_text(json.dumps(audit["closure_signoff_registry_audit_bundle"], indent=2, ensure_ascii=False), encoding="utf-8")
    _write_registry_matrix_csv(paths["registry_matrix_csv"], audit["signoff_registry_matrix"].get("decisions", []))
    _write_signoff_gate_csv(paths["signoff_gate_csv"], audit["signoff_registry_gate"].get("decisions", []))
    paths["markdown_report"].write_text(_markdown_report(audit), encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}


def _write_registry_matrix_csv(path: Path, decisions: list[dict[str, Any]]) -> None:
    fieldnames = ["record_id", "record_type", "signoff_domain", "local_signoff_registry_record_ready", "local_audit_trail_ready", "real_external_reviewer_signoff_ready", "real_closure_signoff_ready", "review_finding_closed", "local_anchor", "reason_codes"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for decision in decisions:
            row = {field: decision.get(field) for field in fieldnames}
            row["reason_codes"] = " | ".join(str(reason) for reason in decision.get("reason_codes", []))
            writer.writerow(row)


def _write_signoff_gate_csv(path: Path, decisions: list[dict[str, Any]]) -> None:
    fieldnames = ["gate_id", "accepted_for_local_signoff_stage", "local_signoff_record_id", "reason_codes"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for decision in decisions:
            row = {field: decision.get(field) for field in fieldnames}
            row["reason_codes"] = " | ".join(str(reason) for reason in decision.get("reason_codes", []))
            writer.writerow(row)


def _markdown_report(audit: dict[str, Any]) -> str:
    answer = audit["direct_answer"]
    lines = [
        "# BioGPU-Core v5.55 Closure Signoff Registry Contract",
        "",
        "## Direct Answer",
        "",
        f"- Closure signoff audit trail added: `{answer['did_we_add_closure_signoff_audit_trail']}`",
        f"- External reviewer signoff registry added: `{answer['did_we_add_external_reviewer_signoff_registry']}`",
        f"- Real external reviewer signoffs ready: `{answer['are_real_external_reviewer_signoffs_ready']}`",
        f"- Real closure signoffs ready: `{answer['are_real_closure_signoffs_ready']}`",
        f"- Real review findings closed: `{answer['are_real_review_findings_closed']}`",
        f"- Real external review ready: `{answer['is_real_external_review_ready']}`",
        f"- Real external pilot ready: `{answer['is_real_external_pilot_ready']}`",
        f"- Production ready: `{answer['is_production_ready']}`",
        f"- Full BioSDK ready: `{answer['is_full_biosdk_ready']}`",
        f"- BioCompute Runtime ready: `{answer['is_biocompute_runtime_ready']}`",
        f"- BiC OS ready: `{answer['is_bic_os_ready']}`",
        f"- Next best build step: {answer['next_best_build_step']}",
        "",
        "## Distance",
        "",
        f"- Production distance: `{audit['production_distance_assessment']['distance']}`",
        f"- BiC OS distance: `{audit['bic_os_distance_assessment']['distance']}`",
        "",
        "## Proof Summary",
        "",
        f"- Overall status: `{audit['overall_status']}`",
        f"- v5.54 dependency ready: `{audit['v554_dependency_ready']}`",
        f"- Signoff registry records: `{audit['signoff_registry_record_count']}`",
        f"- Local registry-ready records: `{audit['local_signoff_registry_record_ready_count']}`",
        f"- Audit events: `{audit['audit_event_count']}`",
        f"- Signoff packet records: `{audit['signoff_packet_record_count']}`",
        f"- Real reviewer signoffs: `{audit['real_external_reviewer_signoff_ready_count']}`",
        f"- Real closure signoffs: `{audit['real_closure_signoff_ready_count']}`",
        f"- Review findings closed: `{audit['review_finding_closed_count']}`",
        f"- Accepted local signoff stages: `{audit['accepted_local_signoff_stage_count']}`",
        f"- Denied signoff registry gates: `{audit['denied_signoff_registry_gate_count']}`",
        "",
        "## Missing Real Inputs",
        "",
    ]
    for missing in audit["missing_real_inputs"]:
        lines.append(f"- {missing}")
    lines.extend(["", "## Boundary", "", audit["claim_boundary"], ""])
    return "\n".join(lines)