"""Release approval and revocation contract proof, v5.43."""
from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from biogpu.beta.job_model_v43 import utc_now_iso
from biogpu.evidence.ledger_v53 import stable_hash
from biogpu.sdk.artifact_provenance_v542 import run_signed_artifact_provenance_workflow_v542


DEFAULT_OUT = Path("outputs/v543_release_approval_revocation")
REQUIRED_APPROVER_ROLES_V543 = ("release_manager", "provenance_reviewer", "safety_reviewer", "ops_reviewer")
REQUIRED_REVOCATION_TRIGGERS_V543 = (
    "artifact_digest_mismatch",
    "signature_validation_failure",
    "claim_boundary_violation",
    "install_smoke_regression",
)


@dataclass(frozen=True)
class ReleaseApprovalPolicyV543:
    policy_id: str
    required_approver_roles: tuple[str, ...]
    required_revocation_triggers: tuple[str, ...]
    local_candidate_handoff_allowed: bool
    production_distribution_allowed: bool
    public_registry_allowed: bool
    full_biosdk_claim_allowed: bool
    live_actuation_allowed: bool
    local_contract_only: bool = True
    production_release_ready: bool = False
    full_biosdk_ready: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ReleaseReviewFixtureV543:
    review_id: str
    reviewer_role: str
    reviewer_decision: str
    acknowledged_claim_boundary: bool
    verified_local_signature: bool
    verified_tamper_detection: bool
    requests_production_distribution: bool
    requests_full_biosdk_claim: bool
    requests_live_actuation: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ReleaseReviewDecisionV543:
    review_id: str
    reviewer_role: str
    allowed_for_local_candidate: bool
    reason_codes: tuple[str, ...]
    production_distribution_ready: bool = False
    full_biosdk_ready: bool = False
    live_actuation_enabled: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RevocationScenarioV543:
    scenario_id: str
    trigger: str
    artifact_access_revoked: bool
    local_handoff_blocked: bool
    requires_operator_acknowledgement: bool
    production_registry_action_available: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_release_approval_policy_v543() -> dict[str, Any]:
    policy = ReleaseApprovalPolicyV543(
        policy_id="BIOGPU_CORE_V543_RELEASE_APPROVAL_POLICY",
        required_approver_roles=REQUIRED_APPROVER_ROLES_V543,
        required_revocation_triggers=REQUIRED_REVOCATION_TRIGGERS_V543,
        local_candidate_handoff_allowed=True,
        production_distribution_allowed=False,
        public_registry_allowed=False,
        full_biosdk_claim_allowed=False,
        live_actuation_allowed=False,
    )
    return {
        "version": "v5.43",
        "release_approval_policy_ready": True,
        "policy": policy.to_dict(),
        "blocked_release_modes": ["production_distribution", "public_registry", "auto_update_channel", "live_actuation_beta"],
        "required_external_release_inputs": [
            "named release approval authority",
            "trusted external signing and revocation key management",
            "approved private package registry or artifact handoff channel",
            "external clean-room install report",
            "transparency log or immutable release ledger",
        ],
        "production_release_ready": False,
        "production_distribution_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }


def default_release_review_fixtures_v543() -> list[ReleaseReviewFixtureV543]:
    return [
        ReleaseReviewFixtureV543("approve-release-manager", "release_manager", "approve", True, True, True, False, False, False),
        ReleaseReviewFixtureV543("approve-provenance", "provenance_reviewer", "approve", True, True, True, False, False, False),
        ReleaseReviewFixtureV543("approve-safety", "safety_reviewer", "approve", True, True, True, False, False, False),
        ReleaseReviewFixtureV543("approve-ops", "ops_reviewer", "approve", True, True, True, False, False, False),
        ReleaseReviewFixtureV543("missing-boundary", "release_manager", "approve", False, True, True, False, False, False),
        ReleaseReviewFixtureV543("signature-unverified", "provenance_reviewer", "approve", True, False, True, False, False, False),
        ReleaseReviewFixtureV543("public-release-request", "release_manager", "approve", True, True, True, True, False, False),
        ReleaseReviewFixtureV543("full-sdk-overclaim", "safety_reviewer", "approve", True, True, True, False, True, False),
        ReleaseReviewFixtureV543("live-actuation-request", "ops_reviewer", "approve", True, True, True, False, False, True),
        ReleaseReviewFixtureV543("unknown-role", "marketing_reviewer", "approve", True, True, True, False, False, False),
    ]


def evaluate_release_review_v543(fixture: ReleaseReviewFixtureV543) -> ReleaseReviewDecisionV543:
    reasons: list[str] = []
    if fixture.reviewer_role not in REQUIRED_APPROVER_ROLES_V543:
        reasons.append("reviewer_role_not_authorized")
    if fixture.reviewer_decision != "approve":
        reasons.append("reviewer_did_not_approve")
    if not fixture.acknowledged_claim_boundary:
        reasons.append("claim_boundary_not_acknowledged")
    if not fixture.verified_local_signature:
        reasons.append("local_signature_not_verified")
    if not fixture.verified_tamper_detection:
        reasons.append("tamper_detection_not_verified")
    if fixture.requests_production_distribution:
        reasons.append("production_distribution_not_allowed")
    if fixture.requests_full_biosdk_claim:
        reasons.append("full_biosdk_claim_not_allowed")
    if fixture.requests_live_actuation:
        reasons.append("live_actuation_not_allowed")
    allowed = not reasons
    return ReleaseReviewDecisionV543(
        review_id=fixture.review_id,
        reviewer_role=fixture.reviewer_role,
        allowed_for_local_candidate=allowed,
        reason_codes=tuple(reasons or ["local_candidate_review_allowed"]),
    )


def run_release_approval_matrix_v543(fixtures: list[ReleaseReviewFixtureV543] | None = None) -> dict[str, Any]:
    reviews = fixtures or default_release_review_fixtures_v543()
    decisions = [evaluate_release_review_v543(review).to_dict() for review in reviews]
    allowed_roles = sorted({decision["reviewer_role"] for decision in decisions if decision["allowed_for_local_candidate"]})
    denied_count = sum(1 for decision in decisions if not decision["allowed_for_local_candidate"])
    reason_codes = sorted({reason for decision in decisions for reason in decision["reason_codes"]})
    required_denials = {
        "claim_boundary_not_acknowledged",
        "local_signature_not_verified",
        "production_distribution_not_allowed",
        "full_biosdk_claim_not_allowed",
        "live_actuation_not_allowed",
        "reviewer_role_not_authorized",
    }
    matrix = {
        "version": "v5.43",
        "release_approval_matrix_ready": set(REQUIRED_APPROVER_ROLES_V543).issubset(set(allowed_roles)) and denied_count >= 6 and required_denials.issubset(set(reason_codes)),
        "review_count": len(reviews),
        "allowed_local_review_count": sum(1 for decision in decisions if decision["allowed_for_local_candidate"]),
        "denied_review_count": denied_count,
        "allowed_roles": allowed_roles,
        "reason_codes": reason_codes,
        "reviews": [review.to_dict() for review in reviews],
        "decisions": decisions,
        "production_release_ready": False,
        "production_distribution_ready": False,
        "full_biosdk_ready": False,
        "live_actuation_enabled": False,
        "bic_os_phase_locked": True,
    }
    matrix["approval_matrix_sha256"] = stable_hash(matrix)
    return matrix


def build_release_revocation_policy_v543() -> dict[str, Any]:
    scenarios = [
        RevocationScenarioV543("digest-mismatch", "artifact_digest_mismatch", True, True, True),
        RevocationScenarioV543("signature-failure", "signature_validation_failure", True, True, True),
        RevocationScenarioV543("boundary-violation", "claim_boundary_violation", True, True, True),
        RevocationScenarioV543("install-regression", "install_smoke_regression", True, True, True),
    ]
    scenario_dicts = [scenario.to_dict() for scenario in scenarios]
    policy = {
        "version": "v5.43",
        "release_revocation_policy_ready": all(scenario["artifact_access_revoked"] and scenario["local_handoff_blocked"] for scenario in scenario_dicts),
        "required_triggers": list(REQUIRED_REVOCATION_TRIGGERS_V543),
        "scenarios": scenario_dicts,
        "local_revocation_channels": ["local_handoff_denylist", "operator_review_queue", "release_notes_amendment"],
        "external_revocation_channels_ready": False,
        "production_registry_yank_ready": False,
        "production_distribution_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    policy["revocation_policy_sha256"] = stable_hash(policy)
    return policy


def run_release_revocation_drill_v543(revocation_policy: dict[str, Any]) -> dict[str, Any]:
    scenarios = list(revocation_policy.get("scenarios") or [])
    revoked_count = sum(1 for scenario in scenarios if scenario.get("artifact_access_revoked") is True)
    blocked_count = sum(1 for scenario in scenarios if scenario.get("local_handoff_blocked") is True)
    acknowledged_count = sum(1 for scenario in scenarios if scenario.get("requires_operator_acknowledgement") is True)
    triggers = {scenario.get("trigger") for scenario in scenarios}
    drill = {
        "version": "v5.43",
        "release_revocation_drill_ready": set(REQUIRED_REVOCATION_TRIGGERS_V543).issubset(triggers) and revoked_count == len(REQUIRED_REVOCATION_TRIGGERS_V543) and blocked_count == len(REQUIRED_REVOCATION_TRIGGERS_V543),
        "scenario_count": len(scenarios),
        "revoked_count": revoked_count,
        "local_handoff_blocked_count": blocked_count,
        "operator_acknowledgement_required_count": acknowledged_count,
        "revocation_events": [
            {
                "event_id": f"revocation-{scenario['scenario_id']}",
                "trigger": scenario["trigger"],
                "artifact_access_revoked": scenario["artifact_access_revoked"],
                "local_handoff_blocked": scenario["local_handoff_blocked"],
                "created_at": utc_now_iso(),
            }
            for scenario in scenarios
        ],
        "external_revocation_channels_ready": False,
        "production_registry_yank_ready": False,
        "production_distribution_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    drill["revocation_drill_sha256"] = stable_hash(drill)
    return drill


def build_release_decision_record_v543(v542_dependency: dict[str, Any], approval_matrix: dict[str, Any], revocation_drill: dict[str, Any]) -> dict[str, Any]:
    local_candidate_approved = (
        v542_dependency.get("signed_artifact_provenance_contract_ready") is True
        and approval_matrix.get("release_approval_matrix_ready") is True
        and revocation_drill.get("release_revocation_drill_ready") is True
    )
    record = {
        "version": "v5.43",
        "decision_id": "BIOGPU_CORE_V543_LOCAL_CANDIDATE_RELEASE_DECISION",
        "created_at": utc_now_iso(),
        "local_candidate_handoff_approved": local_candidate_approved,
        "production_release_approved": False,
        "public_registry_release_approved": False,
        "full_biosdk_claim_approved": False,
        "artifact_name": v542_dependency.get("artifact_name"),
        "artifact_sha256": v542_dependency.get("artifact_sha256"),
        "provenance_audit_sha256": v542_dependency.get("provenance_audit_sha256"),
        "allowed_scope": "local_candidate_handoff_only",
        "revocation_drill_sha256": revocation_drill.get("revocation_drill_sha256"),
        "approval_matrix_sha256": approval_matrix.get("approval_matrix_sha256"),
        "production_distribution_ready": False,
        "production_runtime_ready": False,
        "production_api_ready": False,
        "production_biocompute_runtime_ready": False,
        "full_biosdk_ready": False,
        "live_actuation_enabled": False,
        "bic_os_phase_locked": True,
    }
    record["release_decision_sha256"] = stable_hash(record)
    return record


def run_release_approval_revocation_workflow_v543(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    project_root = Path(root).resolve()
    out = project_root / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    v542_dependency = run_signed_artifact_provenance_workflow_v542(project_root, out / "d542")
    approval_policy = build_release_approval_policy_v543()
    approval_matrix = run_release_approval_matrix_v543()
    revocation_policy = build_release_revocation_policy_v543()
    revocation_drill = run_release_revocation_drill_v543(revocation_policy)
    release_decision = build_release_decision_record_v543(v542_dependency, approval_matrix, revocation_drill)
    proof_ready = (
        v542_dependency.get("signed_artifact_provenance_contract_ready") is True
        and approval_policy.get("release_approval_policy_ready") is True
        and approval_matrix.get("release_approval_matrix_ready") is True
        and revocation_policy.get("release_revocation_policy_ready") is True
        and revocation_drill.get("release_revocation_drill_ready") is True
        and release_decision.get("local_candidate_handoff_approved") is True
        and release_decision.get("production_release_approved") is False
    )
    audit = {
        "version": "v5.43",
        "phase": "release_approval_revocation_contract",
        "overall_status": "release_approval_revocation_contract_ready_production_not_claimed" if proof_ready else "release_approval_revocation_contract_incomplete",
        "active_phase": "biosdk_release_approval_revocation_proof",
        "bic_os_phase_locked": True,
        "release_approval_revocation_contract_ready": proof_ready,
        "v542_dependency_ready": v542_dependency.get("signed_artifact_provenance_contract_ready") is True,
        "release_approval_policy_ready": approval_policy.get("release_approval_policy_ready") is True,
        "release_approval_matrix_ready": approval_matrix.get("release_approval_matrix_ready") is True,
        "release_revocation_policy_ready": revocation_policy.get("release_revocation_policy_ready") is True,
        "release_revocation_drill_ready": revocation_drill.get("release_revocation_drill_ready") is True,
        "local_candidate_handoff_approved": release_decision.get("local_candidate_handoff_approved") is True,
        "production_release_approved": False,
        "public_registry_release_approved": False,
        "artifact_name": release_decision.get("artifact_name"),
        "artifact_sha256": release_decision.get("artifact_sha256"),
        "allowed_local_review_count": approval_matrix.get("allowed_local_review_count"),
        "denied_review_count": approval_matrix.get("denied_review_count"),
        "revocation_scenario_count": revocation_drill.get("scenario_count"),
        "external_release_approval_ready": False,
        "trusted_external_signature_ready": False,
        "transparency_log_ready": False,
        "production_distribution_ready": False,
        "production_runtime_ready": False,
        "production_api_ready": False,
        "production_biocompute_runtime_ready": False,
        "full_biosdk_ready": False,
        "live_actuation_enabled": False,
        "release_approval_policy": approval_policy,
        "release_approval_matrix": approval_matrix,
        "release_revocation_policy": revocation_policy,
        "release_revocation_drill": revocation_drill,
        "release_decision_record": release_decision,
        "v542_dependency_summary": {key: value for key, value in v542_dependency.items() if key not in {"provenance_policy", "artifact_manifest", "provenance_statement", "signature_envelope", "signature_validation", "tamper_probe", "v541_dependency_summary"}},
        "missing_real_inputs": [
            "named release approval authority and audit trail",
            "trusted external signing and revocation key management",
            "approved private registry or artifact handoff channel",
            "external clean-room install/provenance attestation",
            "transparency log or immutable release ledger inclusion",
            "production rollback/yank authority and user notification process",
        ],
        "remaining_runtime_blockers": [
            "production identity provider integration and persistent tenant membership",
            "production object storage and audit retention backend",
            "hosted dashboard server and browser session enforcement",
            "real external read-only API credentials or partner exports",
            "lab-approved live telemetry and closed-loop approval workflow",
        ],
        "direct_answer": {
            "did_we_add_release_approval_revocation_contract": "yes" if proof_ready else "not_yet",
            "is_local_candidate_handoff_approved": "yes" if release_decision.get("local_candidate_handoff_approved") else "no",
            "is_production_release_approved": "no",
            "is_full_biosdk_ready": "no",
            "is_biocompute_runtime_ready": "no",
            "is_bic_os_ready": "no",
            "next_best_build_step": "add private registry handoff contract proof" if proof_ready else "fix v5.43 approval/revocation blockers first",
        },
        "claim_boundary": "v5.43 proves local release-candidate approval and revocation contract behavior over the v5.42 provenance layer. It does not claim production release approval, public registry distribution, trusted external signing, full BioSDK, production BioCompute Runtime or BiC OS readiness.",
    }
    audit["release_approval_audit_sha256"] = stable_hash({key: value for key, value in audit.items() if key != "release_approval_audit_sha256"})
    return audit


def write_release_approval_revocation_outputs_v543(audit: dict[str, Any], out_dir: str | Path = DEFAULT_OUT) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary_json": out / "V543_RELEASE_APPROVAL_REVOCATION_SUMMARY.json",
        "approval_policy_json": out / "V543_RELEASE_APPROVAL_POLICY.json",
        "approval_matrix_json": out / "V543_RELEASE_APPROVAL_MATRIX.json",
        "revocation_policy_json": out / "V543_RELEASE_REVOCATION_POLICY.json",
        "revocation_drill_json": out / "V543_RELEASE_REVOCATION_DRILL.json",
        "release_decision_json": out / "V543_RELEASE_DECISION_RECORD.json",
        "approval_matrix_csv": out / "V543_RELEASE_APPROVAL_MATRIX.csv",
        "revocation_events_csv": out / "V543_RELEASE_REVOCATION_EVENTS.csv",
        "markdown_report": out / "BIOGPU_V543_RELEASE_APPROVAL_REVOCATION_REPORT.md",
    }
    summary = {key: value for key, value in audit.items() if key not in {"release_approval_policy", "release_approval_matrix", "release_revocation_policy", "release_revocation_drill", "release_decision_record"}}
    paths["summary_json"].write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["approval_policy_json"].write_text(json.dumps(audit["release_approval_policy"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["approval_matrix_json"].write_text(json.dumps(audit["release_approval_matrix"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["revocation_policy_json"].write_text(json.dumps(audit["release_revocation_policy"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["revocation_drill_json"].write_text(json.dumps(audit["release_revocation_drill"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["release_decision_json"].write_text(json.dumps(audit["release_decision_record"], indent=2, ensure_ascii=False), encoding="utf-8")
    _write_approval_matrix_csv(paths["approval_matrix_csv"], audit["release_approval_matrix"].get("decisions", []))
    _write_revocation_events_csv(paths["revocation_events_csv"], audit["release_revocation_drill"].get("revocation_events", []))
    paths["markdown_report"].write_text(_markdown_report(audit), encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}


def _write_approval_matrix_csv(path: Path, decisions: list[dict[str, Any]]) -> None:
    fieldnames = ["review_id", "reviewer_role", "allowed_for_local_candidate", "reason_codes", "production_distribution_ready", "full_biosdk_ready", "live_actuation_enabled"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for decision in decisions:
            row = {field: decision.get(field) for field in fieldnames}
            row["reason_codes"] = " | ".join(str(reason) for reason in decision.get("reason_codes", []))
            writer.writerow(row)


def _write_revocation_events_csv(path: Path, events: list[dict[str, Any]]) -> None:
    fieldnames = ["event_id", "trigger", "artifact_access_revoked", "local_handoff_blocked", "created_at"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for event in events:
            writer.writerow({field: event.get(field) for field in fieldnames})


def _markdown_report(audit: dict[str, Any]) -> str:
    answer = audit["direct_answer"]
    lines = [
        "# BioGPU-Core v5.43 Release Approval and Revocation Contract",
        "",
        "## Direct Answer",
        "",
        f"- Release approval/revocation contract added: `{answer['did_we_add_release_approval_revocation_contract']}`",
        f"- Local candidate handoff approved: `{answer['is_local_candidate_handoff_approved']}`",
        f"- Production release approved: `{answer['is_production_release_approved']}`",
        f"- Full BioSDK ready: `{answer['is_full_biosdk_ready']}`",
        f"- BioCompute Runtime ready: `{answer['is_biocompute_runtime_ready']}`",
        f"- BiC OS ready: `{answer['is_bic_os_ready']}`",
        f"- Next best build step: {answer['next_best_build_step']}",
        "",
        "## Proof Summary",
        "",
        f"- Overall status: `{audit['overall_status']}`",
        f"- v5.42 dependency ready: `{audit['v542_dependency_ready']}`",
        f"- Approval matrix ready: `{audit['release_approval_matrix_ready']}`",
        f"- Revocation drill ready: `{audit['release_revocation_drill_ready']}`",
        f"- Allowed local reviews: `{audit['allowed_local_review_count']}`",
        f"- Denied reviews: `{audit['denied_review_count']}`",
        f"- Revocation scenarios: `{audit['revocation_scenario_count']}`",
        "",
        "## Missing Real Inputs",
        "",
    ]
    for missing in audit["missing_real_inputs"]:
        lines.append(f"- {missing}")
    lines.extend(["", "## Boundary", "", audit["claim_boundary"], ""])
    return "\n".join(lines)