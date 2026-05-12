"""External reviewer questionnaire scoring and signed response intake proof, v5.52."""
from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from biogpu.beta.job_model_v43 import utc_now_iso
from biogpu.evidence.ledger_v53 import stable_hash
from biogpu.sdk.partner_dataroom_review_packet_v551 import run_partner_dataroom_review_packet_workflow_v551


DEFAULT_OUT = Path("outputs/v552_external_reviewer_response_intake")
REVIEW_QUESTIONNAIRE_DOMAINS_V552 = (
    "claim_boundary",
    "evidence_completeness",
    "security_identity",
    "storage_retention",
    "registry_distribution",
    "pilot_readiness",
    "incident_support",
    "production_operations",
    "biocompute_runtime",
    "bic_os_boundary",
)
SIGNED_RESPONSE_SECTIONS_V552 = (
    "reviewer_identity",
    "questionnaire_scores",
    "finding_register",
    "signature_attestation",
    "response_timestamp",
    "claim_boundary_acknowledgement",
)
LOCAL_RESPONSE_STAGES_V552 = ("questionnaire_scoring", "response_packet_assembly", "signature_preflight")


@dataclass(frozen=True)
class ExternalReviewerResponsePolicyV552:
    policy_id: str
    questionnaire_domains: tuple[str, ...]
    signed_response_sections: tuple[str, ...]
    local_response_stages: tuple[str, ...]
    requires_v551_dataroom_packet: bool
    requires_questionnaire_scoring: bool
    requires_signed_response_packet: bool
    requires_external_reviewer_identity: bool
    requires_external_reviewer_signature: bool
    requires_review_session_timestamp: bool
    local_contract_only: bool = True
    real_signed_review_response_ready: bool = False
    real_external_review_ready: bool = False
    real_external_pilot_ready: bool = False
    production_ready: bool = False
    full_biosdk_ready: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class QuestionnaireResponseFixtureV552:
    response_id: str
    domain: str
    score: int
    has_v551_anchor: bool
    has_local_score: bool
    has_evidence_reference: bool
    has_claim_boundary_ack: bool
    has_blocker_notes: bool
    has_external_reviewer_identity: bool
    has_external_reviewer_signature: bool
    has_review_session_timestamp: bool
    requests_external_review_completion: bool
    requests_real_external_pilot: bool
    requests_production_release: bool
    requests_bic_os_unlock: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class QuestionnaireScoreDecisionV552:
    response_id: str
    domain: str
    score: int
    local_questionnaire_score_ready: bool
    signed_review_response_ready: bool
    score_band: str
    reason_codes: tuple[str, ...]
    local_anchor: str | None
    real_external_review_ready: bool = False
    real_external_pilot_ready: bool = False
    production_ready: bool = False
    full_biosdk_ready: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SignedReviewResponseGateFixtureV552:
    gate_id: str
    has_v551_dataroom_packet: bool
    has_questionnaire_scores: bool
    has_signed_response_packet: bool
    has_claim_boundary_ack: bool
    has_no_open_review_findings: bool
    has_external_reviewer_identity: bool
    has_external_reviewer_signature: bool
    has_review_session_timestamp: bool
    requests_external_review_completion: bool
    requests_real_external_pilot: bool
    requests_production_release: bool
    requests_bic_os_unlock: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SignedReviewResponseGateDecisionV552:
    gate_id: str
    accepted_for_local_response_stage: bool
    reason_codes: tuple[str, ...]
    local_response_record_id: str | None
    real_signed_review_response_ready: bool = False
    real_external_review_ready: bool = False
    real_external_pilot_ready: bool = False
    production_release_ready: bool = False
    full_biosdk_ready: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_external_reviewer_response_policy_v552() -> dict[str, Any]:
    policy = ExternalReviewerResponsePolicyV552(
        policy_id="BIOGPU_CORE_V552_EXTERNAL_REVIEWER_RESPONSE_INTAKE_POLICY",
        questionnaire_domains=REVIEW_QUESTIONNAIRE_DOMAINS_V552,
        signed_response_sections=SIGNED_RESPONSE_SECTIONS_V552,
        local_response_stages=LOCAL_RESPONSE_STAGES_V552,
        requires_v551_dataroom_packet=True,
        requires_questionnaire_scoring=True,
        requires_signed_response_packet=True,
        requires_external_reviewer_identity=True,
        requires_external_reviewer_signature=True,
        requires_review_session_timestamp=True,
    )
    result = {
        "version": "v5.52",
        "external_reviewer_response_policy_ready": True,
        "policy": policy.to_dict(),
        "blocked_modes": ["real_signed_review_response", "real_external_review", "real_external_pilot", "production_release", "production_ready_claim", "bic_os_unlock"],
        "required_real_records": ["external_reviewer_identity", "external_reviewer_signature", "review_session_timestamp", "signed_response_payload", "immutable_review_transcript"],
        "real_signed_review_response_ready": False,
        "real_external_review_ready": False,
        "real_external_pilot_ready": False,
        "production_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    result["external_reviewer_response_policy_sha256"] = stable_hash(result)
    return result


def default_questionnaire_response_fixtures_v552() -> list[QuestionnaireResponseFixtureV552]:
    fixtures: list[QuestionnaireResponseFixtureV552] = []
    score_by_domain = {
        "claim_boundary": 92,
        "evidence_completeness": 74,
        "security_identity": 42,
        "storage_retention": 48,
        "registry_distribution": 45,
        "pilot_readiness": 35,
        "incident_support": 50,
        "production_operations": 38,
        "biocompute_runtime": 40,
        "bic_os_boundary": 88,
    }
    for domain in REVIEW_QUESTIONNAIRE_DOMAINS_V552:
        fixtures.append(
            QuestionnaireResponseFixtureV552(
                response_id=f"review-response-{domain}",
                domain=domain,
                score=score_by_domain[domain],
                has_v551_anchor=True,
                has_local_score=True,
                has_evidence_reference=True,
                has_claim_boundary_ack=True,
                has_blocker_notes=True,
                has_external_reviewer_identity=False,
                has_external_reviewer_signature=False,
                has_review_session_timestamp=False,
                requests_external_review_completion=domain == "evidence_completeness",
                requests_real_external_pilot=domain == "pilot_readiness",
                requests_production_release=domain == "production_operations",
                requests_bic_os_unlock=domain == "bic_os_boundary",
            )
        )
    return fixtures


def _score_band(score: int) -> str:
    if score >= 85:
        return "strong_local_answer"
    if score >= 60:
        return "partial_local_answer"
    return "blocked_before_real_review"


def evaluate_questionnaire_response_v552(fixture: QuestionnaireResponseFixtureV552, v551_dependency: dict[str, Any]) -> QuestionnaireScoreDecisionV552:
    reasons: list[str] = []
    if v551_dependency.get("partner_dataroom_review_packet_contract_ready") is not True or not fixture.has_v551_anchor:
        reasons.append("v551_dataroom_review_packet_missing")
    if fixture.domain not in REVIEW_QUESTIONNAIRE_DOMAINS_V552:
        reasons.append("questionnaire_domain_not_allowed")
    if not fixture.has_local_score:
        reasons.append("local_score_missing")
    if not fixture.has_evidence_reference:
        reasons.append("evidence_reference_missing")
    if not fixture.has_claim_boundary_ack:
        reasons.append("claim_boundary_ack_missing")
    if not fixture.has_blocker_notes:
        reasons.append("blocker_notes_missing")
    local_ready = not any(
        reason in reasons
        for reason in {
            "v551_dataroom_review_packet_missing",
            "questionnaire_domain_not_allowed",
            "local_score_missing",
            "evidence_reference_missing",
            "claim_boundary_ack_missing",
            "blocker_notes_missing",
        }
    )
    if not fixture.has_external_reviewer_identity:
        reasons.append("external_reviewer_identity_missing")
    if not fixture.has_external_reviewer_signature:
        reasons.append("external_reviewer_signature_missing")
    if not fixture.has_review_session_timestamp:
        reasons.append("review_session_timestamp_missing")
    if fixture.requests_external_review_completion:
        reasons.append("real_external_review_not_ready")
    if fixture.requests_real_external_pilot:
        reasons.append("real_external_pilot_not_ready")
    if fixture.requests_production_release:
        reasons.append("production_release_not_allowed")
    if fixture.requests_bic_os_unlock:
        reasons.append("bic_os_unlock_not_allowed")
    return QuestionnaireScoreDecisionV552(
        response_id=fixture.response_id,
        domain=fixture.domain,
        score=fixture.score,
        local_questionnaire_score_ready=local_ready,
        signed_review_response_ready=False,
        score_band=_score_band(fixture.score),
        reason_codes=tuple(reasons or ["signed_review_response_ready"]),
        local_anchor=str(v551_dependency.get("partner_dataroom_review_packet_audit_sha256") or "") or None,
    )


def build_questionnaire_scoring_matrix_v552(v551_dependency: dict[str, Any], fixtures: list[QuestionnaireResponseFixtureV552] | None = None) -> dict[str, Any]:
    response_fixtures = fixtures or default_questionnaire_response_fixtures_v552()
    decisions = [evaluate_questionnaire_response_v552(fixture, v551_dependency).to_dict() for fixture in response_fixtures]
    local_ready_count = sum(1 for decision in decisions if decision["local_questionnaire_score_ready"])
    signed_ready_count = sum(1 for decision in decisions if decision["signed_review_response_ready"])
    domains = sorted({decision["domain"] for decision in decisions})
    reason_codes = sorted({reason for decision in decisions for reason in decision["reason_codes"]})
    score_bands = sorted({decision["score_band"] for decision in decisions})
    required_reasons = {
        "external_reviewer_identity_missing",
        "external_reviewer_signature_missing",
        "review_session_timestamp_missing",
        "real_external_review_not_ready",
        "real_external_pilot_not_ready",
        "production_release_not_allowed",
        "bic_os_unlock_not_allowed",
    }
    matrix = {
        "version": "v5.52",
        "questionnaire_scoring_matrix_ready": local_ready_count == len(REVIEW_QUESTIONNAIRE_DOMAINS_V552) and signed_ready_count == 0 and set(domains) == set(REVIEW_QUESTIONNAIRE_DOMAINS_V552) and required_reasons.issubset(set(reason_codes)),
        "questionnaire_domain_count": len(decisions),
        "local_questionnaire_score_ready_count": local_ready_count,
        "signed_review_response_ready_count": signed_ready_count,
        "domains": domains,
        "score_bands": score_bands,
        "reason_codes": reason_codes,
        "fixtures": [fixture.to_dict() for fixture in response_fixtures],
        "decisions": decisions,
        "real_signed_review_response_ready": False,
        "real_external_review_ready": False,
        "real_external_pilot_ready": False,
        "production_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    matrix["questionnaire_scoring_matrix_sha256"] = stable_hash(matrix)
    return matrix


def build_signed_review_response_packet_v552(v551_dependency: dict[str, Any], scoring_matrix: dict[str, Any]) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for decision in scoring_matrix.get("decisions", []):
        if decision.get("local_questionnaire_score_ready") is not True:
            continue
        record = {
            "version": "v5.52",
            "signed_response_record_id": f"signed-packet-{decision['response_id']}",
            "domain": decision.get("domain"),
            "score": decision.get("score"),
            "score_band": decision.get("score_band"),
            "v551_dataroom_packet_anchor": v551_dependency.get("partner_dataroom_review_packet_audit_sha256"),
            "questionnaire_matrix_anchor": scoring_matrix.get("questionnaire_scoring_matrix_sha256"),
            "local_response_packet_record_ready": True,
            "external_reviewer_signature_present": False,
            "review_session_timestamp_present": False,
            "signed_review_response_ready": False,
            "real_external_review_ready": False,
            "real_external_pilot_ready": False,
            "production_ready": False,
            "created_at": utc_now_iso(),
        }
        record["signed_response_record_sha256"] = stable_hash(record)
        records.append(record)
    packet = {
        "version": "v5.52",
        "signed_review_response_packet_ready": len(records) == len(REVIEW_QUESTIONNAIRE_DOMAINS_V552) and scoring_matrix.get("questionnaire_scoring_matrix_ready") is True,
        "response_packet_record_count": len(records),
        "local_response_packet_record_ready_count": sum(1 for record in records if record["local_response_packet_record_ready"]),
        "signed_review_response_ready_count": sum(1 for record in records if record["signed_review_response_ready"]),
        "external_review_completed_count": 0,
        "signed_response_records": records,
        "real_signed_review_response_ready": False,
        "real_external_review_ready": False,
        "real_external_pilot_ready": False,
        "production_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    packet["signed_review_response_packet_sha256"] = stable_hash(packet)
    return packet


def default_signed_review_response_gate_fixtures_v552() -> list[SignedReviewResponseGateFixtureV552]:
    return [
        SignedReviewResponseGateFixtureV552("questionnaire-scoring", True, True, True, True, False, True, True, True, False, False, False, False),
        SignedReviewResponseGateFixtureV552("response-packet-assembly", True, True, True, True, False, True, True, True, False, False, False, False),
        SignedReviewResponseGateFixtureV552("signature-preflight", True, True, True, True, False, True, True, True, False, False, False, False),
        SignedReviewResponseGateFixtureV552("missing-v551-contract", False, True, True, True, False, True, True, True, False, False, False, False),
        SignedReviewResponseGateFixtureV552("missing-questionnaire-scores", True, False, True, True, False, True, True, True, False, False, False, False),
        SignedReviewResponseGateFixtureV552("missing-response-packet", True, True, False, True, False, True, True, True, False, False, False, False),
        SignedReviewResponseGateFixtureV552("missing-claim-boundary", True, True, True, False, False, True, True, True, False, False, False, False),
        SignedReviewResponseGateFixtureV552("missing-signed-review-response", True, True, True, True, True, False, False, False, True, False, False, False),
        SignedReviewResponseGateFixtureV552("review-completion-with-open-findings", True, True, True, True, False, True, True, True, True, False, False, False),
        SignedReviewResponseGateFixtureV552("real-pilot-request", True, True, True, True, True, True, True, True, False, True, False, False),
        SignedReviewResponseGateFixtureV552("production-release-request", True, True, True, True, True, True, True, True, False, False, True, False),
        SignedReviewResponseGateFixtureV552("bic-os-unlock-request", True, True, True, True, True, True, True, True, False, False, False, True),
    ]


def evaluate_signed_review_response_gate_v552(fixture: SignedReviewResponseGateFixtureV552, v551_dependency: dict[str, Any], scoring_matrix: dict[str, Any], response_packet: dict[str, Any]) -> SignedReviewResponseGateDecisionV552:
    reasons: list[str] = []
    if v551_dependency.get("partner_dataroom_review_packet_contract_ready") is not True or not fixture.has_v551_dataroom_packet:
        reasons.append("v551_dataroom_review_packet_missing")
    if scoring_matrix.get("questionnaire_scoring_matrix_ready") is not True or not fixture.has_questionnaire_scores:
        reasons.append("questionnaire_scores_missing")
    if response_packet.get("signed_review_response_packet_ready") is not True or not fixture.has_signed_response_packet:
        reasons.append("signed_response_packet_missing")
    if not fixture.has_claim_boundary_ack:
        reasons.append("claim_boundary_ack_missing")
    if fixture.requests_external_review_completion:
        if not fixture.has_no_open_review_findings:
            reasons.append("review_findings_still_open")
        if not fixture.has_external_reviewer_identity:
            reasons.append("external_reviewer_identity_missing")
        if not fixture.has_external_reviewer_signature:
            reasons.append("external_reviewer_signature_missing")
        if not fixture.has_review_session_timestamp:
            reasons.append("review_session_timestamp_missing")
        reasons.append("real_external_review_not_ready")
    if fixture.requests_real_external_pilot:
        reasons.append("real_external_pilot_not_ready")
    if fixture.requests_production_release:
        reasons.append("production_release_not_allowed")
    if fixture.requests_bic_os_unlock:
        reasons.append("bic_os_unlock_not_allowed")
    accepted = not reasons
    return SignedReviewResponseGateDecisionV552(
        gate_id=fixture.gate_id,
        accepted_for_local_response_stage=accepted,
        reason_codes=tuple(reasons or ["local_response_stage_accepted"]),
        local_response_record_id=f"local-response-{fixture.gate_id}" if accepted else None,
    )


def run_signed_review_response_gate_v552(v551_dependency: dict[str, Any], scoring_matrix: dict[str, Any], response_packet: dict[str, Any], fixtures: list[SignedReviewResponseGateFixtureV552] | None = None) -> dict[str, Any]:
    gate_fixtures = fixtures or default_signed_review_response_gate_fixtures_v552()
    decisions = [evaluate_signed_review_response_gate_v552(fixture, v551_dependency, scoring_matrix, response_packet).to_dict() for fixture in gate_fixtures]
    accepted_count = sum(1 for decision in decisions if decision["accepted_for_local_response_stage"])
    denied_count = len(decisions) - accepted_count
    reason_codes = sorted({reason for decision in decisions for reason in decision["reason_codes"]})
    required_denials = {
        "v551_dataroom_review_packet_missing",
        "questionnaire_scores_missing",
        "signed_response_packet_missing",
        "claim_boundary_ack_missing",
        "review_findings_still_open",
        "external_reviewer_identity_missing",
        "external_reviewer_signature_missing",
        "review_session_timestamp_missing",
        "real_external_review_not_ready",
        "real_external_pilot_not_ready",
        "production_release_not_allowed",
        "bic_os_unlock_not_allowed",
    }
    gate = {
        "version": "v5.52",
        "signed_review_response_gate_ready": accepted_count == len(LOCAL_RESPONSE_STAGES_V552) and denied_count == 9 and required_denials.issubset(set(reason_codes)),
        "gate_fixture_count": len(gate_fixtures),
        "accepted_local_response_stage_count": accepted_count,
        "denied_signed_response_gate_count": denied_count,
        "reason_codes": reason_codes,
        "fixtures": [fixture.to_dict() for fixture in gate_fixtures],
        "decisions": decisions,
        "real_signed_review_response_ready": False,
        "real_external_review_ready": False,
        "real_external_pilot_ready": False,
        "production_release_ready": False,
        "production_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    gate["signed_review_response_gate_sha256"] = stable_hash(gate)
    return gate


def build_signed_response_blocker_register_v552(scoring_matrix: dict[str, Any], response_gate: dict[str, Any]) -> dict[str, Any]:
    blockers: list[dict[str, Any]] = []
    for decision in scoring_matrix.get("decisions", []):
        if decision.get("signed_review_response_ready") is True:
            continue
        blocker = {
            "version": "v5.52",
            "blocker_id": f"questionnaire-blocker-{decision['response_id']}",
            "source": "questionnaire_scoring_matrix",
            "record_id": decision.get("response_id"),
            "reason_codes": decision.get("reason_codes", []),
            "must_be_resolved_before_signed_response": True,
            "must_be_resolved_before_external_review": True,
            "must_be_resolved_before_real_pilot": True,
            "must_be_resolved_before_production": True,
            "must_be_resolved_before_bic_os": True,
        }
        blocker["blocker_sha256"] = stable_hash(blocker)
        blockers.append(blocker)
    for decision in response_gate.get("decisions", []):
        if decision.get("accepted_for_local_response_stage") is True:
            continue
        blocker = {
            "version": "v5.52",
            "blocker_id": f"signed-response-gate-blocker-{decision['gate_id']}",
            "source": "signed_review_response_gate",
            "record_id": decision.get("gate_id"),
            "reason_codes": decision.get("reason_codes", []),
            "must_be_resolved_before_signed_response": True,
            "must_be_resolved_before_external_review": True,
            "must_be_resolved_before_real_pilot": True,
            "must_be_resolved_before_production": True,
            "must_be_resolved_before_bic_os": True,
        }
        blocker["blocker_sha256"] = stable_hash(blocker)
        blockers.append(blocker)
    register = {
        "version": "v5.52",
        "signed_response_blocker_register_ready": len(blockers) == len(REVIEW_QUESTIONNAIRE_DOMAINS_V552) + 9,
        "blocker_count": len(blockers),
        "blockers": blockers,
        "real_signed_review_response_ready": False,
        "real_external_review_ready": False,
        "real_external_pilot_ready": False,
        "production_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    register["signed_response_blocker_register_sha256"] = stable_hash(register)
    return register


def build_external_reviewer_response_audit_bundle_v552(policy: dict[str, Any], scoring_matrix: dict[str, Any], response_packet: dict[str, Any], response_gate: dict[str, Any], blocker_register: dict[str, Any]) -> dict[str, Any]:
    bundle_ready = (
        policy.get("external_reviewer_response_policy_ready") is True
        and scoring_matrix.get("questionnaire_scoring_matrix_ready") is True
        and response_packet.get("signed_review_response_packet_ready") is True
        and response_gate.get("signed_review_response_gate_ready") is True
        and blocker_register.get("signed_response_blocker_register_ready") is True
    )
    bundle = {
        "version": "v5.52",
        "external_reviewer_response_audit_bundle_ready": bundle_ready,
        "policy_sha256": policy.get("external_reviewer_response_policy_sha256"),
        "scoring_matrix_sha256": scoring_matrix.get("questionnaire_scoring_matrix_sha256"),
        "response_packet_sha256": response_packet.get("signed_review_response_packet_sha256"),
        "response_gate_sha256": response_gate.get("signed_review_response_gate_sha256"),
        "blocker_register_sha256": blocker_register.get("signed_response_blocker_register_sha256"),
        "real_signed_review_response_ready": False,
        "real_external_review_ready": False,
        "real_external_pilot_ready": False,
        "production_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    bundle["external_reviewer_response_audit_bundle_sha256"] = stable_hash(bundle)
    return bundle


def run_external_reviewer_response_intake_workflow_v552(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    project_root = Path(root).resolve()
    out = project_root / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    v551_dependency = run_partner_dataroom_review_packet_workflow_v551(project_root, out.parent / "d552")
    policy = build_external_reviewer_response_policy_v552()
    scoring_matrix = build_questionnaire_scoring_matrix_v552(v551_dependency)
    response_packet = build_signed_review_response_packet_v552(v551_dependency, scoring_matrix)
    response_gate = run_signed_review_response_gate_v552(v551_dependency, scoring_matrix, response_packet)
    blocker_register = build_signed_response_blocker_register_v552(scoring_matrix, response_gate)
    audit_bundle = build_external_reviewer_response_audit_bundle_v552(policy, scoring_matrix, response_packet, response_gate, blocker_register)
    proof_ready = (
        v551_dependency.get("partner_dataroom_review_packet_contract_ready") is True
        and policy.get("external_reviewer_response_policy_ready") is True
        and scoring_matrix.get("questionnaire_scoring_matrix_ready") is True
        and response_packet.get("signed_review_response_packet_ready") is True
        and response_gate.get("signed_review_response_gate_ready") is True
        and blocker_register.get("signed_response_blocker_register_ready") is True
        and audit_bundle.get("external_reviewer_response_audit_bundle_ready") is True
    )
    audit = {
        "version": "v5.52",
        "phase": "external_reviewer_questionnaire_signed_response_intake_contract",
        "overall_status": "external_reviewer_response_intake_contract_ready_review_not_claimed" if proof_ready else "external_reviewer_response_intake_contract_incomplete",
        "active_phase": "biosdk_external_reviewer_response_intake_proof",
        "bic_os_phase_locked": True,
        "external_reviewer_response_intake_contract_ready": proof_ready,
        "v551_dependency_ready": v551_dependency.get("partner_dataroom_review_packet_contract_ready") is True,
        "external_reviewer_response_policy_ready": policy.get("external_reviewer_response_policy_ready") is True,
        "questionnaire_scoring_matrix_ready": scoring_matrix.get("questionnaire_scoring_matrix_ready") is True,
        "signed_review_response_packet_ready": response_packet.get("signed_review_response_packet_ready") is True,
        "signed_review_response_gate_ready": response_gate.get("signed_review_response_gate_ready") is True,
        "signed_response_blocker_register_ready": blocker_register.get("signed_response_blocker_register_ready") is True,
        "external_reviewer_response_audit_bundle_ready": audit_bundle.get("external_reviewer_response_audit_bundle_ready") is True,
        "artifact_name": v551_dependency.get("artifact_name"),
        "artifact_sha256": v551_dependency.get("artifact_sha256"),
        "questionnaire_domain_count": scoring_matrix.get("questionnaire_domain_count"),
        "local_questionnaire_score_ready_count": scoring_matrix.get("local_questionnaire_score_ready_count"),
        "signed_review_response_ready_count": scoring_matrix.get("signed_review_response_ready_count"),
        "response_packet_record_count": response_packet.get("response_packet_record_count"),
        "external_review_completed_count": response_packet.get("external_review_completed_count"),
        "accepted_local_response_stage_count": response_gate.get("accepted_local_response_stage_count"),
        "denied_signed_response_gate_count": response_gate.get("denied_signed_response_gate_count"),
        "signed_response_blocker_count": blocker_register.get("blocker_count"),
        "real_signed_review_response_ready": False,
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
        "external_reviewer_response_policy": policy,
        "questionnaire_scoring_matrix": scoring_matrix,
        "signed_review_response_packet": response_packet,
        "signed_review_response_gate": response_gate,
        "signed_response_blocker_register": blocker_register,
        "external_reviewer_response_audit_bundle": audit_bundle,
        "v551_dependency_summary": {key: value for key, value in v551_dependency.items() if key not in {"partner_dataroom_policy", "partner_dataroom_manifest", "external_review_packet", "external_review_gate", "external_review_blocker_register", "partner_dataroom_audit_bundle", "v550_dependency_summary"}},
        "missing_real_inputs": [
            "real external reviewer identity records",
            "external reviewer signed questionnaire responses",
            "review session timestamp and immutable transcript",
            "signed review-response payload with verification material",
            "real partner data-room workspace and access-control logs",
            "external reviewer finding register and disposition approvals",
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
            "did_we_add_questionnaire_scoring": "yes" if scoring_matrix.get("questionnaire_scoring_matrix_ready") else "no",
            "did_we_add_signed_review_response_intake_gate": "yes" if response_gate.get("signed_review_response_gate_ready") else "no",
            "are_real_signed_review_responses_ready": "no",
            "is_real_external_review_ready": "no",
            "is_real_external_pilot_ready": "no",
            "is_production_ready": "no",
            "is_full_biosdk_ready": "no",
            "is_biocompute_runtime_ready": "no",
            "is_bic_os_ready": "no",
            "next_best_build_step": "add external review finding triage and remediation-plan proof" if proof_ready else "fix v5.52 reviewer-response intake blockers first",
        },
        "claim_boundary": "v5.52 proves a local external reviewer questionnaire scoring matrix, signed review-response packet shape and signed-response intake gate over the v5.51 partner data-room review packet contract. It does not claim real signed reviewer responses, completed external review, real external pilot readiness, production readiness, full BioSDK, production BioCompute Runtime or BiC OS readiness.",
    }
    audit["external_reviewer_response_intake_audit_sha256"] = stable_hash({key: value for key, value in audit.items() if key != "external_reviewer_response_intake_audit_sha256"})
    return audit


def write_external_reviewer_response_intake_outputs_v552(audit: dict[str, Any], out_dir: str | Path = DEFAULT_OUT) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary_json": out / "V552_EXTERNAL_REVIEWER_RESPONSE_INTAKE_SUMMARY.json",
        "policy_json": out / "V552_EXTERNAL_REVIEWER_RESPONSE_POLICY.json",
        "scoring_matrix_json": out / "V552_QUESTIONNAIRE_SCORING_MATRIX.json",
        "response_packet_json": out / "V552_SIGNED_REVIEW_RESPONSE_PACKET.json",
        "response_gate_json": out / "V552_SIGNED_REVIEW_RESPONSE_GATE.json",
        "blocker_register_json": out / "V552_SIGNED_RESPONSE_BLOCKER_REGISTER.json",
        "audit_bundle_json": out / "V552_EXTERNAL_REVIEWER_RESPONSE_AUDIT_BUNDLE.json",
        "scoring_matrix_csv": out / "V552_QUESTIONNAIRE_SCORING_MATRIX.csv",
        "response_gate_csv": out / "V552_SIGNED_REVIEW_RESPONSE_GATE.csv",
        "markdown_report": out / "BIOGPU_V552_EXTERNAL_REVIEWER_RESPONSE_INTAKE_REPORT.md",
    }
    summary = {key: value for key, value in audit.items() if key not in {"external_reviewer_response_policy", "questionnaire_scoring_matrix", "signed_review_response_packet", "signed_review_response_gate", "signed_response_blocker_register", "external_reviewer_response_audit_bundle"}}
    paths["summary_json"].write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["policy_json"].write_text(json.dumps(audit["external_reviewer_response_policy"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["scoring_matrix_json"].write_text(json.dumps(audit["questionnaire_scoring_matrix"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["response_packet_json"].write_text(json.dumps(audit["signed_review_response_packet"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["response_gate_json"].write_text(json.dumps(audit["signed_review_response_gate"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["blocker_register_json"].write_text(json.dumps(audit["signed_response_blocker_register"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["audit_bundle_json"].write_text(json.dumps(audit["external_reviewer_response_audit_bundle"], indent=2, ensure_ascii=False), encoding="utf-8")
    _write_scoring_matrix_csv(paths["scoring_matrix_csv"], audit["questionnaire_scoring_matrix"].get("decisions", []))
    _write_response_gate_csv(paths["response_gate_csv"], audit["signed_review_response_gate"].get("decisions", []))
    paths["markdown_report"].write_text(_markdown_report(audit), encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}


def _write_scoring_matrix_csv(path: Path, decisions: list[dict[str, Any]]) -> None:
    fieldnames = ["response_id", "domain", "score", "score_band", "local_questionnaire_score_ready", "signed_review_response_ready", "local_anchor", "reason_codes"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for decision in decisions:
            row = {field: decision.get(field) for field in fieldnames}
            row["reason_codes"] = " | ".join(str(reason) for reason in decision.get("reason_codes", []))
            writer.writerow(row)


def _write_response_gate_csv(path: Path, decisions: list[dict[str, Any]]) -> None:
    fieldnames = ["gate_id", "accepted_for_local_response_stage", "local_response_record_id", "reason_codes"]
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
        "# BioGPU-Core v5.52 External Reviewer Response Intake Contract",
        "",
        "## Direct Answer",
        "",
        f"- Questionnaire scoring added: `{answer['did_we_add_questionnaire_scoring']}`",
        f"- Signed review-response intake gate added: `{answer['did_we_add_signed_review_response_intake_gate']}`",
        f"- Real signed review responses ready: `{answer['are_real_signed_review_responses_ready']}`",
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
        f"- v5.51 dependency ready: `{audit['v551_dependency_ready']}`",
        f"- Questionnaire domains: `{audit['questionnaire_domain_count']}`",
        f"- Local score-ready domains: `{audit['local_questionnaire_score_ready_count']}`",
        f"- Signed review-response-ready records: `{audit['signed_review_response_ready_count']}`",
        f"- Response packet records: `{audit['response_packet_record_count']}`",
        f"- External review completed records: `{audit['external_review_completed_count']}`",
        f"- Accepted local response stages: `{audit['accepted_local_response_stage_count']}`",
        f"- Denied signed-response gates: `{audit['denied_signed_response_gate_count']}`",
        "",
        "## Missing Real Inputs",
        "",
    ]
    for missing in audit["missing_real_inputs"]:
        lines.append(f"- {missing}")
    lines.extend(["", "## Boundary", "", audit["claim_boundary"], ""])
    return "\n".join(lines)