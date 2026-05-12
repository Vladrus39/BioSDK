"""External review finding triage and remediation-plan proof, v5.53."""
from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from biogpu.beta.job_model_v43 import utc_now_iso
from biogpu.evidence.ledger_v53 import stable_hash
from biogpu.sdk.external_reviewer_response_intake_v552 import run_external_reviewer_response_intake_workflow_v552


DEFAULT_OUT = Path("outputs/v553_external_review_finding_triage")
REVIEW_FINDING_CATEGORIES_V553 = (
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
REMEDIATION_PLAN_SECTIONS_V553 = (
    "finding_summary",
    "severity_and_owner",
    "remediation_action",
    "evidence_required",
    "acceptance_criteria",
    "claim_boundary_acknowledgement",
    "closure_signature_placeholder",
)
LOCAL_TRIAGE_STAGES_V553 = ("finding_triage", "remediation_plan_assembly", "closure_preflight")


@dataclass(frozen=True)
class ExternalReviewFindingTriagePolicyV553:
    policy_id: str
    finding_categories: tuple[str, ...]
    remediation_plan_sections: tuple[str, ...]
    local_triage_stages: tuple[str, ...]
    requires_v552_response_intake: bool
    requires_finding_triage_matrix: bool
    requires_remediation_plan_packet: bool
    requires_external_reviewer_identity: bool
    requires_external_reviewer_signature: bool
    requires_remediation_approval: bool
    local_contract_only: bool = True
    real_review_finding_closure_ready: bool = False
    real_external_review_ready: bool = False
    real_external_pilot_ready: bool = False
    production_ready: bool = False
    full_biosdk_ready: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ReviewFindingFixtureV553:
    finding_id: str
    category: str
    severity: str
    has_v552_anchor: bool
    has_local_finding_text: bool
    has_owner_role: bool
    has_remediation_plan: bool
    has_claim_boundary_ack: bool
    has_external_reviewer_identity: bool
    has_external_reviewer_signature: bool
    has_remediation_approval: bool
    requests_review_closure: bool
    requests_real_external_pilot: bool
    requests_production_release: bool
    requests_bic_os_unlock: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ReviewFindingDecisionV553:
    finding_id: str
    category: str
    severity: str
    remediation_priority: str
    local_finding_triage_ready: bool
    local_remediation_plan_ready: bool
    real_remediation_approval_ready: bool
    review_finding_closed: bool
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
class RemediationClosureGateFixtureV553:
    gate_id: str
    has_v552_response_intake: bool
    has_finding_triage_matrix: bool
    has_remediation_plan_packet: bool
    has_claim_boundary_ack: bool
    has_no_open_review_findings: bool
    has_external_reviewer_identity: bool
    has_external_reviewer_signature: bool
    has_remediation_approval: bool
    requests_review_closure: bool
    requests_real_external_pilot: bool
    requests_production_release: bool
    requests_bic_os_unlock: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RemediationClosureGateDecisionV553:
    gate_id: str
    accepted_for_local_triage_stage: bool
    reason_codes: tuple[str, ...]
    local_triage_record_id: str | None
    real_review_finding_closure_ready: bool = False
    real_external_review_ready: bool = False
    real_external_pilot_ready: bool = False
    production_release_ready: bool = False
    full_biosdk_ready: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_external_review_finding_triage_policy_v553() -> dict[str, Any]:
    policy = ExternalReviewFindingTriagePolicyV553(
        policy_id="BIOGPU_CORE_V553_EXTERNAL_REVIEW_FINDING_TRIAGE_POLICY",
        finding_categories=REVIEW_FINDING_CATEGORIES_V553,
        remediation_plan_sections=REMEDIATION_PLAN_SECTIONS_V553,
        local_triage_stages=LOCAL_TRIAGE_STAGES_V553,
        requires_v552_response_intake=True,
        requires_finding_triage_matrix=True,
        requires_remediation_plan_packet=True,
        requires_external_reviewer_identity=True,
        requires_external_reviewer_signature=True,
        requires_remediation_approval=True,
    )
    result = {
        "version": "v5.53",
        "external_review_finding_triage_policy_ready": True,
        "policy": policy.to_dict(),
        "blocked_modes": ["real_review_finding_closure", "real_external_review", "real_external_pilot", "production_release", "production_ready_claim", "bic_os_unlock"],
        "required_real_records": ["external_review_finding_register", "external_reviewer_identity", "external_reviewer_signature", "remediation_approval", "finding_closure_timestamp"],
        "real_review_finding_closure_ready": False,
        "real_external_review_ready": False,
        "real_external_pilot_ready": False,
        "production_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    result["external_review_finding_triage_policy_sha256"] = stable_hash(result)
    return result


def default_review_finding_fixtures_v553() -> list[ReviewFindingFixtureV553]:
    severity_by_category = {
        "claim_boundary": "minor",
        "evidence_completeness": "major",
        "security_identity": "critical",
        "storage_retention": "major",
        "registry_distribution": "major",
        "pilot_readiness": "critical",
        "incident_support": "major",
        "production_operations": "critical",
        "biocompute_runtime": "critical",
        "bic_os_boundary": "minor",
    }
    fixtures: list[ReviewFindingFixtureV553] = []
    for category in REVIEW_FINDING_CATEGORIES_V553:
        fixtures.append(
            ReviewFindingFixtureV553(
                finding_id=f"finding-{category}",
                category=category,
                severity=severity_by_category[category],
                has_v552_anchor=True,
                has_local_finding_text=True,
                has_owner_role=True,
                has_remediation_plan=True,
                has_claim_boundary_ack=True,
                has_external_reviewer_identity=False,
                has_external_reviewer_signature=False,
                has_remediation_approval=False,
                requests_review_closure=category == "evidence_completeness",
                requests_real_external_pilot=category == "pilot_readiness",
                requests_production_release=category == "production_operations",
                requests_bic_os_unlock=category == "bic_os_boundary",
            )
        )
    return fixtures


def _remediation_priority(severity: str) -> str:
    if severity == "critical":
        return "blocker_before_external_review_or_pilot"
    if severity == "major":
        return "must_remediate_before_review_closure"
    return "track_before_review_closure"


def evaluate_review_finding_v553(fixture: ReviewFindingFixtureV553, v552_dependency: dict[str, Any]) -> ReviewFindingDecisionV553:
    reasons: list[str] = []
    if v552_dependency.get("external_reviewer_response_intake_contract_ready") is not True or not fixture.has_v552_anchor:
        reasons.append("v552_response_intake_missing")
    if fixture.category not in REVIEW_FINDING_CATEGORIES_V553:
        reasons.append("finding_category_not_allowed")
    if fixture.severity not in {"minor", "major", "critical"}:
        reasons.append("finding_severity_not_allowed")
    if not fixture.has_local_finding_text:
        reasons.append("local_finding_text_missing")
    if not fixture.has_owner_role:
        reasons.append("owner_role_missing")
    if not fixture.has_remediation_plan:
        reasons.append("remediation_plan_missing")
    if not fixture.has_claim_boundary_ack:
        reasons.append("claim_boundary_ack_missing")
    local_ready = not any(
        reason in reasons
        for reason in {
            "v552_response_intake_missing",
            "finding_category_not_allowed",
            "finding_severity_not_allowed",
            "local_finding_text_missing",
            "owner_role_missing",
            "remediation_plan_missing",
            "claim_boundary_ack_missing",
        }
    )
    if not fixture.has_external_reviewer_identity:
        reasons.append("external_reviewer_identity_missing")
    if not fixture.has_external_reviewer_signature:
        reasons.append("external_reviewer_signature_missing")
    if not fixture.has_remediation_approval:
        reasons.append("remediation_approval_missing")
    if fixture.requests_review_closure:
        reasons.append("real_review_finding_closure_not_ready")
        reasons.append("real_external_review_not_ready")
    if fixture.requests_real_external_pilot:
        reasons.append("real_external_pilot_not_ready")
    if fixture.requests_production_release:
        reasons.append("production_release_not_allowed")
    if fixture.requests_bic_os_unlock:
        reasons.append("bic_os_unlock_not_allowed")
    return ReviewFindingDecisionV553(
        finding_id=fixture.finding_id,
        category=fixture.category,
        severity=fixture.severity,
        remediation_priority=_remediation_priority(fixture.severity),
        local_finding_triage_ready=local_ready,
        local_remediation_plan_ready=local_ready and fixture.has_remediation_plan,
        real_remediation_approval_ready=False,
        review_finding_closed=False,
        reason_codes=tuple(reasons or ["review_finding_closed"]),
        local_anchor=str(v552_dependency.get("external_reviewer_response_intake_audit_sha256") or "") or None,
    )


def build_review_finding_triage_matrix_v553(v552_dependency: dict[str, Any], fixtures: list[ReviewFindingFixtureV553] | None = None) -> dict[str, Any]:
    finding_fixtures = fixtures or default_review_finding_fixtures_v553()
    decisions = [evaluate_review_finding_v553(fixture, v552_dependency).to_dict() for fixture in finding_fixtures]
    triage_ready_count = sum(1 for decision in decisions if decision["local_finding_triage_ready"])
    remediation_ready_count = sum(1 for decision in decisions if decision["local_remediation_plan_ready"])
    real_approval_count = sum(1 for decision in decisions if decision["real_remediation_approval_ready"])
    closed_count = sum(1 for decision in decisions if decision["review_finding_closed"])
    categories = sorted({decision["category"] for decision in decisions})
    reason_codes = sorted({reason for decision in decisions for reason in decision["reason_codes"]})
    priorities = sorted({decision["remediation_priority"] for decision in decisions})
    required_reasons = {
        "external_reviewer_identity_missing",
        "external_reviewer_signature_missing",
        "remediation_approval_missing",
        "real_review_finding_closure_not_ready",
        "real_external_review_not_ready",
        "real_external_pilot_not_ready",
        "production_release_not_allowed",
        "bic_os_unlock_not_allowed",
    }
    matrix = {
        "version": "v5.53",
        "review_finding_triage_matrix_ready": triage_ready_count == len(REVIEW_FINDING_CATEGORIES_V553) and remediation_ready_count == len(REVIEW_FINDING_CATEGORIES_V553) and real_approval_count == 0 and closed_count == 0 and set(categories) == set(REVIEW_FINDING_CATEGORIES_V553) and required_reasons.issubset(set(reason_codes)),
        "review_finding_count": len(decisions),
        "local_finding_triage_ready_count": triage_ready_count,
        "local_remediation_plan_ready_count": remediation_ready_count,
        "real_remediation_approval_count": real_approval_count,
        "review_finding_closed_count": closed_count,
        "categories": categories,
        "remediation_priorities": priorities,
        "reason_codes": reason_codes,
        "fixtures": [fixture.to_dict() for fixture in finding_fixtures],
        "decisions": decisions,
        "real_review_finding_closure_ready": False,
        "real_external_review_ready": False,
        "real_external_pilot_ready": False,
        "production_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    matrix["review_finding_triage_matrix_sha256"] = stable_hash(matrix)
    return matrix


def build_remediation_plan_packet_v553(v552_dependency: dict[str, Any], triage_matrix: dict[str, Any]) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for decision in triage_matrix.get("decisions", []):
        if decision.get("local_remediation_plan_ready") is not True:
            continue
        record = {
            "version": "v5.53",
            "remediation_record_id": f"remediation-{decision['finding_id']}",
            "category": decision.get("category"),
            "severity": decision.get("severity"),
            "remediation_priority": decision.get("remediation_priority"),
            "v552_response_intake_anchor": v552_dependency.get("external_reviewer_response_intake_audit_sha256"),
            "triage_matrix_anchor": triage_matrix.get("review_finding_triage_matrix_sha256"),
            "local_remediation_record_ready": True,
            "external_reviewer_signature_present": False,
            "remediation_approval_present": False,
            "review_finding_closed": False,
            "real_external_review_ready": False,
            "real_external_pilot_ready": False,
            "production_ready": False,
            "created_at": utc_now_iso(),
        }
        record["remediation_record_sha256"] = stable_hash(record)
        records.append(record)
    packet = {
        "version": "v5.53",
        "remediation_plan_packet_ready": len(records) == len(REVIEW_FINDING_CATEGORIES_V553) and triage_matrix.get("review_finding_triage_matrix_ready") is True,
        "remediation_plan_record_count": len(records),
        "local_remediation_record_ready_count": sum(1 for record in records if record["local_remediation_record_ready"]),
        "real_remediation_approval_count": sum(1 for record in records if record["remediation_approval_present"]),
        "review_finding_closed_count": sum(1 for record in records if record["review_finding_closed"]),
        "remediation_records": records,
        "real_review_finding_closure_ready": False,
        "real_external_review_ready": False,
        "real_external_pilot_ready": False,
        "production_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    packet["remediation_plan_packet_sha256"] = stable_hash(packet)
    return packet


def default_remediation_closure_gate_fixtures_v553() -> list[RemediationClosureGateFixtureV553]:
    return [
        RemediationClosureGateFixtureV553("finding-triage", True, True, True, True, False, True, True, True, False, False, False, False),
        RemediationClosureGateFixtureV553("remediation-plan-assembly", True, True, True, True, False, True, True, True, False, False, False, False),
        RemediationClosureGateFixtureV553("closure-preflight", True, True, True, True, False, True, True, True, False, False, False, False),
        RemediationClosureGateFixtureV553("missing-v552-contract", False, True, True, True, False, True, True, True, False, False, False, False),
        RemediationClosureGateFixtureV553("missing-finding-triage", True, False, True, True, False, True, True, True, False, False, False, False),
        RemediationClosureGateFixtureV553("missing-remediation-packet", True, True, False, True, False, True, True, True, False, False, False, False),
        RemediationClosureGateFixtureV553("missing-claim-boundary", True, True, True, False, False, True, True, True, False, False, False, False),
        RemediationClosureGateFixtureV553("missing-real-approval", True, True, True, True, True, False, False, False, True, False, False, False),
        RemediationClosureGateFixtureV553("closure-with-open-findings", True, True, True, True, False, True, True, True, True, False, False, False),
        RemediationClosureGateFixtureV553("real-pilot-request", True, True, True, True, True, True, True, True, False, True, False, False),
        RemediationClosureGateFixtureV553("production-release-request", True, True, True, True, True, True, True, True, False, False, True, False),
        RemediationClosureGateFixtureV553("bic-os-unlock-request", True, True, True, True, True, True, True, True, False, False, False, True),
    ]


def evaluate_remediation_closure_gate_v553(fixture: RemediationClosureGateFixtureV553, v552_dependency: dict[str, Any], triage_matrix: dict[str, Any], remediation_packet: dict[str, Any]) -> RemediationClosureGateDecisionV553:
    reasons: list[str] = []
    if v552_dependency.get("external_reviewer_response_intake_contract_ready") is not True or not fixture.has_v552_response_intake:
        reasons.append("v552_response_intake_missing")
    if triage_matrix.get("review_finding_triage_matrix_ready") is not True or not fixture.has_finding_triage_matrix:
        reasons.append("finding_triage_matrix_missing")
    if remediation_packet.get("remediation_plan_packet_ready") is not True or not fixture.has_remediation_plan_packet:
        reasons.append("remediation_plan_packet_missing")
    if not fixture.has_claim_boundary_ack:
        reasons.append("claim_boundary_ack_missing")
    if fixture.requests_review_closure:
        if not fixture.has_no_open_review_findings:
            reasons.append("review_findings_still_open")
        if not fixture.has_external_reviewer_identity:
            reasons.append("external_reviewer_identity_missing")
        if not fixture.has_external_reviewer_signature:
            reasons.append("external_reviewer_signature_missing")
        if not fixture.has_remediation_approval:
            reasons.append("remediation_approval_missing")
        reasons.append("real_review_finding_closure_not_ready")
        reasons.append("real_external_review_not_ready")
    if fixture.requests_real_external_pilot:
        reasons.append("real_external_pilot_not_ready")
    if fixture.requests_production_release:
        reasons.append("production_release_not_allowed")
    if fixture.requests_bic_os_unlock:
        reasons.append("bic_os_unlock_not_allowed")
    accepted = not reasons
    return RemediationClosureGateDecisionV553(
        gate_id=fixture.gate_id,
        accepted_for_local_triage_stage=accepted,
        reason_codes=tuple(reasons or ["local_triage_stage_accepted"]),
        local_triage_record_id=f"local-triage-{fixture.gate_id}" if accepted else None,
    )


def run_remediation_closure_gate_v553(v552_dependency: dict[str, Any], triage_matrix: dict[str, Any], remediation_packet: dict[str, Any], fixtures: list[RemediationClosureGateFixtureV553] | None = None) -> dict[str, Any]:
    gate_fixtures = fixtures or default_remediation_closure_gate_fixtures_v553()
    decisions = [evaluate_remediation_closure_gate_v553(fixture, v552_dependency, triage_matrix, remediation_packet).to_dict() for fixture in gate_fixtures]
    accepted_count = sum(1 for decision in decisions if decision["accepted_for_local_triage_stage"])
    denied_count = len(decisions) - accepted_count
    reason_codes = sorted({reason for decision in decisions for reason in decision["reason_codes"]})
    required_denials = {
        "v552_response_intake_missing",
        "finding_triage_matrix_missing",
        "remediation_plan_packet_missing",
        "claim_boundary_ack_missing",
        "review_findings_still_open",
        "external_reviewer_identity_missing",
        "external_reviewer_signature_missing",
        "remediation_approval_missing",
        "real_review_finding_closure_not_ready",
        "real_external_review_not_ready",
        "real_external_pilot_not_ready",
        "production_release_not_allowed",
        "bic_os_unlock_not_allowed",
    }
    gate = {
        "version": "v5.53",
        "remediation_closure_gate_ready": accepted_count == len(LOCAL_TRIAGE_STAGES_V553) and denied_count == 9 and required_denials.issubset(set(reason_codes)),
        "gate_fixture_count": len(gate_fixtures),
        "accepted_local_triage_stage_count": accepted_count,
        "denied_remediation_closure_gate_count": denied_count,
        "reason_codes": reason_codes,
        "fixtures": [fixture.to_dict() for fixture in gate_fixtures],
        "decisions": decisions,
        "real_review_finding_closure_ready": False,
        "real_external_review_ready": False,
        "real_external_pilot_ready": False,
        "production_release_ready": False,
        "production_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    gate["remediation_closure_gate_sha256"] = stable_hash(gate)
    return gate


def build_remediation_blocker_register_v553(triage_matrix: dict[str, Any], closure_gate: dict[str, Any]) -> dict[str, Any]:
    blockers: list[dict[str, Any]] = []
    for decision in triage_matrix.get("decisions", []):
        if decision.get("review_finding_closed") is True:
            continue
        blocker = {
            "version": "v5.53",
            "blocker_id": f"finding-blocker-{decision['finding_id']}",
            "source": "review_finding_triage_matrix",
            "record_id": decision.get("finding_id"),
            "reason_codes": decision.get("reason_codes", []),
            "must_be_resolved_before_review_closure": True,
            "must_be_resolved_before_external_review": True,
            "must_be_resolved_before_real_pilot": True,
            "must_be_resolved_before_production": True,
            "must_be_resolved_before_bic_os": True,
        }
        blocker["blocker_sha256"] = stable_hash(blocker)
        blockers.append(blocker)
    for decision in closure_gate.get("decisions", []):
        if decision.get("accepted_for_local_triage_stage") is True:
            continue
        blocker = {
            "version": "v5.53",
            "blocker_id": f"remediation-gate-blocker-{decision['gate_id']}",
            "source": "remediation_closure_gate",
            "record_id": decision.get("gate_id"),
            "reason_codes": decision.get("reason_codes", []),
            "must_be_resolved_before_review_closure": True,
            "must_be_resolved_before_external_review": True,
            "must_be_resolved_before_real_pilot": True,
            "must_be_resolved_before_production": True,
            "must_be_resolved_before_bic_os": True,
        }
        blocker["blocker_sha256"] = stable_hash(blocker)
        blockers.append(blocker)
    register = {
        "version": "v5.53",
        "remediation_blocker_register_ready": len(blockers) == len(REVIEW_FINDING_CATEGORIES_V553) + 9,
        "blocker_count": len(blockers),
        "blockers": blockers,
        "real_review_finding_closure_ready": False,
        "real_external_review_ready": False,
        "real_external_pilot_ready": False,
        "production_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    register["remediation_blocker_register_sha256"] = stable_hash(register)
    return register


def build_external_review_finding_triage_audit_bundle_v553(policy: dict[str, Any], triage_matrix: dict[str, Any], remediation_packet: dict[str, Any], closure_gate: dict[str, Any], blocker_register: dict[str, Any]) -> dict[str, Any]:
    bundle_ready = (
        policy.get("external_review_finding_triage_policy_ready") is True
        and triage_matrix.get("review_finding_triage_matrix_ready") is True
        and remediation_packet.get("remediation_plan_packet_ready") is True
        and closure_gate.get("remediation_closure_gate_ready") is True
        and blocker_register.get("remediation_blocker_register_ready") is True
    )
    bundle = {
        "version": "v5.53",
        "external_review_finding_triage_audit_bundle_ready": bundle_ready,
        "policy_sha256": policy.get("external_review_finding_triage_policy_sha256"),
        "triage_matrix_sha256": triage_matrix.get("review_finding_triage_matrix_sha256"),
        "remediation_packet_sha256": remediation_packet.get("remediation_plan_packet_sha256"),
        "closure_gate_sha256": closure_gate.get("remediation_closure_gate_sha256"),
        "blocker_register_sha256": blocker_register.get("remediation_blocker_register_sha256"),
        "real_review_finding_closure_ready": False,
        "real_external_review_ready": False,
        "real_external_pilot_ready": False,
        "production_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    bundle["external_review_finding_triage_audit_bundle_sha256"] = stable_hash(bundle)
    return bundle


def run_external_review_finding_triage_workflow_v553(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    project_root = Path(root).resolve()
    out = project_root / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    v552_dependency = run_external_reviewer_response_intake_workflow_v552(project_root, out.parent / "d553")
    policy = build_external_review_finding_triage_policy_v553()
    triage_matrix = build_review_finding_triage_matrix_v553(v552_dependency)
    remediation_packet = build_remediation_plan_packet_v553(v552_dependency, triage_matrix)
    closure_gate = run_remediation_closure_gate_v553(v552_dependency, triage_matrix, remediation_packet)
    blocker_register = build_remediation_blocker_register_v553(triage_matrix, closure_gate)
    audit_bundle = build_external_review_finding_triage_audit_bundle_v553(policy, triage_matrix, remediation_packet, closure_gate, blocker_register)
    proof_ready = (
        v552_dependency.get("external_reviewer_response_intake_contract_ready") is True
        and policy.get("external_review_finding_triage_policy_ready") is True
        and triage_matrix.get("review_finding_triage_matrix_ready") is True
        and remediation_packet.get("remediation_plan_packet_ready") is True
        and closure_gate.get("remediation_closure_gate_ready") is True
        and blocker_register.get("remediation_blocker_register_ready") is True
        and audit_bundle.get("external_review_finding_triage_audit_bundle_ready") is True
    )
    audit = {
        "version": "v5.53",
        "phase": "external_review_finding_triage_remediation_plan_contract",
        "overall_status": "external_review_finding_triage_contract_ready_closure_not_claimed" if proof_ready else "external_review_finding_triage_contract_incomplete",
        "active_phase": "biosdk_external_review_finding_triage_proof",
        "bic_os_phase_locked": True,
        "external_review_finding_triage_contract_ready": proof_ready,
        "v552_dependency_ready": v552_dependency.get("external_reviewer_response_intake_contract_ready") is True,
        "external_review_finding_triage_policy_ready": policy.get("external_review_finding_triage_policy_ready") is True,
        "review_finding_triage_matrix_ready": triage_matrix.get("review_finding_triage_matrix_ready") is True,
        "remediation_plan_packet_ready": remediation_packet.get("remediation_plan_packet_ready") is True,
        "remediation_closure_gate_ready": closure_gate.get("remediation_closure_gate_ready") is True,
        "remediation_blocker_register_ready": blocker_register.get("remediation_blocker_register_ready") is True,
        "external_review_finding_triage_audit_bundle_ready": audit_bundle.get("external_review_finding_triage_audit_bundle_ready") is True,
        "artifact_name": v552_dependency.get("artifact_name"),
        "artifact_sha256": v552_dependency.get("artifact_sha256"),
        "review_finding_count": triage_matrix.get("review_finding_count"),
        "local_finding_triage_ready_count": triage_matrix.get("local_finding_triage_ready_count"),
        "local_remediation_plan_ready_count": triage_matrix.get("local_remediation_plan_ready_count"),
        "real_remediation_approval_count": triage_matrix.get("real_remediation_approval_count"),
        "review_finding_closed_count": triage_matrix.get("review_finding_closed_count"),
        "remediation_plan_record_count": remediation_packet.get("remediation_plan_record_count"),
        "accepted_local_triage_stage_count": closure_gate.get("accepted_local_triage_stage_count"),
        "denied_remediation_closure_gate_count": closure_gate.get("denied_remediation_closure_gate_count"),
        "remediation_blocker_count": blocker_register.get("blocker_count"),
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
        "external_review_finding_triage_policy": policy,
        "review_finding_triage_matrix": triage_matrix,
        "remediation_plan_packet": remediation_packet,
        "remediation_closure_gate": closure_gate,
        "remediation_blocker_register": blocker_register,
        "external_review_finding_triage_audit_bundle": audit_bundle,
        "v552_dependency_summary": {key: value for key, value in v552_dependency.items() if key not in {"external_reviewer_response_policy", "questionnaire_scoring_matrix", "signed_review_response_packet", "signed_review_response_gate", "signed_response_blocker_register", "external_reviewer_response_audit_bundle", "v551_dependency_summary"}},
        "missing_real_inputs": [
            "real external review finding register",
            "external reviewer identity records",
            "external reviewer signed finding dispositions",
            "remediation owner approvals and closure signatures",
            "review finding closure timestamps and immutable transcript",
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
            "did_we_add_finding_triage": "yes" if triage_matrix.get("review_finding_triage_matrix_ready") else "no",
            "did_we_add_remediation_plan_proof": "yes" if remediation_packet.get("remediation_plan_packet_ready") else "no",
            "are_real_review_findings_closed": "no",
            "is_real_external_review_ready": "no",
            "is_real_external_pilot_ready": "no",
            "is_production_ready": "no",
            "is_full_biosdk_ready": "no",
            "is_biocompute_runtime_ready": "no",
            "is_bic_os_ready": "no",
            "next_best_build_step": "add remediation evidence verification and closure attestation proof" if proof_ready else "fix v5.53 finding-triage blockers first",
        },
        "claim_boundary": "v5.53 proves a local external review finding triage matrix, remediation-plan packet shape and closure preflight gate over the v5.52 external reviewer response intake contract. It does not claim real finding closure, completed external review, real external pilot readiness, production readiness, full BioSDK, production BioCompute Runtime or BiC OS readiness.",
    }
    audit["external_review_finding_triage_audit_sha256"] = stable_hash({key: value for key, value in audit.items() if key != "external_review_finding_triage_audit_sha256"})
    return audit


def write_external_review_finding_triage_outputs_v553(audit: dict[str, Any], out_dir: str | Path = DEFAULT_OUT) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary_json": out / "V553_EXTERNAL_REVIEW_FINDING_TRIAGE_SUMMARY.json",
        "policy_json": out / "V553_EXTERNAL_REVIEW_FINDING_TRIAGE_POLICY.json",
        "triage_matrix_json": out / "V553_REVIEW_FINDING_TRIAGE_MATRIX.json",
        "remediation_packet_json": out / "V553_REMEDIATION_PLAN_PACKET.json",
        "closure_gate_json": out / "V553_REMEDIATION_CLOSURE_GATE.json",
        "blocker_register_json": out / "V553_REMEDIATION_BLOCKER_REGISTER.json",
        "audit_bundle_json": out / "V553_EXTERNAL_REVIEW_FINDING_TRIAGE_AUDIT_BUNDLE.json",
        "triage_matrix_csv": out / "V553_REVIEW_FINDING_TRIAGE_MATRIX.csv",
        "closure_gate_csv": out / "V553_REMEDIATION_CLOSURE_GATE.csv",
        "markdown_report": out / "BIOGPU_V553_EXTERNAL_REVIEW_FINDING_TRIAGE_REPORT.md",
    }
    summary = {key: value for key, value in audit.items() if key not in {"external_review_finding_triage_policy", "review_finding_triage_matrix", "remediation_plan_packet", "remediation_closure_gate", "remediation_blocker_register", "external_review_finding_triage_audit_bundle"}}
    paths["summary_json"].write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["policy_json"].write_text(json.dumps(audit["external_review_finding_triage_policy"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["triage_matrix_json"].write_text(json.dumps(audit["review_finding_triage_matrix"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["remediation_packet_json"].write_text(json.dumps(audit["remediation_plan_packet"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["closure_gate_json"].write_text(json.dumps(audit["remediation_closure_gate"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["blocker_register_json"].write_text(json.dumps(audit["remediation_blocker_register"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["audit_bundle_json"].write_text(json.dumps(audit["external_review_finding_triage_audit_bundle"], indent=2, ensure_ascii=False), encoding="utf-8")
    _write_triage_matrix_csv(paths["triage_matrix_csv"], audit["review_finding_triage_matrix"].get("decisions", []))
    _write_closure_gate_csv(paths["closure_gate_csv"], audit["remediation_closure_gate"].get("decisions", []))
    paths["markdown_report"].write_text(_markdown_report(audit), encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}


def _write_triage_matrix_csv(path: Path, decisions: list[dict[str, Any]]) -> None:
    fieldnames = ["finding_id", "category", "severity", "remediation_priority", "local_finding_triage_ready", "local_remediation_plan_ready", "real_remediation_approval_ready", "review_finding_closed", "local_anchor", "reason_codes"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for decision in decisions:
            row = {field: decision.get(field) for field in fieldnames}
            row["reason_codes"] = " | ".join(str(reason) for reason in decision.get("reason_codes", []))
            writer.writerow(row)


def _write_closure_gate_csv(path: Path, decisions: list[dict[str, Any]]) -> None:
    fieldnames = ["gate_id", "accepted_for_local_triage_stage", "local_triage_record_id", "reason_codes"]
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
        "# BioGPU-Core v5.53 External Review Finding Triage Contract",
        "",
        "## Direct Answer",
        "",
        f"- Finding triage added: `{answer['did_we_add_finding_triage']}`",
        f"- Remediation-plan proof added: `{answer['did_we_add_remediation_plan_proof']}`",
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
        f"- v5.52 dependency ready: `{audit['v552_dependency_ready']}`",
        f"- Review findings: `{audit['review_finding_count']}`",
        f"- Local triage-ready findings: `{audit['local_finding_triage_ready_count']}`",
        f"- Local remediation-ready findings: `{audit['local_remediation_plan_ready_count']}`",
        f"- Real remediation approvals: `{audit['real_remediation_approval_count']}`",
        f"- Review findings closed: `{audit['review_finding_closed_count']}`",
        f"- Accepted local triage stages: `{audit['accepted_local_triage_stage_count']}`",
        f"- Denied remediation closure gates: `{audit['denied_remediation_closure_gate_count']}`",
        "",
        "## Missing Real Inputs",
        "",
    ]
    for missing in audit["missing_real_inputs"]:
        lines.append(f"- {missing}")
    lines.extend(["", "## Boundary", "", audit["claim_boundary"], ""])
    return "\n".join(lines)