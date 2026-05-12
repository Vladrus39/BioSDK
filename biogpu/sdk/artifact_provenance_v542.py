"""Signed artifact and provenance contract proof, v5.42."""
from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from biogpu.beta.job_model_v43 import utc_now_iso
from biogpu.evidence.ledger_v53 import local_signature, sha256_file, stable_hash
from biogpu.sdk.clean_room_install_report_v541 import run_clean_room_install_report_workflow_v541
from biogpu.sdk.package_install_gate_v539 import load_pyproject_v539


DEFAULT_OUT = Path("outputs/v542_signed_artifact_provenance")
LOCAL_PROVENANCE_KEY_ID_V542 = "local_hmac_v53_provenance_contract_not_trusted_release_key"


@dataclass(frozen=True)
class ArtifactProvenancePolicyV542:
    policy_id: str
    required_artifact_kind: str
    required_digest_algorithm: str
    local_signature_algorithm: str
    local_signature_required: bool
    trusted_external_signature_required_for_release: bool
    transparency_log_required_for_release: bool
    local_contract_only: bool = True
    trusted_external_signature_ready: bool = False
    transparency_log_ready: bool = False
    production_distribution_ready: bool = False
    full_biosdk_ready: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ProvenanceMaterialV542:
    material_name: str
    material_kind: str
    digest_sha256: str
    local_only: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_artifact_provenance_policy_v542() -> dict[str, Any]:
    policy = ArtifactProvenancePolicyV542(
        policy_id="BIOGPU_CORE_V542_LOCAL_PROVENANCE_POLICY",
        required_artifact_kind="wheel",
        required_digest_algorithm="sha256",
        local_signature_algorithm="hmac-sha256-local-integrity",
        local_signature_required=True,
        trusted_external_signature_required_for_release=True,
        transparency_log_required_for_release=True,
    )
    return {
        "version": "v5.42",
        "policy_ready": True,
        "policy": policy.to_dict(),
        "external_release_requirements": [
            "trusted signing identity or hardware-backed signing key",
            "provenance attestation from an independent clean-room runner",
            "transparency log or immutable release ledger inclusion",
            "signed checksum file published through approved channel",
        ],
        "trusted_external_signature_ready": False,
        "transparency_log_ready": False,
        "production_distribution_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }


def build_artifact_manifest_v542(project_root: str | Path, v541_audit: dict[str, Any]) -> dict[str, Any]:
    local_probe = dict(v541_audit.get("local_install_probe") or {})
    wheel_path = Path(str(local_probe.get("wheel_path") or ""))
    wheel_manifest = dict(local_probe.get("wheel_manifest") or {})
    errors: list[str] = []
    if not wheel_path.exists():
        errors.append("wheel_artifact_missing")
    actual_sha256 = sha256_file(wheel_path) if wheel_path.exists() else None
    expected_sha256 = wheel_manifest.get("wheel_sha256")
    if actual_sha256 and expected_sha256 and actual_sha256 != expected_sha256:
        errors.append("wheel_sha256_mismatch")
    if wheel_manifest.get("wheel_inspection_ready") is not True:
        errors.append("wheel_inspection_not_ready")
    manifest = {
        "version": "v5.42",
        "artifact_manifest_ready": not errors,
        "artifact_name": wheel_manifest.get("wheel_name", wheel_path.name if wheel_path.name else "missing_wheel"),
        "artifact_kind": "wheel",
        "artifact_path": str(wheel_path).replace("\\", "/") if wheel_path else "",
        "artifact_size_bytes": wheel_path.stat().st_size if wheel_path.exists() else None,
        "artifact_sha256": actual_sha256,
        "declared_artifact_sha256": expected_sha256,
        "file_count": wheel_manifest.get("file_count"),
        "v541_probe_sha256": local_probe.get("probe_sha256"),
        "errors": errors,
        "trusted_external_signature_ready": False,
        "production_distribution_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    manifest["artifact_manifest_sha256"] = stable_hash(manifest)
    return manifest


def build_provenance_statement_v542(project_root: str | Path, artifact_manifest: dict[str, Any], v541_audit: dict[str, Any]) -> dict[str, Any]:
    root = Path(project_root).resolve()
    pyproject = load_pyproject_v539(root)
    pyproject_hash = stable_hash(pyproject)
    materials = [
        ProvenanceMaterialV542("pyproject.toml", "package_metadata", pyproject_hash).to_dict(),
        ProvenanceMaterialV542("v5.41_clean_room_audit", "dependency_audit", str(v541_audit.get("clean_room_audit_sha256", "missing"))).to_dict(),
        ProvenanceMaterialV542("wheel_artifact", "release_candidate_artifact", str(artifact_manifest.get("artifact_sha256", "missing"))).to_dict(),
    ]
    statement = {
        "version": "v5.42",
        "predicate_type": "biogpu-core.local-provenance.v1",
        "created_at": utc_now_iso(),
        "subject": {
            "name": artifact_manifest.get("artifact_name"),
            "digest": {"sha256": artifact_manifest.get("artifact_sha256")},
            "artifact_manifest_sha256": artifact_manifest.get("artifact_manifest_sha256"),
        },
        "builder": {
            "id": "local_biogpu_v542_builder_contract",
            "trusted_external_builder": False,
            "clean_room_dependency": "v5.41_local_probe",
        },
        "build_type": "local_wheel_build_no_deps_no_build_isolation",
        "materials": materials,
        "invocation": {
            "entrypoint": "biogpu-v542-signed-artifact-provenance",
            "source_root": str(root).replace("\\", "/"),
            "v541_status": v541_audit.get("overall_status"),
            "v541_local_probe_ready": v541_audit.get("local_clean_room_install_probe_ready"),
        },
        "claim_boundary_acknowledged": True,
        "trusted_external_signature_ready": False,
        "transparency_log_ready": False,
        "production_distribution_ready": False,
        "production_biocompute_runtime_ready": False,
        "full_biosdk_ready": False,
        "live_actuation_enabled": False,
        "bic_os_phase_locked": True,
    }
    statement["provenance_statement_sha256"] = stable_hash(statement)
    return statement


def sign_provenance_statement_v542(provenance_statement: dict[str, Any]) -> dict[str, Any]:
    payload_hash = stable_hash(provenance_statement)
    signature = local_signature(payload_hash)
    envelope = {
        "version": "v5.42",
        "signature_envelope_kind": "local_hmac_integrity_signature",
        "key_id": LOCAL_PROVENANCE_KEY_ID_V542,
        "payload_hash": payload_hash,
        "local_signature": signature,
        "signature_algorithm": "hmac-sha256-local-integrity",
        "signed_at": utc_now_iso(),
        "provenance_statement": provenance_statement,
        "local_signature_ready": True,
        "trusted_external_signature_ready": False,
        "transparency_log_ready": False,
        "production_distribution_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    envelope["signature_envelope_sha256"] = stable_hash(envelope)
    return envelope


def validate_signature_envelope_v542(signature_envelope: dict[str, Any]) -> dict[str, Any]:
    statement = dict(signature_envelope.get("provenance_statement") or {})
    expected_payload_hash = stable_hash(statement)
    expected_signature = local_signature(expected_payload_hash)
    errors: list[str] = []
    boundary_errors: list[str] = []
    if signature_envelope.get("payload_hash") != expected_payload_hash:
        errors.append("payload_hash_mismatch")
    if signature_envelope.get("local_signature") != expected_signature:
        errors.append("local_signature_mismatch")
    if statement.get("subject", {}).get("digest", {}).get("sha256") in {None, "missing"}:
        errors.append("subject_digest_missing")
    if signature_envelope.get("trusted_external_signature_ready") is not False:
        boundary_errors.append("trusted_external_signature_must_not_be_claimed")
    if signature_envelope.get("transparency_log_ready") is not False:
        boundary_errors.append("transparency_log_must_not_be_claimed")
    if signature_envelope.get("full_biosdk_ready") is not False:
        boundary_errors.append("full_biosdk_must_not_be_claimed")
    if statement.get("bic_os_phase_locked") is not True:
        boundary_errors.append("bic_os_phase_must_remain_locked")
    return {
        "version": "v5.42",
        "signature_validation_ready": not errors and not boundary_errors,
        "payload_hash_valid": signature_envelope.get("payload_hash") == expected_payload_hash,
        "local_signature_valid": signature_envelope.get("local_signature") == expected_signature,
        "subject_digest_present": statement.get("subject", {}).get("digest", {}).get("sha256") not in {None, "missing"},
        "errors": errors,
        "boundary_errors": boundary_errors,
        "trusted_external_signature_ready": False,
        "transparency_log_ready": False,
        "production_distribution_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }


def run_provenance_tamper_probe_v542(signature_envelope: dict[str, Any]) -> dict[str, Any]:
    tampered = json.loads(json.dumps(signature_envelope))
    tampered["provenance_statement"]["subject"]["digest"]["sha256"] = "0" * 64
    validation = validate_signature_envelope_v542(tampered)
    return {
        "version": "v5.42",
        "tamper_detection_ready": validation["signature_validation_ready"] is False and "payload_hash_mismatch" in validation["errors"],
        "tampered_validation": validation,
        "trusted_external_signature_ready": False,
        "production_distribution_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }


def run_signed_artifact_provenance_workflow_v542(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    project_root = Path(root).resolve()
    out = project_root / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    v541_dependency = run_clean_room_install_report_workflow_v541(project_root, out / "d541", run_local_install_probe=True, require_local_install_probe=True)
    policy = build_artifact_provenance_policy_v542()
    artifact_manifest = build_artifact_manifest_v542(project_root, v541_dependency)
    provenance_statement = build_provenance_statement_v542(project_root, artifact_manifest, v541_dependency)
    signature_envelope = sign_provenance_statement_v542(provenance_statement)
    signature_validation = validate_signature_envelope_v542(signature_envelope)
    tamper_probe = run_provenance_tamper_probe_v542(signature_envelope)
    proof_ready = (
        v541_dependency.get("clean_room_install_report_contract_ready") is True
        and policy.get("policy_ready") is True
        and artifact_manifest.get("artifact_manifest_ready") is True
        and signature_validation.get("signature_validation_ready") is True
        and tamper_probe.get("tamper_detection_ready") is True
    )
    audit = {
        "version": "v5.42",
        "phase": "signed_artifact_provenance_contract",
        "overall_status": "signed_artifact_provenance_contract_ready_external_not_claimed" if proof_ready else "signed_artifact_provenance_contract_incomplete",
        "active_phase": "biosdk_signed_artifact_provenance_proof",
        "bic_os_phase_locked": True,
        "signed_artifact_provenance_contract_ready": proof_ready,
        "v541_dependency_ready": v541_dependency.get("clean_room_install_report_contract_ready") is True,
        "provenance_policy_ready": policy.get("policy_ready") is True,
        "artifact_manifest_ready": artifact_manifest.get("artifact_manifest_ready") is True,
        "local_signature_ready": signature_envelope.get("local_signature_ready") is True,
        "signature_validation_ready": signature_validation.get("signature_validation_ready") is True,
        "tamper_detection_ready": tamper_probe.get("tamper_detection_ready") is True,
        "artifact_name": artifact_manifest.get("artifact_name"),
        "artifact_sha256": artifact_manifest.get("artifact_sha256"),
        "payload_hash": signature_envelope.get("payload_hash"),
        "trusted_external_signature_ready": False,
        "transparency_log_ready": False,
        "external_clean_room_report_ready": False,
        "production_distribution_ready": False,
        "production_runtime_ready": False,
        "production_api_ready": False,
        "production_biocompute_runtime_ready": False,
        "full_biosdk_ready": False,
        "live_actuation_enabled": False,
        "provenance_policy": policy,
        "artifact_manifest": artifact_manifest,
        "provenance_statement": provenance_statement,
        "signature_envelope": signature_envelope,
        "signature_validation": signature_validation,
        "tamper_probe": tamper_probe,
        "v541_dependency_summary": {key: value for key, value in v541_dependency.items() if key not in {"environment_contract", "report_sections", "local_install_probe", "clean_room_report_fixture", "report_completeness", "v540_dependency_summary"}},
        "missing_real_inputs": [
            "trusted release signing identity or hardware-backed key",
            "external provenance attestation from independent clean-room runner",
            "transparency log or immutable release ledger inclusion",
            "approved private artifact handoff channel or registry",
            "signed checksum publication process",
            "release approval authority and revocation policy",
        ],
        "remaining_runtime_blockers": [
            "production identity provider integration and persistent tenant membership",
            "production object storage and audit retention backend",
            "hosted dashboard server and browser session enforcement",
            "real external read-only API credentials or partner exports",
            "lab-approved live telemetry and closed-loop approval workflow",
        ],
        "direct_answer": {
            "did_we_add_signed_artifact_provenance_contract": "yes" if proof_ready else "not_yet",
            "did_we_create_local_signature": "yes" if signature_envelope.get("local_signature_ready") else "no",
            "is_trusted_external_signature_ready": "no",
            "is_transparency_log_ready": "no",
            "is_full_biosdk_ready": "no",
            "is_biocompute_runtime_ready": "no",
            "is_bic_os_ready": "no",
            "next_best_build_step": "add release approval and revocation contract proof" if proof_ready else "fix v5.42 provenance blockers first",
        },
        "claim_boundary": "v5.42 proves local wheel artifact hashing, local provenance statement generation, local HMAC-style signature validation and tamper detection over the v5.41 clean-room install report. It does not claim trusted external signing, transparency-log inclusion, published distribution, full BioSDK, production BioCompute Runtime or BiC OS readiness.",
    }
    audit["provenance_audit_sha256"] = stable_hash({key: value for key, value in audit.items() if key != "provenance_audit_sha256"})
    return audit


def write_signed_artifact_provenance_outputs_v542(audit: dict[str, Any], out_dir: str | Path = DEFAULT_OUT) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary_json": out / "V542_SIGNED_ARTIFACT_PROVENANCE_SUMMARY.json",
        "policy_json": out / "V542_PROVENANCE_POLICY.json",
        "artifact_manifest_json": out / "V542_ARTIFACT_MANIFEST.json",
        "provenance_statement_json": out / "V542_PROVENANCE_STATEMENT.json",
        "signature_envelope_json": out / "V542_LOCAL_SIGNATURE_ENVELOPE.json",
        "signature_validation_json": out / "V542_SIGNATURE_VALIDATION.json",
        "tamper_probe_json": out / "V542_PROVENANCE_TAMPER_PROBE.json",
        "materials_csv": out / "V542_PROVENANCE_MATERIALS.csv",
        "markdown_report": out / "BIOGPU_V542_SIGNED_ARTIFACT_PROVENANCE_REPORT.md",
    }
    summary = {key: value for key, value in audit.items() if key not in {"provenance_policy", "artifact_manifest", "provenance_statement", "signature_envelope", "signature_validation", "tamper_probe"}}
    paths["summary_json"].write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["policy_json"].write_text(json.dumps(audit["provenance_policy"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["artifact_manifest_json"].write_text(json.dumps(audit["artifact_manifest"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["provenance_statement_json"].write_text(json.dumps(audit["provenance_statement"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["signature_envelope_json"].write_text(json.dumps(audit["signature_envelope"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["signature_validation_json"].write_text(json.dumps(audit["signature_validation"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["tamper_probe_json"].write_text(json.dumps(audit["tamper_probe"], indent=2, ensure_ascii=False), encoding="utf-8")
    _write_materials_csv(paths["materials_csv"], audit["provenance_statement"].get("materials", []))
    paths["markdown_report"].write_text(_markdown_report(audit), encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}


def _write_materials_csv(path: Path, materials: list[dict[str, Any]]) -> None:
    fieldnames = ["material_name", "material_kind", "digest_sha256", "local_only"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for material in materials:
            writer.writerow({field: material.get(field) for field in fieldnames})


def _markdown_report(audit: dict[str, Any]) -> str:
    answer = audit["direct_answer"]
    lines = [
        "# BioGPU-Core v5.42 Signed Artifact Provenance Contract",
        "",
        "## Direct Answer",
        "",
        f"- Signed artifact provenance contract added: `{answer['did_we_add_signed_artifact_provenance_contract']}`",
        f"- Local signature created: `{answer['did_we_create_local_signature']}`",
        f"- Trusted external signature ready: `{answer['is_trusted_external_signature_ready']}`",
        f"- Transparency log ready: `{answer['is_transparency_log_ready']}`",
        f"- Full BioSDK ready: `{answer['is_full_biosdk_ready']}`",
        f"- BioCompute Runtime ready: `{answer['is_biocompute_runtime_ready']}`",
        f"- BiC OS ready: `{answer['is_bic_os_ready']}`",
        f"- Next best build step: {answer['next_best_build_step']}",
        "",
        "## Proof Summary",
        "",
        f"- Overall status: `{audit['overall_status']}`",
        f"- v5.41 dependency ready: `{audit['v541_dependency_ready']}`",
        f"- Artifact manifest ready: `{audit['artifact_manifest_ready']}`",
        f"- Local signature ready: `{audit['local_signature_ready']}`",
        f"- Signature validation ready: `{audit['signature_validation_ready']}`",
        f"- Tamper detection ready: `{audit['tamper_detection_ready']}`",
        f"- Artifact SHA-256: `{audit['artifact_sha256']}`",
        "",
        "## Missing Real Inputs",
        "",
    ]
    for missing in audit["missing_real_inputs"]:
        lines.append(f"- {missing}")
    lines.extend(["", "## Boundary", "", audit["claim_boundary"], ""])
    return "\n".join(lines)