"""External acceptance evidence schema and real-pilot intake gate proof, v5.50."""
from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from biogpu.beta.job_model_v43 import utc_now_iso
from biogpu.evidence.ledger_v53 import stable_hash
from biogpu.sdk.production_readiness_gap_v549 import run_production_readiness_gap_workflow_v549


DEFAULT_OUT = Path("outputs/v550_external_acceptance_intake")
REQUIRED_EXTERNAL_EVIDENCE_TYPES_V550 = (
    "pilot_partner_identity",
    "data_use_approval",
    "external_security_signoff",
    "production_idp_approval",
    "live_registry_admin_approval",
    "trusted_signing_approval",
    "ci_cd_gate_acceptance",
    "support_incident_acceptance",
    "notification_acceptance",
    "rollback_and_yank_acceptance",
)
LOCAL_INTAKE_STAGES_V550 = ("schema_review", "packet_review", "operator_preflight")


@dataclass(frozen=True)
class ExternalAcceptanceIntakePolicyV550:
    policy_id: str
    required_evidence_types: tuple[str, ...]
    local_intake_stages: tuple[str, ...]
    requires_v549_readiness_gap_contract: bool
    requires_external_acceptance_schema: bool
    requires_real_submitter_identity: bool
    requires_external_signature: bool
    requires_acceptance_scope_boundary: bool
    requires_real_pilot_intake_gate: bool
    local_contract_only: bool = True
    real_external_pilot_ready: bool = False
    production_ready: bool = False
    full_biosdk_ready: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ExternalAcceptanceEvidenceFixtureV550:
    evidence_id: str
    evidence_type: str
    has_v549_gap_context: bool
    has_real_submitter_identity: bool
    has_external_signature: bool
    has_scope_boundary: bool
    has_contact_channel: bool
    has_acceptance_timestamp: bool
    requests_live_pilot: bool
    requests_production_release: bool
    requests_bic_os_unlock: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ExternalAcceptanceEvidenceDecisionV550:
    evidence_id: str
    evidence_type: str
    schema_record_valid: bool
    real_acceptance_record_ready: bool
    reason_codes: tuple[str, ...]
    local_evidence_anchor: str | None
    real_external_pilot_ready: bool = False
    production_ready: bool = False
    full_biosdk_ready: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RealPilotIntakeGateFixtureV550:
    gate_id: str
    has_evidence_schema: bool
    has_v549_gap_context: bool
    has_all_required_evidence_types: bool
    has_no_open_production_gaps: bool
    has_external_acceptance_signatures: bool
    has_real_operator_approval: bool
    requests_real_external_pilot: bool
    requests_production_release: bool
    requests_bic_os_unlock: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RealPilotIntakeGateDecisionV550:
    gate_id: str
    accepted_for_local_intake_stage: bool
    reason_codes: tuple[str, ...]
    local_intake_record_id: str | None
    real_external_pilot_ready: bool = False
    production_release_ready: bool = False
    full_biosdk_ready: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_external_acceptance_intake_policy_v550() -> dict[str, Any]:
    policy = ExternalAcceptanceIntakePolicyV550(
        policy_id="BIOGPU_CORE_V550_EXTERNAL_ACCEPTANCE_INTAKE_POLICY",
        required_evidence_types=REQUIRED_EXTERNAL_EVIDENCE_TYPES_V550,
        local_intake_stages=LOCAL_INTAKE_STAGES_V550,
        requires_v549_readiness_gap_contract=True,
        requires_external_acceptance_schema=True,
        requires_real_submitter_identity=True,
        requires_external_signature=True,
        requires_acceptance_scope_boundary=True,
        requires_real_pilot_intake_gate=True,
    )
    result = {
        "version": "v5.50",
        "external_acceptance_intake_policy_ready": True,
        "policy": policy.to_dict(),
        "blocked_modes": ["real_external_pilot", "production_release", "production_ready_claim", "bic_os_unlock"],
        "required_real_records": ["real_submitter_identity", "external_signature", "acceptance_scope", "partner_contact", "pilot_acceptance_timestamp"],
        "real_external_pilot_ready": False,
        "production_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    result["external_acceptance_intake_policy_sha256"] = stable_hash(result)
    return result


def build_external_acceptance_evidence_schema_v550(policy: dict[str, Any]) -> dict[str, Any]:
    fields = [
        "evidence_id",
        "evidence_type",
        "submitter_identity",
        "external_signature",
        "acceptance_scope",
        "contact_channel",
        "acceptance_timestamp",
        "v549_gap_matrix_anchor",
        "claim_boundary_ack",
    ]
    schema = {
        "version": "v5.50",
        "external_acceptance_evidence_schema_ready": policy.get("external_acceptance_intake_policy_ready") is True,
        "schema_id": "BIOGPU_CORE_V550_EXTERNAL_ACCEPTANCE_EVIDENCE_SCHEMA",
        "required_evidence_types": list(REQUIRED_EXTERNAL_EVIDENCE_TYPES_V550),
        "required_fields": fields,
        "local_schema_only": True,
        "real_external_pilot_ready": False,
        "production_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    schema["external_acceptance_evidence_schema_sha256"] = stable_hash(schema)
    return schema


def default_external_acceptance_evidence_fixtures_v550() -> list[ExternalAcceptanceEvidenceFixtureV550]:
    fixtures: list[ExternalAcceptanceEvidenceFixtureV550] = []
    for evidence_type in REQUIRED_EXTERNAL_EVIDENCE_TYPES_V550:
        fixtures.append(
            ExternalAcceptanceEvidenceFixtureV550(
                evidence_id=f"draft-{evidence_type}",
                evidence_type=evidence_type,
                has_v549_gap_context=True,
                has_real_submitter_identity=False,
                has_external_signature=False,
                has_scope_boundary=True,
                has_contact_channel=True,
                has_acceptance_timestamp=True,
                requests_live_pilot=evidence_type == "pilot_partner_identity",
                requests_production_release=evidence_type == "ci_cd_gate_acceptance",
                requests_bic_os_unlock=evidence_type == "rollback_and_yank_acceptance",
            )
        )
    return fixtures


def evaluate_external_acceptance_evidence_v550(fixture: ExternalAcceptanceEvidenceFixtureV550, v549_dependency: dict[str, Any]) -> ExternalAcceptanceEvidenceDecisionV550:
    reasons: list[str] = []
    if v549_dependency.get("production_readiness_gap_contract_ready") is not True or not fixture.has_v549_gap_context:
        reasons.append("v549_gap_context_missing")
    if fixture.evidence_type not in REQUIRED_EXTERNAL_EVIDENCE_TYPES_V550:
        reasons.append("evidence_type_not_allowed")
    if not fixture.has_scope_boundary:
        reasons.append("acceptance_scope_missing")
    if not fixture.has_contact_channel:
        reasons.append("contact_channel_missing")
    if not fixture.has_acceptance_timestamp:
        reasons.append("acceptance_timestamp_missing")
    schema_record_valid = not any(
        reason in reasons
        for reason in {
            "v549_gap_context_missing",
            "evidence_type_not_allowed",
            "acceptance_scope_missing",
            "contact_channel_missing",
            "acceptance_timestamp_missing",
        }
    )
    if not fixture.has_real_submitter_identity:
        reasons.append("real_submitter_identity_missing")
    if not fixture.has_external_signature:
        reasons.append("external_signature_missing")
    if fixture.requests_live_pilot:
        reasons.append("real_pilot_request_blocked")
    if fixture.requests_production_release:
        reasons.append("production_release_not_allowed")
    if fixture.requests_bic_os_unlock:
        reasons.append("bic_os_unlock_not_allowed")
    real_ready = False
    return ExternalAcceptanceEvidenceDecisionV550(
        evidence_id=fixture.evidence_id,
        evidence_type=fixture.evidence_type,
        schema_record_valid=schema_record_valid,
        real_acceptance_record_ready=real_ready,
        reason_codes=tuple(reasons or ["external_acceptance_record_ready"]),
        local_evidence_anchor=str(v549_dependency.get("production_readiness_gap_audit_sha256") or "") or None,
    )


def build_external_acceptance_evidence_matrix_v550(v549_dependency: dict[str, Any], fixtures: list[ExternalAcceptanceEvidenceFixtureV550] | None = None) -> dict[str, Any]:
    evidence_fixtures = fixtures or default_external_acceptance_evidence_fixtures_v550()
    decisions = [evaluate_external_acceptance_evidence_v550(fixture, v549_dependency).to_dict() for fixture in evidence_fixtures]
    schema_valid_count = sum(1 for decision in decisions if decision["schema_record_valid"])
    real_ready_count = sum(1 for decision in decisions if decision["real_acceptance_record_ready"])
    evidence_types = sorted({decision["evidence_type"] for decision in decisions})
    reason_codes = sorted({reason for decision in decisions for reason in decision["reason_codes"]})
    required_reasons = {
        "real_submitter_identity_missing",
        "external_signature_missing",
        "real_pilot_request_blocked",
        "production_release_not_allowed",
        "bic_os_unlock_not_allowed",
    }
    matrix = {
        "version": "v5.50",
        "external_acceptance_evidence_matrix_ready": schema_valid_count == len(REQUIRED_EXTERNAL_EVIDENCE_TYPES_V550) and real_ready_count == 0 and set(evidence_types) == set(REQUIRED_EXTERNAL_EVIDENCE_TYPES_V550) and required_reasons.issubset(set(reason_codes)),
        "evidence_record_count": len(decisions),
        "schema_valid_record_count": schema_valid_count,
        "real_acceptance_ready_count": real_ready_count,
        "evidence_types": evidence_types,
        "reason_codes": reason_codes,
        "fixtures": [fixture.to_dict() for fixture in evidence_fixtures],
        "decisions": decisions,
        "real_external_pilot_ready": False,
        "production_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    matrix["external_acceptance_evidence_matrix_sha256"] = stable_hash(matrix)
    return matrix


def default_real_pilot_intake_gate_fixtures_v550() -> list[RealPilotIntakeGateFixtureV550]:
    return [
        RealPilotIntakeGateFixtureV550("schema-review", True, True, True, False, True, True, False, False, False),
        RealPilotIntakeGateFixtureV550("packet-review", True, True, True, False, True, True, False, False, False),
        RealPilotIntakeGateFixtureV550("operator-preflight", True, True, True, False, True, True, False, False, False),
        RealPilotIntakeGateFixtureV550("missing-schema", False, True, True, False, True, True, False, False, False),
        RealPilotIntakeGateFixtureV550("missing-v549-context", True, False, True, False, True, True, False, False, False),
        RealPilotIntakeGateFixtureV550("missing-evidence-types", True, True, False, False, True, True, False, False, False),
        RealPilotIntakeGateFixtureV550("missing-external-signatures", True, True, True, False, False, True, False, False, False),
        RealPilotIntakeGateFixtureV550("missing-real-operator", True, True, True, False, True, False, False, False, False),
        RealPilotIntakeGateFixtureV550("real-pilot-with-open-gaps", True, True, True, False, True, True, True, False, False),
        RealPilotIntakeGateFixtureV550("live-pilot-request", True, True, True, True, True, True, True, False, False),
        RealPilotIntakeGateFixtureV550("production-release-request", True, True, True, True, True, True, False, True, False),
        RealPilotIntakeGateFixtureV550("bic-os-unlock-request", True, True, True, True, True, True, False, False, True),
    ]


def evaluate_real_pilot_intake_gate_v550(fixture: RealPilotIntakeGateFixtureV550, v549_dependency: dict[str, Any], evidence_matrix: dict[str, Any]) -> RealPilotIntakeGateDecisionV550:
    reasons: list[str] = []
    if evidence_matrix.get("external_acceptance_evidence_matrix_ready") is not True or not fixture.has_evidence_schema:
        reasons.append("evidence_schema_missing")
    if v549_dependency.get("production_readiness_gap_contract_ready") is not True or not fixture.has_v549_gap_context:
        reasons.append("v549_gap_context_missing")
    if not fixture.has_all_required_evidence_types:
        reasons.append("required_evidence_types_missing")
    if not fixture.has_external_acceptance_signatures:
        reasons.append("external_acceptance_signatures_missing")
    if not fixture.has_real_operator_approval:
        reasons.append("real_operator_approval_missing")
    if fixture.requests_real_external_pilot and not fixture.has_no_open_production_gaps:
        reasons.append("production_gaps_still_open")
    if fixture.requests_real_external_pilot:
        reasons.append("real_external_pilot_not_ready")
    if fixture.requests_production_release:
        reasons.append("production_release_not_allowed")
    if fixture.requests_bic_os_unlock:
        reasons.append("bic_os_unlock_not_allowed")
    accepted = not reasons
    return RealPilotIntakeGateDecisionV550(
        gate_id=fixture.gate_id,
        accepted_for_local_intake_stage=accepted,
        reason_codes=tuple(reasons or ["local_intake_stage_accepted"]),
        local_intake_record_id=f"local-intake-{fixture.gate_id}" if accepted else None,
    )


def run_real_pilot_intake_gate_v550(v549_dependency: dict[str, Any], evidence_matrix: dict[str, Any], fixtures: list[RealPilotIntakeGateFixtureV550] | None = None) -> dict[str, Any]:
    gate_fixtures = fixtures or default_real_pilot_intake_gate_fixtures_v550()
    decisions = [evaluate_real_pilot_intake_gate_v550(fixture, v549_dependency, evidence_matrix).to_dict() for fixture in gate_fixtures]
    accepted_count = sum(1 for decision in decisions if decision["accepted_for_local_intake_stage"])
    denied_count = len(decisions) - accepted_count
    reason_codes = sorted({reason for decision in decisions for reason in decision["reason_codes"]})
    required_denials = {
        "evidence_schema_missing",
        "v549_gap_context_missing",
        "required_evidence_types_missing",
        "external_acceptance_signatures_missing",
        "real_operator_approval_missing",
        "production_gaps_still_open",
        "real_external_pilot_not_ready",
        "production_release_not_allowed",
        "bic_os_unlock_not_allowed",
    }
    gate = {
        "version": "v5.50",
        "real_pilot_intake_gate_ready": accepted_count == len(LOCAL_INTAKE_STAGES_V550) and denied_count >= 9 and required_denials.issubset(set(reason_codes)),
        "gate_fixture_count": len(gate_fixtures),
        "accepted_local_intake_stage_count": accepted_count,
        "denied_intake_gate_count": denied_count,
        "reason_codes": reason_codes,
        "fixtures": [fixture.to_dict() for fixture in gate_fixtures],
        "decisions": decisions,
        "real_external_pilot_ready": False,
        "production_release_ready": False,
        "production_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    gate["real_pilot_intake_gate_sha256"] = stable_hash(gate)
    return gate


def build_external_acceptance_packet_v550(v549_dependency: dict[str, Any], evidence_schema: dict[str, Any], evidence_matrix: dict[str, Any], intake_gate: dict[str, Any]) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for decision in evidence_matrix.get("decisions", []):
        if decision.get("schema_record_valid") is not True:
            continue
        record = {
            "version": "v5.50",
            "packet_record_id": f"packet-{decision['evidence_id']}",
            "evidence_type": decision.get("evidence_type"),
            "schema_sha256": evidence_schema.get("external_acceptance_evidence_schema_sha256"),
            "v549_gap_matrix_anchor": v549_dependency.get("production_readiness_gap_audit_sha256"),
            "real_acceptance_record_ready": False,
            "real_external_pilot_ready": False,
            "production_ready": False,
            "created_at": utc_now_iso(),
        }
        record["packet_record_sha256"] = stable_hash(record)
        records.append(record)
    packet = {
        "version": "v5.50",
        "external_acceptance_packet_ready": len(records) == len(REQUIRED_EXTERNAL_EVIDENCE_TYPES_V550) and intake_gate.get("real_pilot_intake_gate_ready") is True,
        "packet_record_count": len(records),
        "packet_records": records,
        "real_acceptance_ready_count": evidence_matrix.get("real_acceptance_ready_count"),
        "accepted_local_intake_stage_count": intake_gate.get("accepted_local_intake_stage_count"),
        "real_external_pilot_ready": False,
        "production_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    packet["external_acceptance_packet_sha256"] = stable_hash(packet)
    return packet


def build_real_pilot_intake_blocker_register_v550(evidence_matrix: dict[str, Any], intake_gate: dict[str, Any]) -> dict[str, Any]:
    blockers: list[dict[str, Any]] = []
    for decision in evidence_matrix.get("decisions", []):
        if decision.get("real_acceptance_record_ready") is True:
            continue
        blocker = {
            "version": "v5.50",
            "blocker_id": f"evidence-blocker-{decision['evidence_id']}",
            "source": "external_acceptance_evidence",
            "record_id": decision.get("evidence_id"),
            "reason_codes": decision.get("reason_codes", []),
            "must_be_resolved_before_real_pilot": True,
            "must_be_resolved_before_production": True,
            "must_be_resolved_before_bic_os": True,
        }
        blocker["blocker_sha256"] = stable_hash(blocker)
        blockers.append(blocker)
    for decision in intake_gate.get("decisions", []):
        if decision.get("accepted_for_local_intake_stage") is True:
            continue
        blocker = {
            "version": "v5.50",
            "blocker_id": f"intake-blocker-{decision['gate_id']}",
            "source": "real_pilot_intake_gate",
            "record_id": decision.get("gate_id"),
            "reason_codes": decision.get("reason_codes", []),
            "must_be_resolved_before_real_pilot": True,
            "must_be_resolved_before_production": True,
            "must_be_resolved_before_bic_os": True,
        }
        blocker["blocker_sha256"] = stable_hash(blocker)
        blockers.append(blocker)
    register = {
        "version": "v5.50",
        "real_pilot_intake_blocker_register_ready": len(blockers) >= len(REQUIRED_EXTERNAL_EVIDENCE_TYPES_V550) + 9,
        "blocker_count": len(blockers),
        "blockers": blockers,
        "real_external_pilot_ready": False,
        "production_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    register["real_pilot_intake_blocker_register_sha256"] = stable_hash(register)
    return register


def build_external_acceptance_audit_bundle_v550(policy: dict[str, Any], schema: dict[str, Any], evidence_matrix: dict[str, Any], intake_gate: dict[str, Any], packet: dict[str, Any], blocker_register: dict[str, Any]) -> dict[str, Any]:
    bundle_ready = (
        policy.get("external_acceptance_intake_policy_ready") is True
        and schema.get("external_acceptance_evidence_schema_ready") is True
        and evidence_matrix.get("external_acceptance_evidence_matrix_ready") is True
        and intake_gate.get("real_pilot_intake_gate_ready") is True
        and packet.get("external_acceptance_packet_ready") is True
        and blocker_register.get("real_pilot_intake_blocker_register_ready") is True
    )
    bundle = {
        "version": "v5.50",
        "external_acceptance_audit_bundle_ready": bundle_ready,
        "policy_sha256": policy.get("external_acceptance_intake_policy_sha256"),
        "schema_sha256": schema.get("external_acceptance_evidence_schema_sha256"),
        "evidence_matrix_sha256": evidence_matrix.get("external_acceptance_evidence_matrix_sha256"),
        "intake_gate_sha256": intake_gate.get("real_pilot_intake_gate_sha256"),
        "packet_sha256": packet.get("external_acceptance_packet_sha256"),
        "blocker_register_sha256": blocker_register.get("real_pilot_intake_blocker_register_sha256"),
        "real_external_pilot_ready": False,
        "production_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    bundle["external_acceptance_audit_bundle_sha256"] = stable_hash(bundle)
    return bundle


def run_external_acceptance_intake_workflow_v550(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    project_root = Path(root).resolve()
    out = project_root / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    v549_dependency = run_production_readiness_gap_workflow_v549(project_root, out.parent / "d550")
    policy = build_external_acceptance_intake_policy_v550()
    schema = build_external_acceptance_evidence_schema_v550(policy)
    evidence_matrix = build_external_acceptance_evidence_matrix_v550(v549_dependency)
    intake_gate = run_real_pilot_intake_gate_v550(v549_dependency, evidence_matrix)
    packet = build_external_acceptance_packet_v550(v549_dependency, schema, evidence_matrix, intake_gate)
    blocker_register = build_real_pilot_intake_blocker_register_v550(evidence_matrix, intake_gate)
    audit_bundle = build_external_acceptance_audit_bundle_v550(policy, schema, evidence_matrix, intake_gate, packet, blocker_register)
    proof_ready = (
        v549_dependency.get("production_readiness_gap_contract_ready") is True
        and policy.get("external_acceptance_intake_policy_ready") is True
        and schema.get("external_acceptance_evidence_schema_ready") is True
        and evidence_matrix.get("external_acceptance_evidence_matrix_ready") is True
        and intake_gate.get("real_pilot_intake_gate_ready") is True
        and packet.get("external_acceptance_packet_ready") is True
        and blocker_register.get("real_pilot_intake_blocker_register_ready") is True
        and audit_bundle.get("external_acceptance_audit_bundle_ready") is True
    )
    audit = {
        "version": "v5.50",
        "phase": "external_acceptance_evidence_real_pilot_intake_contract",
        "overall_status": "external_acceptance_intake_contract_ready_pilot_not_claimed" if proof_ready else "external_acceptance_intake_contract_incomplete",
        "active_phase": "biosdk_external_acceptance_intake_proof",
        "bic_os_phase_locked": True,
        "external_acceptance_intake_contract_ready": proof_ready,
        "v549_dependency_ready": v549_dependency.get("production_readiness_gap_contract_ready") is True,
        "external_acceptance_intake_policy_ready": policy.get("external_acceptance_intake_policy_ready") is True,
        "external_acceptance_evidence_schema_ready": schema.get("external_acceptance_evidence_schema_ready") is True,
        "external_acceptance_evidence_matrix_ready": evidence_matrix.get("external_acceptance_evidence_matrix_ready") is True,
        "real_pilot_intake_gate_ready": intake_gate.get("real_pilot_intake_gate_ready") is True,
        "external_acceptance_packet_ready": packet.get("external_acceptance_packet_ready") is True,
        "real_pilot_intake_blocker_register_ready": blocker_register.get("real_pilot_intake_blocker_register_ready") is True,
        "external_acceptance_audit_bundle_ready": audit_bundle.get("external_acceptance_audit_bundle_ready") is True,
        "artifact_name": v549_dependency.get("artifact_name"),
        "artifact_sha256": v549_dependency.get("artifact_sha256"),
        "required_evidence_type_count": len(REQUIRED_EXTERNAL_EVIDENCE_TYPES_V550),
        "schema_valid_record_count": evidence_matrix.get("schema_valid_record_count"),
        "real_acceptance_ready_count": evidence_matrix.get("real_acceptance_ready_count"),
        "accepted_local_intake_stage_count": intake_gate.get("accepted_local_intake_stage_count"),
        "denied_intake_gate_count": intake_gate.get("denied_intake_gate_count"),
        "external_acceptance_packet_record_count": packet.get("packet_record_count"),
        "real_pilot_intake_blocker_count": blocker_register.get("blocker_count"),
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
        "external_acceptance_intake_policy": policy,
        "external_acceptance_evidence_schema": schema,
        "external_acceptance_evidence_matrix": evidence_matrix,
        "real_pilot_intake_gate": intake_gate,
        "external_acceptance_packet": packet,
        "real_pilot_intake_blocker_register": blocker_register,
        "external_acceptance_audit_bundle": audit_bundle,
        "v549_dependency_summary": {key: value for key, value in v549_dependency.items() if key not in {"production_readiness_gap_policy", "production_readiness_gap_matrix", "staged_pilot_acceptance_matrix", "staged_pilot_acceptance_plan", "readiness_blocker_register", "production_readiness_audit_bundle", "v548_dependency_summary"}},
        "missing_real_inputs": [
            "real pilot partner identity records",
            "signed data-use and acceptance approvals",
            "external security review signoff",
            "production identity-provider approval",
            "live registry administrative approval",
            "trusted signing authority approval",
            "production CI/CD gate acceptance",
            "support and incident response acceptance",
            "notification provider acceptance and recipient acknowledgement plan",
            "rollback/yank acceptance and legal/compliance approval",
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
            "did_we_add_external_acceptance_schema": "yes" if schema.get("external_acceptance_evidence_schema_ready") else "no",
            "did_we_add_real_pilot_intake_gate": "yes" if intake_gate.get("real_pilot_intake_gate_ready") else "no",
            "are_real_external_acceptance_records_ready": "no",
            "is_real_external_pilot_ready": "no",
            "is_production_ready": "no",
            "is_full_biosdk_ready": "no",
            "is_biocompute_runtime_ready": "no",
            "is_bic_os_ready": "no",
            "next_best_build_step": "add partner data-room package manifest and external review packet proof" if proof_ready else "fix v5.50 acceptance-intake blockers first",
        },
        "claim_boundary": "v5.50 proves a local external-acceptance evidence schema, local evidence packet shape and real-pilot intake gate over the v5.49 production readiness gap contract. It does not claim real external acceptance records, real external pilot readiness, production readiness, full BioSDK, production BioCompute Runtime or BiC OS readiness.",
    }
    audit["external_acceptance_intake_audit_sha256"] = stable_hash({key: value for key, value in audit.items() if key != "external_acceptance_intake_audit_sha256"})
    return audit


def write_external_acceptance_intake_outputs_v550(audit: dict[str, Any], out_dir: str | Path = DEFAULT_OUT) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary_json": out / "V550_EXTERNAL_ACCEPTANCE_INTAKE_SUMMARY.json",
        "policy_json": out / "V550_EXTERNAL_ACCEPTANCE_INTAKE_POLICY.json",
        "schema_json": out / "V550_EXTERNAL_ACCEPTANCE_EVIDENCE_SCHEMA.json",
        "evidence_matrix_json": out / "V550_EXTERNAL_ACCEPTANCE_EVIDENCE_MATRIX.json",
        "intake_gate_json": out / "V550_REAL_PILOT_INTAKE_GATE.json",
        "packet_json": out / "V550_EXTERNAL_ACCEPTANCE_PACKET.json",
        "blocker_register_json": out / "V550_REAL_PILOT_INTAKE_BLOCKER_REGISTER.json",
        "audit_bundle_json": out / "V550_EXTERNAL_ACCEPTANCE_AUDIT_BUNDLE.json",
        "evidence_matrix_csv": out / "V550_EXTERNAL_ACCEPTANCE_EVIDENCE_MATRIX.csv",
        "intake_gate_csv": out / "V550_REAL_PILOT_INTAKE_GATE.csv",
        "markdown_report": out / "BIOGPU_V550_EXTERNAL_ACCEPTANCE_INTAKE_REPORT.md",
    }
    summary = {key: value for key, value in audit.items() if key not in {"external_acceptance_intake_policy", "external_acceptance_evidence_schema", "external_acceptance_evidence_matrix", "real_pilot_intake_gate", "external_acceptance_packet", "real_pilot_intake_blocker_register", "external_acceptance_audit_bundle"}}
    paths["summary_json"].write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["policy_json"].write_text(json.dumps(audit["external_acceptance_intake_policy"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["schema_json"].write_text(json.dumps(audit["external_acceptance_evidence_schema"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["evidence_matrix_json"].write_text(json.dumps(audit["external_acceptance_evidence_matrix"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["intake_gate_json"].write_text(json.dumps(audit["real_pilot_intake_gate"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["packet_json"].write_text(json.dumps(audit["external_acceptance_packet"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["blocker_register_json"].write_text(json.dumps(audit["real_pilot_intake_blocker_register"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["audit_bundle_json"].write_text(json.dumps(audit["external_acceptance_audit_bundle"], indent=2, ensure_ascii=False), encoding="utf-8")
    _write_evidence_matrix_csv(paths["evidence_matrix_csv"], audit["external_acceptance_evidence_matrix"].get("decisions", []))
    _write_intake_gate_csv(paths["intake_gate_csv"], audit["real_pilot_intake_gate"].get("decisions", []))
    paths["markdown_report"].write_text(_markdown_report(audit), encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}


def _write_evidence_matrix_csv(path: Path, decisions: list[dict[str, Any]]) -> None:
    fieldnames = ["evidence_id", "evidence_type", "schema_record_valid", "real_acceptance_record_ready", "local_evidence_anchor", "reason_codes"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for decision in decisions:
            row = {field: decision.get(field) for field in fieldnames}
            row["reason_codes"] = " | ".join(str(reason) for reason in decision.get("reason_codes", []))
            writer.writerow(row)


def _write_intake_gate_csv(path: Path, decisions: list[dict[str, Any]]) -> None:
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
        "# BioGPU-Core v5.50 External Acceptance Intake Contract",
        "",
        "## Direct Answer",
        "",
        f"- External acceptance schema added: `{answer['did_we_add_external_acceptance_schema']}`",
        f"- Real-pilot intake gate added: `{answer['did_we_add_real_pilot_intake_gate']}`",
        f"- Real external acceptance records ready: `{answer['are_real_external_acceptance_records_ready']}`",
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
        f"- v5.49 dependency ready: `{audit['v549_dependency_ready']}`",
        f"- Required evidence types: `{audit['required_evidence_type_count']}`",
        f"- Schema-valid records: `{audit['schema_valid_record_count']}`",
        f"- Real acceptance-ready records: `{audit['real_acceptance_ready_count']}`",
        f"- Accepted local intake stages: `{audit['accepted_local_intake_stage_count']}`",
        f"- Denied intake gates: `{audit['denied_intake_gate_count']}`",
        "",
        "## Missing Real Inputs",
        "",
    ]
    for missing in audit["missing_real_inputs"]:
        lines.append(f"- {missing}")
    lines.extend(["", "## Boundary", "", audit["claim_boundary"], ""])
    return "\n".join(lines)