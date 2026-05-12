"""Clean-room install reporting contract proof, v5.41."""
from __future__ import annotations

import csv
import json
import platform
import shutil
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from biogpu.beta.job_model_v43 import utc_now_iso
from biogpu.evidence.ledger_v53 import stable_hash
from biogpu.sdk.package_install_gate_v539 import build_and_install_wheel_v539, load_pyproject_v539
from biogpu.sdk.private_beta_onboarding_v540 import run_private_beta_onboarding_contract_workflow_v540


DEFAULT_OUT = Path("outputs/v541_clean_room_install_report")
REQUIRED_REPORT_FIELDS_V541 = (
    "report_id",
    "artifact_name",
    "artifact_sha256",
    "python_version",
    "os_profile",
    "install_command",
    "import_smoke_result",
    "claim_boundary_acknowledged",
    "live_actuation_enabled",
    "external_clean_room_report_ready",
)


@dataclass(frozen=True)
class CleanRoomEnvironmentContractV541:
    environment_id: str
    python_requires: str
    isolated_target_install_required: bool
    network_required_for_install: bool
    global_site_packages_allowed: bool
    allowed_install_modes: tuple[str, ...]
    blocked_install_modes: tuple[str, ...]
    local_contract_only: bool = True
    external_clean_room_report_ready: bool = False
    production_distribution_ready: bool = False
    full_biosdk_ready: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CleanRoomReportSectionV541:
    section_name: str
    purpose: str
    required: bool
    local_contract_ready: bool
    external_evidence_required: bool
    production_ready: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_clean_room_environment_contract_v541(root: str | Path) -> dict[str, Any]:
    pyproject = load_pyproject_v539(root)
    python_requires = str(pyproject.get("project", {}).get("requires-python", ""))
    contract = CleanRoomEnvironmentContractV541(
        environment_id="local_isolated_target_install_contract",
        python_requires=python_requires,
        isolated_target_install_required=True,
        network_required_for_install=False,
        global_site_packages_allowed=False,
        allowed_install_modes=("wheel_target_install_no_deps", "source_tree_readonly_validation"),
        blocked_install_modes=("public_registry_install", "auto_update_channel", "credentialed_live_runtime", "global_site_packages_mutation"),
    )
    errors: list[str] = []
    if not python_requires.startswith(">=3."):
        errors.append("missing_python_requirement")
    if contract.network_required_for_install:
        errors.append("network_install_not_allowed_for_local_contract")
    if contract.global_site_packages_allowed:
        errors.append("global_site_packages_must_be_blocked")
    return {
        "version": "v5.41",
        "environment_contract_ready": not errors,
        "contract": contract.to_dict(),
        "errors": errors,
        "external_clean_room_report_ready": False,
        "production_distribution_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }


def build_clean_room_report_sections_v541() -> list[dict[str, Any]]:
    sections = [
        CleanRoomReportSectionV541("artifact_identity", "wheel name, version and SHA-256 hash", True, True, True),
        CleanRoomReportSectionV541("environment_profile", "OS, Python and installer command profile", True, True, True),
        CleanRoomReportSectionV541("install_transcript", "bounded command transcript and return codes", True, True, True),
        CleanRoomReportSectionV541("import_smoke", "installed package import smoke result", True, True, True),
        CleanRoomReportSectionV541("claim_boundary", "explicit no-production/no-OS acknowledgement", True, True, True),
        CleanRoomReportSectionV541("rollback_readiness", "local rollback/handoff recovery notes", True, True, False),
        CleanRoomReportSectionV541("support_intake", "issue intake and severity labels", True, True, False),
        CleanRoomReportSectionV541("external_attestation", "independent tester signature or CI attestation", False, False, True),
    ]
    return [section.to_dict() for section in sections]


def build_clean_room_report_fixture_v541(local_probe: dict[str, Any] | None = None) -> dict[str, Any]:
    probe = local_probe or {"local_clean_room_install_probe_ready": False, "build_distribution_attempted": False}
    wheel_manifest = dict(probe.get("wheel_manifest") or {})
    report = {
        "version": "v5.41",
        "report_id": "local-clean-room-report-contract-v541",
        "created_at": utc_now_iso(),
        "artifact_name": wheel_manifest.get("wheel_name", "biogpu_core-5.0.0-py3-none-any.whl"),
        "artifact_sha256": wheel_manifest.get("wheel_sha256", "local_probe_not_attempted"),
        "python_version": sys.version.split()[0],
        "os_profile": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
        },
        "install_command": probe.get("build_command", "python -m pip install --target <isolated-target> <wheel>"),
        "install_returncode": probe.get("install_returncode"),
        "import_smoke_result": "passed" if probe.get("local_install_smoke_ready") is True else "not_attempted",
        "claim_boundary_acknowledged": True,
        "live_actuation_enabled": False,
        "production_distribution_ready": False,
        "full_biosdk_ready": False,
        "external_clean_room_report_ready": False,
        "local_clean_room_install_probe_ready": probe.get("local_clean_room_install_probe_ready") is True,
        "missing_external_evidence": [
            "independent machine or CI runner identifier",
            "signed tester identity or automated attestation",
            "full clean-room command transcript",
            "network isolation or dependency cache evidence",
        ],
    }
    report["report_sha256"] = stable_hash(report)
    return report


