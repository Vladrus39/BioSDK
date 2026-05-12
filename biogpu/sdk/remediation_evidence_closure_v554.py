"""Remediation evidence verification and closure attestation proof, v5.54."""
from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from biogpu.beta.job_model_v43 import utc_now_iso
from biogpu.evidence.ledger_v53 import stable_hash
from biogpu.sdk.external_review_finding_triage_v553 import run_external_review_finding_triage_workflow_v553


DEFAULT_OUT = Path("outputs/v554_remediation_evidence_closure")
REMEDIATION_EVIDENCE_TYPES_V554 = (
    "owner_remediation_note",
    "code_or_config_change_evidence",
    "test_rerun_evidence",
    "security_identity_evidence",
    "storage_retention_evidence",
    "registry_distribution_evidence",
    "incident_support_evidence",
    "production_operations_evidence",
    "biocompute_runtime_evidence",
    "bic_os_boundary_evidence",
)
CLOSURE_ATTESTATION_SECTIONS_V554 = (
    "finding_reference",
    "remediation_evidence",
    "verification_result",
    "reviewer_recheck",
    "owner_attestation",
    "closure_signature_placeholder",
    "claim_boundary_acknowledgement",
)
LOCAL_CLOSURE_STAGES_V554 = ("evidence_verification", "closure_attestation_packet", "closure_attestation_preflight")


