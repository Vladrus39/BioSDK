"""Production readiness gap matrix and staged pilot acceptance proof, v5.49."""
from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from biogpu.beta.job_model_v43 import utc_now_iso
from biogpu.evidence.ledger_v53 import stable_hash
from biogpu.sdk.release_operations_handoff_v548 import run_release_operations_handoff_workflow_v548


DEFAULT_OUT = Path("outputs/v549_production_readiness_gap")
READINESS_DOMAINS_V549 = (
    "production_identity_provider",
    "persistent_tenant_membership",
    "production_object_storage",
    "hosted_runtime_workers",
    "live_private_registry",
    "trusted_release_signing",
    "production_ci_cd_gates",
    "security_review_and_threat_model",
    "support_incident_system",
    "notification_provider",
    "external_beta_acceptance",
    "os_service_supervision",
)
PILOT_STAGES_V549 = ("local_dry_run", "operator_tabletop", "shadow_pilot_preflight", "external_packet_draft")


@dataclass(frozen=True)
class ProductionReadinessGapPolicyV549:
    policy_id: str
    readiness_domains: tuple[str, ...]
    pilot_stages: tuple[str, ...]
    requires_v548_release_ops_handoff: bool
    requires_gap_matrix: bool
    requires_staged_pilot_acceptance: bool
    requires_external_acceptance_records: bool
    requires_production_service_evidence: bool
    local_contract_only: bool = True
    production_ready: bool = False
    staged_pilot_ready: bool = False
    full_biosdk_ready: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ProductionReadinessGapFixtureV549:
    domain_id: str
    local_evidence_present: bool
    real_input_present: bool
    external_signoff_present: bool
    production_service_configured: bool
    acceptance_record_present: bool
    attempts_production_ready_claim: bool
    attempts_bic_os_unlock: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ProductionReadinessGapDecisionV549:
    domain_id: str
    production_ready_for_domain: bool
    gap_open: bool
    reason_codes: tuple[str, ...]
    missing_real_inputs: tuple[str, ...]
    local_evidence_anchor: str | None
    production_ready: bool = False
    full_biosdk_ready: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PilotAcceptanceFixtureV549:
    stage_id: str
    has_gap_matrix: bool
    has_release_ops_handoff: bool
    has_claim_boundary_ack: bool
    has_rollback_boundary: bool
    has_support_path: bool
    requests_live_pilot: bool
    requests_production_release: bool
    requests_bic_os_unlock: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PilotAcceptanceDecisionV549:
    stage_id: str
    accepted_for_local_pilot_stage: bool
    reason_codes: tuple[str, ...]
    acceptance_record_id: str | None
    production_release_ready: bool = False
    real_external_pilot_ready: bool = False
    full_biosdk_ready: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_production_readiness_gap_policy_v549() -> dict[str, Any]:
    policy = ProductionReadinessGapPolicyV549(
        policy_id="BIOGPU_CORE_V549_PRODUCTION_READINESS_GAP_POLICY",
        readiness_domains=READINESS_DOMAINS_V549,
        pilot_stages=PILOT_STAGES_V549,
        requires_v548_release_ops_handoff=True,
        requires_gap_matrix=True,
        requires_staged_pilot_acceptance=True,
        requires_external_acceptance_records=True,
        requires_production_service_evidence=True,
    )
    result = {
        "version": "v5.49",
        "production_readiness_gap_policy_ready": True,
        "policy": policy.to_dict(),
        "blocked_modes": ["production_ready_claim", "live_external_pilot", "production_release", "bic_os_unlock"],
        "required_real_records": ["real_operator_approvals", "production_service_evidence", "external_acceptance_records", "security_review", "ci_cd_gate_results"],
        "production_ready": False,
        "staged_pilot_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    result["production_readiness_gap_policy_sha256"] = stable_hash(result)
    return result


def default_production_readiness_gap_fixtures_v549() -> list[ProductionReadinessGapFixtureV549]:
    fixtures: list[ProductionReadinessGapFixtureV549] = []
    for domain_id in READINESS_DOMAINS_V549:
        fixtures.append(
            ProductionReadinessGapFixtureV549(
                domain_id=domain_id,
                local_evidence_present=True,
                real_input_present=False,
                external_signoff_present=False,
                production_service_configured=False,
                acceptance_record_present=False,
                attempts_production_ready_claim=domain_id == "production_ci_cd_gates",
                attempts_bic_os_unlock=domain_id == "os_service_supervision",
            )
        )
    return fixtures


def evaluate_production_readiness_gap_v549(fixture: ProductionReadinessGapFixtureV549, v548_dependency: dict[str, Any]) -> ProductionReadinessGapDecisionV549:
    reasons: list[str] = []
    missing: list[str] = []
    local_evidence_anchor = str(v548_dependency.get("release_operations_handoff_audit_sha256") or "") or None
    if v548_dependency.get("release_operations_handoff_contract_ready") is not True:
        reasons.append("v548_release_ops_handoff_not_ready")
    if not fixture.local_evidence_present:
        reasons.append("local_evidence_missing")
        missing.append("local evidence anchor")
    if not fixture.real_input_present:
        reasons.append("real_input_missing")
        missing.append(f"real input for {fixture.domain_id}")
    if not fixture.external_signoff_present:
        reasons.append("external_signoff_missing")
        missing.append(f"external signoff for {fixture.domain_id}")
    if not fixture.production_service_configured:
        reasons.append("production_service_missing")
        missing.append(f"production service evidence for {fixture.domain_id}")
    if not fixture.acceptance_record_present:
        reasons.append("acceptance_record_missing")
        missing.append(f"acceptance record for {fixture.domain_id}")
    if fixture.attempts_production_ready_claim:
        reasons.append("production_ready_claim_blocked")
    if fixture.attempts_bic_os_unlock:
        reasons.append("bic_os_unlock_blocked")
    domain_ready = not reasons
    return ProductionReadinessGapDecisionV549(
        domain_id=fixture.domain_id,
        production_ready_for_domain=False if not domain_ready else False,
        gap_open=True,
        reason_codes=tuple(reasons or ["production_domain_still_requires_external_validation"]),
        missing_real_inputs=tuple(missing),
        local_evidence_anchor=local_evidence_anchor if fixture.local_evidence_present else None,
    )


def build_production_readiness_gap_matrix_v549(v548_dependency: dict[str, Any], fixtures: list[ProductionReadinessGapFixtureV549] | None = None) -> dict[str, Any]:
    gap_fixtures = fixtures or default_production_readiness_gap_fixtures_v549()
    decisions = [evaluate_production_readiness_gap_v549(fixture, v548_dependency).to_dict() for fixture in gap_fixtures]
    open_gap_count = sum(1 for decision in decisions if decision["gap_open"])
    production_ready_count = sum(1 for decision in decisions if decision["production_ready_for_domain"])
    reason_codes = sorted({reason for decision in decisions for reason in decision["reason_codes"]})
    required_reasons = {
        "real_input_missing",
        "external_signoff_missing",
        "production_service_missing",
        "acceptance_record_missing",
        "production_ready_claim_blocked",
        "bic_os_unlock_blocked",
    }
    matrix = {
        "version": "v5.49",
        "production_readiness_gap_matrix_ready": len(decisions) == len(READINESS_DOMAINS_V549) and open_gap_count == len(decisions) and production_ready_count == 0 and required_reasons.issubset(set(reason_codes)),
        "domain_count": len(decisions),
        "open_gap_count": open_gap_count,
        "production_ready_domain_count": production_ready_count,
        "reason_codes": reason_codes,
        "fixtures": [fixture.to_dict() for fixture in gap_fixtures],
        "decisions": decisions,
        "production_ready": False,
        "staged_pilot_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    matrix["production_readiness_gap_matrix_sha256"] = stable_hash(matrix)
    return matrix


def default_pilot_acceptance_fixtures_v549() -> list[PilotAcceptanceFixtureV549]:
    return [
        PilotAcceptanceFixtureV549("local-dry-run", True, True, True, True, True, False, False, False),
        PilotAcceptanceFixtureV549("operator-tabletop", True, True, True, True, True, False, False, False),
        PilotAcceptanceFixtureV549("shadow-pilot-preflight", True, True, True, True, True, False, False, False),
        PilotAcceptanceFixtureV549("external-packet-draft", True, True, True, True, True, False, False, False),
        PilotAcceptanceFixtureV549("missing-gap-matrix", False, True, True, True, True, False, False, False),
        PilotAcceptanceFixtureV549("missing-release-ops", True, False, True, True, True, False, False, False),
        PilotAcceptanceFixtureV549("missing-claim-boundary", True, True, False, True, True, False, False, False),
        PilotAcceptanceFixtureV549("missing-rollback", True, True, True, False, True, False, False, False),
        PilotAcceptanceFixtureV549("missing-support-path", True, True, True, True, False, False, False, False),
        PilotAcceptanceFixtureV549("live-pilot-request", True, True, True, True, True, True, False, False),
        PilotAcceptanceFixtureV549("production-release-request", True, True, True, True, True, False, True, False),
        PilotAcceptanceFixtureV549("bic-os-unlock-request", True, True, True, True, True, False, False, True),
    ]


def evaluate_pilot_acceptance_v549(fixture: PilotAcceptanceFixtureV549, v548_dependency: dict[str, Any], gap_matrix: dict[str, Any]) -> PilotAcceptanceDecisionV549:
    reasons: list[str] = []
    if v548_dependency.get("release_operations_handoff_contract_ready") is not True or not fixture.has_release_ops_handoff:
        reasons.append("release_ops_handoff_missing")
    if gap_matrix.get("production_readiness_gap_matrix_ready") is not True or not fixture.has_gap_matrix:
        reasons.append("gap_matrix_missing")
    if not fixture.has_claim_boundary_ack:
        reasons.append("claim_boundary_ack_missing")
    if not fixture.has_rollback_boundary:
        reasons.append("rollback_boundary_missing")
    if not fixture.has_support_path:
        reasons.append("support_path_missing")
    if fixture.requests_live_pilot:
        reasons.append("live_pilot_not_ready")
    if fixture.requests_production_release:
        reasons.append("production_release_not_allowed")
    if fixture.requests_bic_os_unlock:
        reasons.append("bic_os_unlock_not_allowed")
    accepted = not reasons
    return PilotAcceptanceDecisionV549(
        stage_id=fixture.stage_id,
        accepted_for_local_pilot_stage=accepted,
        reason_codes=tuple(reasons or ["local_pilot_stage_acceptance_recorded"]),
        acceptance_record_id=f"local-pilot-acceptance-{fixture.stage_id}" if accepted else None,
    )


def run_staged_pilot_acceptance_matrix_v549(v548_dependency: dict[str, Any], gap_matrix: dict[str, Any], fixtures: list[PilotAcceptanceFixtureV549] | None = None) -> dict[str, Any]:
    pilot_fixtures = fixtures or default_pilot_acceptance_fixtures_v549()
    decisions = [evaluate_pilot_acceptance_v549(fixture, v548_dependency, gap_matrix).to_dict() for fixture in pilot_fixtures]
    accepted_count = sum(1 for decision in decisions if decision["accepted_for_local_pilot_stage"])
    denied_count = len(decisions) - accepted_count
    reason_codes = sorted({reason for decision in decisions for reason in decision["reason_codes"]})
    required_denials = {
        "gap_matrix_missing",
        "release_ops_handoff_missing",
        "claim_boundary_ack_missing",
        "rollback_boundary_missing",
        "support_path_missing",
        "live_pilot_not_ready",
        "production_release_not_allowed",
        "bic_os_unlock_not_allowed",
    }
    matrix = {
        "version": "v5.49",
        "staged_pilot_acceptance_matrix_ready": accepted_count == len(PILOT_STAGES_V549) and denied_count >= 8 and required_denials.issubset(set(reason_codes)),
        "stage_count": len(pilot_fixtures),
        "accepted_local_pilot_stage_count": accepted_count,
        "denied_pilot_stage_count": denied_count,
        "reason_codes": reason_codes,
        "fixtures": [fixture.to_dict() for fixture in pilot_fixtures],
        "decisions": decisions,
        "real_external_pilot_ready": False,
        "production_release_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    matrix["staged_pilot_acceptance_matrix_sha256"] = stable_hash(matrix)
    return matrix


def build_staged_pilot_acceptance_plan_v549(gap_matrix: dict[str, Any], pilot_matrix: dict[str, Any]) -> dict[str, Any]:
    accepted = [decision for decision in pilot_matrix.get("decisions", []) if decision.get("accepted_for_local_pilot_stage") is True]
    records: list[dict[str, Any]] = []
    for decision in accepted:
        record = {
            "version": "v5.49",
            "acceptance_record_id": decision.get("acceptance_record_id"),
            "stage_id": decision.get("stage_id"),
            "gap_matrix_sha256": gap_matrix.get("production_readiness_gap_matrix_sha256"),
            "open_gap_count": gap_matrix.get("open_gap_count"),
            "local_stage_only": True,
            "real_external_pilot_ready": False,
            "production_release_ready": False,
            "created_at": utc_now_iso(),
        }
        record["acceptance_record_sha256"] = stable_hash(record)
        records.append(record)
    plan = {
        "version": "v5.49",
        "staged_pilot_acceptance_plan_ready": len(records) == len(PILOT_STAGES_V549) and gap_matrix.get("open_gap_count", 0) >= len(READINESS_DOMAINS_V549),
        "accepted_stage_count": len(records),
        "accepted_stage_records": records,
        "real_external_pilot_ready": False,
        "production_release_ready": False,
        "production_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    plan["staged_pilot_acceptance_plan_sha256"] = stable_hash(plan)
    return plan


def build_readiness_blocker_register_v549(gap_matrix: dict[str, Any]) -> dict[str, Any]:
    blockers: list[dict[str, Any]] = []
    for decision in gap_matrix.get("decisions", []):
        blocker = {
            "version": "v5.49",
            "blocker_id": f"blocker-{decision['domain_id']}",
            "domain_id": decision.get("domain_id"),
            "reason_codes": decision.get("reason_codes", []),
            "missing_real_inputs": decision.get("missing_real_inputs", []),
            "must_be_resolved_before_production": True,
            "must_be_resolved_before_bic_os": True,
        }
        blocker["blocker_sha256"] = stable_hash(blocker)
        blockers.append(blocker)
    register = {
        "version": "v5.49",
        "readiness_blocker_register_ready": len(blockers) == gap_matrix.get("domain_count") and len(blockers) >= 12,
        "blocker_count": len(blockers),
        "blockers": blockers,
        "production_ready": False,
        "real_external_pilot_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    register["readiness_blocker_register_sha256"] = stable_hash(register)
    return register


def build_production_readiness_audit_bundle_v549(policy: dict[str, Any], gap_matrix: dict[str, Any], pilot_matrix: dict[str, Any], pilot_plan: dict[str, Any], blocker_register: dict[str, Any]) -> dict[str, Any]:
    bundle_ready = (
        policy.get("production_readiness_gap_policy_ready") is True
        and gap_matrix.get("production_readiness_gap_matrix_ready") is True
        and pilot_matrix.get("staged_pilot_acceptance_matrix_ready") is True
        and pilot_plan.get("staged_pilot_acceptance_plan_ready") is True
        and blocker_register.get("readiness_blocker_register_ready") is True
    )
    bundle = {
        "version": "v5.49",
        "production_readiness_audit_bundle_ready": bundle_ready,
        "policy_sha256": policy.get("production_readiness_gap_policy_sha256"),
        "gap_matrix_sha256": gap_matrix.get("production_readiness_gap_matrix_sha256"),
        "pilot_matrix_sha256": pilot_matrix.get("staged_pilot_acceptance_matrix_sha256"),
        "pilot_plan_sha256": pilot_plan.get("staged_pilot_acceptance_plan_sha256"),
        "blocker_register_sha256": blocker_register.get("readiness_blocker_register_sha256"),
        "production_ready": False,
        "real_external_pilot_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    bundle["production_readiness_audit_bundle_sha256"] = stable_hash(bundle)
    return bundle


def run_production_readiness_gap_workflow_v549(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    project_root = Path(root).resolve()
    out = project_root / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    v548_dependency = run_release_operations_handoff_workflow_v548(project_root, out.parent / "d549")
    policy = build_production_readiness_gap_policy_v549()
    gap_matrix = build_production_readiness_gap_matrix_v549(v548_dependency)
    pilot_matrix = run_staged_pilot_acceptance_matrix_v549(v548_dependency, gap_matrix)
    pilot_plan = build_staged_pilot_acceptance_plan_v549(gap_matrix, pilot_matrix)
    blocker_register = build_readiness_blocker_register_v549(gap_matrix)
    audit_bundle = build_production_readiness_audit_bundle_v549(policy, gap_matrix, pilot_matrix, pilot_plan, blocker_register)
    proof_ready = (
        v548_dependency.get("release_operations_handoff_contract_ready") is True
        and policy.get("production_readiness_gap_policy_ready") is True
        and gap_matrix.get("production_readiness_gap_matrix_ready") is True
        and pilot_matrix.get("staged_pilot_acceptance_matrix_ready") is True
        and pilot_plan.get("staged_pilot_acceptance_plan_ready") is True
        and blocker_register.get("readiness_blocker_register_ready") is True
        and audit_bundle.get("production_readiness_audit_bundle_ready") is True
    )
    audit = {
        "version": "v5.49",
        "phase": "production_readiness_gap_staged_pilot_contract",
        "overall_status": "production_readiness_gap_contract_ready_production_not_claimed" if proof_ready else "production_readiness_gap_contract_incomplete",
        "active_phase": "biosdk_production_readiness_gap_proof",
        "bic_os_phase_locked": True,
        "production_readiness_gap_contract_ready": proof_ready,
        "v548_dependency_ready": v548_dependency.get("release_operations_handoff_contract_ready") is True,
        "production_readiness_gap_policy_ready": policy.get("production_readiness_gap_policy_ready") is True,
        "production_readiness_gap_matrix_ready": gap_matrix.get("production_readiness_gap_matrix_ready") is True,
        "staged_pilot_acceptance_matrix_ready": pilot_matrix.get("staged_pilot_acceptance_matrix_ready") is True,
        "staged_pilot_acceptance_plan_ready": pilot_plan.get("staged_pilot_acceptance_plan_ready") is True,
        "readiness_blocker_register_ready": blocker_register.get("readiness_blocker_register_ready") is True,
        "production_readiness_audit_bundle_ready": audit_bundle.get("production_readiness_audit_bundle_ready") is True,
        "artifact_name": v548_dependency.get("artifact_name"),
        "artifact_sha256": v548_dependency.get("artifact_sha256"),
        "readiness_domain_count": gap_matrix.get("domain_count"),
        "open_gap_count": gap_matrix.get("open_gap_count"),
        "production_ready_domain_count": gap_matrix.get("production_ready_domain_count"),
        "accepted_local_pilot_stage_count": pilot_matrix.get("accepted_local_pilot_stage_count"),
        "denied_pilot_stage_count": pilot_matrix.get("denied_pilot_stage_count"),
        "readiness_blocker_count": blocker_register.get("blocker_count"),
        "production_ready": False,
        "production_release_ready": False,
        "production_operations_ready": False,
        "real_external_pilot_ready": False,
        "live_private_registry_ready": False,
        "private_registry_ready": False,
        "public_registry_ready": False,
        "production_distribution_ready": False,
        "production_runtime_ready": False,
        "production_api_ready": False,
        "production_biocompute_runtime_ready": False,
        "full_biosdk_ready": False,
        "live_actuation_enabled": False,
        "production_readiness_gap_policy": policy,
        "production_readiness_gap_matrix": gap_matrix,
        "staged_pilot_acceptance_matrix": pilot_matrix,
        "staged_pilot_acceptance_plan": pilot_plan,
        "readiness_blocker_register": blocker_register,
        "production_readiness_audit_bundle": audit_bundle,
        "v548_dependency_summary": {key: value for key, value in v548_dependency.items() if key not in {"release_operations_handoff_policy", "release_operations_runbook", "operator_handoff_matrix", "operator_handoff_packet", "claim_boundary_attestation", "release_operations_audit_bundle", "v547_dependency_summary"}},
        "missing_real_inputs": [
            "real production identity provider and persistent tenant membership",
            "production object storage and audit retention backend",
            "hosted BioCompute Runtime workers and service supervision",
            "live private registry with authentication and revocation authority",
            "trusted release signing and transparency-log inclusion",
            "production CI/CD gates and deployment rollback evidence",
            "security review, threat model and vulnerability management signoff",
            "production support and incident management systems",
            "notification provider integration and real recipient acknowledgements",
            "external beta/pilot acceptance records",
            "lab-approved live telemetry and closed-loop approval workflow",
            "OS service lifecycle, update and recovery supervision",
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
            "did_we_add_production_readiness_gap_matrix": "yes" if gap_matrix.get("production_readiness_gap_matrix_ready") else "no",
            "did_we_add_staged_pilot_acceptance_proof": "yes" if pilot_plan.get("staged_pilot_acceptance_plan_ready") else "no",
            "are_all_production_domains_still_blocked": "yes" if gap_matrix.get("production_ready_domain_count") == 0 else "no",
            "do_we_still_need_many_layers_before_production_and_os": "yes",
            "is_production_ready": "no",
            "is_real_external_pilot_ready": "no",
            "is_full_biosdk_ready": "no",
            "is_biocompute_runtime_ready": "no",
            "is_bic_os_ready": "no",
            "next_best_build_step": "add external acceptance evidence schema and real-pilot intake gate" if proof_ready else "fix v5.49 readiness blockers first",
        },
        "claim_boundary": "v5.49 proves a local production-readiness gap matrix and staged pilot acceptance contract over the v5.48 release operations handoff. It does not claim production readiness, real external pilot readiness, production distribution, full BioSDK, production BioCompute Runtime or BiC OS readiness. Every production domain remains blocked until real services, approvals and external acceptance records exist.",
    }
    audit["production_readiness_gap_audit_sha256"] = stable_hash({key: value for key, value in audit.items() if key != "production_readiness_gap_audit_sha256"})
    return audit


def write_production_readiness_gap_outputs_v549(audit: dict[str, Any], out_dir: str | Path = DEFAULT_OUT) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary_json": out / "V549_PRODUCTION_READINESS_GAP_SUMMARY.json",
        "policy_json": out / "V549_PRODUCTION_READINESS_GAP_POLICY.json",
        "gap_matrix_json": out / "V549_PRODUCTION_READINESS_GAP_MATRIX.json",
        "pilot_matrix_json": out / "V549_STAGED_PILOT_ACCEPTANCE_MATRIX.json",
        "pilot_plan_json": out / "V549_STAGED_PILOT_ACCEPTANCE_PLAN.json",
        "blocker_register_json": out / "V549_READINESS_BLOCKER_REGISTER.json",
        "audit_bundle_json": out / "V549_PRODUCTION_READINESS_AUDIT_BUNDLE.json",
        "gap_matrix_csv": out / "V549_PRODUCTION_READINESS_GAP_MATRIX.csv",
        "pilot_matrix_csv": out / "V549_STAGED_PILOT_ACCEPTANCE_MATRIX.csv",
        "markdown_report": out / "BIOGPU_V549_PRODUCTION_READINESS_GAP_REPORT.md",
    }
    summary = {key: value for key, value in audit.items() if key not in {"production_readiness_gap_policy", "production_readiness_gap_matrix", "staged_pilot_acceptance_matrix", "staged_pilot_acceptance_plan", "readiness_blocker_register", "production_readiness_audit_bundle"}}
    paths["summary_json"].write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["policy_json"].write_text(json.dumps(audit["production_readiness_gap_policy"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["gap_matrix_json"].write_text(json.dumps(audit["production_readiness_gap_matrix"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["pilot_matrix_json"].write_text(json.dumps(audit["staged_pilot_acceptance_matrix"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["pilot_plan_json"].write_text(json.dumps(audit["staged_pilot_acceptance_plan"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["blocker_register_json"].write_text(json.dumps(audit["readiness_blocker_register"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["audit_bundle_json"].write_text(json.dumps(audit["production_readiness_audit_bundle"], indent=2, ensure_ascii=False), encoding="utf-8")
    _write_gap_matrix_csv(paths["gap_matrix_csv"], audit["production_readiness_gap_matrix"].get("decisions", []))
    _write_pilot_matrix_csv(paths["pilot_matrix_csv"], audit["staged_pilot_acceptance_matrix"].get("decisions", []))
    paths["markdown_report"].write_text(_markdown_report(audit), encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}


def _write_gap_matrix_csv(path: Path, decisions: list[dict[str, Any]]) -> None:
    fieldnames = ["domain_id", "production_ready_for_domain", "gap_open", "local_evidence_anchor", "missing_real_inputs", "reason_codes"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for decision in decisions:
            row = {field: decision.get(field) for field in fieldnames}
            row["missing_real_inputs"] = " | ".join(str(item) for item in decision.get("missing_real_inputs", []))
            row["reason_codes"] = " | ".join(str(reason) for reason in decision.get("reason_codes", []))
            writer.writerow(row)


def _write_pilot_matrix_csv(path: Path, decisions: list[dict[str, Any]]) -> None:
    fieldnames = ["stage_id", "accepted_for_local_pilot_stage", "acceptance_record_id", "reason_codes"]
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
        "# BioGPU-Core v5.49 Production Readiness Gap Contract",
        "",
        "## Direct Answer",
        "",
        f"- Production readiness gap matrix added: `{answer['did_we_add_production_readiness_gap_matrix']}`",
        f"- Staged pilot acceptance proof added: `{answer['did_we_add_staged_pilot_acceptance_proof']}`",
        f"- All production domains still blocked: `{answer['are_all_production_domains_still_blocked']}`",
        f"- More layers needed before production and OS: `{answer['do_we_still_need_many_layers_before_production_and_os']}`",
        f"- Production ready: `{answer['is_production_ready']}`",
        f"- Real external pilot ready: `{answer['is_real_external_pilot_ready']}`",
        f"- Full BioSDK ready: `{answer['is_full_biosdk_ready']}`",
        f"- BioCompute Runtime ready: `{answer['is_biocompute_runtime_ready']}`",
        f"- BiC OS ready: `{answer['is_bic_os_ready']}`",
        f"- Next best build step: {answer['next_best_build_step']}",
        "",
        "## Proof Summary",
        "",
        f"- Overall status: `{audit['overall_status']}`",
        f"- v5.48 dependency ready: `{audit['v548_dependency_ready']}`",
        f"- Readiness domains: `{audit['readiness_domain_count']}`",
        f"- Open production gaps: `{audit['open_gap_count']}`",
        f"- Production-ready domains: `{audit['production_ready_domain_count']}`",
        f"- Accepted local pilot stages: `{audit['accepted_local_pilot_stage_count']}`",
        f"- Denied pilot stages: `{audit['denied_pilot_stage_count']}`",
        "",
        "## Missing Real Inputs",
        "",
    ]
    for missing in audit["missing_real_inputs"]:
        lines.append(f"- {missing}")
    lines.extend(["", "## Boundary", "", audit["claim_boundary"], ""])
    return "\n".join(lines)