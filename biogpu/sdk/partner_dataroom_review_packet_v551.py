"""Partner data-room manifest and external review packet proof, v5.51."""
from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from biogpu.beta.job_model_v43 import utc_now_iso
from biogpu.evidence.ledger_v53 import stable_hash
from biogpu.sdk.external_acceptance_intake_v550 import run_external_acceptance_intake_workflow_v550


DEFAULT_OUT = Path("outputs/v551_partner_dataroom_review_packet")
REQUIRED_DATAROOM_ITEMS_V551 = (
    "project_identity_and_claim_boundary",
    "v550_external_acceptance_intake_summary",
    "v549_production_readiness_gap_summary",
    "sdk_install_gate_and_runbook",
    "artifact_hashes_and_provenance",
    "security_and_identity_gap_summary",
    "storage_retention_gap_summary",
    "registry_revocation_notification_summary",
    "pilot_intake_blocker_register",
    "missing_real_inputs_register",
    "external_review_questionnaire",
    "reviewer_attestation_template",
)
EXTERNAL_REVIEW_PACKET_SECTIONS_V551 = (
    "cover_note",
    "claim_boundary_attestation",
    "evidence_index",
    "data_use_boundary",
    "security_review_questions",
    "pilot_readiness_questions",
    "blocker_register_summary",
    "signature_placeholders",
)
LOCAL_REVIEW_STAGES_V551 = ("manifest_assembly", "packet_assembly", "reviewer_preflight")


