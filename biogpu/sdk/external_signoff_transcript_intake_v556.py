"""Real external signoff intake and signed closure transcript acceptance contract, v5.56."""
from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from biogpu.beta.job_model_v43 import utc_now_iso
from biogpu.evidence.ledger_v53 import stable_hash
from biogpu.sdk.closure_signoff_registry_v555 import run_closure_signoff_registry_workflow_v555


DEFAULT_OUT = Path("outputs/v556_external_signoff_transcript_intake")
SIGNOFF_INTAKE_RECORD_TYPES_V556 = (
    "reviewer_identity_evidence",
    "reviewer_authorization_evidence",
    "reviewer_recheck_evidence",
    "signed_signoff_manifest",
    "signed_closure_transcript",
    "closure_timestamp_evidence",
    "owner_counter_attestation",
    "finding_closure_crosswalk",
    "dataroom_access_evidence",
    "claim_boundary_counter_attestation",
)
TRANSCRIPT_ACCEPTANCE_SECTIONS_V556 = (
    "identity_and_authority",
    "v555_registry_anchor",
    "finding_disposition",
    "remediation_evidence_reference",
    "reviewer_signature",
    "owner_counter_signature",
    "immutable_transcript_anchor",
    "claim_boundary_confirmation",
)
LOCAL_INTAKE_STAGES_V556 = ("signoff_intake_schema", "transcript_packet", "transcript_acceptance_preflight")