def run_local_clean_room_install_probe_v541(root: str | Path, out_dir: str | Path) -> dict[str, Any]:
    project_root = Path(root).resolve()
    out = Path(out_dir)
    probe_dir = out / "local_clean_room_probe"
    if probe_dir.exists():
        shutil.rmtree(probe_dir)
    result = build_and_install_wheel_v539(project_root, probe_dir)
    ready = result.get("local_wheel_build_ready") is True and result.get("local_install_smoke_ready") is True
    probe = {
        **result,
        "version": "v5.41",
        "local_clean_room_install_probe_ready": ready,
        "local_probe_only": True,
        "external_clean_room_report_ready": False,
        "environment_profile": {
            "python_executable": sys.executable.replace("\\", "/"),
            "python_version": sys.version.split()[0],
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
        },
    }
    probe["probe_sha256"] = stable_hash({key: value for key, value in probe.items() if key != "probe_sha256"})
    return probe


def validate_clean_room_report_completeness_v541(report: dict[str, Any], sections: list[dict[str, Any]]) -> dict[str, Any]:
    missing_fields = [field for field in REQUIRED_REPORT_FIELDS_V541 if field not in report]
    required_sections = [section for section in sections if section["required"]]
    missing_sections = [section["section_name"] for section in required_sections if not section["local_contract_ready"]]
    boundary_errors: list[str] = []
    if report.get("live_actuation_enabled") is not False:
        boundary_errors.append("live_actuation_must_remain_disabled")
    if report.get("full_biosdk_ready") is not False:
        boundary_errors.append("full_biosdk_must_not_be_claimed")
    if report.get("external_clean_room_report_ready") is not False:
        boundary_errors.append("external_clean_room_report_must_not_be_claimed")
    return {
        "version": "v5.41",
        "report_completeness_ready": not missing_fields and not missing_sections and not boundary_errors,
        "required_field_count": len(REQUIRED_REPORT_FIELDS_V541),
        "required_section_count": len(required_sections),
        "missing_fields": missing_fields,
        "missing_sections": missing_sections,
        "boundary_errors": boundary_errors,
        "report_sha256": report.get("report_sha256"),
        "external_clean_room_report_ready": False,
        "production_distribution_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }


def run_clean_room_install_report_workflow_v541(
    root: str | Path = ".",
    out_dir: str | Path = DEFAULT_OUT,
    run_local_install_probe: bool = False,
    require_local_install_probe: bool = False,
) -> dict[str, Any]:
    project_root = Path(root).resolve()
    out = project_root / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    v540_dependency = run_private_beta_onboarding_contract_workflow_v540(project_root, out / "d540")
    environment_contract = build_clean_room_environment_contract_v541(project_root)
    sections = build_clean_room_report_sections_v541()
    local_probe: dict[str, Any] = {
        "version": "v5.41",
        "local_clean_room_install_probe_ready": False,
        "build_distribution_attempted": False,
        "external_clean_room_report_ready": False,
    }
    if run_local_install_probe:
        local_probe = run_local_clean_room_install_probe_v541(project_root, out)
    report_fixture = build_clean_room_report_fixture_v541(local_probe)
    completeness = validate_clean_room_report_completeness_v541(report_fixture, sections)
    local_probe_requirement_ready = (not require_local_install_probe) or local_probe.get("local_clean_room_install_probe_ready") is True
    required_sections_ready = all(section["local_contract_ready"] for section in sections if section["required"])
    proof_ready = (
        v540_dependency.get("private_beta_onboarding_contract_ready") is True
        and environment_contract.get("environment_contract_ready") is True
        and required_sections_ready
        and completeness.get("report_completeness_ready") is True
        and local_probe_requirement_ready
    )
    audit = {
        "version": "v5.41",
        "phase": "clean_room_install_report_contract",
        "overall_status": "clean_room_install_report_contract_ready_external_not_claimed" if proof_ready else "clean_room_install_report_contract_incomplete",
        "active_phase": "biosdk_clean_room_install_reporting_proof",
        "bic_os_phase_locked": True,
        "clean_room_install_report_contract_ready": proof_ready,
        "v540_dependency_ready": v540_dependency.get("private_beta_onboarding_contract_ready") is True,
        "environment_contract_ready": environment_contract.get("environment_contract_ready") is True,
        "report_sections_ready": required_sections_ready,
        "report_completeness_ready": completeness.get("report_completeness_ready") is True,
        "local_install_probe_attempted": run_local_install_probe,
        "local_install_probe_required_for_gate": require_local_install_probe,
        "local_clean_room_install_probe_ready": local_probe.get("local_clean_room_install_probe_ready") is True,
        "external_clean_room_report_ready": False,
        "production_distribution_ready": False,
        "production_runtime_ready": False,
        "production_api_ready": False,
        "production_biocompute_runtime_ready": False,
        "full_biosdk_ready": False,
        "live_actuation_enabled": False,
        "environment_contract": environment_contract,
        "report_sections": sections,
        "local_install_probe": local_probe,
        "clean_room_report_fixture": report_fixture,
        "report_completeness": completeness,
        "v540_dependency_summary": {key: value for key, value in v540_dependency.items() if key not in {"program_contract", "onboarding_artifacts", "release_operations_contract", "participant_decision_matrix", "v539_dependency_summary"}},
        "missing_real_inputs": [
            "independent clean-room machine or CI runner",
            "signed tester identity or automated attestation",
            "approved private artifact handoff channel",
            "full command transcript from a fresh environment",
            "network isolation/dependency cache evidence",
            "external beta participant approval records",
        ],
        "remaining_runtime_blockers": [
            "production identity provider integration and persistent tenant membership",
            "production object storage and audit retention backend",
            "hosted dashboard server and browser session enforcement",
            "real external read-only API credentials or partner exports",
            "lab-approved live telemetry and closed-loop approval workflow",
        ],
        "direct_answer": {
            "did_we_add_clean_room_report_contract": "yes" if proof_ready else "not_yet",
            "did_we_run_local_install_probe": "yes" if local_probe.get("local_clean_room_install_probe_ready") else "no",
            "is_external_clean_room_report_ready": "no",
            "is_external_beta_ready": "no",
            "is_full_biosdk_ready": "no",
            "is_biocompute_runtime_ready": "no",
            "is_bic_os_ready": "no",
            "next_best_build_step": "add signed artifact/provenance contract proof" if proof_ready else "fix v5.41 clean-room report blockers first",
        },
        "claim_boundary": "v5.41 proves a local clean-room install reporting contract and, when enabled, a local isolated-target install probe over the v5.40 onboarding contract. It does not claim an independent external clean-room report, external beta launch, published distribution, full BioSDK, production BioCompute Runtime or BiC OS readiness.",
    }
    audit["clean_room_audit_sha256"] = stable_hash({key: value for key, value in audit.items() if key != "clean_room_audit_sha256"})
    return audit


def write_clean_room_install_report_outputs_v541(audit: dict[str, Any], out_dir: str | Path = DEFAULT_OUT) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary_json": out / "V541_CLEAN_ROOM_INSTALL_REPORT_SUMMARY.json",
        "environment_contract_json": out / "V541_CLEAN_ROOM_ENVIRONMENT_CONTRACT.json",
        "report_sections_json": out / "V541_CLEAN_ROOM_REPORT_SECTIONS.json",
        "local_probe_json": out / "V541_LOCAL_CLEAN_ROOM_INSTALL_PROBE.json",
        "report_fixture_json": out / "V541_CLEAN_ROOM_REPORT_FIXTURE.json",
        "completeness_json": out / "V541_CLEAN_ROOM_REPORT_COMPLETENESS.json",
        "sections_csv": out / "V541_CLEAN_ROOM_REPORT_SECTIONS.csv",
        "markdown_report": out / "BIOGPU_V541_CLEAN_ROOM_INSTALL_REPORT.md",
    }
    summary = {key: value for key, value in audit.items() if key not in {"environment_contract", "report_sections", "local_install_probe", "clean_room_report_fixture", "report_completeness"}}
    paths["summary_json"].write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["environment_contract_json"].write_text(json.dumps(audit["environment_contract"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["report_sections_json"].write_text(json.dumps(audit["report_sections"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["local_probe_json"].write_text(json.dumps(audit["local_install_probe"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["report_fixture_json"].write_text(json.dumps(audit["clean_room_report_fixture"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["completeness_json"].write_text(json.dumps(audit["report_completeness"], indent=2, ensure_ascii=False), encoding="utf-8")
    _write_report_sections_csv(paths["sections_csv"], audit["report_sections"])
    paths["markdown_report"].write_text(_markdown_report(audit), encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}


def _write_report_sections_csv(path: Path, sections: list[dict[str, Any]]) -> None:
    fieldnames = ["section_name", "purpose", "required", "local_contract_ready", "external_evidence_required", "production_ready"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for section in sections:
            writer.writerow({field: section.get(field) for field in fieldnames})


def _markdown_report(audit: dict[str, Any]) -> str:
    answer = audit["direct_answer"]
    lines = [
        "# BioGPU-Core v5.41 Clean-Room Install Report Contract",
        "",
        "## Direct Answer",
        "",
        f"- Clean-room report contract added: `{answer['did_we_add_clean_room_report_contract']}`",
        f"- Local install probe run: `{answer['did_we_run_local_install_probe']}`",
        f"- External clean-room report ready: `{answer['is_external_clean_room_report_ready']}`",
        f"- External beta ready: `{answer['is_external_beta_ready']}`",
        f"- Full BioSDK ready: `{answer['is_full_biosdk_ready']}`",
        f"- BioCompute Runtime ready: `{answer['is_biocompute_runtime_ready']}`",
        f"- BiC OS ready: `{answer['is_bic_os_ready']}`",
        f"- Next best build step: {answer['next_best_build_step']}",
        "",
        "## Proof Summary",
        "",
        f"- Overall status: `{audit['overall_status']}`",
        f"- v5.40 dependency ready: `{audit['v540_dependency_ready']}`",
        f"- Environment contract ready: `{audit['environment_contract_ready']}`",
        f"- Report sections ready: `{audit['report_sections_ready']}`",
        f"- Report completeness ready: `{audit['report_completeness_ready']}`",
        f"- Local install probe ready: `{audit['local_clean_room_install_probe_ready']}`",
        "",
        "## Missing Real Inputs",
        "",
    ]
    for missing in audit["missing_real_inputs"]:
        lines.append(f"- {missing}")
    lines.extend(["", "## Boundary", "", audit["claim_boundary"], ""])
    return "\n".join(lines)