@dataclass(frozen=True)
class PartnerDataRoomPolicyV551:
    policy_id: str
    required_dataroom_items: tuple[str, ...]
    external_review_packet_sections: tuple[str, ...]
    local_review_stages: tuple[str, ...]
    requires_v550_external_acceptance_intake: bool
    requires_claim_boundary_attestation: bool
    requires_manifest_hash_anchors: bool
    requires_external_reviewer_identity: bool
    requires_external_reviewer_signature: bool
    requires_real_dataroom_upload: bool
    local_contract_only: bool = True
    real_external_review_ready: bool = False
    real_external_pilot_ready: bool = False
    production_ready: bool = False
    full_biosdk_ready: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DataRoomManifestItemFixtureV551:
    item_id: str
    item_type: str
    has_v550_anchor: bool
    has_local_artifact_reference: bool
    has_claim_boundary: bool
    has_missing_input_notes: bool
    has_hash_anchor: bool
    has_real_partner_dataroom_upload: bool
    has_external_reviewer_access: bool
    requests_real_external_review: bool
    requests_real_external_pilot: bool
    requests_production_release: bool
    requests_bic_os_unlock: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DataRoomManifestItemDecisionV551:
    item_id: str
    item_type: str
    local_manifest_item_ready: bool
    real_dataroom_item_ready: bool
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
class ExternalReviewGateFixtureV551:
    gate_id: str
    has_v550_intake_contract: bool
    has_dataroom_manifest: bool
    has_external_review_packet: bool
    has_claim_boundary: bool
    has_no_open_intake_blockers: bool
    has_external_reviewer_identity: bool
    has_external_reviewer_signature: bool
    requests_external_review_session: bool
    requests_real_external_pilot: bool
    requests_production_release: bool
    requests_bic_os_unlock: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ExternalReviewGateDecisionV551:
    gate_id: str
    accepted_for_local_review_stage: bool
    reason_codes: tuple[str, ...]
    local_review_record_id: str | None
    real_external_review_ready: bool = False
    real_external_pilot_ready: bool = False
    production_release_ready: bool = False
    full_biosdk_ready: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_partner_dataroom_policy_v551() -> dict[str, Any]:
    policy = PartnerDataRoomPolicyV551(
        policy_id="BIOGPU_CORE_V551_PARTNER_DATAROOM_REVIEW_PACKET_POLICY",
        required_dataroom_items=REQUIRED_DATAROOM_ITEMS_V551,
        external_review_packet_sections=EXTERNAL_REVIEW_PACKET_SECTIONS_V551,
        local_review_stages=LOCAL_REVIEW_STAGES_V551,
        requires_v550_external_acceptance_intake=True,
        requires_claim_boundary_attestation=True,
        requires_manifest_hash_anchors=True,
        requires_external_reviewer_identity=True,
        requires_external_reviewer_signature=True,
        requires_real_dataroom_upload=True,
    )
    result = {
        "version": "v5.51",
        "partner_dataroom_policy_ready": True,
        "policy": policy.to_dict(),
        "blocked_modes": ["real_external_review", "real_external_pilot", "production_release", "production_ready_claim", "bic_os_unlock"],
        "required_real_records": ["real_partner_dataroom_upload", "external_reviewer_identity", "external_reviewer_access", "external_reviewer_signature", "review_session_timestamp"],
        "real_external_review_ready": False,
        "real_external_pilot_ready": False,
        "production_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    result["partner_dataroom_policy_sha256"] = stable_hash(result)
    return result


def default_dataroom_manifest_item_fixtures_v551() -> list[DataRoomManifestItemFixtureV551]:
    fixtures: list[DataRoomManifestItemFixtureV551] = []
    for item_type in REQUIRED_DATAROOM_ITEMS_V551:
        fixtures.append(
            DataRoomManifestItemFixtureV551(
                item_id=f"manifest-{item_type}",
                item_type=item_type,
                has_v550_anchor=True,
                has_local_artifact_reference=True,
                has_claim_boundary=True,
                has_missing_input_notes=True,
                has_hash_anchor=True,
                has_real_partner_dataroom_upload=False,
                has_external_reviewer_access=False,
                requests_real_external_review=item_type == "external_review_questionnaire",
                requests_real_external_pilot=item_type == "pilot_intake_blocker_register",
                requests_production_release=item_type == "sdk_install_gate_and_runbook",
                requests_bic_os_unlock=item_type == "reviewer_attestation_template",
            )
        )
    return fixtures


def evaluate_dataroom_manifest_item_v551(fixture: DataRoomManifestItemFixtureV551, v550_dependency: dict[str, Any]) -> DataRoomManifestItemDecisionV551:
    reasons: list[str] = []
    if v550_dependency.get("external_acceptance_intake_contract_ready") is not True or not fixture.has_v550_anchor:
        reasons.append("v550_external_acceptance_intake_missing")
    if fixture.item_type not in REQUIRED_DATAROOM_ITEMS_V551:
        reasons.append("dataroom_item_type_not_allowed")
    if not fixture.has_local_artifact_reference:
        reasons.append("local_artifact_reference_missing")
    if not fixture.has_claim_boundary:
        reasons.append("claim_boundary_missing")
    if not fixture.has_missing_input_notes:
        reasons.append("missing_input_notes_missing")
    if not fixture.has_hash_anchor:
        reasons.append("manifest_hash_anchor_missing")
    local_ready = not any(
        reason in reasons
        for reason in {
            "v550_external_acceptance_intake_missing",
            "dataroom_item_type_not_allowed",
            "local_artifact_reference_missing",
            "claim_boundary_missing",
            "missing_input_notes_missing",
            "manifest_hash_anchor_missing",
        }
    )
    if not fixture.has_real_partner_dataroom_upload:
        reasons.append("real_partner_dataroom_upload_missing")
    if not fixture.has_external_reviewer_access:
        reasons.append("external_reviewer_access_missing")
    if fixture.requests_real_external_review:
        reasons.append("real_external_review_not_ready")
    if fixture.requests_real_external_pilot:
        reasons.append("real_external_pilot_not_ready")
    if fixture.requests_production_release:
        reasons.append("production_release_not_allowed")
    if fixture.requests_bic_os_unlock:
        reasons.append("bic_os_unlock_not_allowed")
    return DataRoomManifestItemDecisionV551(
        item_id=fixture.item_id,
        item_type=fixture.item_type,
        local_manifest_item_ready=local_ready,
        real_dataroom_item_ready=False,
        reason_codes=tuple(reasons or ["dataroom_manifest_item_ready"]),
        local_anchor=str(v550_dependency.get("external_acceptance_intake_audit_sha256") or "") or None,
    )


def build_partner_dataroom_manifest_v551(v550_dependency: dict[str, Any], fixtures: list[DataRoomManifestItemFixtureV551] | None = None) -> dict[str, Any]:
    manifest_fixtures = fixtures or default_dataroom_manifest_item_fixtures_v551()
    decisions = [evaluate_dataroom_manifest_item_v551(fixture, v550_dependency).to_dict() for fixture in manifest_fixtures]
    local_ready_count = sum(1 for decision in decisions if decision["local_manifest_item_ready"])
    real_ready_count = sum(1 for decision in decisions if decision["real_dataroom_item_ready"])
    item_types = sorted({decision["item_type"] for decision in decisions})
    reason_codes = sorted({reason for decision in decisions for reason in decision["reason_codes"]})
    required_reasons = {
        "real_partner_dataroom_upload_missing",
        "external_reviewer_access_missing",
        "real_external_review_not_ready",
        "real_external_pilot_not_ready",
        "production_release_not_allowed",
        "bic_os_unlock_not_allowed",
    }
    manifest = {
        "version": "v5.51",
        "partner_dataroom_manifest_ready": local_ready_count == len(REQUIRED_DATAROOM_ITEMS_V551) and real_ready_count == 0 and set(item_types) == set(REQUIRED_DATAROOM_ITEMS_V551) and required_reasons.issubset(set(reason_codes)),
        "manifest_item_count": len(decisions),
        "local_manifest_item_ready_count": local_ready_count,
        "real_dataroom_item_ready_count": real_ready_count,
        "item_types": item_types,
        "reason_codes": reason_codes,
        "fixtures": [fixture.to_dict() for fixture in manifest_fixtures],
        "decisions": decisions,
        "real_external_review_ready": False,
        "real_external_pilot_ready": False,
        "production_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    manifest["partner_dataroom_manifest_sha256"] = stable_hash(manifest)
    return manifest


def build_external_review_packet_v551(v550_dependency: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for section in EXTERNAL_REVIEW_PACKET_SECTIONS_V551:
        record = {
            "version": "v5.51",
            "packet_section_id": f"review-section-{section}",
            "section_type": section,
            "v550_acceptance_intake_anchor": v550_dependency.get("external_acceptance_intake_audit_sha256"),
            "dataroom_manifest_anchor": manifest.get("partner_dataroom_manifest_sha256"),
            "local_review_packet_section_ready": manifest.get("partner_dataroom_manifest_ready") is True,
            "external_review_completed": False,
            "external_reviewer_signature_present": False,
            "real_external_review_ready": False,
            "real_external_pilot_ready": False,
            "production_ready": False,
            "created_at": utc_now_iso(),
        }
        record["packet_section_sha256"] = stable_hash(record)
        records.append(record)
    packet = {
        "version": "v5.51",
        "external_review_packet_ready": len(records) == len(EXTERNAL_REVIEW_PACKET_SECTIONS_V551) and manifest.get("partner_dataroom_manifest_ready") is True,
        "packet_section_count": len(records),
        "local_review_packet_section_ready_count": sum(1 for record in records if record["local_review_packet_section_ready"]),
        "external_review_completed_count": sum(1 for record in records if record["external_review_completed"]),
        "packet_sections": records,
        "real_external_review_ready": False,
        "real_external_pilot_ready": False,
        "production_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    packet["external_review_packet_sha256"] = stable_hash(packet)
    return packet


def default_external_review_gate_fixtures_v551() -> list[ExternalReviewGateFixtureV551]:
    return [
        ExternalReviewGateFixtureV551("manifest-assembly", True, True, True, True, False, True, True, False, False, False, False),
        ExternalReviewGateFixtureV551("packet-assembly", True, True, True, True, False, True, True, False, False, False, False),
        ExternalReviewGateFixtureV551("reviewer-preflight", True, True, True, True, False, True, True, False, False, False, False),
        ExternalReviewGateFixtureV551("missing-v550-contract", False, True, True, True, False, True, True, False, False, False, False),
        ExternalReviewGateFixtureV551("missing-dataroom-manifest", True, False, True, True, False, True, True, False, False, False, False),
        ExternalReviewGateFixtureV551("missing-review-packet", True, True, False, True, False, True, True, False, False, False, False),
        ExternalReviewGateFixtureV551("missing-claim-boundary", True, True, True, False, False, True, True, False, False, False, False),
        ExternalReviewGateFixtureV551("missing-reviewer-approval", True, True, True, True, True, False, False, True, False, False, False),
        ExternalReviewGateFixtureV551("external-review-with-open-blockers", True, True, True, True, False, True, True, True, False, False, False),
        ExternalReviewGateFixtureV551("real-pilot-request", True, True, True, True, True, True, True, False, True, False, False),
        ExternalReviewGateFixtureV551("production-release-request", True, True, True, True, True, True, True, False, False, True, False),
        ExternalReviewGateFixtureV551("bic-os-unlock-request", True, True, True, True, True, True, True, False, False, False, True),
    ]


def evaluate_external_review_gate_v551(fixture: ExternalReviewGateFixtureV551, v550_dependency: dict[str, Any], manifest: dict[str, Any], review_packet: dict[str, Any]) -> ExternalReviewGateDecisionV551:
    reasons: list[str] = []
    if v550_dependency.get("external_acceptance_intake_contract_ready") is not True or not fixture.has_v550_intake_contract:
        reasons.append("v550_external_acceptance_intake_missing")
    if manifest.get("partner_dataroom_manifest_ready") is not True or not fixture.has_dataroom_manifest:
        reasons.append("dataroom_manifest_missing")
    if review_packet.get("external_review_packet_ready") is not True or not fixture.has_external_review_packet:
        reasons.append("external_review_packet_missing")
    if not fixture.has_claim_boundary:
        reasons.append("claim_boundary_missing")
    if fixture.requests_external_review_session:
        if not fixture.has_no_open_intake_blockers:
            reasons.append("intake_blockers_still_open")
        if not fixture.has_external_reviewer_identity:
            reasons.append("external_reviewer_identity_missing")
        if not fixture.has_external_reviewer_signature:
            reasons.append("external_reviewer_signature_missing")
        reasons.append("real_external_review_not_ready")
    if fixture.requests_real_external_pilot:
        reasons.append("real_external_pilot_not_ready")
    if fixture.requests_production_release:
        reasons.append("production_release_not_allowed")
    if fixture.requests_bic_os_unlock:
        reasons.append("bic_os_unlock_not_allowed")
    accepted = not reasons
    return ExternalReviewGateDecisionV551(
        gate_id=fixture.gate_id,
        accepted_for_local_review_stage=accepted,
        reason_codes=tuple(reasons or ["local_review_stage_accepted"]),
        local_review_record_id=f"local-review-{fixture.gate_id}" if accepted else None,
    )


def run_external_review_gate_v551(v550_dependency: dict[str, Any], manifest: dict[str, Any], review_packet: dict[str, Any], fixtures: list[ExternalReviewGateFixtureV551] | None = None) -> dict[str, Any]:
    gate_fixtures = fixtures or default_external_review_gate_fixtures_v551()
    decisions = [evaluate_external_review_gate_v551(fixture, v550_dependency, manifest, review_packet).to_dict() for fixture in gate_fixtures]
    accepted_count = sum(1 for decision in decisions if decision["accepted_for_local_review_stage"])
    denied_count = len(decisions) - accepted_count
    reason_codes = sorted({reason for decision in decisions for reason in decision["reason_codes"]})
    required_denials = {
        "v550_external_acceptance_intake_missing",
        "dataroom_manifest_missing",
        "external_review_packet_missing",
        "claim_boundary_missing",
        "external_reviewer_identity_missing",
        "external_reviewer_signature_missing",
        "intake_blockers_still_open",
        "real_external_review_not_ready",
        "real_external_pilot_not_ready",
        "production_release_not_allowed",
        "bic_os_unlock_not_allowed",
    }
    gate = {
        "version": "v5.51",
        "external_review_gate_ready": accepted_count == len(LOCAL_REVIEW_STAGES_V551) and denied_count == 9 and required_denials.issubset(set(reason_codes)),
        "gate_fixture_count": len(gate_fixtures),
        "accepted_local_review_stage_count": accepted_count,
        "denied_external_review_gate_count": denied_count,
        "reason_codes": reason_codes,
        "fixtures": [fixture.to_dict() for fixture in gate_fixtures],
        "decisions": decisions,
        "real_external_review_ready": False,
        "real_external_pilot_ready": False,
        "production_release_ready": False,
        "production_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    gate["external_review_gate_sha256"] = stable_hash(gate)
    return gate


def build_external_review_blocker_register_v551(manifest: dict[str, Any], review_gate: dict[str, Any]) -> dict[str, Any]:
    blockers: list[dict[str, Any]] = []
    for decision in manifest.get("decisions", []):
        if decision.get("real_dataroom_item_ready") is True:
            continue
        blocker = {
            "version": "v5.51",
            "blocker_id": f"dataroom-blocker-{decision['item_id']}",
            "source": "partner_dataroom_manifest",
            "record_id": decision.get("item_id"),
            "reason_codes": decision.get("reason_codes", []),
            "must_be_resolved_before_external_review": True,
            "must_be_resolved_before_real_pilot": True,
            "must_be_resolved_before_production": True,
            "must_be_resolved_before_bic_os": True,
        }
        blocker["blocker_sha256"] = stable_hash(blocker)
        blockers.append(blocker)
    for decision in review_gate.get("decisions", []):
        if decision.get("accepted_for_local_review_stage") is True:
            continue
        blocker = {
            "version": "v5.51",
            "blocker_id": f"review-gate-blocker-{decision['gate_id']}",
            "source": "external_review_gate",
            "record_id": decision.get("gate_id"),
            "reason_codes": decision.get("reason_codes", []),
            "must_be_resolved_before_external_review": True,
            "must_be_resolved_before_real_pilot": True,
            "must_be_resolved_before_production": True,
            "must_be_resolved_before_bic_os": True,
        }
        blocker["blocker_sha256"] = stable_hash(blocker)
        blockers.append(blocker)
    register = {
        "version": "v5.51",
        "external_review_blocker_register_ready": len(blockers) == len(REQUIRED_DATAROOM_ITEMS_V551) + 9,
        "blocker_count": len(blockers),
        "blockers": blockers,
        "real_external_review_ready": False,
        "real_external_pilot_ready": False,
        "production_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    register["external_review_blocker_register_sha256"] = stable_hash(register)
    return register


def build_partner_dataroom_audit_bundle_v551(policy: dict[str, Any], manifest: dict[str, Any], review_packet: dict[str, Any], review_gate: dict[str, Any], blocker_register: dict[str, Any]) -> dict[str, Any]:
    bundle_ready = (
        policy.get("partner_dataroom_policy_ready") is True
        and manifest.get("partner_dataroom_manifest_ready") is True
        and review_packet.get("external_review_packet_ready") is True
        and review_gate.get("external_review_gate_ready") is True
        and blocker_register.get("external_review_blocker_register_ready") is True
    )
    bundle = {
        "version": "v5.51",
        "partner_dataroom_audit_bundle_ready": bundle_ready,
        "policy_sha256": policy.get("partner_dataroom_policy_sha256"),
        "manifest_sha256": manifest.get("partner_dataroom_manifest_sha256"),
        "review_packet_sha256": review_packet.get("external_review_packet_sha256"),
        "review_gate_sha256": review_gate.get("external_review_gate_sha256"),
        "blocker_register_sha256": blocker_register.get("external_review_blocker_register_sha256"),
        "real_external_review_ready": False,
        "real_external_pilot_ready": False,
        "production_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    bundle["partner_dataroom_audit_bundle_sha256"] = stable_hash(bundle)
    return bundle


def run_partner_dataroom_review_packet_workflow_v551(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    project_root = Path(root).resolve()
    out = project_root / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    v550_dependency = run_external_acceptance_intake_workflow_v550(project_root, out.parent / "d551")
    policy = build_partner_dataroom_policy_v551()
    manifest = build_partner_dataroom_manifest_v551(v550_dependency)
    review_packet = build_external_review_packet_v551(v550_dependency, manifest)
    review_gate = run_external_review_gate_v551(v550_dependency, manifest, review_packet)
    blocker_register = build_external_review_blocker_register_v551(manifest, review_gate)
    audit_bundle = build_partner_dataroom_audit_bundle_v551(policy, manifest, review_packet, review_gate, blocker_register)
    proof_ready = (
        v550_dependency.get("external_acceptance_intake_contract_ready") is True
        and policy.get("partner_dataroom_policy_ready") is True
        and manifest.get("partner_dataroom_manifest_ready") is True
        and review_packet.get("external_review_packet_ready") is True
        and review_gate.get("external_review_gate_ready") is True
        and blocker_register.get("external_review_blocker_register_ready") is True
        and audit_bundle.get("partner_dataroom_audit_bundle_ready") is True
    )
    audit = {
        "version": "v5.51",
        "phase": "partner_dataroom_external_review_packet_contract",
        "overall_status": "partner_dataroom_review_packet_contract_ready_review_not_claimed" if proof_ready else "partner_dataroom_review_packet_contract_incomplete",
        "active_phase": "biosdk_partner_dataroom_review_packet_proof",
        "bic_os_phase_locked": True,
        "partner_dataroom_review_packet_contract_ready": proof_ready,
        "v550_dependency_ready": v550_dependency.get("external_acceptance_intake_contract_ready") is True,
        "partner_dataroom_policy_ready": policy.get("partner_dataroom_policy_ready") is True,
        "partner_dataroom_manifest_ready": manifest.get("partner_dataroom_manifest_ready") is True,
        "external_review_packet_ready": review_packet.get("external_review_packet_ready") is True,
        "external_review_gate_ready": review_gate.get("external_review_gate_ready") is True,
        "external_review_blocker_register_ready": blocker_register.get("external_review_blocker_register_ready") is True,
        "partner_dataroom_audit_bundle_ready": audit_bundle.get("partner_dataroom_audit_bundle_ready") is True,
        "artifact_name": v550_dependency.get("artifact_name"),
        "artifact_sha256": v550_dependency.get("artifact_sha256"),
        "required_dataroom_item_count": len(REQUIRED_DATAROOM_ITEMS_V551),
        "local_manifest_item_ready_count": manifest.get("local_manifest_item_ready_count"),
        "real_dataroom_item_ready_count": manifest.get("real_dataroom_item_ready_count"),
        "external_review_packet_section_count": review_packet.get("packet_section_count"),
        "external_review_completed_count": review_packet.get("external_review_completed_count"),
        "accepted_local_review_stage_count": review_gate.get("accepted_local_review_stage_count"),
        "denied_external_review_gate_count": review_gate.get("denied_external_review_gate_count"),
        "external_review_blocker_count": blocker_register.get("blocker_count"),
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
        "partner_dataroom_policy": policy,
        "partner_dataroom_manifest": manifest,
        "external_review_packet": review_packet,
        "external_review_gate": review_gate,
        "external_review_blocker_register": blocker_register,
        "partner_dataroom_audit_bundle": audit_bundle,
        "v550_dependency_summary": {key: value for key, value in v550_dependency.items() if key not in {"external_acceptance_intake_policy", "external_acceptance_evidence_schema", "external_acceptance_evidence_matrix", "real_pilot_intake_gate", "external_acceptance_packet", "real_pilot_intake_blocker_register", "external_acceptance_audit_bundle", "v549_dependency_summary"}},
        "missing_real_inputs": [
            "real partner data-room workspace and access-control configuration",
            "real external reviewer identity records",
            "external reviewer account access acknowledgement",
            "external reviewer signed packet acceptance",
            "real review session timestamp and immutable transcript",
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
            "did_we_add_partner_dataroom_manifest": "yes" if manifest.get("partner_dataroom_manifest_ready") else "no",
            "did_we_add_external_review_packet": "yes" if review_packet.get("external_review_packet_ready") else "no",
            "are_real_dataroom_items_ready": "no",
            "is_real_external_review_ready": "no",
            "is_real_external_pilot_ready": "no",
            "is_production_ready": "no",
            "is_full_biosdk_ready": "no",
            "is_biocompute_runtime_ready": "no",
            "is_bic_os_ready": "no",
            "next_best_build_step": "add external reviewer questionnaire scoring and signed review-response intake proof" if proof_ready else "fix v5.51 data-room/review-packet blockers first",
        },
        "claim_boundary": "v5.51 proves a local partner data-room manifest, local external review packet shape and review preflight gate over the v5.50 external acceptance intake contract. It does not claim real data-room upload, real external reviewer access, completed external review, real external pilot readiness, production readiness, full BioSDK, production BioCompute Runtime or BiC OS readiness.",
    }
    audit["partner_dataroom_review_packet_audit_sha256"] = stable_hash({key: value for key, value in audit.items() if key != "partner_dataroom_review_packet_audit_sha256"})
    return audit


def write_partner_dataroom_review_packet_outputs_v551(audit: dict[str, Any], out_dir: str | Path = DEFAULT_OUT) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary_json": out / "V551_PARTNER_DATAROOM_REVIEW_PACKET_SUMMARY.json",
        "policy_json": out / "V551_PARTNER_DATAROOM_POLICY.json",
        "manifest_json": out / "V551_PARTNER_DATAROOM_MANIFEST.json",
        "review_packet_json": out / "V551_EXTERNAL_REVIEW_PACKET.json",
        "review_gate_json": out / "V551_EXTERNAL_REVIEW_GATE.json",
        "blocker_register_json": out / "V551_EXTERNAL_REVIEW_BLOCKER_REGISTER.json",
        "audit_bundle_json": out / "V551_PARTNER_DATAROOM_AUDIT_BUNDLE.json",
        "manifest_csv": out / "V551_PARTNER_DATAROOM_MANIFEST.csv",
        "review_gate_csv": out / "V551_EXTERNAL_REVIEW_GATE.csv",
        "markdown_report": out / "BIOGPU_V551_PARTNER_DATAROOM_REVIEW_PACKET_REPORT.md",
    }
    summary = {key: value for key, value in audit.items() if key not in {"partner_dataroom_policy", "partner_dataroom_manifest", "external_review_packet", "external_review_gate", "external_review_blocker_register", "partner_dataroom_audit_bundle"}}
    paths["summary_json"].write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["policy_json"].write_text(json.dumps(audit["partner_dataroom_policy"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["manifest_json"].write_text(json.dumps(audit["partner_dataroom_manifest"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["review_packet_json"].write_text(json.dumps(audit["external_review_packet"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["review_gate_json"].write_text(json.dumps(audit["external_review_gate"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["blocker_register_json"].write_text(json.dumps(audit["external_review_blocker_register"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["audit_bundle_json"].write_text(json.dumps(audit["partner_dataroom_audit_bundle"], indent=2, ensure_ascii=False), encoding="utf-8")
    _write_manifest_csv(paths["manifest_csv"], audit["partner_dataroom_manifest"].get("decisions", []))
    _write_review_gate_csv(paths["review_gate_csv"], audit["external_review_gate"].get("decisions", []))
    paths["markdown_report"].write_text(_markdown_report(audit), encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}


def _write_manifest_csv(path: Path, decisions: list[dict[str, Any]]) -> None:
    fieldnames = ["item_id", "item_type", "local_manifest_item_ready", "real_dataroom_item_ready", "local_anchor", "reason_codes"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for decision in decisions:
            row = {field: decision.get(field) for field in fieldnames}
            row["reason_codes"] = " | ".join(str(reason) for reason in decision.get("reason_codes", []))
            writer.writerow(row)


def _write_review_gate_csv(path: Path, decisions: list[dict[str, Any]]) -> None:
    fieldnames = ["gate_id", "accepted_for_local_review_stage", "local_review_record_id", "reason_codes"]
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
        "# BioGPU-Core v5.51 Partner Data-Room Review Packet Contract",
        "",
        "## Direct Answer",
        "",
        f"- Partner data-room manifest added: `{answer['did_we_add_partner_dataroom_manifest']}`",
        f"- External review packet added: `{answer['did_we_add_external_review_packet']}`",
        f"- Real data-room items ready: `{answer['are_real_dataroom_items_ready']}`",
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
        f"- v5.50 dependency ready: `{audit['v550_dependency_ready']}`",
        f"- Required data-room items: `{audit['required_dataroom_item_count']}`",
        f"- Local manifest-ready items: `{audit['local_manifest_item_ready_count']}`",
        f"- Real data-room-ready items: `{audit['real_dataroom_item_ready_count']}`",
        f"- External review packet sections: `{audit['external_review_packet_section_count']}`",
        f"- Accepted local review stages: `{audit['accepted_local_review_stage_count']}`",
        f"- Denied external review gates: `{audit['denied_external_review_gate_count']}`",
        "",
        "## Missing Real Inputs",
        "",
    ]
    for missing in audit["missing_real_inputs"]:
        lines.append(f"- {missing}")
    lines.extend(["", "## Boundary", "", audit["claim_boundary"], ""])
    return "\n".join(lines)