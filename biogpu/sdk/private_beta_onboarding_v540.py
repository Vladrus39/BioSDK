"""Private beta onboarding and release operations contract proof, v5.40."""
from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from biogpu.beta.job_model_v43 import utc_now_iso
from biogpu.evidence.ledger_v53 import stable_hash
from biogpu.sdk.package_install_gate_v539 import run_packaged_sdk_install_gate_workflow_v539


DEFAULT_OUT = Path("outputs/v540_private_beta_onboarding_contract")
APPROVED_DATA_MODES_V540 = {"public_sample", "user_upload_sample", "read_only_external_export"}
APPROVED_ROLES_V540 = {"beta_admin", "beta_operator", "beta_auditor", "beta_researcher"}


@dataclass(frozen=True)
class BetaOnboardingArtifactV540:
    artifact_name: str
    purpose: str
    required_before_handoff: bool
    local_only_ready: bool
    production_ready: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BetaParticipantFixtureV540:
    participant_id: str
    organization: str
    role: str
    requested_data_mode: str
    has_data_use_agreement: bool
    accepted_install_gate_boundary: bool
    requested_live_actuation: bool
    requested_production_sla: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BetaOnboardingDecisionV540:
    participant_id: str
    allowed: bool
    reason_codes: tuple[str, ...]
    allowed_data_mode: str | None
    live_actuation_enabled: bool = False
    production_sla_enabled: bool = False
    production_distribution_ready: bool = False
    full_biosdk_ready: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_private_beta_program_contract_v540(project_root: str | Path) -> dict[str, Any]:
    root = Path(project_root)
    artifacts = build_beta_onboarding_artifacts_v540()
    contract = {
        "version": "v5.40",
        "program_name": "BioGPU-Core Private Beta Contract",
        "project_root": str(root).replace("\\", "/"),
        "release_candidate_version": "5.0.0",
        "allowed_distribution_modes": ["local_wheel_handoff", "source_tree_handoff"],
        "blocked_distribution_modes": ["public_package_index", "production_marketplace", "auto_update_channel"],
        "allowed_data_modes": sorted(APPROVED_DATA_MODES_V540),
        "blocked_capabilities": ["live_actuation", "production_sla", "unsupervised_remote_control", "production_identity_bypass"],
        "required_artifact_count": sum(1 for artifact in artifacts if artifact["required_before_handoff"]),
        "artifact_contract_ready": all(artifact["local_only_ready"] for artifact in artifacts if artifact["required_before_handoff"]),
        "local_contract_only": True,
        "external_beta_ready": False,
        "production_distribution_ready": False,
        "production_runtime_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    contract["contract_sha256"] = stable_hash(contract)
    return contract


def build_beta_onboarding_artifacts_v540() -> list[dict[str, Any]]:
    artifacts = [
        BetaOnboardingArtifactV540("install_gate_summary", "validated v5.39 local wheel/install smoke boundary", True, True),
        BetaOnboardingArtifactV540("release_notes", "human-readable scope and claim boundary for the beta package", True, True),
        BetaOnboardingArtifactV540("data_use_agreement_template", "read-only data use and upload boundary acknowledgement", True, True),
        BetaOnboardingArtifactV540("support_intake_runbook", "local issue intake, severity labels and escalation boundary", True, True),
        BetaOnboardingArtifactV540("rollback_plan", "return to prior wheel/source snapshot if beta install fails", True, True),
        BetaOnboardingArtifactV540("participant_access_matrix", "role/data-mode gating for limited testers", True, True),
        BetaOnboardingArtifactV540("public_registry_release", "published package index artifact", False, False),
        BetaOnboardingArtifactV540("production_sla", "production support and uptime commitment", False, False),
    ]
    return [artifact.to_dict() for artifact in artifacts]


def build_release_operations_contract_v540(project_root: str | Path) -> dict[str, Any]:
    root = Path(project_root)
    contract = {
        "version": "v5.40",
        "created_at": utc_now_iso(),
        "root": str(root).replace("\\", "/"),
        "candidate_version": "5.0.0",
        "release_channels": [
            {"name": "local_wheel_handoff", "ready": True, "production_ready": False},
            {"name": "source_tree_handoff", "ready": True, "production_ready": False},
            {"name": "private_package_index", "ready": False, "production_ready": False},
            {"name": "public_package_index", "ready": False, "production_ready": False},
        ],
        "required_release_checks": [
            "v5.39 install gate summary present",
            "claim boundary acknowledged by recipient",
            "read-only data mode selected",
            "live actuation explicitly blocked",
            "support intake owner assigned",
            "rollback plan attached",
        ],
        "rollback_contract": {
            "rollback_trigger_count": 4,
            "rollback_window_hours": 24,
            "requires_local_artifact_hash": True,
            "requires_handoff_log": True,
        },
        "support_contract": {
            "channels": ["local_issue_log", "operator_review_queue"],
            "severity_levels": ["low", "medium", "high", "blocker"],
            "production_sla_ready": False,
        },
        "release_operations_contract_ready": True,
        "private_index_ready": False,
        "public_distribution_ready": False,
        "production_distribution_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    contract["contract_sha256"] = stable_hash(contract)
    return contract


def default_beta_participant_fixtures_v540() -> list[BetaParticipantFixtureV540]:
    return [
        BetaParticipantFixtureV540("internal-audit-01", "BioGPU internal", "beta_auditor", "public_sample", True, True, False, False),
        BetaParticipantFixtureV540("partner-lab-01", "Partner read-only lab", "beta_researcher", "read_only_external_export", True, True, False, False),
        BetaParticipantFixtureV540("user-upload-01", "User upload pilot", "beta_operator", "user_upload_sample", True, True, False, False),
        BetaParticipantFixtureV540("missing-dua-01", "Unapproved lab", "beta_researcher", "read_only_external_export", False, True, False, False),
        BetaParticipantFixtureV540("live-request-01", "Closed-loop request", "beta_operator", "read_only_external_export", True, True, True, False),
        BetaParticipantFixtureV540("sla-request-01", "Production support request", "beta_admin", "public_sample", True, True, False, True),
        BetaParticipantFixtureV540("unknown-role-01", "Unknown org", "viewer", "public_sample", True, True, False, False),
    ]


def authorize_beta_participant_v540(fixture: BetaParticipantFixtureV540) -> BetaOnboardingDecisionV540:
    reasons: list[str] = []
    if fixture.role not in APPROVED_ROLES_V540:
        reasons.append("role_not_approved_for_beta")
    if fixture.requested_data_mode not in APPROVED_DATA_MODES_V540:
        reasons.append("data_mode_not_approved")
    if not fixture.has_data_use_agreement:
        reasons.append("missing_data_use_agreement")
    if not fixture.accepted_install_gate_boundary:
        reasons.append("install_gate_boundary_not_accepted")
    if fixture.requested_live_actuation:
        reasons.append("live_actuation_not_allowed")
    if fixture.requested_production_sla:
        reasons.append("production_sla_not_available")
    allowed = not reasons
    return BetaOnboardingDecisionV540(
        participant_id=fixture.participant_id,
        allowed=allowed,
        reason_codes=tuple(reasons or ["private_beta_read_only_handoff_allowed"]),
        allowed_data_mode=fixture.requested_data_mode if allowed else None,
    )


def run_beta_onboarding_decision_matrix_v540(fixtures: list[BetaParticipantFixtureV540] | None = None) -> dict[str, Any]:
    participants = fixtures or default_beta_participant_fixtures_v540()
    decisions = [authorize_beta_participant_v540(participant).to_dict() for participant in participants]
    allowed_count = sum(1 for decision in decisions if decision["allowed"])
    denied_count = len(decisions) - allowed_count
    reason_codes = sorted({reason for decision in decisions for reason in decision["reason_codes"]})
    required_denials = {"missing_data_use_agreement", "live_actuation_not_allowed", "production_sla_not_available", "role_not_approved_for_beta"}
    return {
        "version": "v5.40",
        "participant_count": len(participants),
        "allowed_count": allowed_count,
        "denied_count": denied_count,
        "reason_codes": reason_codes,
        "participants": [participant.to_dict() for participant in participants],
        "decisions": decisions,
        "participant_gate_ready": allowed_count >= 3 and denied_count >= 4 and required_denials.issubset(set(reason_codes)),
        "external_beta_ready": False,
        "live_actuation_enabled": False,
        "production_distribution_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }


def run_private_beta_onboarding_contract_workflow_v540(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    project_root = Path(root).resolve()
    out = project_root / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    v539_dependency = run_packaged_sdk_install_gate_workflow_v539(project_root, out / "d539", build_distribution=False, require_wheel_build=False)
    program_contract = build_private_beta_program_contract_v540(project_root)
    artifacts = build_beta_onboarding_artifacts_v540()
    release_operations = build_release_operations_contract_v540(project_root)
    decision_matrix = run_beta_onboarding_decision_matrix_v540()
    proof_ready = (
        v539_dependency.get("packaged_sdk_install_gate_ready") is True
        and program_contract.get("artifact_contract_ready") is True
        and release_operations.get("release_operations_contract_ready") is True
        and decision_matrix.get("participant_gate_ready") is True
    )
    audit = {
        "version": "v5.40",
        "phase": "private_beta_onboarding_contract",
        "overall_status": "private_beta_onboarding_contract_ready_release_not_claimed" if proof_ready else "private_beta_onboarding_contract_incomplete",
        "active_phase": "biosdk_private_beta_release_operations_proof",
        "bic_os_phase_locked": True,
        "private_beta_onboarding_contract_ready": proof_ready,
        "v539_dependency_ready": v539_dependency.get("packaged_sdk_install_gate_ready") is True,
        "program_contract_ready": program_contract.get("artifact_contract_ready") is True,
        "release_operations_contract_ready": release_operations.get("release_operations_contract_ready") is True,
        "participant_gate_ready": decision_matrix.get("participant_gate_ready") is True,
        "allowed_participant_count": decision_matrix.get("allowed_count"),
        "denied_participant_count": decision_matrix.get("denied_count"),
        "required_artifact_count": program_contract.get("required_artifact_count"),
        "external_beta_ready": False,
        "production_distribution_ready": False,
        "production_runtime_ready": False,
        "production_api_ready": False,
        "production_biocompute_runtime_ready": False,
        "full_biosdk_ready": False,
        "live_actuation_enabled": False,
        "program_contract": program_contract,
        "onboarding_artifacts": artifacts,
        "release_operations_contract": release_operations,
        "participant_decision_matrix": decision_matrix,
        "v539_dependency_summary": {key: value for key, value in v539_dependency.items() if key not in {"package_metadata_contract", "package_discovery", "entrypoint_contracts", "distribution_manifest", "local_build_install_result", "v538_dependency_summary"}},
        "missing_real_inputs": [
            "named beta participants with signed agreements",
            "private package registry or approved artifact handoff channel",
            "signed release artifact/provenance attestation",
            "external clean-room install report",
            "support owner roster and response process approval",
            "production incident and rollback authority",
        ],
        "remaining_runtime_blockers": [
            "production identity provider integration and persistent tenant membership",
            "production object storage and audit retention backend",
            "hosted dashboard server and browser session enforcement",
            "real external read-only API credentials or partner exports",
            "lab-approved live telemetry and closed-loop approval workflow",
        ],
        "direct_answer": {
            "did_we_add_private_beta_onboarding_contract": "yes" if proof_ready else "not_yet",
            "is_external_beta_ready": "no",
            "is_full_biosdk_ready": "no",
            "is_biocompute_runtime_ready": "no",
            "is_bic_os_ready": "no",
            "next_best_build_step": "add clean-room install/reporting contract proof" if proof_ready else "fix v5.40 onboarding blockers first",
        },
        "claim_boundary": "v5.40 proves a local private-beta onboarding and release-operations contract over the v5.39 install gate. It does not claim external beta launch, published distribution, production support, full BioSDK, production BioCompute Runtime or BiC OS readiness.",
    }
    audit["onboarding_audit_sha256"] = stable_hash({key: value for key, value in audit.items() if key != "onboarding_audit_sha256"})
    return audit


def write_private_beta_onboarding_outputs_v540(audit: dict[str, Any], out_dir: str | Path = DEFAULT_OUT) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary_json": out / "V540_PRIVATE_BETA_ONBOARDING_SUMMARY.json",
        "program_contract_json": out / "V540_PRIVATE_BETA_PROGRAM_CONTRACT.json",
        "artifacts_json": out / "V540_ONBOARDING_ARTIFACTS.json",
        "release_operations_json": out / "V540_RELEASE_OPERATIONS_CONTRACT.json",
        "participant_matrix_json": out / "V540_PARTICIPANT_DECISION_MATRIX.json",
        "participant_matrix_csv": out / "V540_PARTICIPANT_DECISION_MATRIX.csv",
        "markdown_report": out / "BIOGPU_V540_PRIVATE_BETA_ONBOARDING_REPORT.md",
    }
    summary = {key: value for key, value in audit.items() if key not in {"program_contract", "onboarding_artifacts", "release_operations_contract", "participant_decision_matrix"}}
    paths["summary_json"].write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["program_contract_json"].write_text(json.dumps(audit["program_contract"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["artifacts_json"].write_text(json.dumps(audit["onboarding_artifacts"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["release_operations_json"].write_text(json.dumps(audit["release_operations_contract"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["participant_matrix_json"].write_text(json.dumps(audit["participant_decision_matrix"], indent=2, ensure_ascii=False), encoding="utf-8")
    _write_participant_matrix_csv(paths["participant_matrix_csv"], audit["participant_decision_matrix"]["decisions"])
    paths["markdown_report"].write_text(_markdown_report(audit), encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}


def _write_participant_matrix_csv(path: Path, decisions: list[dict[str, Any]]) -> None:
    fieldnames = ["participant_id", "allowed", "allowed_data_mode", "reason_codes", "live_actuation_enabled", "production_sla_enabled"]
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
        "# BioGPU-Core v5.40 Private Beta Onboarding Contract",
        "",
        "## Direct Answer",
        "",
        f"- Private beta onboarding contract added: `{answer['did_we_add_private_beta_onboarding_contract']}`",
        f"- External beta ready: `{answer['is_external_beta_ready']}`",
        f"- Full BioSDK ready: `{answer['is_full_biosdk_ready']}`",
        f"- BioCompute Runtime ready: `{answer['is_biocompute_runtime_ready']}`",
        f"- BiC OS ready: `{answer['is_bic_os_ready']}`",
        f"- Next best build step: {answer['next_best_build_step']}",
        "",
        "## Proof Summary",
        "",
        f"- Overall status: `{audit['overall_status']}`",
        f"- v5.39 dependency ready: `{audit['v539_dependency_ready']}`",
        f"- Program contract ready: `{audit['program_contract_ready']}`",
        f"- Release operations ready: `{audit['release_operations_contract_ready']}`",
        f"- Participant gate ready: `{audit['participant_gate_ready']}`",
        f"- Allowed participant fixtures: `{audit['allowed_participant_count']}`",
        f"- Denied participant fixtures: `{audit['denied_participant_count']}`",
        "",
        "## Missing Real Inputs",
        "",
    ]
    for missing in audit["missing_real_inputs"]:
        lines.append(f"- {missing}")
    lines.extend(["", "## Boundary", "", audit["claim_boundary"], ""])
    return "\n".join(lines)