@dataclass(frozen=True)
class RemediationEvidenceClosurePolicyV554:
    policy_id: str
    remediation_evidence_types: tuple[str, ...]
    closure_attestation_sections: tuple[str, ...]
    local_closure_stages: tuple[str, ...]
    requires_v553_finding_triage: bool
    requires_remediation_evidence_matrix: bool
    requires_closure_attestation_packet: bool
    requires_external_reviewer_recheck: bool
    requires_remediation_owner_attestation: bool
    requires_closure_signature: bool
    local_contract_only: bool = True
    real_closure_attestation_ready: bool = False
    real_review_finding_closure_ready: bool = False
    real_external_review_ready: bool = False
    real_external_pilot_ready: bool = False
    production_ready: bool = False
    full_biosdk_ready: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RemediationEvidenceFixtureV554:
    evidence_id: str
    evidence_type: str
    finding_category: str
    has_v553_anchor: bool
    has_local_evidence_reference: bool
    has_verification_result: bool
    has_remediation_owner_role: bool
    has_claim_boundary_ack: bool
    has_external_reviewer_recheck: bool
    has_remediation_owner_attestation: bool
    has_closure_signature: bool
    requests_finding_closure_attestation: bool
    requests_external_review_completion: bool
    requests_real_external_pilot: bool
    requests_production_release: bool
    requests_bic_os_unlock: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RemediationEvidenceDecisionV554:
    evidence_id: str
    evidence_type: str
    finding_category: str
    verification_status: str
    local_remediation_evidence_verified: bool
    real_closure_attestation_ready: bool
    finding_closure_attested: bool
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
class ClosureAttestationGateFixtureV554:
    gate_id: str
    has_v553_finding_triage: bool
    has_remediation_evidence_matrix: bool
    has_closure_attestation_packet: bool
    has_claim_boundary_ack: bool
    has_no_open_closure_attestations: bool
    has_external_reviewer_recheck: bool
    has_remediation_owner_attestation: bool
    has_closure_signature: bool
    requests_finding_closure_attestation: bool
    requests_external_review_completion: bool
    requests_real_external_pilot: bool
    requests_production_release: bool
    requests_bic_os_unlock: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ClosureAttestationGateDecisionV554:
    gate_id: str
    accepted_for_local_closure_stage: bool
    reason_codes: tuple[str, ...]
    local_closure_record_id: str | None
    real_closure_attestation_ready: bool = False
    real_review_finding_closure_ready: bool = False
    real_external_review_ready: bool = False
    real_external_pilot_ready: bool = False
    production_release_ready: bool = False
    full_biosdk_ready: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_remediation_evidence_closure_policy_v554() -> dict[str, Any]:
    policy = RemediationEvidenceClosurePolicyV554(
        policy_id="BIOGPU_CORE_V554_REMEDIATION_EVIDENCE_CLOSURE_POLICY",
        remediation_evidence_types=REMEDIATION_EVIDENCE_TYPES_V554,
        closure_attestation_sections=CLOSURE_ATTESTATION_SECTIONS_V554,
        local_closure_stages=LOCAL_CLOSURE_STAGES_V554,
        requires_v553_finding_triage=True,
        requires_remediation_evidence_matrix=True,
        requires_closure_attestation_packet=True,
        requires_external_reviewer_recheck=True,
        requires_remediation_owner_attestation=True,
        requires_closure_signature=True,
    )
    result = {
        "version": "v5.54",
        "remediation_evidence_closure_policy_ready": True,
        "policy": policy.to_dict(),
        "blocked_modes": ["real_closure_attestation", "real_review_finding_closure", "real_external_review", "real_external_pilot", "production_release", "production_ready_claim", "bic_os_unlock"],
        "required_real_records": ["remediation_evidence_payload", "external_reviewer_recheck", "remediation_owner_attestation", "closure_signature", "finding_closure_timestamp"],
        "real_closure_attestation_ready": False,
        "real_review_finding_closure_ready": False,
        "real_external_review_ready": False,
        "real_external_pilot_ready": False,
        "production_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    result["remediation_evidence_closure_policy_sha256"] = stable_hash(result)
    return result


def default_remediation_evidence_fixtures_v554() -> list[RemediationEvidenceFixtureV554]:
    category_by_type = {
        "owner_remediation_note": "evidence_completeness",
        "code_or_config_change_evidence": "production_operations",
        "test_rerun_evidence": "evidence_completeness",
        "security_identity_evidence": "security_identity",
        "storage_retention_evidence": "storage_retention",
        "registry_distribution_evidence": "registry_distribution",
        "incident_support_evidence": "incident_support",
        "production_operations_evidence": "production_operations",
        "biocompute_runtime_evidence": "biocompute_runtime",
        "bic_os_boundary_evidence": "bic_os_boundary",
    }
    fixtures: list[RemediationEvidenceFixtureV554] = []
    for evidence_type in REMEDIATION_EVIDENCE_TYPES_V554:
        fixtures.append(
            RemediationEvidenceFixtureV554(
                evidence_id=f"remediation-evidence-{evidence_type}",
                evidence_type=evidence_type,
                finding_category=category_by_type[evidence_type],
                has_v553_anchor=True,
                has_local_evidence_reference=True,
                has_verification_result=True,
                has_remediation_owner_role=True,
                has_claim_boundary_ack=True,
                has_external_reviewer_recheck=False,
                has_remediation_owner_attestation=False,
                has_closure_signature=False,
                requests_finding_closure_attestation=evidence_type == "test_rerun_evidence",
                requests_external_review_completion=evidence_type == "owner_remediation_note",
                requests_real_external_pilot=evidence_type == "biocompute_runtime_evidence",
                requests_production_release=evidence_type == "production_operations_evidence",
                requests_bic_os_unlock=evidence_type == "bic_os_boundary_evidence",
            )
        )
    return fixtures


def evaluate_remediation_evidence_v554(fixture: RemediationEvidenceFixtureV554, v553_dependency: dict[str, Any]) -> RemediationEvidenceDecisionV554:
    reasons: list[str] = []
    if v553_dependency.get("external_review_finding_triage_contract_ready") is not True or not fixture.has_v553_anchor:
        reasons.append("v553_finding_triage_missing")
    if fixture.evidence_type not in REMEDIATION_EVIDENCE_TYPES_V554:
        reasons.append("remediation_evidence_type_not_allowed")
    if not fixture.has_local_evidence_reference:
        reasons.append("local_evidence_reference_missing")
    if not fixture.has_verification_result:
        reasons.append("verification_result_missing")
    if not fixture.has_remediation_owner_role:
        reasons.append("remediation_owner_role_missing")
    if not fixture.has_claim_boundary_ack:
        reasons.append("claim_boundary_ack_missing")
    local_verified = not any(
        reason in reasons
        for reason in {
            "v553_finding_triage_missing",
            "remediation_evidence_type_not_allowed",
            "local_evidence_reference_missing",
            "verification_result_missing",
            "remediation_owner_role_missing",
            "claim_boundary_ack_missing",
        }
    )
    if not fixture.has_external_reviewer_recheck:
        reasons.append("external_reviewer_recheck_missing")
    if not fixture.has_remediation_owner_attestation:
        reasons.append("remediation_owner_attestation_missing")
    if not fixture.has_closure_signature:
        reasons.append("closure_signature_missing")
    if fixture.requests_finding_closure_attestation:
        reasons.append("real_closure_attestation_not_ready")
        reasons.append("real_review_finding_closure_not_ready")
    if fixture.requests_external_review_completion:
        reasons.append("real_external_review_not_ready")
    if fixture.requests_real_external_pilot:
        reasons.append("real_external_pilot_not_ready")
    if fixture.requests_production_release:
        reasons.append("production_release_not_allowed")
    if fixture.requests_bic_os_unlock:
        reasons.append("bic_os_unlock_not_allowed")
    return RemediationEvidenceDecisionV554(
        evidence_id=fixture.evidence_id,
        evidence_type=fixture.evidence_type,
        finding_category=fixture.finding_category,
        verification_status="local_verified_open" if local_verified else "local_verification_incomplete",
        local_remediation_evidence_verified=local_verified,
        real_closure_attestation_ready=False,
        finding_closure_attested=False,
        reason_codes=tuple(reasons or ["closure_attested"]),
        local_anchor=str(v553_dependency.get("external_review_finding_triage_audit_sha256") or "") or None,
    )


def build_remediation_evidence_matrix_v554(v553_dependency: dict[str, Any], fixtures: list[RemediationEvidenceFixtureV554] | None = None) -> dict[str, Any]:
    evidence_fixtures = fixtures or default_remediation_evidence_fixtures_v554()
    decisions = [evaluate_remediation_evidence_v554(fixture, v553_dependency).to_dict() for fixture in evidence_fixtures]
    local_verified_count = sum(1 for decision in decisions if decision["local_remediation_evidence_verified"])
    real_attestation_count = sum(1 for decision in decisions if decision["real_closure_attestation_ready"])
    closure_count = sum(1 for decision in decisions if decision["finding_closure_attested"])
    evidence_types = sorted({decision["evidence_type"] for decision in decisions})
    reason_codes = sorted({reason for decision in decisions for reason in decision["reason_codes"]})
    required_reasons = {
        "external_reviewer_recheck_missing",
        "remediation_owner_attestation_missing",
        "closure_signature_missing",
        "real_closure_attestation_not_ready",
        "real_review_finding_closure_not_ready",
        "real_external_review_not_ready",
        "real_external_pilot_not_ready",
        "production_release_not_allowed",
        "bic_os_unlock_not_allowed",
    }
    matrix = {
        "version": "v5.54",
        "remediation_evidence_matrix_ready": local_verified_count == len(REMEDIATION_EVIDENCE_TYPES_V554) and real_attestation_count == 0 and closure_count == 0 and set(evidence_types) == set(REMEDIATION_EVIDENCE_TYPES_V554) and required_reasons.issubset(set(reason_codes)),
        "remediation_evidence_record_count": len(decisions),
        "local_remediation_evidence_verified_count": local_verified_count,
        "real_closure_attestation_ready_count": real_attestation_count,
        "finding_closure_attested_count": closure_count,
        "evidence_types": evidence_types,
        "verification_statuses": sorted({decision["verification_status"] for decision in decisions}),
        "reason_codes": reason_codes,
        "fixtures": [fixture.to_dict() for fixture in evidence_fixtures],
        "decisions": decisions,
        "real_closure_attestation_ready": False,
        "real_review_finding_closure_ready": False,
        "real_external_review_ready": False,
        "real_external_pilot_ready": False,
        "production_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    matrix["remediation_evidence_matrix_sha256"] = stable_hash(matrix)
    return matrix


def build_closure_attestation_packet_v554(v553_dependency: dict[str, Any], evidence_matrix: dict[str, Any]) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for decision in evidence_matrix.get("decisions", []):
        if decision.get("local_remediation_evidence_verified") is not True:
            continue
        record = {
            "version": "v5.54",
            "closure_attestation_record_id": f"closure-attestation-{decision['evidence_id']}",
            "evidence_type": decision.get("evidence_type"),
            "finding_category": decision.get("finding_category"),
            "verification_status": decision.get("verification_status"),
            "v553_finding_triage_anchor": v553_dependency.get("external_review_finding_triage_audit_sha256"),
            "evidence_matrix_anchor": evidence_matrix.get("remediation_evidence_matrix_sha256"),
            "local_closure_attestation_record_ready": True,
            "external_reviewer_recheck_present": False,
            "remediation_owner_attestation_present": False,
            "closure_signature_present": False,
            "real_closure_attestation_ready": False,
            "finding_closure_attested": False,
            "real_external_review_ready": False,
            "real_external_pilot_ready": False,
            "production_ready": False,
            "created_at": utc_now_iso(),
        }
        record["closure_attestation_record_sha256"] = stable_hash(record)
        records.append(record)
    packet = {
        "version": "v5.54",
        "closure_attestation_packet_ready": len(records) == len(REMEDIATION_EVIDENCE_TYPES_V554) and evidence_matrix.get("remediation_evidence_matrix_ready") is True,
        "closure_attestation_record_count": len(records),
        "local_closure_attestation_record_ready_count": sum(1 for record in records if record["local_closure_attestation_record_ready"]),
        "real_closure_attestation_ready_count": sum(1 for record in records if record["real_closure_attestation_ready"]),
        "finding_closure_attested_count": sum(1 for record in records if record["finding_closure_attested"]),
        "closure_attestation_records": records,
        "real_closure_attestation_ready": False,
        "real_review_finding_closure_ready": False,
        "real_external_review_ready": False,
        "real_external_pilot_ready": False,
        "production_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    packet["closure_attestation_packet_sha256"] = stable_hash(packet)
    return packet


def default_closure_attestation_gate_fixtures_v554() -> list[ClosureAttestationGateFixtureV554]:
    return [
        ClosureAttestationGateFixtureV554("evidence-verification", True, True, True, True, False, True, True, True, False, False, False, False, False),
        ClosureAttestationGateFixtureV554("closure-attestation-packet", True, True, True, True, False, True, True, True, False, False, False, False, False),
        ClosureAttestationGateFixtureV554("closure-attestation-preflight", True, True, True, True, False, True, True, True, False, False, False, False, False),
        ClosureAttestationGateFixtureV554("missing-v553-contract", False, True, True, True, False, True, True, True, False, False, False, False, False),
        ClosureAttestationGateFixtureV554("missing-evidence-matrix", True, False, True, True, False, True, True, True, False, False, False, False, False),
        ClosureAttestationGateFixtureV554("missing-closure-packet", True, True, False, True, False, True, True, True, False, False, False, False, False),
        ClosureAttestationGateFixtureV554("missing-claim-boundary", True, True, True, False, False, True, True, True, False, False, False, False, False),
        ClosureAttestationGateFixtureV554("missing-closure-attestation", True, True, True, True, True, False, False, False, True, False, False, False, False),
        ClosureAttestationGateFixtureV554("closure-with-open-attestations", True, True, True, True, False, True, True, True, True, True, False, False, False),
        ClosureAttestationGateFixtureV554("real-pilot-request", True, True, True, True, True, True, True, True, False, False, True, False, False),
        ClosureAttestationGateFixtureV554("production-release-request", True, True, True, True, True, True, True, True, False, False, False, True, False),
        ClosureAttestationGateFixtureV554("bic-os-unlock-request", True, True, True, True, True, True, True, True, False, False, False, False, True),
    ]


def evaluate_closure_attestation_gate_v554(fixture: ClosureAttestationGateFixtureV554, v553_dependency: dict[str, Any], evidence_matrix: dict[str, Any], closure_packet: dict[str, Any]) -> ClosureAttestationGateDecisionV554:
    reasons: list[str] = []
    if v553_dependency.get("external_review_finding_triage_contract_ready") is not True or not fixture.has_v553_finding_triage:
        reasons.append("v553_finding_triage_missing")
    if evidence_matrix.get("remediation_evidence_matrix_ready") is not True or not fixture.has_remediation_evidence_matrix:
        reasons.append("remediation_evidence_matrix_missing")
    if closure_packet.get("closure_attestation_packet_ready") is not True or not fixture.has_closure_attestation_packet:
        reasons.append("closure_attestation_packet_missing")
    if not fixture.has_claim_boundary_ack:
        reasons.append("claim_boundary_ack_missing")
    if fixture.requests_finding_closure_attestation:
        if not fixture.has_no_open_closure_attestations:
            reasons.append("closure_attestations_still_open")
        if not fixture.has_external_reviewer_recheck:
            reasons.append("external_reviewer_recheck_missing")
        if not fixture.has_remediation_owner_attestation:
            reasons.append("remediation_owner_attestation_missing")
        if not fixture.has_closure_signature:
            reasons.append("closure_signature_missing")
        reasons.append("real_closure_attestation_not_ready")
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
    return ClosureAttestationGateDecisionV554(
        gate_id=fixture.gate_id,
        accepted_for_local_closure_stage=accepted,
        reason_codes=tuple(reasons or ["local_closure_stage_accepted"]),
        local_closure_record_id=f"local-closure-{fixture.gate_id}" if accepted else None,
    )


def run_closure_attestation_gate_v554(v553_dependency: dict[str, Any], evidence_matrix: dict[str, Any], closure_packet: dict[str, Any], fixtures: list[ClosureAttestationGateFixtureV554] | None = None) -> dict[str, Any]:
    gate_fixtures = fixtures or default_closure_attestation_gate_fixtures_v554()
    decisions = [evaluate_closure_attestation_gate_v554(fixture, v553_dependency, evidence_matrix, closure_packet).to_dict() for fixture in gate_fixtures]
    accepted_count = sum(1 for decision in decisions if decision["accepted_for_local_closure_stage"])
    denied_count = len(decisions) - accepted_count
    reason_codes = sorted({reason for decision in decisions for reason in decision["reason_codes"]})
    required_denials = {
        "v553_finding_triage_missing",
        "remediation_evidence_matrix_missing",
        "closure_attestation_packet_missing",
        "claim_boundary_ack_missing",
        "closure_attestations_still_open",
        "external_reviewer_recheck_missing",
        "remediation_owner_attestation_missing",
        "closure_signature_missing",
        "real_closure_attestation_not_ready",
        "real_review_finding_closure_not_ready",
        "real_external_review_not_ready",
        "real_external_pilot_not_ready",
        "production_release_not_allowed",
        "bic_os_unlock_not_allowed",
    }
    gate = {
        "version": "v5.54",
        "closure_attestation_gate_ready": accepted_count == len(LOCAL_CLOSURE_STAGES_V554) and denied_count == 9 and required_denials.issubset(set(reason_codes)),
        "gate_fixture_count": len(gate_fixtures),
        "accepted_local_closure_stage_count": accepted_count,
        "denied_closure_attestation_gate_count": denied_count,
        "reason_codes": reason_codes,
        "fixtures": [fixture.to_dict() for fixture in gate_fixtures],
        "decisions": decisions,
        "real_closure_attestation_ready": False,
        "real_review_finding_closure_ready": False,
        "real_external_review_ready": False,
        "real_external_pilot_ready": False,
        "production_release_ready": False,
        "production_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    gate["closure_attestation_gate_sha256"] = stable_hash(gate)
    return gate


def build_closure_attestation_blocker_register_v554(evidence_matrix: dict[str, Any], closure_gate: dict[str, Any]) -> dict[str, Any]:
    blockers: list[dict[str, Any]] = []
    for decision in evidence_matrix.get("decisions", []):
        if decision.get("finding_closure_attested") is True:
            continue
        blocker = {
            "version": "v5.54",
            "blocker_id": f"closure-evidence-blocker-{decision['evidence_id']}",
            "source": "remediation_evidence_matrix",
            "record_id": decision.get("evidence_id"),
            "reason_codes": decision.get("reason_codes", []),
            "must_be_resolved_before_closure_attestation": True,
            "must_be_resolved_before_review_closure": True,
            "must_be_resolved_before_external_review": True,
            "must_be_resolved_before_real_pilot": True,
            "must_be_resolved_before_production": True,
            "must_be_resolved_before_bic_os": True,
        }
        blocker["blocker_sha256"] = stable_hash(blocker)
        blockers.append(blocker)
    for decision in closure_gate.get("decisions", []):
        if decision.get("accepted_for_local_closure_stage") is True:
            continue
        blocker = {
            "version": "v5.54",
            "blocker_id": f"closure-gate-blocker-{decision['gate_id']}",
            "source": "closure_attestation_gate",
            "record_id": decision.get("gate_id"),
            "reason_codes": decision.get("reason_codes", []),
            "must_be_resolved_before_closure_attestation": True,
            "must_be_resolved_before_review_closure": True,
            "must_be_resolved_before_external_review": True,
            "must_be_resolved_before_real_pilot": True,
            "must_be_resolved_before_production": True,
            "must_be_resolved_before_bic_os": True,
        }
        blocker["blocker_sha256"] = stable_hash(blocker)
        blockers.append(blocker)
    register = {
        "version": "v5.54",
        "closure_attestation_blocker_register_ready": len(blockers) == len(REMEDIATION_EVIDENCE_TYPES_V554) + 9,
        "blocker_count": len(blockers),
        "blockers": blockers,
        "real_closure_attestation_ready": False,
        "real_review_finding_closure_ready": False,
        "real_external_review_ready": False,
        "real_external_pilot_ready": False,
        "production_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    register["closure_attestation_blocker_register_sha256"] = stable_hash(register)
    return register


def build_remediation_evidence_closure_audit_bundle_v554(policy: dict[str, Any], evidence_matrix: dict[str, Any], closure_packet: dict[str, Any], closure_gate: dict[str, Any], blocker_register: dict[str, Any]) -> dict[str, Any]:
    bundle_ready = (
        policy.get("remediation_evidence_closure_policy_ready") is True
        and evidence_matrix.get("remediation_evidence_matrix_ready") is True
        and closure_packet.get("closure_attestation_packet_ready") is True
        and closure_gate.get("closure_attestation_gate_ready") is True
        and blocker_register.get("closure_attestation_blocker_register_ready") is True
    )
    bundle = {
        "version": "v5.54",
        "remediation_evidence_closure_audit_bundle_ready": bundle_ready,
        "policy_sha256": policy.get("remediation_evidence_closure_policy_sha256"),
        "evidence_matrix_sha256": evidence_matrix.get("remediation_evidence_matrix_sha256"),
        "closure_packet_sha256": closure_packet.get("closure_attestation_packet_sha256"),
        "closure_gate_sha256": closure_gate.get("closure_attestation_gate_sha256"),
        "blocker_register_sha256": blocker_register.get("closure_attestation_blocker_register_sha256"),
        "real_closure_attestation_ready": False,
        "real_review_finding_closure_ready": False,
        "real_external_review_ready": False,
        "real_external_pilot_ready": False,
        "production_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    bundle["remediation_evidence_closure_audit_bundle_sha256"] = stable_hash(bundle)
    return bundle


def run_remediation_evidence_closure_workflow_v554(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    project_root = Path(root).resolve()
    out = project_root / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    v553_dependency = run_external_review_finding_triage_workflow_v553(project_root, out.parent / "d554")
    policy = build_remediation_evidence_closure_policy_v554()
    evidence_matrix = build_remediation_evidence_matrix_v554(v553_dependency)
    closure_packet = build_closure_attestation_packet_v554(v553_dependency, evidence_matrix)
    closure_gate = run_closure_attestation_gate_v554(v553_dependency, evidence_matrix, closure_packet)
    blocker_register = build_closure_attestation_blocker_register_v554(evidence_matrix, closure_gate)
    audit_bundle = build_remediation_evidence_closure_audit_bundle_v554(policy, evidence_matrix, closure_packet, closure_gate, blocker_register)
    proof_ready = (
        v553_dependency.get("external_review_finding_triage_contract_ready") is True
        and policy.get("remediation_evidence_closure_policy_ready") is True
        and evidence_matrix.get("remediation_evidence_matrix_ready") is True
        and closure_packet.get("closure_attestation_packet_ready") is True
        and closure_gate.get("closure_attestation_gate_ready") is True
        and blocker_register.get("closure_attestation_blocker_register_ready") is True
        and audit_bundle.get("remediation_evidence_closure_audit_bundle_ready") is True
    )
    audit = {
        "version": "v5.54",
        "phase": "remediation_evidence_verification_closure_attestation_contract",
        "overall_status": "remediation_evidence_closure_contract_ready_attestation_not_claimed" if proof_ready else "remediation_evidence_closure_contract_incomplete",
        "active_phase": "biosdk_remediation_evidence_closure_proof",
        "bic_os_phase_locked": True,
        "remediation_evidence_closure_contract_ready": proof_ready,
        "v553_dependency_ready": v553_dependency.get("external_review_finding_triage_contract_ready") is True,
        "remediation_evidence_closure_policy_ready": policy.get("remediation_evidence_closure_policy_ready") is True,
        "remediation_evidence_matrix_ready": evidence_matrix.get("remediation_evidence_matrix_ready") is True,
        "closure_attestation_packet_ready": closure_packet.get("closure_attestation_packet_ready") is True,
        "closure_attestation_gate_ready": closure_gate.get("closure_attestation_gate_ready") is True,
        "closure_attestation_blocker_register_ready": blocker_register.get("closure_attestation_blocker_register_ready") is True,
        "remediation_evidence_closure_audit_bundle_ready": audit_bundle.get("remediation_evidence_closure_audit_bundle_ready") is True,
        "artifact_name": v553_dependency.get("artifact_name"),
        "artifact_sha256": v553_dependency.get("artifact_sha256"),
        "remediation_evidence_record_count": evidence_matrix.get("remediation_evidence_record_count"),
        "local_remediation_evidence_verified_count": evidence_matrix.get("local_remediation_evidence_verified_count"),
        "real_closure_attestation_ready_count": evidence_matrix.get("real_closure_attestation_ready_count"),
        "finding_closure_attested_count": evidence_matrix.get("finding_closure_attested_count"),
        "closure_attestation_record_count": closure_packet.get("closure_attestation_record_count"),
        "accepted_local_closure_stage_count": closure_gate.get("accepted_local_closure_stage_count"),
        "denied_closure_attestation_gate_count": closure_gate.get("denied_closure_attestation_gate_count"),
        "closure_attestation_blocker_count": blocker_register.get("blocker_count"),
        "real_closure_attestation_ready": False,
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
        "remediation_evidence_closure_policy": policy,
        "remediation_evidence_matrix": evidence_matrix,
        "closure_attestation_packet": closure_packet,
        "closure_attestation_gate": closure_gate,
        "closure_attestation_blocker_register": blocker_register,
        "remediation_evidence_closure_audit_bundle": audit_bundle,
        "v553_dependency_summary": {key: value for key, value in v553_dependency.items() if key not in {"external_review_finding_triage_policy", "review_finding_triage_matrix", "remediation_plan_packet", "remediation_closure_gate", "remediation_blocker_register", "external_review_finding_triage_audit_bundle", "v552_dependency_summary"}},
        "missing_real_inputs": [
            "real remediation evidence payloads",
            "external reviewer recheck records",
            "remediation owner attestations",
            "closure signatures and timestamps",
            "immutable closure transcript",
            "real partner data-room access logs",
            "signed partner data-use approval",
            "external security review signoff",
            "production identity-provider approval",
            "live registry administrative approval",
            "trusted signing authority approval",
            "production CI/CD and rollback/yank acceptance",
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
            "did_we_add_remediation_evidence_verification": "yes" if evidence_matrix.get("remediation_evidence_matrix_ready") else "no",
            "did_we_add_closure_attestation_proof": "yes" if closure_packet.get("closure_attestation_packet_ready") else "no",
            "are_real_closure_attestations_ready": "no",
            "are_real_review_findings_closed": "no",
            "is_real_external_review_ready": "no",
            "is_real_external_pilot_ready": "no",
            "is_production_ready": "no",
            "is_full_biosdk_ready": "no",
            "is_biocompute_runtime_ready": "no",
            "is_bic_os_ready": "no",
            "next_best_build_step": "add closure attestation audit trail and external reviewer signoff registry proof" if proof_ready else "fix v5.54 remediation-evidence closure blockers first",
        },
        "claim_boundary": "v5.54 proves a local remediation evidence verification matrix, closure attestation packet shape and closure-attestation preflight gate over the v5.53 external review finding triage contract. It does not claim real closure attestations, real finding closure, completed external review, real external pilot readiness, production readiness, full BioSDK, production BioCompute Runtime or BiC OS readiness.",
    }
    audit["remediation_evidence_closure_audit_sha256"] = stable_hash({key: value for key, value in audit.items() if key != "remediation_evidence_closure_audit_sha256"})
    return audit


def write_remediation_evidence_closure_outputs_v554(audit: dict[str, Any], out_dir: str | Path = DEFAULT_OUT) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary_json": out / "V554_REMEDIATION_EVIDENCE_CLOSURE_SUMMARY.json",
        "policy_json": out / "V554_REMEDIATION_EVIDENCE_CLOSURE_POLICY.json",
        "evidence_matrix_json": out / "V554_REMEDIATION_EVIDENCE_MATRIX.json",
        "closure_packet_json": out / "V554_CLOSURE_ATTESTATION_PACKET.json",
        "closure_gate_json": out / "V554_CLOSURE_ATTESTATION_GATE.json",
        "blocker_register_json": out / "V554_CLOSURE_ATTESTATION_BLOCKER_REGISTER.json",
        "audit_bundle_json": out / "V554_REMEDIATION_EVIDENCE_CLOSURE_AUDIT_BUNDLE.json",
        "evidence_matrix_csv": out / "V554_REMEDIATION_EVIDENCE_MATRIX.csv",
        "closure_gate_csv": out / "V554_CLOSURE_ATTESTATION_GATE.csv",
        "markdown_report": out / "BIOGPU_V554_REMEDIATION_EVIDENCE_CLOSURE_REPORT.md",
    }
    summary = {key: value for key, value in audit.items() if key not in {"remediation_evidence_closure_policy", "remediation_evidence_matrix", "closure_attestation_packet", "closure_attestation_gate", "closure_attestation_blocker_register", "remediation_evidence_closure_audit_bundle"}}
    paths["summary_json"].write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["policy_json"].write_text(json.dumps(audit["remediation_evidence_closure_policy"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["evidence_matrix_json"].write_text(json.dumps(audit["remediation_evidence_matrix"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["closure_packet_json"].write_text(json.dumps(audit["closure_attestation_packet"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["closure_gate_json"].write_text(json.dumps(audit["closure_attestation_gate"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["blocker_register_json"].write_text(json.dumps(audit["closure_attestation_blocker_register"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["audit_bundle_json"].write_text(json.dumps(audit["remediation_evidence_closure_audit_bundle"], indent=2, ensure_ascii=False), encoding="utf-8")
    _write_evidence_matrix_csv(paths["evidence_matrix_csv"], audit["remediation_evidence_matrix"].get("decisions", []))
    _write_closure_gate_csv(paths["closure_gate_csv"], audit["closure_attestation_gate"].get("decisions", []))
    paths["markdown_report"].write_text(_markdown_report(audit), encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}


def _write_evidence_matrix_csv(path: Path, decisions: list[dict[str, Any]]) -> None:
    fieldnames = ["evidence_id", "evidence_type", "finding_category", "verification_status", "local_remediation_evidence_verified", "real_closure_attestation_ready", "finding_closure_attested", "local_anchor", "reason_codes"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for decision in decisions:
            row = {field: decision.get(field) for field in fieldnames}
            row["reason_codes"] = " | ".join(str(reason) for reason in decision.get("reason_codes", []))
            writer.writerow(row)


def _write_closure_gate_csv(path: Path, decisions: list[dict[str, Any]]) -> None:
    fieldnames = ["gate_id", "accepted_for_local_closure_stage", "local_closure_record_id", "reason_codes"]
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
        "# BioGPU-Core v5.54 Remediation Evidence Closure Contract",
        "",
        "## Direct Answer",
        "",
        f"- Remediation evidence verification added: `{answer['did_we_add_remediation_evidence_verification']}`",
        f"- Closure attestation proof added: `{answer['did_we_add_closure_attestation_proof']}`",
        f"- Real closure attestations ready: `{answer['are_real_closure_attestations_ready']}`",
        f"- Real review findings closed: `{answer['are_real_review_findings_closed']}`",
        f"- Real external review ready: `{answer['is_real_external_review_ready']}`",
        f"- Real external pilot ready: `{answer['is_real_external_pilot_ready']}`",
        f"- Production ready: `{answer['is_production_ready']}`",
        f"- Full BioSDK ready: `{answer['is_full_biosdk_ready']}`",
        f"- BioCompute Runtime ready: `{answer['is_biocompute_runtime_ready']}`",
        f"- BiC OS ready: `{answer['is_bic_os_ready']}`",
        f"- Next best build step: {answer['next_best_build_step']}",
        "",
        "## Proof Summary",
        "",
        f"- Overall status: `{audit['overall_status']}`",
        f"- v5.53 dependency ready: `{audit['v553_dependency_ready']}`",
        f"- Evidence records: `{audit['remediation_evidence_record_count']}`",
        f"- Local verified evidence records: `{audit['local_remediation_evidence_verified_count']}`",
        f"- Real closure attestations: `{audit['real_closure_attestation_ready_count']}`",
        f"- Finding closures attested: `{audit['finding_closure_attested_count']}`",
        f"- Closure attestation records: `{audit['closure_attestation_record_count']}`",
        f"- Accepted local closure stages: `{audit['accepted_local_closure_stage_count']}`",
        f"- Denied closure attestation gates: `{audit['denied_closure_attestation_gate_count']}`",
        "",
        "## Missing Real Inputs",
        "",
    ]
    for missing in audit["missing_real_inputs"]:
        lines.append(f"- {missing}")
    lines.extend(["", "## Boundary", "", audit["claim_boundary"], ""])
    return "\n".join(lines)