@dataclass(frozen=True)
class ExternalSignoffTranscriptIntakePolicyV556:
    policy_id: str
    signoff_intake_record_types: tuple[str, ...]
    transcript_acceptance_sections: tuple[str, ...]
    local_intake_stages: tuple[str, ...]
    requires_v555_signoff_registry: bool
    requires_external_reviewer_identity: bool
    requires_reviewer_authorization: bool
    requires_reviewer_recheck: bool
    requires_signed_signoff_manifest: bool
    requires_signed_closure_transcript: bool
    requires_closure_timestamp: bool
    requires_owner_counter_attestation: bool
    requires_immutable_transcript_anchor: bool
    local_contract_only: bool = True
    real_external_signoff_intake_ready: bool = False
    real_external_signoff_accepted: bool = False
    signed_closure_transcript_accepted: bool = False
    real_review_finding_closure_ready: bool = False
    real_external_review_ready: bool = False
    real_external_pilot_ready: bool = False
    production_ready: bool = False
    full_biosdk_ready: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SignoffIntakeRecordFixtureV556:
    record_id: str
    record_type: str
    intake_domain: str
    has_v555_registry_anchor: bool
    has_local_intake_schema: bool
    has_local_transcript_reference: bool
    has_claim_boundary_ack: bool
    has_external_reviewer_identity_payload: bool
    has_reviewer_authorization_payload: bool
    has_reviewer_recheck_payload: bool
    has_signed_signoff_manifest_payload: bool
    has_signed_closure_transcript_payload: bool
    has_closure_timestamp_payload: bool
    has_owner_counter_attestation_payload: bool
    has_immutable_transcript_anchor_payload: bool
    requests_real_external_signoff_acceptance: bool
    requests_signed_closure_transcript_acceptance: bool
    requests_review_finding_closure: bool
    requests_external_review_completion: bool
    requests_real_external_pilot: bool
    requests_production_release: bool
    requests_bic_os_unlock: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SignoffIntakeRecordDecisionV556:
    record_id: str
    record_type: str
    intake_domain: str
    local_signoff_intake_record_ready: bool
    local_transcript_reference_ready: bool
    real_external_signoff_accepted: bool
    signed_closure_transcript_accepted: bool
    review_finding_closed: bool
    reason_codes: tuple[str, ...]
    local_anchor: str | None
    real_external_signoff_intake_ready: bool = False
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
class TranscriptAcceptanceGateFixtureV556:
    gate_id: str
    has_v555_signoff_registry: bool
    has_signoff_intake_matrix: bool
    has_signed_closure_transcript_packet: bool
    has_claim_boundary_ack: bool
    has_external_reviewer_identity_payload: bool
    has_reviewer_authorization_payload: bool
    has_reviewer_recheck_payload: bool
    has_signed_signoff_manifest_payload: bool
    has_signed_closure_transcript_payload: bool
    has_closure_timestamp_payload: bool
    has_owner_counter_attestation_payload: bool
    has_immutable_transcript_anchor_payload: bool
    requests_real_external_signoff_acceptance: bool
    requests_signed_closure_transcript_acceptance: bool
    requests_review_finding_closure: bool
    requests_external_review_completion: bool
    requests_real_external_pilot: bool
    requests_production_release: bool
    requests_bic_os_unlock: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TranscriptAcceptanceGateDecisionV556:
    gate_id: str
    accepted_for_local_intake_stage: bool
    reason_codes: tuple[str, ...]
    local_intake_record_id: str | None
    real_external_signoff_intake_ready: bool = False
    real_external_signoff_accepted: bool = False
    signed_closure_transcript_accepted: bool = False
    real_closure_signoff_ready: bool = False
    real_review_finding_closure_ready: bool = False
    real_external_review_ready: bool = False
    real_external_pilot_ready: bool = False
    production_release_ready: bool = False
    full_biosdk_ready: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_external_signoff_transcript_intake_policy_v556() -> dict[str, Any]:
    policy = ExternalSignoffTranscriptIntakePolicyV556(
        policy_id="BIOGPU_CORE_V556_EXTERNAL_SIGNOFF_TRANSCRIPT_INTAKE_POLICY",
        signoff_intake_record_types=SIGNOFF_INTAKE_RECORD_TYPES_V556,
        transcript_acceptance_sections=TRANSCRIPT_ACCEPTANCE_SECTIONS_V556,
        local_intake_stages=LOCAL_INTAKE_STAGES_V556,
        requires_v555_signoff_registry=True,
        requires_external_reviewer_identity=True,
        requires_reviewer_authorization=True,
        requires_reviewer_recheck=True,
        requires_signed_signoff_manifest=True,
        requires_signed_closure_transcript=True,
        requires_closure_timestamp=True,
        requires_owner_counter_attestation=True,
        requires_immutable_transcript_anchor=True,
    )
    result = {
        "version": "v5.56",
        "external_signoff_transcript_intake_policy_ready": True,
        "policy": policy.to_dict(),
        "blocked_modes": [
            "accepting_unsigned_signoffs",
            "accepting_unsigned_closure_transcripts",
            "real_external_signoff_acceptance",
            "real_closure_signoff",
            "real_review_finding_closure",
            "real_external_review_completion",
            "real_external_pilot",
            "production_release",
            "production_ready_claim",
            "bic_os_unlock",
        ],
        "required_real_payloads": [
            "external reviewer identity evidence",
            "reviewer authorization evidence",
            "reviewer recheck evidence",
            "signed external reviewer signoff manifest",
            "signed closure transcript",
            "closure timestamp evidence",
            "owner counter-attestation",
            "immutable transcript anchor",
        ],
        "real_external_signoff_intake_ready": False,
        "real_external_signoff_accepted": False,
        "signed_closure_transcript_accepted": False,
        "real_closure_signoff_ready": False,
        "real_review_finding_closure_ready": False,
        "real_external_review_ready": False,
        "real_external_pilot_ready": False,
        "production_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    result["external_signoff_transcript_intake_policy_sha256"] = stable_hash(result)
    return result


def default_signoff_intake_record_fixtures_v556() -> list[SignoffIntakeRecordFixtureV556]:
    domain_by_type = {
        "reviewer_identity_evidence": "reviewer_identity",
        "reviewer_authorization_evidence": "reviewer_authorization",
        "reviewer_recheck_evidence": "reviewer_recheck",
        "signed_signoff_manifest": "signoff_manifest",
        "signed_closure_transcript": "closure_transcript",
        "closure_timestamp_evidence": "closure_timestamp",
        "owner_counter_attestation": "owner_attestation",
        "finding_closure_crosswalk": "finding_closure",
        "dataroom_access_evidence": "dataroom_access",
        "claim_boundary_counter_attestation": "claim_boundary",
    }
    return [
        SignoffIntakeRecordFixtureV556(
            record_id=f"signoff-intake-{record_type}",
            record_type=record_type,
            intake_domain=domain_by_type[record_type],
            has_v555_registry_anchor=True,
            has_local_intake_schema=True,
            has_local_transcript_reference=True,
            has_claim_boundary_ack=True,
            has_external_reviewer_identity_payload=False,
            has_reviewer_authorization_payload=False,
            has_reviewer_recheck_payload=False,
            has_signed_signoff_manifest_payload=False,
            has_signed_closure_transcript_payload=False,
            has_closure_timestamp_payload=False,
            has_owner_counter_attestation_payload=False,
            has_immutable_transcript_anchor_payload=False,
            requests_real_external_signoff_acceptance=record_type == "signed_signoff_manifest",
            requests_signed_closure_transcript_acceptance=record_type == "signed_closure_transcript",
            requests_review_finding_closure=record_type == "finding_closure_crosswalk",
            requests_external_review_completion=record_type == "reviewer_recheck_evidence",
            requests_real_external_pilot=record_type == "dataroom_access_evidence",
            requests_production_release=record_type == "owner_counter_attestation",
            requests_bic_os_unlock=record_type == "claim_boundary_counter_attestation",
        )
        for record_type in SIGNOFF_INTAKE_RECORD_TYPES_V556
    ]


def evaluate_signoff_intake_record_v556(
    fixture: SignoffIntakeRecordFixtureV556,
    v555_dependency: dict[str, Any],
) -> SignoffIntakeRecordDecisionV556:
    reasons: list[str] = []
    if v555_dependency.get("closure_signoff_registry_contract_ready") is not True or not fixture.has_v555_registry_anchor:
        reasons.append("v555_signoff_registry_missing")
    if fixture.record_type not in SIGNOFF_INTAKE_RECORD_TYPES_V556:
        reasons.append("signoff_intake_record_type_not_allowed")
    if not fixture.has_local_intake_schema:
        reasons.append("local_intake_schema_missing")
    if not fixture.has_local_transcript_reference:
        reasons.append("local_transcript_reference_missing")
    if not fixture.has_claim_boundary_ack:
        reasons.append("claim_boundary_ack_missing")
    local_blockers = {
        "v555_signoff_registry_missing",
        "signoff_intake_record_type_not_allowed",
        "local_intake_schema_missing",
        "local_transcript_reference_missing",
        "claim_boundary_ack_missing",
    }
    local_ready = not any(reason in local_blockers for reason in reasons)
    if not fixture.has_external_reviewer_identity_payload:
        reasons.append("external_reviewer_identity_payload_missing")
    if not fixture.has_reviewer_authorization_payload:
        reasons.append("reviewer_authorization_payload_missing")
    if not fixture.has_reviewer_recheck_payload:
        reasons.append("reviewer_recheck_payload_missing")
    if not fixture.has_signed_signoff_manifest_payload:
        reasons.append("signed_signoff_manifest_payload_missing")
    if not fixture.has_signed_closure_transcript_payload:
        reasons.append("signed_closure_transcript_payload_missing")
    if not fixture.has_closure_timestamp_payload:
        reasons.append("closure_timestamp_payload_missing")
    if not fixture.has_owner_counter_attestation_payload:
        reasons.append("owner_counter_attestation_payload_missing")
    if not fixture.has_immutable_transcript_anchor_payload:
        reasons.append("immutable_transcript_anchor_payload_missing")
    if fixture.requests_real_external_signoff_acceptance:
        reasons.append("real_external_signoff_intake_not_accepted")
    if fixture.requests_signed_closure_transcript_acceptance:
        reasons.append("signed_closure_transcript_not_accepted")
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
    return SignoffIntakeRecordDecisionV556(
        record_id=fixture.record_id,
        record_type=fixture.record_type,
        intake_domain=fixture.intake_domain,
        local_signoff_intake_record_ready=local_ready,
        local_transcript_reference_ready=local_ready and fixture.has_local_transcript_reference,
        real_external_signoff_accepted=False,
        signed_closure_transcript_accepted=False,
        review_finding_closed=False,
        reason_codes=tuple(reasons or ["local_intake_record_ready"]),
        local_anchor=str(v555_dependency.get("closure_signoff_registry_audit_sha256") or "") or None,
    )


def build_external_signoff_intake_matrix_v556(
    v555_dependency: dict[str, Any],
    fixtures: list[SignoffIntakeRecordFixtureV556] | None = None,
) -> dict[str, Any]:
    intake_fixtures = fixtures or default_signoff_intake_record_fixtures_v556()
    decisions = [evaluate_signoff_intake_record_v556(fixture, v555_dependency).to_dict() for fixture in intake_fixtures]
    reason_codes = sorted({reason for decision in decisions for reason in decision["reason_codes"]})
    required_reasons = {
        "external_reviewer_identity_payload_missing",
        "reviewer_authorization_payload_missing",
        "reviewer_recheck_payload_missing",
        "signed_signoff_manifest_payload_missing",
        "signed_closure_transcript_payload_missing",
        "closure_timestamp_payload_missing",
        "owner_counter_attestation_payload_missing",
        "immutable_transcript_anchor_payload_missing",
        "real_external_signoff_intake_not_accepted",
        "signed_closure_transcript_not_accepted",
        "real_closure_signoff_not_ready",
        "real_review_finding_closure_not_ready",
        "real_external_review_not_ready",
        "real_external_pilot_not_ready",
        "production_release_not_allowed",
        "bic_os_unlock_not_allowed",
    }
    local_ready_count = sum(1 for decision in decisions if decision["local_signoff_intake_record_ready"])
    transcript_reference_count = sum(1 for decision in decisions if decision["local_transcript_reference_ready"])
    matrix = {
        "version": "v5.56",
        "external_signoff_intake_matrix_ready": local_ready_count == len(SIGNOFF_INTAKE_RECORD_TYPES_V556) and required_reasons.issubset(set(reason_codes)),
        "signoff_intake_record_count": len(decisions),
        "local_signoff_intake_record_ready_count": local_ready_count,
        "local_transcript_reference_ready_count": transcript_reference_count,
        "real_external_signoff_accepted_count": sum(1 for decision in decisions if decision["real_external_signoff_accepted"]),
        "signed_closure_transcript_accepted_count": sum(1 for decision in decisions if decision["signed_closure_transcript_accepted"]),
        "review_finding_closed_count": sum(1 for decision in decisions if decision["review_finding_closed"]),
        "record_types": sorted({decision["record_type"] for decision in decisions}),
        "reason_codes": reason_codes,
        "fixtures": [fixture.to_dict() for fixture in intake_fixtures],
        "decisions": decisions,
        "real_external_signoff_intake_ready": False,
        "real_external_signoff_accepted": False,
        "signed_closure_transcript_accepted": False,
        "real_closure_signoff_ready": False,
        "real_review_finding_closure_ready": False,
        "real_external_review_ready": False,
        "real_external_pilot_ready": False,
        "production_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    matrix["external_signoff_intake_matrix_sha256"] = stable_hash(matrix)
    return matrix


def build_signed_closure_transcript_packet_v556(
    v555_dependency: dict[str, Any],
    intake_matrix: dict[str, Any],
) -> dict[str, Any]:
    sections: list[dict[str, Any]] = []
    for section_name in TRANSCRIPT_ACCEPTANCE_SECTIONS_V556:
        section = {
            "version": "v5.56",
            "section_id": f"signed-transcript-section-{section_name}",
            "section_name": section_name,
            "v555_signoff_registry_anchor": v555_dependency.get("closure_signoff_registry_audit_sha256"),
            "signoff_intake_matrix_anchor": intake_matrix.get("external_signoff_intake_matrix_sha256"),
            "local_transcript_packet_section_ready": True,
            "real_external_reviewer_identity_payload_present": False,
            "signed_signoff_manifest_payload_present": False,
            "signed_closure_transcript_payload_present": False,
            "closure_timestamp_payload_present": False,
            "owner_counter_attestation_payload_present": False,
            "immutable_transcript_anchor_payload_present": False,
            "real_external_signoff_accepted": False,
            "signed_closure_transcript_accepted": False,
            "created_at": utc_now_iso(),
        }
        section["transcript_packet_section_sha256"] = stable_hash(section)
        sections.append(section)
    packet = {
        "version": "v5.56",
        "signed_closure_transcript_packet_ready": len(sections) == len(TRANSCRIPT_ACCEPTANCE_SECTIONS_V556) and intake_matrix.get("external_signoff_intake_matrix_ready") is True,
        "transcript_packet_section_count": len(sections),
        "local_transcript_packet_section_ready_count": sum(1 for section in sections if section["local_transcript_packet_section_ready"]),
        "real_external_signoff_accepted_count": sum(1 for section in sections if section["real_external_signoff_accepted"]),
        "signed_closure_transcript_accepted_count": sum(1 for section in sections if section["signed_closure_transcript_accepted"]),
        "sections": sections,
        "real_external_signoff_intake_ready": False,
        "real_external_signoff_accepted": False,
        "signed_closure_transcript_accepted": False,
        "real_closure_signoff_ready": False,
        "real_review_finding_closure_ready": False,
        "real_external_review_ready": False,
        "real_external_pilot_ready": False,
        "production_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    packet["signed_closure_transcript_packet_sha256"] = stable_hash(packet)
    return packet


def default_transcript_acceptance_gate_fixtures_v556() -> list[TranscriptAcceptanceGateFixtureV556]:
    return [
        TranscriptAcceptanceGateFixtureV556("signoff-intake-schema", True, True, True, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False),
        TranscriptAcceptanceGateFixtureV556("transcript-packet", True, True, True, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False),
        TranscriptAcceptanceGateFixtureV556("transcript-acceptance-preflight", True, True, True, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False),
        TranscriptAcceptanceGateFixtureV556("missing-v555-contract", False, True, True, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False),
        TranscriptAcceptanceGateFixtureV556("missing-intake-matrix", True, False, True, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False),
        TranscriptAcceptanceGateFixtureV556("missing-transcript-packet", True, True, False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False),
        TranscriptAcceptanceGateFixtureV556("missing-claim-boundary", True, True, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False),
        TranscriptAcceptanceGateFixtureV556("missing-real-signoff-intake", True, True, True, True, False, False, False, False, False, False, False, False, True, False, False, False, False, False, False),
        TranscriptAcceptanceGateFixtureV556("signed-transcript-acceptance-request", True, True, True, True, False, False, False, False, False, False, False, False, False, True, True, False, False, False, False),
        TranscriptAcceptanceGateFixtureV556("external-review-completion-request", True, True, True, True, False, False, False, False, False, False, False, False, False, False, False, True, False, False, False),
        TranscriptAcceptanceGateFixtureV556("real-pilot-request", True, True, True, True, False, False, False, False, False, False, False, False, False, False, False, False, True, False, False),
        TranscriptAcceptanceGateFixtureV556("production-release-request", True, True, True, True, False, False, False, False, False, False, False, False, False, False, False, False, False, True, False),
        TranscriptAcceptanceGateFixtureV556("bic-os-unlock-request", True, True, True, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True),
    ]


def evaluate_transcript_acceptance_gate_v556(
    fixture: TranscriptAcceptanceGateFixtureV556,
    v555_dependency: dict[str, Any],
    intake_matrix: dict[str, Any],
    transcript_packet: dict[str, Any],
) -> TranscriptAcceptanceGateDecisionV556:
    reasons: list[str] = []
    if v555_dependency.get("closure_signoff_registry_contract_ready") is not True or not fixture.has_v555_signoff_registry:
        reasons.append("v555_signoff_registry_missing")
    if intake_matrix.get("external_signoff_intake_matrix_ready") is not True or not fixture.has_signoff_intake_matrix:
        reasons.append("external_signoff_intake_matrix_missing")
    if transcript_packet.get("signed_closure_transcript_packet_ready") is not True or not fixture.has_signed_closure_transcript_packet:
        reasons.append("signed_closure_transcript_packet_missing")
    if not fixture.has_claim_boundary_ack:
        reasons.append("claim_boundary_ack_missing")
    needs_signed_payloads = fixture.requests_real_external_signoff_acceptance or fixture.requests_signed_closure_transcript_acceptance or fixture.requests_review_finding_closure
    if needs_signed_payloads:
        if not fixture.has_external_reviewer_identity_payload:
            reasons.append("external_reviewer_identity_payload_missing")
        if not fixture.has_reviewer_authorization_payload:
            reasons.append("reviewer_authorization_payload_missing")
        if not fixture.has_reviewer_recheck_payload:
            reasons.append("reviewer_recheck_payload_missing")
        if not fixture.has_signed_signoff_manifest_payload:
            reasons.append("signed_signoff_manifest_payload_missing")
        if not fixture.has_signed_closure_transcript_payload:
            reasons.append("signed_closure_transcript_payload_missing")
        if not fixture.has_closure_timestamp_payload:
            reasons.append("closure_timestamp_payload_missing")
        if not fixture.has_owner_counter_attestation_payload:
            reasons.append("owner_counter_attestation_payload_missing")
        if not fixture.has_immutable_transcript_anchor_payload:
            reasons.append("immutable_transcript_anchor_payload_missing")
    if fixture.requests_real_external_signoff_acceptance:
        reasons.append("real_external_signoff_intake_not_accepted")
    if fixture.requests_signed_closure_transcript_acceptance:
        reasons.append("signed_closure_transcript_not_accepted")
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
    return TranscriptAcceptanceGateDecisionV556(
        gate_id=fixture.gate_id,
        accepted_for_local_intake_stage=accepted,
        reason_codes=tuple(reasons or ["local_intake_stage_accepted"]),
        local_intake_record_id=f"local-intake-{fixture.gate_id}" if accepted else None,
    )


def run_transcript_acceptance_gate_v556(
    v555_dependency: dict[str, Any],
    intake_matrix: dict[str, Any],
    transcript_packet: dict[str, Any],
    fixtures: list[TranscriptAcceptanceGateFixtureV556] | None = None,
) -> dict[str, Any]:
    gate_fixtures = fixtures or default_transcript_acceptance_gate_fixtures_v556()
    decisions = [evaluate_transcript_acceptance_gate_v556(fixture, v555_dependency, intake_matrix, transcript_packet).to_dict() for fixture in gate_fixtures]
    reason_codes = sorted({reason for decision in decisions for reason in decision["reason_codes"]})
    required_denials = {
        "v555_signoff_registry_missing",
        "external_signoff_intake_matrix_missing",
        "signed_closure_transcript_packet_missing",
        "claim_boundary_ack_missing",
        "external_reviewer_identity_payload_missing",
        "reviewer_authorization_payload_missing",
        "reviewer_recheck_payload_missing",
        "signed_signoff_manifest_payload_missing",
        "signed_closure_transcript_payload_missing",
        "closure_timestamp_payload_missing",
        "owner_counter_attestation_payload_missing",
        "immutable_transcript_anchor_payload_missing",
        "real_external_signoff_intake_not_accepted",
        "signed_closure_transcript_not_accepted",
        "real_closure_signoff_not_ready",
        "real_review_finding_closure_not_ready",
        "real_external_review_not_ready",
        "real_external_pilot_not_ready",
        "production_release_not_allowed",
        "bic_os_unlock_not_allowed",
    }
    accepted_count = sum(1 for decision in decisions if decision["accepted_for_local_intake_stage"])
    denied_count = len(decisions) - accepted_count
    gate = {
        "version": "v5.56",
        "transcript_acceptance_gate_ready": accepted_count == len(LOCAL_INTAKE_STAGES_V556) and denied_count == 10 and required_denials.issubset(set(reason_codes)),
        "gate_fixture_count": len(gate_fixtures),
        "accepted_local_intake_stage_count": accepted_count,
        "denied_transcript_acceptance_gate_count": denied_count,
        "reason_codes": reason_codes,
        "fixtures": [fixture.to_dict() for fixture in gate_fixtures],
        "decisions": decisions,
        "real_external_signoff_intake_ready": False,
        "real_external_signoff_accepted": False,
        "signed_closure_transcript_accepted": False,
        "real_closure_signoff_ready": False,
        "real_review_finding_closure_ready": False,
        "real_external_review_ready": False,
        "real_external_pilot_ready": False,
        "production_release_ready": False,
        "production_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    gate["transcript_acceptance_gate_sha256"] = stable_hash(gate)
    return gate


def build_transcript_acceptance_blocker_register_v556(
    intake_matrix: dict[str, Any],
    transcript_gate: dict[str, Any],
) -> dict[str, Any]:
    blockers: list[dict[str, Any]] = []
    for decision in intake_matrix.get("decisions", []):
        if decision.get("real_external_signoff_accepted") is not True or decision.get("signed_closure_transcript_accepted") is not True or decision.get("review_finding_closed") is not True:
            blockers.append(
                {
                    "version": "v5.56",
                    "blocker_id": f"signoff-intake-blocker-{decision['record_id']}",
                    "source": "external_signoff_intake_matrix",
                    "record_id": decision.get("record_id"),
                    "reason_codes": decision.get("reason_codes", []),
                    "must_be_resolved_before_external_signoff_acceptance": True,
                    "must_be_resolved_before_signed_transcript_acceptance": True,
                    "must_be_resolved_before_review_closure": True,
                    "must_be_resolved_before_external_review": True,
                    "must_be_resolved_before_real_pilot": True,
                    "must_be_resolved_before_production": True,
                    "must_be_resolved_before_bic_os": True,
                }
            )
    for decision in transcript_gate.get("decisions", []):
        if decision.get("accepted_for_local_intake_stage") is not True:
            blockers.append(
                {
                    "version": "v5.56",
                    "blocker_id": f"transcript-gate-blocker-{decision['gate_id']}",
                    "source": "transcript_acceptance_gate",
                    "record_id": decision.get("gate_id"),
                    "reason_codes": decision.get("reason_codes", []),
                    "must_be_resolved_before_external_signoff_acceptance": True,
                    "must_be_resolved_before_signed_transcript_acceptance": True,
                    "must_be_resolved_before_review_closure": True,
                    "must_be_resolved_before_external_review": True,
                    "must_be_resolved_before_real_pilot": True,
                    "must_be_resolved_before_production": True,
                    "must_be_resolved_before_bic_os": True,
                }
            )
    for blocker in blockers:
        blocker["blocker_sha256"] = stable_hash(blocker)
    register = {
        "version": "v5.56",
        "transcript_acceptance_blocker_register_ready": len(blockers) == len(SIGNOFF_INTAKE_RECORD_TYPES_V556) + 10,
        "blocker_count": len(blockers),
        "blockers": blockers,
        "real_external_signoff_intake_ready": False,
        "real_external_signoff_accepted": False,
        "signed_closure_transcript_accepted": False,
        "real_closure_signoff_ready": False,
        "real_review_finding_closure_ready": False,
        "real_external_review_ready": False,
        "real_external_pilot_ready": False,
        "production_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    register["transcript_acceptance_blocker_register_sha256"] = stable_hash(register)
    return register


def build_external_signoff_transcript_intake_audit_bundle_v556(
    policy: dict[str, Any],
    intake_matrix: dict[str, Any],
    transcript_packet: dict[str, Any],
    transcript_gate: dict[str, Any],
    blocker_register: dict[str, Any],
) -> dict[str, Any]:
    bundle_ready = (
        policy.get("external_signoff_transcript_intake_policy_ready") is True
        and intake_matrix.get("external_signoff_intake_matrix_ready") is True
        and transcript_packet.get("signed_closure_transcript_packet_ready") is True
        and transcript_gate.get("transcript_acceptance_gate_ready") is True
        and blocker_register.get("transcript_acceptance_blocker_register_ready") is True
    )
    bundle = {
        "version": "v5.56",
        "external_signoff_transcript_intake_audit_bundle_ready": bundle_ready,
        "policy_sha256": policy.get("external_signoff_transcript_intake_policy_sha256"),
        "intake_matrix_sha256": intake_matrix.get("external_signoff_intake_matrix_sha256"),
        "transcript_packet_sha256": transcript_packet.get("signed_closure_transcript_packet_sha256"),
        "transcript_gate_sha256": transcript_gate.get("transcript_acceptance_gate_sha256"),
        "blocker_register_sha256": blocker_register.get("transcript_acceptance_blocker_register_sha256"),
        "real_external_signoff_intake_ready": False,
        "real_external_signoff_accepted": False,
        "signed_closure_transcript_accepted": False,
        "real_closure_signoff_ready": False,
        "real_review_finding_closure_ready": False,
        "real_external_review_ready": False,
        "real_external_pilot_ready": False,
        "production_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    bundle["external_signoff_transcript_intake_audit_bundle_sha256"] = stable_hash(bundle)
    return bundle


def run_external_signoff_transcript_intake_workflow_v556(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    project_root = Path(root).resolve()
    out = project_root / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    v555_dependency = run_closure_signoff_registry_workflow_v555(project_root, out.parent / "d556")
    policy = build_external_signoff_transcript_intake_policy_v556()
    intake_matrix = build_external_signoff_intake_matrix_v556(v555_dependency)
    transcript_packet = build_signed_closure_transcript_packet_v556(v555_dependency, intake_matrix)
    transcript_gate = run_transcript_acceptance_gate_v556(v555_dependency, intake_matrix, transcript_packet)
    blocker_register = build_transcript_acceptance_blocker_register_v556(intake_matrix, transcript_gate)
    audit_bundle = build_external_signoff_transcript_intake_audit_bundle_v556(policy, intake_matrix, transcript_packet, transcript_gate, blocker_register)
    proof_ready = (
        v555_dependency.get("closure_signoff_registry_contract_ready") is True
        and policy.get("external_signoff_transcript_intake_policy_ready") is True
        and intake_matrix.get("external_signoff_intake_matrix_ready") is True
        and transcript_packet.get("signed_closure_transcript_packet_ready") is True
        and transcript_gate.get("transcript_acceptance_gate_ready") is True
        and blocker_register.get("transcript_acceptance_blocker_register_ready") is True
        and audit_bundle.get("external_signoff_transcript_intake_audit_bundle_ready") is True
    )
    audit = {
        "version": "v5.56",
        "phase": "real_external_signoff_intake_signed_closure_transcript_acceptance_contract",
        "overall_status": "external_signoff_transcript_intake_contract_ready_signoff_not_accepted" if proof_ready else "external_signoff_transcript_intake_contract_incomplete",
        "active_phase": "biosdk_external_signoff_transcript_intake_proof",
        "bic_os_phase_locked": True,
        "external_signoff_transcript_intake_contract_ready": proof_ready,
        "v555_dependency_ready": v555_dependency.get("closure_signoff_registry_contract_ready") is True,
        "external_signoff_transcript_intake_policy_ready": policy.get("external_signoff_transcript_intake_policy_ready") is True,
        "external_signoff_intake_matrix_ready": intake_matrix.get("external_signoff_intake_matrix_ready") is True,
        "signed_closure_transcript_packet_ready": transcript_packet.get("signed_closure_transcript_packet_ready") is True,
        "transcript_acceptance_gate_ready": transcript_gate.get("transcript_acceptance_gate_ready") is True,
        "transcript_acceptance_blocker_register_ready": blocker_register.get("transcript_acceptance_blocker_register_ready") is True,
        "external_signoff_transcript_intake_audit_bundle_ready": audit_bundle.get("external_signoff_transcript_intake_audit_bundle_ready") is True,
        "artifact_name": v555_dependency.get("artifact_name"),
        "artifact_sha256": v555_dependency.get("artifact_sha256"),
        "signoff_intake_record_count": intake_matrix.get("signoff_intake_record_count"),
        "local_signoff_intake_record_ready_count": intake_matrix.get("local_signoff_intake_record_ready_count"),
        "local_transcript_reference_ready_count": intake_matrix.get("local_transcript_reference_ready_count"),
        "transcript_packet_section_count": transcript_packet.get("transcript_packet_section_count"),
        "local_transcript_packet_section_ready_count": transcript_packet.get("local_transcript_packet_section_ready_count"),
        "real_external_signoff_accepted_count": intake_matrix.get("real_external_signoff_accepted_count"),
        "signed_closure_transcript_accepted_count": intake_matrix.get("signed_closure_transcript_accepted_count"),
        "review_finding_closed_count": intake_matrix.get("review_finding_closed_count"),
        "accepted_local_intake_stage_count": transcript_gate.get("accepted_local_intake_stage_count"),
        "denied_transcript_acceptance_gate_count": transcript_gate.get("denied_transcript_acceptance_gate_count"),
        "transcript_acceptance_blocker_count": blocker_register.get("blocker_count"),
        "real_external_signoff_intake_ready": False,
        "real_external_signoff_accepted": False,
        "signed_closure_transcript_accepted": False,
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
        "external_signoff_transcript_intake_policy": policy,
        "external_signoff_intake_matrix": intake_matrix,
        "signed_closure_transcript_packet": transcript_packet,
        "transcript_acceptance_gate": transcript_gate,
        "transcript_acceptance_blocker_register": blocker_register,
        "external_signoff_transcript_intake_audit_bundle": audit_bundle,
        "v555_dependency_summary": {
            key: value
            for key, value in v555_dependency.items()
            if key
            not in {
                "closure_signoff_registry_policy",
                "signoff_registry_matrix",
                "closure_signoff_audit_trail",
                "external_reviewer_signoff_packet",
                "signoff_registry_gate",
                "signoff_registry_blocker_register",
                "closure_signoff_registry_audit_bundle",
                "v554_dependency_summary",
            }
        },
        "missing_real_inputs": [
            "real external reviewer identity evidence",
            "reviewer authorization evidence",
            "reviewer recheck evidence",
            "signed external reviewer signoff manifest",
            "signed closure transcript",
            "closure timestamp evidence",
            "owner counter-attestation",
            "immutable transcript anchor",
            "real finding closure crosswalk",
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
        "production_distance_assessment": {
            "distance": "far",
            "reason": "v5.56 adds the intake and acceptance gate for real signoff material, but production still needs actual signed external reviewer payloads, pilot acceptance, production identity/storage/registry/CI services, hosted API/dashboard enforcement and operational runtime supervision",
            "minimum_missing_evidence_families": 6,
        },
        "bic_os_distance_assessment": {
            "distance": "very_far",
            "reason": "BiC OS remains after full BioSDK, production BioCompute Runtime, NSI/control-plane maturity, durable daemon scheduling, permissions, service supervision and real-world validation",
            "bic_os_phase_locked": True,
        },
        "direct_answer": {
            "did_we_add_real_external_signoff_intake_contract": "yes" if intake_matrix.get("external_signoff_intake_matrix_ready") else "no",
            "did_we_add_signed_closure_transcript_acceptance_gate": "yes" if transcript_gate.get("transcript_acceptance_gate_ready") else "no",
            "are_real_external_signoffs_accepted": "no",
            "are_signed_closure_transcripts_accepted": "no",
            "are_real_review_findings_closed": "no",
            "is_real_external_review_ready": "no",
            "is_real_external_pilot_ready": "no",
            "is_production_ready": "no_far",
            "is_full_biosdk_ready": "no",
            "is_biocompute_runtime_ready": "no",
            "is_bic_os_ready": "no_very_far",
            "next_best_build_step": "add external reviewer identity and signature verification contract over imported signoff packages" if proof_ready else "fix v5.56 signoff-intake blockers first",
        },
        "claim_boundary": "v5.56 proves a local intake contract for real external reviewer signoff payloads and a signed closure transcript acceptance gate over the v5.55 closure signoff registry contract. It does not accept real external signoffs, does not accept signed closure transcripts, does not close review findings, and does not claim completed external review, real external pilot readiness, production readiness, full BioSDK, production BioCompute Runtime or BiC OS readiness.",
    }
    audit["external_signoff_transcript_intake_audit_sha256"] = stable_hash({key: value for key, value in audit.items() if key != "external_signoff_transcript_intake_audit_sha256"})
    return audit


def write_external_signoff_transcript_intake_outputs_v556(audit: dict[str, Any], out_dir: str | Path = DEFAULT_OUT) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary_json": out / "V556_EXTERNAL_SIGNOFF_TRANSCRIPT_INTAKE_SUMMARY.json",
        "policy_json": out / "V556_EXTERNAL_SIGNOFF_TRANSCRIPT_INTAKE_POLICY.json",
        "intake_matrix_json": out / "V556_EXTERNAL_SIGNOFF_INTAKE_MATRIX.json",
        "transcript_packet_json": out / "V556_SIGNED_CLOSURE_TRANSCRIPT_PACKET.json",
        "transcript_gate_json": out / "V556_TRANSCRIPT_ACCEPTANCE_GATE.json",
        "blocker_register_json": out / "V556_TRANSCRIPT_ACCEPTANCE_BLOCKER_REGISTER.json",
        "audit_bundle_json": out / "V556_EXTERNAL_SIGNOFF_TRANSCRIPT_INTAKE_AUDIT_BUNDLE.json",
        "intake_matrix_csv": out / "V556_EXTERNAL_SIGNOFF_INTAKE_MATRIX.csv",
        "transcript_gate_csv": out / "V556_TRANSCRIPT_ACCEPTANCE_GATE.csv",
        "markdown_report": out / "BIOGPU_V556_EXTERNAL_SIGNOFF_TRANSCRIPT_INTAKE_REPORT.md",
    }
    summary = {
        key: value
        for key, value in audit.items()
        if key
        not in {
            "external_signoff_transcript_intake_policy",
            "external_signoff_intake_matrix",
            "signed_closure_transcript_packet",
            "transcript_acceptance_gate",
            "transcript_acceptance_blocker_register",
            "external_signoff_transcript_intake_audit_bundle",
        }
    }
    paths["summary_json"].write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["policy_json"].write_text(json.dumps(audit["external_signoff_transcript_intake_policy"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["intake_matrix_json"].write_text(json.dumps(audit["external_signoff_intake_matrix"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["transcript_packet_json"].write_text(json.dumps(audit["signed_closure_transcript_packet"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["transcript_gate_json"].write_text(json.dumps(audit["transcript_acceptance_gate"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["blocker_register_json"].write_text(json.dumps(audit["transcript_acceptance_blocker_register"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["audit_bundle_json"].write_text(json.dumps(audit["external_signoff_transcript_intake_audit_bundle"], indent=2, ensure_ascii=False), encoding="utf-8")
    _write_intake_matrix_csv(paths["intake_matrix_csv"], audit["external_signoff_intake_matrix"].get("decisions", []))
    _write_transcript_gate_csv(paths["transcript_gate_csv"], audit["transcript_acceptance_gate"].get("decisions", []))
    paths["markdown_report"].write_text(_markdown_report(audit), encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}


def _write_intake_matrix_csv(path: Path, decisions: list[dict[str, Any]]) -> None:
    fieldnames = [
        "record_id",
        "record_type",
        "intake_domain",
        "local_signoff_intake_record_ready",
        "local_transcript_reference_ready",
        "real_external_signoff_accepted",
        "signed_closure_transcript_accepted",
        "review_finding_closed",
        "local_anchor",
        "reason_codes",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for decision in decisions:
            row = {field: decision.get(field) for field in fieldnames}
            row["reason_codes"] = " | ".join(str(reason) for reason in decision.get("reason_codes", []))
            writer.writerow(row)


def _write_transcript_gate_csv(path: Path, decisions: list[dict[str, Any]]) -> None:
    fieldnames = ["gate_id", "accepted_for_local_intake_stage", "local_intake_record_id", "reason_codes"]
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
        "# BioGPU-Core v5.56 External Signoff Transcript Intake Contract",
        "",
        "## Direct Answer",
        "",
        f"- Real external signoff intake contract added: `{answer['did_we_add_real_external_signoff_intake_contract']}`",
        f"- Signed closure transcript acceptance gate added: `{answer['did_we_add_signed_closure_transcript_acceptance_gate']}`",
        f"- Real external signoffs accepted: `{answer['are_real_external_signoffs_accepted']}`",
        f"- Signed closure transcripts accepted: `{answer['are_signed_closure_transcripts_accepted']}`",
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
        f"- v5.55 dependency ready: `{audit['v555_dependency_ready']}`",
        f"- Signoff intake records: `{audit['signoff_intake_record_count']}`",
        f"- Local intake-ready records: `{audit['local_signoff_intake_record_ready_count']}`",
        f"- Transcript packet sections: `{audit['transcript_packet_section_count']}`",
        f"- Real external signoffs accepted: `{audit['real_external_signoff_accepted_count']}`",
        f"- Signed closure transcripts accepted: `{audit['signed_closure_transcript_accepted_count']}`",
        f"- Review findings closed: `{audit['review_finding_closed_count']}`",
        f"- Accepted local intake stages: `{audit['accepted_local_intake_stage_count']}`",
        f"- Denied transcript gates: `{audit['denied_transcript_acceptance_gate_count']}`",
        "",
        "## Missing Real Inputs",
        "",
    ]
    for missing in audit["missing_real_inputs"]:
        lines.append(f"- {missing}")
    lines.extend(["", "## Boundary", "", audit["claim_boundary"], ""])
    return "\n".join(lines)