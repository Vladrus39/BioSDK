"""Private registry/artifact handoff contract proof, v5.44."""
from __future__ import annotations

import csv
import json
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from biogpu.beta.job_model_v43 import utc_now_iso
from biogpu.evidence.ledger_v53 import sha256_file, stable_hash
from biogpu.sdk.release_approval_v543 import run_release_approval_revocation_workflow_v543


DEFAULT_OUT = Path("outputs/v544_private_registry_handoff")
APPROVED_HANDOFF_ROLES_V544 = {"release_manager", "provenance_reviewer", "beta_operator", "artifact_recipient"}
APPROVED_HANDOFF_CHANNELS_V544 = ("local_signed_artifact_handoff", "private_registry_contract_dry_run")


@dataclass(frozen=True)
class PrivateRegistryHandoffContractV544:
    contract_id: str
    allowed_channels: tuple[str, ...]
    blocked_channels: tuple[str, ...]
    requires_release_decision: bool
    requires_artifact_sha256: bool
    requires_local_provenance_signature: bool
    requires_revocation_check: bool
    live_registry_endpoint_configured: bool
    local_contract_only: bool = True
    private_registry_ready: bool = False
    public_registry_ready: bool = False
    production_distribution_ready: bool = False
    full_biosdk_ready: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class HandoffPrincipalFixtureV544:
    principal_id: str
    role: str
    accepted_claim_boundary: bool
    has_release_access: bool
    requested_channel: str
    requested_artifact_sha256: str
    revoked_access: bool
    requests_public_registry: bool
    requests_production_distribution: bool
    requests_live_actuation: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class HandoffAccessDecisionV544:
    principal_id: str
    role: str
    allowed: bool
    reason_codes: tuple[str, ...]
    allowed_channel: str | None
    private_registry_ready: bool = False
    production_distribution_ready: bool = False
    full_biosdk_ready: bool = False
    live_actuation_enabled: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_private_registry_handoff_contract_v544() -> dict[str, Any]:
    contract = PrivateRegistryHandoffContractV544(
        contract_id="BIOGPU_CORE_V544_PRIVATE_REGISTRY_HANDOFF_CONTRACT",
        allowed_channels=APPROVED_HANDOFF_CHANNELS_V544,
        blocked_channels=("public_registry", "production_marketplace", "auto_update_channel", "live_runtime_feed"),
        requires_release_decision=True,
        requires_artifact_sha256=True,
        requires_local_provenance_signature=True,
        requires_revocation_check=True,
        live_registry_endpoint_configured=False,
    )
    return {
        "version": "v5.44",
        "private_registry_handoff_contract_ready": True,
        "contract": contract.to_dict(),
        "local_handoff_channels_ready": True,
        "live_private_registry_ready": False,
        "public_registry_ready": False,
        "production_distribution_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(char in "0123456789abcdef" for char in value.lower())


def find_dependency_wheel_v544(dependency_out: str | Path, artifact_sha256: str | None) -> Path | None:
    root = Path(dependency_out)
    if not root.exists():
        return None
    candidates = sorted(root.rglob("*.whl"))
    if artifact_sha256:
        for candidate in candidates:
            try:
                if sha256_file(candidate) == artifact_sha256:
                    return candidate
            except OSError:
                continue
    return candidates[-1] if candidates else None


def build_handoff_artifact_record_v544(v543_dependency: dict[str, Any], artifact_path: str | Path | None = None) -> dict[str, Any]:
    artifact_name = str(v543_dependency.get("artifact_name") or "")
    artifact_sha256 = str(v543_dependency.get("artifact_sha256") or "")
    local_candidate_approved = v543_dependency.get("local_candidate_handoff_approved") is True
    path = Path(artifact_path) if artifact_path else None
    file_exists = path.exists() if path else False
    file_sha256 = sha256_file(path) if file_exists and path is not None else None
    errors: list[str] = []
    if not artifact_name.endswith(".whl"):
        errors.append("artifact_name_not_wheel")
    if not _is_sha256(artifact_sha256):
        errors.append("artifact_sha256_missing_or_invalid")
    if not local_candidate_approved:
        errors.append("local_candidate_not_approved")
    if not file_exists:
        errors.append("local_artifact_file_missing")
    if file_sha256 and artifact_sha256 and file_sha256 != artifact_sha256:
        errors.append("artifact_file_sha256_mismatch")
    record = {
        "version": "v5.44",
        "handoff_artifact_record_ready": not errors,
        "artifact_name": artifact_name,
        "artifact_sha256": artifact_sha256,
        "artifact_path": str(path).replace("\\", "/") if path else None,
        "artifact_file_present": file_exists,
        "artifact_file_sha256": file_sha256,
        "artifact_file_sha256_matches": file_sha256 == artifact_sha256 if file_sha256 else False,
        "release_decision_sha256": v543_dependency.get("release_approval_audit_sha256"),
        "local_candidate_handoff_approved": local_candidate_approved,
        "errors": errors,
        "private_registry_ready": False,
        "public_registry_ready": False,
        "production_distribution_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    record["handoff_artifact_record_sha256"] = stable_hash(record)
    return record


def stage_local_handoff_artifact_v544(artifact_record: dict[str, Any], out_dir: str | Path) -> dict[str, Any]:
    out = Path(out_dir)
    handoff_dir = out / "local_handoff_artifacts"
    handoff_dir.mkdir(parents=True, exist_ok=True)
    source = Path(str(artifact_record.get("artifact_path") or ""))
    destination = handoff_dir / str(artifact_record.get("artifact_name") or "artifact.whl")
    errors: list[str] = []
    if not source.exists():
        errors.append("source_artifact_missing")
    else:
        if destination.exists():
            destination.unlink()
        shutil.copy2(source, destination)
    staged_sha256 = sha256_file(destination) if destination.exists() else None
    expected_sha256 = artifact_record.get("artifact_sha256")
    if staged_sha256 and expected_sha256 and staged_sha256 != expected_sha256:
        errors.append("staged_artifact_sha256_mismatch")
    staged = {
        "version": "v5.44",
        "local_handoff_package_ready": not errors and destination.exists(),
        "handoff_dir": str(handoff_dir).replace("\\", "/"),
        "staged_artifact_path": str(destination).replace("\\", "/") if destination.exists() else None,
        "staged_artifact_sha256": staged_sha256,
        "expected_artifact_sha256": expected_sha256,
        "errors": errors,
        "private_registry_ready": False,
        "public_registry_ready": False,
        "production_distribution_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    staged["local_handoff_package_sha256"] = stable_hash(staged)
    return staged


def default_handoff_principal_fixtures_v544(artifact_sha256: str) -> list[HandoffPrincipalFixtureV544]:
    wrong_sha = "0" * 64 if artifact_sha256 != "0" * 64 else "1" * 64
    return [
        HandoffPrincipalFixtureV544("release-manager", "release_manager", True, True, "local_signed_artifact_handoff", artifact_sha256, False, False, False, False),
        HandoffPrincipalFixtureV544("provenance-reviewer", "provenance_reviewer", True, True, "local_signed_artifact_handoff", artifact_sha256, False, False, False, False),
        HandoffPrincipalFixtureV544("beta-operator", "beta_operator", True, True, "private_registry_contract_dry_run", artifact_sha256, False, False, False, False),
        HandoffPrincipalFixtureV544("recipient", "artifact_recipient", True, True, "local_signed_artifact_handoff", artifact_sha256, False, False, False, False),
        HandoffPrincipalFixtureV544("missing-boundary", "artifact_recipient", False, True, "local_signed_artifact_handoff", artifact_sha256, False, False, False, False),
        HandoffPrincipalFixtureV544("no-release-access", "artifact_recipient", True, False, "local_signed_artifact_handoff", artifact_sha256, False, False, False, False),
        HandoffPrincipalFixtureV544("wrong-artifact", "artifact_recipient", True, True, "local_signed_artifact_handoff", wrong_sha, False, False, False, False),
        HandoffPrincipalFixtureV544("revoked-recipient", "artifact_recipient", True, True, "local_signed_artifact_handoff", artifact_sha256, True, False, False, False),
        HandoffPrincipalFixtureV544("public-registry-request", "release_manager", True, True, "public_registry", artifact_sha256, False, True, False, False),
        HandoffPrincipalFixtureV544("production-request", "release_manager", True, True, "local_signed_artifact_handoff", artifact_sha256, False, False, True, False),
        HandoffPrincipalFixtureV544("live-request", "beta_operator", True, True, "local_signed_artifact_handoff", artifact_sha256, False, False, False, True),
        HandoffPrincipalFixtureV544("unknown-role", "viewer", True, True, "local_signed_artifact_handoff", artifact_sha256, False, False, False, False),
    ]


def authorize_handoff_access_v544(principal: HandoffPrincipalFixtureV544, artifact_record: dict[str, Any]) -> HandoffAccessDecisionV544:
    reasons: list[str] = []
    expected_sha = str(artifact_record.get("artifact_sha256") or "")
    if principal.role not in APPROVED_HANDOFF_ROLES_V544:
        reasons.append("role_not_authorized_for_handoff")
    if not principal.accepted_claim_boundary:
        reasons.append("claim_boundary_not_accepted")
    if not principal.has_release_access:
        reasons.append("release_access_missing")
    if principal.requested_channel not in APPROVED_HANDOFF_CHANNELS_V544:
        reasons.append("handoff_channel_not_allowed")
    if principal.requested_artifact_sha256 != expected_sha:
        reasons.append("artifact_digest_mismatch")
    if principal.revoked_access:
        reasons.append("access_revoked")
    if principal.requests_public_registry:
        reasons.append("public_registry_not_allowed")
    if principal.requests_production_distribution:
        reasons.append("production_distribution_not_allowed")
    if principal.requests_live_actuation:
        reasons.append("live_actuation_not_allowed")
    allowed = not reasons
    return HandoffAccessDecisionV544(
        principal_id=principal.principal_id,
        role=principal.role,
        allowed=allowed,
        reason_codes=tuple(reasons or ["local_handoff_allowed"]),
        allowed_channel=principal.requested_channel if allowed else None,
    )


def run_handoff_access_matrix_v544(artifact_record: dict[str, Any], fixtures: list[HandoffPrincipalFixtureV544] | None = None) -> dict[str, Any]:
    principals = fixtures or default_handoff_principal_fixtures_v544(str(artifact_record.get("artifact_sha256") or ""))
    decisions = [authorize_handoff_access_v544(principal, artifact_record).to_dict() for principal in principals]
    allowed_count = sum(1 for decision in decisions if decision["allowed"])
    denied_count = len(decisions) - allowed_count
    reason_codes = sorted({reason for decision in decisions for reason in decision["reason_codes"]})
    required_denials = {
        "claim_boundary_not_accepted",
        "release_access_missing",
        "artifact_digest_mismatch",
        "access_revoked",
        "handoff_channel_not_allowed",
        "production_distribution_not_allowed",
        "live_actuation_not_allowed",
        "role_not_authorized_for_handoff",
    }
    matrix = {
        "version": "v5.44",
        "handoff_access_matrix_ready": allowed_count >= 4 and denied_count >= 8 and required_denials.issubset(set(reason_codes)),
        "principal_count": len(principals),
        "allowed_count": allowed_count,
        "denied_count": denied_count,
        "reason_codes": reason_codes,
        "principals": [principal.to_dict() for principal in principals],
        "decisions": decisions,
        "private_registry_ready": False,
        "public_registry_ready": False,
        "production_distribution_ready": False,
        "full_biosdk_ready": False,
        "live_actuation_enabled": False,
        "bic_os_phase_locked": True,
    }
    matrix["handoff_access_matrix_sha256"] = stable_hash(matrix)
    return matrix


def run_handoff_revocation_probe_v544(artifact_record: dict[str, Any]) -> dict[str, Any]:
    revoked_principal = HandoffPrincipalFixtureV544(
        "revoked-probe-recipient",
        "artifact_recipient",
        True,
        True,
        "local_signed_artifact_handoff",
        str(artifact_record.get("artifact_sha256") or ""),
        True,
        False,
        False,
        False,
    )
    decision = authorize_handoff_access_v544(revoked_principal, artifact_record).to_dict()
    denylist = {
        "artifact_sha256": artifact_record.get("artifact_sha256"),
        "revoked_principals": [revoked_principal.principal_id],
        "revoked_at": utc_now_iso(),
        "reason": "v5.44_revocation_probe",
    }
    probe = {
        "version": "v5.44",
        "handoff_revocation_probe_ready": decision["allowed"] is False and "access_revoked" in decision["reason_codes"],
        "denylist": denylist,
        "revoked_access_decision": decision,
        "private_registry_ready": False,
        "production_distribution_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    probe["handoff_revocation_probe_sha256"] = stable_hash(probe)
    return probe


def build_local_registry_index_v544(artifact_record: dict[str, Any], staged_handoff: dict[str, Any], access_matrix: dict[str, Any], revocation_probe: dict[str, Any]) -> dict[str, Any]:
    index = {
        "version": "v5.44",
        "local_registry_index_ready": staged_handoff.get("local_handoff_package_ready") is True and access_matrix.get("handoff_access_matrix_ready") is True and revocation_probe.get("handoff_revocation_probe_ready") is True,
        "registry_kind": "local_private_registry_contract_dry_run",
        "live_registry_endpoint": None,
        "artifact_name": artifact_record.get("artifact_name"),
        "artifact_sha256": artifact_record.get("artifact_sha256"),
        "staged_artifact_path": staged_handoff.get("staged_artifact_path"),
        "allowed_channels": list(APPROVED_HANDOFF_CHANNELS_V544),
        "allowed_principal_count": access_matrix.get("allowed_count"),
        "denied_principal_count": access_matrix.get("denied_count"),
        "revocation_probe_sha256": revocation_probe.get("handoff_revocation_probe_sha256"),
        "private_registry_ready": False,
        "public_registry_ready": False,
        "production_distribution_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    index["local_registry_index_sha256"] = stable_hash(index)
    return index


def run_private_registry_handoff_workflow_v544(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    project_root = Path(root).resolve()
    out = project_root / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    dependency_out = out / "d543"
    v543_dependency = run_release_approval_revocation_workflow_v543(project_root, dependency_out)
    artifact_path = find_dependency_wheel_v544(dependency_out, str(v543_dependency.get("artifact_sha256") or ""))
    contract = build_private_registry_handoff_contract_v544()
    artifact_record = build_handoff_artifact_record_v544(v543_dependency, artifact_path)
    staged_handoff = stage_local_handoff_artifact_v544(artifact_record, out)
    access_matrix = run_handoff_access_matrix_v544(artifact_record)
    revocation_probe = run_handoff_revocation_probe_v544(artifact_record)
    registry_index = build_local_registry_index_v544(artifact_record, staged_handoff, access_matrix, revocation_probe)
    proof_ready = (
        v543_dependency.get("release_approval_revocation_contract_ready") is True
        and contract.get("private_registry_handoff_contract_ready") is True
        and artifact_record.get("handoff_artifact_record_ready") is True
        and staged_handoff.get("local_handoff_package_ready") is True
        and access_matrix.get("handoff_access_matrix_ready") is True
        and revocation_probe.get("handoff_revocation_probe_ready") is True
        and registry_index.get("local_registry_index_ready") is True
    )
    audit = {
        "version": "v5.44",
        "phase": "private_registry_artifact_handoff_contract",
        "overall_status": "private_registry_handoff_contract_ready_production_not_claimed" if proof_ready else "private_registry_handoff_contract_incomplete",
        "active_phase": "biosdk_private_registry_handoff_proof",
        "bic_os_phase_locked": True,
        "private_registry_handoff_contract_ready": proof_ready,
        "v543_dependency_ready": v543_dependency.get("release_approval_revocation_contract_ready") is True,
        "handoff_contract_ready": contract.get("private_registry_handoff_contract_ready") is True,
        "handoff_artifact_record_ready": artifact_record.get("handoff_artifact_record_ready") is True,
        "local_handoff_package_ready": staged_handoff.get("local_handoff_package_ready") is True,
        "handoff_access_matrix_ready": access_matrix.get("handoff_access_matrix_ready") is True,
        "handoff_revocation_probe_ready": revocation_probe.get("handoff_revocation_probe_ready") is True,
        "local_registry_index_ready": registry_index.get("local_registry_index_ready") is True,
        "artifact_name": artifact_record.get("artifact_name"),
        "artifact_sha256": artifact_record.get("artifact_sha256"),
        "staged_artifact_path": staged_handoff.get("staged_artifact_path"),
        "allowed_handoff_count": access_matrix.get("allowed_count"),
        "denied_handoff_count": access_matrix.get("denied_count"),
        "local_candidate_handoff_approved": True,
        "live_private_registry_ready": False,
        "private_registry_ready": False,
        "public_registry_ready": False,
        "production_distribution_ready": False,
        "production_runtime_ready": False,
        "production_api_ready": False,
        "production_biocompute_runtime_ready": False,
        "full_biosdk_ready": False,
        "live_actuation_enabled": False,
        "handoff_contract": contract,
        "handoff_artifact_record": artifact_record,
        "local_handoff_package": staged_handoff,
        "handoff_access_matrix": access_matrix,
        "handoff_revocation_probe": revocation_probe,
        "local_registry_index": registry_index,
        "v543_dependency_summary": {key: value for key, value in v543_dependency.items() if key not in {"release_approval_policy", "release_approval_matrix", "release_revocation_policy", "release_revocation_drill", "release_decision_record", "v542_dependency_summary"}},
        "missing_real_inputs": [
            "actual private package registry or approved artifact repository",
            "registry authentication/authorization integration",
            "named recipient accounts and organization approvals",
            "signed URL or package feed expiration enforcement",
            "artifact retention and registry audit export",
            "production registry yank/revoke authority",
        ],
        "remaining_runtime_blockers": [
            "production identity provider integration and persistent tenant membership",
            "production object storage and audit retention backend",
            "hosted dashboard server and browser session enforcement",
            "real external read-only API credentials or partner exports",
            "lab-approved live telemetry and closed-loop approval workflow",
        ],
        "direct_answer": {
            "did_we_add_private_registry_handoff_contract": "yes" if proof_ready else "not_yet",
            "did_we_stage_local_handoff_artifact": "yes" if staged_handoff.get("local_handoff_package_ready") else "no",
            "is_live_private_registry_ready": "no",
            "is_production_distribution_ready": "no",
            "is_full_biosdk_ready": "no",
            "is_biocompute_runtime_ready": "no",
            "is_bic_os_ready": "no",
            "next_best_build_step": "add recipient onboarding audit contract proof" if proof_ready else "fix v5.44 handoff blockers first",
        },
        "claim_boundary": "v5.44 proves local artifact handoff staging, private-registry dry-run indexing, access decisions and revocation denial over the v5.43 release approval layer. It does not claim a live private registry, public distribution, production release, full BioSDK, production BioCompute Runtime or BiC OS readiness.",
    }
    audit["private_registry_handoff_audit_sha256"] = stable_hash({key: value for key, value in audit.items() if key != "private_registry_handoff_audit_sha256"})
    return audit


def write_private_registry_handoff_outputs_v544(audit: dict[str, Any], out_dir: str | Path = DEFAULT_OUT) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary_json": out / "V544_PRIVATE_REGISTRY_HANDOFF_SUMMARY.json",
        "contract_json": out / "V544_PRIVATE_REGISTRY_HANDOFF_CONTRACT.json",
        "artifact_record_json": out / "V544_HANDOFF_ARTIFACT_RECORD.json",
        "handoff_package_json": out / "V544_LOCAL_HANDOFF_PACKAGE.json",
        "access_matrix_json": out / "V544_HANDOFF_ACCESS_MATRIX.json",
        "revocation_probe_json": out / "V544_HANDOFF_REVOCATION_PROBE.json",
        "registry_index_json": out / "V544_LOCAL_REGISTRY_INDEX.json",
        "access_matrix_csv": out / "V544_HANDOFF_ACCESS_MATRIX.csv",
        "markdown_report": out / "BIOGPU_V544_PRIVATE_REGISTRY_HANDOFF_REPORT.md",
    }
    summary = {key: value for key, value in audit.items() if key not in {"handoff_contract", "handoff_artifact_record", "local_handoff_package", "handoff_access_matrix", "handoff_revocation_probe", "local_registry_index"}}
    paths["summary_json"].write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["contract_json"].write_text(json.dumps(audit["handoff_contract"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["artifact_record_json"].write_text(json.dumps(audit["handoff_artifact_record"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["handoff_package_json"].write_text(json.dumps(audit["local_handoff_package"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["access_matrix_json"].write_text(json.dumps(audit["handoff_access_matrix"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["revocation_probe_json"].write_text(json.dumps(audit["handoff_revocation_probe"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["registry_index_json"].write_text(json.dumps(audit["local_registry_index"], indent=2, ensure_ascii=False), encoding="utf-8")
    _write_access_matrix_csv(paths["access_matrix_csv"], audit["handoff_access_matrix"].get("decisions", []))
    paths["markdown_report"].write_text(_markdown_report(audit), encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}


def _write_access_matrix_csv(path: Path, decisions: list[dict[str, Any]]) -> None:
    fieldnames = ["principal_id", "role", "allowed", "allowed_channel", "reason_codes", "private_registry_ready", "production_distribution_ready", "full_biosdk_ready"]
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
        "# BioGPU-Core v5.44 Private Registry Handoff Contract",
        "",
        "## Direct Answer",
        "",
        f"- Private registry handoff contract added: `{answer['did_we_add_private_registry_handoff_contract']}`",
        f"- Local handoff artifact staged: `{answer['did_we_stage_local_handoff_artifact']}`",
        f"- Live private registry ready: `{answer['is_live_private_registry_ready']}`",
        f"- Production distribution ready: `{answer['is_production_distribution_ready']}`",
        f"- Full BioSDK ready: `{answer['is_full_biosdk_ready']}`",
        f"- BioCompute Runtime ready: `{answer['is_biocompute_runtime_ready']}`",
        f"- BiC OS ready: `{answer['is_bic_os_ready']}`",
        f"- Next best build step: {answer['next_best_build_step']}",
        "",
        "## Proof Summary",
        "",
        f"- Overall status: `{audit['overall_status']}`",
        f"- v5.43 dependency ready: `{audit['v543_dependency_ready']}`",
        f"- Local handoff package ready: `{audit['local_handoff_package_ready']}`",
        f"- Access matrix ready: `{audit['handoff_access_matrix_ready']}`",
        f"- Revocation probe ready: `{audit['handoff_revocation_probe_ready']}`",
        f"- Local registry index ready: `{audit['local_registry_index_ready']}`",
        f"- Allowed handoffs: `{audit['allowed_handoff_count']}`",
        f"- Denied handoffs: `{audit['denied_handoff_count']}`",
        "",
        "## Missing Real Inputs",
        "",
    ]
    for missing in audit["missing_real_inputs"]:
        lines.append(f"- {missing}")
    lines.extend(["", "## Boundary", "", audit["claim_boundary"], ""])
    return "\n".join(lines)