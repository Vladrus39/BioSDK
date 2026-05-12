"""Packaged SDK distribution and install gate proof, v5.39."""
from __future__ import annotations

import csv
import importlib
import json
import os
import subprocess
import sys
import tomllib
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from biogpu.beta.job_model_v43 import utc_now_iso
from biogpu.evidence.ledger_v53 import stable_hash
from biogpu.runtime.storage_retention_v538 import run_storage_retention_contract_workflow_v538


DEFAULT_OUT = Path("outputs/v539_packaged_sdk_install_gate")
CRITICAL_ENTRYPOINTS_V539 = (
    "biogpu-v525-biosdk-release-candidate-evidence",
    "biogpu-v538-storage-retention-contract",
    "biogpu-v539-packaged-sdk-install-gate",
)


@dataclass(frozen=True)
class PackageMetadataContractV539:
    name: str
    version: str
    requires_python: str
    dependency_count: int
    script_count: int
    package_include: tuple[str, ...]
    build_backend: str
    local_contract_only: bool = True
    production_distribution_ready: bool = False
    full_biosdk_ready: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class EntryPointProbeV539:
    script_name: str
    target: str
    module_name: str
    function_name: str
    importable: bool
    callable_target: bool
    errors: tuple[str, ...]
    production_distribution_ready: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_pyproject_v539(root: str | Path) -> dict[str, Any]:
    path = Path(root) / "pyproject.toml"
    return tomllib.loads(path.read_text(encoding="utf-8"))


def build_package_metadata_contract_v539(root: str | Path) -> dict[str, Any]:
    pyproject = load_pyproject_v539(root)
    project = dict(pyproject.get("project") or {})
    build_system = dict(pyproject.get("build-system") or {})
    scripts = dict(project.get("scripts") or {})
    package_include = tuple(pyproject.get("tool", {}).get("setuptools", {}).get("packages", {}).get("find", {}).get("include", []))
    contract = PackageMetadataContractV539(
        name=str(project.get("name", "")),
        version=str(project.get("version", "")),
        requires_python=str(project.get("requires-python", "")),
        dependency_count=len(project.get("dependencies") or []),
        script_count=len(scripts),
        package_include=package_include,
        build_backend=str(build_system.get("build-backend", "")),
    )
    errors: list[str] = []
    if contract.name != "biogpu-core":
        errors.append("unexpected_project_name")
    if not contract.version:
        errors.append("missing_project_version")
    if not contract.requires_python.startswith(">=3."):
        errors.append("missing_python_requirement")
    if contract.dependency_count < 5:
        errors.append("dependency_contract_too_small")
    if contract.script_count < 35:
        errors.append("script_entrypoint_count_too_small")
    if "biogpu*" not in contract.package_include:
        errors.append("setuptools_package_include_missing")
    if contract.build_backend != "setuptools.build_meta":
        errors.append("unexpected_build_backend")
    return {
        "version": "v5.39",
        "package_metadata_contract_ready": not errors,
        "metadata": contract.to_dict(),
        "errors": errors,
        "production_distribution_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }


def discover_packages_v539(root: str | Path) -> dict[str, Any]:
    root_path = Path(root)
    package_root = root_path / "biogpu"
    package_names: list[str] = []
    for init_file in package_root.rglob("__init__.py"):
        package_dir = init_file.parent
        package_names.append(".".join(package_dir.relative_to(root_path).parts))
    package_names = sorted(package_names)
    return {
        "version": "v5.39",
        "package_discovery_ready": "biogpu" in package_names and len(package_names) >= 10,
        "package_count": len(package_names),
        "packages": package_names,
        "production_distribution_ready": False,
        "bic_os_phase_locked": True,
    }


def parse_entrypoint_target_v539(target: str) -> tuple[str, str]:
    if ":" not in target:
        return target, ""
    module_name, function_name = target.split(":", 1)
    return module_name.strip(), function_name.strip()


def validate_entrypoint_contracts_v539(root: str | Path, critical_entrypoints: tuple[str, ...] = CRITICAL_ENTRYPOINTS_V539) -> dict[str, Any]:
    pyproject = load_pyproject_v539(root)
    scripts = dict(pyproject.get("project", {}).get("scripts") or {})
    malformed = [name for name, target in scripts.items() if ":" not in str(target)]
    missing_critical = [name for name in critical_entrypoints if name not in scripts]
    probes: list[dict[str, Any]] = []
    for script_name in critical_entrypoints:
        target = str(scripts.get(script_name, ""))
        module_name, function_name = parse_entrypoint_target_v539(target)
        errors: list[str] = []
        module = None
        if not target:
            errors.append("missing_script")
        try:
            module = importlib.import_module(module_name) if module_name else None
        except Exception as exc:
            errors.append(f"import_error:{type(exc).__name__}:{exc}")
        callable_target = False
        if module is not None and function_name:
            callable_target = callable(getattr(module, function_name, None))
            if not callable_target:
                errors.append("target_not_callable")
        elif module is not None:
            errors.append("missing_function_name")
        probes.append(EntryPointProbeV539(script_name, target, module_name, function_name, module is not None, callable_target, tuple(errors)).to_dict())
    ready = not malformed and not missing_critical and all(probe["importable"] and probe["callable_target"] for probe in probes)
    return {
        "version": "v5.39",
        "entrypoint_contract_ready": ready,
        "script_count": len(scripts),
        "malformed_entrypoints": malformed,
        "missing_critical_entrypoints": missing_critical,
        "critical_entrypoint_probes": probes,
        "production_distribution_ready": False,
        "bic_os_phase_locked": True,
    }


def build_distribution_manifest_v539(root: str | Path, metadata_contract: dict[str, Any], package_discovery: dict[str, Any], entrypoints: dict[str, Any], v538_summary: dict[str, Any]) -> dict[str, Any]:
    metadata = dict(metadata_contract.get("metadata") or {})
    package_name = str(metadata.get("name", "biogpu-core")).replace("-", "_")
    version = str(metadata.get("version", "0.0.0"))
    expected_wheel = f"{package_name}-{version}-py3-none-any.whl"
    manifest = {
        "version": "v5.39",
        "created_at": utc_now_iso(),
        "project_name": metadata.get("name"),
        "project_version": metadata.get("version"),
        "expected_wheel_name": expected_wheel,
        "build_backend": metadata.get("build_backend"),
        "package_count": package_discovery.get("package_count"),
        "script_count": entrypoints.get("script_count"),
        "critical_entrypoints": list(CRITICAL_ENTRYPOINTS_V539),
        "v538_dependency_status": v538_summary.get("overall_status"),
        "v538_storage_contract_ready": v538_summary.get("storage_retention_contract_ready"),
        "source_tree_sha256": stable_hash({
            "pyproject": load_pyproject_v539(root),
            "packages": package_discovery.get("packages"),
            "critical_entrypoints": entrypoints.get("critical_entrypoint_probes"),
        }),
        "local_contract_only": True,
        "production_distribution_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    manifest["manifest_sha256"] = stable_hash(manifest)
    return manifest


def build_and_install_wheel_v539(root: str | Path, out_dir: str | Path, timeout_seconds: int = 240) -> dict[str, Any]:
    root_path = Path(root).resolve()
    out = Path(out_dir)
    dist_dir = out / "dist"
    install_dir = out / "install_target"
    dist_dir.mkdir(parents=True, exist_ok=True)
    install_dir.mkdir(parents=True, exist_ok=True)
    build_cmd = [sys.executable, "-m", "pip", "wheel", ".", "--no-deps", "--no-build-isolation", "--wheel-dir", str(dist_dir)]
    build = subprocess.run(build_cmd, cwd=root_path, text=True, capture_output=True, timeout=timeout_seconds)
    wheel_files = sorted(dist_dir.glob("*.whl"))
    wheel_path = wheel_files[-1] if wheel_files else None
    install_ready = False
    smoke_ready = False
    install_returncode: int | None = None
    smoke_returncode: int | None = None
    install_stdout = ""
    install_stderr = ""
    smoke_stdout = ""
    smoke_stderr = ""
    if wheel_path is not None and build.returncode == 0:
        install_cmd = [sys.executable, "-m", "pip", "install", "--no-deps", "--force-reinstall", "--target", str(install_dir), str(wheel_path)]
        install = subprocess.run(install_cmd, cwd=out, text=True, capture_output=True, timeout=timeout_seconds)
        install_returncode = install.returncode
        install_stdout = install.stdout[-4000:]
        install_stderr = install.stderr[-4000:]
        install_ready = install.returncode == 0
        if install_ready:
            smoke_code = "import importlib; mods=['biogpu','biogpu.sdk.package_install_gate_v539','biogpu.runtime.storage_retention_v538']; [importlib.import_module(m) for m in mods]; print('v539_install_smoke_ok')"
            env = dict(os.environ)
            env["PYTHONPATH"] = str(install_dir)
            smoke = subprocess.run([sys.executable, "-c", smoke_code], cwd=out, text=True, capture_output=True, timeout=timeout_seconds, env=env)
            smoke_returncode = smoke.returncode
            smoke_stdout = smoke.stdout[-4000:]
            smoke_stderr = smoke.stderr[-4000:]
            smoke_ready = smoke.returncode == 0 and "v539_install_smoke_ok" in smoke.stdout
    wheel_manifest = inspect_wheel_artifact_v539(wheel_path) if wheel_path is not None else {"wheel_inspection_ready": False, "errors": ["wheel_not_found"]}
    return {
        "version": "v5.39",
        "build_distribution_attempted": True,
        "build_command": " ".join(build_cmd),
        "build_returncode": build.returncode,
        "build_stdout_tail": build.stdout[-4000:],
        "build_stderr_tail": build.stderr[-4000:],
        "wheel_path": str(wheel_path).replace("\\", "/") if wheel_path else None,
        "local_wheel_build_ready": build.returncode == 0 and wheel_path is not None and wheel_manifest.get("wheel_inspection_ready") is True,
        "install_returncode": install_returncode,
        "install_stdout_tail": install_stdout,
        "install_stderr_tail": install_stderr,
        "local_install_ready": install_ready,
        "install_smoke_returncode": smoke_returncode,
        "install_smoke_stdout_tail": smoke_stdout,
        "install_smoke_stderr_tail": smoke_stderr,
        "local_install_smoke_ready": smoke_ready,
        "wheel_manifest": wheel_manifest,
        "production_distribution_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }


def inspect_wheel_artifact_v539(wheel_path: Path | None) -> dict[str, Any]:
    if wheel_path is None or not wheel_path.exists():
        return {"version": "v5.39", "wheel_inspection_ready": False, "errors": ["wheel_missing"], "production_distribution_ready": False}
    errors: list[str] = []
    names: list[str] = []
    with zipfile.ZipFile(wheel_path, "r") as archive:
        names = archive.namelist()
    if not any(name.endswith(".dist-info/METADATA") for name in names):
        errors.append("metadata_missing")
    if not any(name.endswith(".dist-info/entry_points.txt") for name in names):
        errors.append("entry_points_missing")
    if not any(name == "biogpu/__init__.py" for name in names):
        errors.append("biogpu_package_missing")
    if not any(name.endswith("package_install_gate_v539.py") for name in names):
        errors.append("v539_module_missing")
    return {
        "version": "v5.39",
        "wheel_inspection_ready": not errors,
        "wheel_name": wheel_path.name,
        "wheel_size_bytes": wheel_path.stat().st_size,
        "wheel_sha256": _file_sha256(wheel_path),
        "file_count": len(names),
        "errors": errors,
        "production_distribution_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }


def _file_sha256(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_package_install_audit_bundle_v539(audit: dict[str, Any], out_dir: str | Path) -> dict[str, Any]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    bundle = {
        "version": "v5.39",
        "created_at": utc_now_iso(),
        "package_metadata_contract_ready": audit.get("package_metadata_contract_ready"),
        "package_discovery_ready": audit.get("package_discovery_ready"),
        "entrypoint_contract_ready": audit.get("entrypoint_contract_ready"),
        "local_wheel_build_ready": audit.get("local_wheel_build_ready"),
        "local_install_smoke_ready": audit.get("local_install_smoke_ready"),
        "v538_dependency_status": audit.get("v538_dependency_summary", {}).get("overall_status"),
        "production_distribution_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }
    bundle_hash = stable_hash(bundle)
    bundle["bundle_sha256"] = bundle_hash
    path = out / "V539_PACKAGE_INSTALL_AUDIT_BUNDLE.json"
    path.write_text(json.dumps(bundle, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"bundle_path": str(path).replace("\\", "/"), "bundle_sha256": bundle_hash, "bundle_ready": path.exists() and len(bundle_hash) == 64, "bundle": bundle}


def run_packaged_sdk_install_gate_workflow_v539(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT, build_distribution: bool = False, require_wheel_build: bool = False) -> dict[str, Any]:
    project_root = Path(root).resolve()
    out = project_root / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    v538_dependency = run_storage_retention_contract_workflow_v538(project_root, out / "d538")
    metadata_contract = build_package_metadata_contract_v539(project_root)
    package_discovery = discover_packages_v539(project_root)
    entrypoints = validate_entrypoint_contracts_v539(project_root)
    distribution_manifest = build_distribution_manifest_v539(project_root, metadata_contract, package_discovery, entrypoints, v538_dependency)
    build_result = {"build_distribution_attempted": False, "local_wheel_build_ready": False, "local_install_ready": False, "local_install_smoke_ready": False, "wheel_manifest": {"wheel_inspection_ready": False}}
    if build_distribution:
        build_result = build_and_install_wheel_v539(project_root, out)
    build_requirement_ready = (not require_wheel_build) or (build_result.get("local_wheel_build_ready") is True and build_result.get("local_install_smoke_ready") is True)
    proof_ready = (
        v538_dependency.get("storage_retention_contract_ready") is True
        and metadata_contract.get("package_metadata_contract_ready") is True
        and package_discovery.get("package_discovery_ready") is True
        and entrypoints.get("entrypoint_contract_ready") is True
        and build_requirement_ready
    )
    audit = {
        "version": "v5.39",
        "phase": "packaged_sdk_install_gate",
        "overall_status": "packaged_sdk_install_gate_ready_full_sdk_not_claimed" if proof_ready else "packaged_sdk_install_gate_incomplete",
        "active_phase": "biosdk_packaging_install_gate_proof",
        "bic_os_phase_locked": True,
        "packaged_sdk_install_gate_ready": proof_ready,
        "package_metadata_contract_ready": metadata_contract.get("package_metadata_contract_ready") is True,
        "package_discovery_ready": package_discovery.get("package_discovery_ready") is True,
        "entrypoint_contract_ready": entrypoints.get("entrypoint_contract_ready") is True,
        "local_wheel_build_ready": build_result.get("local_wheel_build_ready") is True,
        "local_install_ready": build_result.get("local_install_ready") is True,
        "local_install_smoke_ready": build_result.get("local_install_smoke_ready") is True,
        "build_distribution_attempted": build_distribution,
        "wheel_build_required_for_gate": require_wheel_build,
        "v538_dependency_ready": v538_dependency.get("storage_retention_contract_ready") is True,
        "package_count": package_discovery.get("package_count"),
        "script_count": entrypoints.get("script_count"),
        "production_distribution_ready": False,
        "production_runtime_ready": False,
        "production_api_ready": False,
        "production_biocompute_runtime_ready": False,
        "full_biosdk_ready": False,
        "live_actuation_enabled": False,
        "package_metadata_contract": metadata_contract,
        "package_discovery": package_discovery,
        "entrypoint_contracts": entrypoints,
        "distribution_manifest": distribution_manifest,
        "local_build_install_result": build_result,
        "v538_dependency_summary": {key: value for key, value in v538_dependency.items() if key not in {"bucket_contracts", "object_manifest", "storage_integrity", "local_access_contract", "immutable_overwrite_probe", "v537_dependency_summary"}},
        "missing_real_inputs": [
            "published package repository or private index",
            "signed release artifact and provenance attestation",
            "clean-room install validation on a fresh machine or CI runner",
            "versioned SDK documentation site",
            "release approval process and rollback policy",
            "production support/SLA process",
        ],
        "remaining_runtime_blockers": [
            "production identity provider integration and persistent tenant membership",
            "hosted dashboard server and browser session enforcement",
            "production object storage and audit retention backend",
            "real external read-only API credentials or partner exports",
            "lab-approved live telemetry and closed-loop approval workflow",
        ],
        "direct_answer": {
            "did_we_add_installable_sdk_gate": "yes" if proof_ready else "not_yet",
            "did_we_build_local_wheel_in_gate": "yes" if build_result.get("local_wheel_build_ready") else "no",
            "is_full_biosdk_ready": "no",
            "is_biocompute_runtime_ready": "no",
            "is_bic_os_ready": "no",
            "next_best_build_step": "add private beta onboarding contract proof" if proof_ready else "fix v5.39 package install blockers first",
        },
        "claim_boundary": "v5.39 proves package metadata, package discovery, critical CLI entrypoint importability and optionally a local wheel build/install smoke over the v5.38 storage contract. It does not claim published distribution, full BioSDK, production BioCompute Runtime or BiC OS readiness.",
    }
    bundle = build_package_install_audit_bundle_v539(audit, out)
    audit["package_install_audit_bundle"] = {key: value for key, value in bundle.items() if key != "bundle"}
    audit["package_install_audit_bundle_ready"] = bundle.get("bundle_ready") is True
    return audit


def write_packaged_sdk_install_gate_outputs_v539(audit: dict[str, Any], out_dir: str | Path = DEFAULT_OUT) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary_json": out / "V539_PACKAGED_SDK_INSTALL_GATE_SUMMARY.json",
        "metadata_json": out / "V539_PACKAGE_METADATA_CONTRACT.json",
        "packages_json": out / "V539_PACKAGE_DISCOVERY.json",
        "entrypoints_json": out / "V539_ENTRYPOINT_CONTRACTS.json",
        "distribution_manifest_json": out / "V539_DISTRIBUTION_MANIFEST.json",
        "build_install_json": out / "V539_LOCAL_BUILD_INSTALL_RESULT.json",
        "entrypoints_csv": out / "V539_ENTRYPOINT_PROBES.csv",
        "markdown_report": out / "BIOGPU_V539_PACKAGED_SDK_INSTALL_GATE_REPORT.md",
    }
    summary = {key: value for key, value in audit.items() if key not in {"package_metadata_contract", "package_discovery", "entrypoint_contracts", "distribution_manifest", "local_build_install_result"}}
    paths["summary_json"].write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["metadata_json"].write_text(json.dumps(audit["package_metadata_contract"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["packages_json"].write_text(json.dumps(audit["package_discovery"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["entrypoints_json"].write_text(json.dumps(audit["entrypoint_contracts"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["distribution_manifest_json"].write_text(json.dumps(audit["distribution_manifest"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["build_install_json"].write_text(json.dumps(audit["local_build_install_result"], indent=2, ensure_ascii=False), encoding="utf-8")
    _write_entrypoint_probes_csv(paths["entrypoints_csv"], audit["entrypoint_contracts"].get("critical_entrypoint_probes", []))
    paths["markdown_report"].write_text(_markdown_report(audit), encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}


def _write_entrypoint_probes_csv(path: Path, probes: list[dict[str, Any]]) -> None:
    fieldnames = ["script_name", "target", "module_name", "function_name", "importable", "callable_target", "errors"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for probe in probes:
            row = {field: probe.get(field) for field in fieldnames}
            row["errors"] = " | ".join(str(error) for error in probe.get("errors", []))
            writer.writerow(row)


def _markdown_report(audit: dict[str, Any]) -> str:
    answer = audit["direct_answer"]
    lines = [
        "# BioGPU-Core v5.39 Packaged SDK Install Gate",
        "",
        "## Direct Answer",
        "",
        f"- Installable SDK gate added: `{answer['did_we_add_installable_sdk_gate']}`",
        f"- Local wheel built in gate: `{answer['did_we_build_local_wheel_in_gate']}`",
        f"- Full BioSDK ready: `{answer['is_full_biosdk_ready']}`",
        f"- BioCompute Runtime ready: `{answer['is_biocompute_runtime_ready']}`",
        f"- BiC OS ready: `{answer['is_bic_os_ready']}`",
        f"- Next best build step: {answer['next_best_build_step']}",
        "",
        "## Proof Summary",
        "",
        f"- Overall status: `{audit['overall_status']}`",
        f"- Package metadata contract ready: `{audit['package_metadata_contract_ready']}`",
        f"- Package discovery ready: `{audit['package_discovery_ready']}`",
        f"- Entrypoint contract ready: `{audit['entrypoint_contract_ready']}`",
        f"- Local wheel build ready: `{audit['local_wheel_build_ready']}`",
        f"- Local install smoke ready: `{audit['local_install_smoke_ready']}`",
        f"- Packages: `{audit['package_count']}`",
        f"- Scripts: `{audit['script_count']}`",
        "",
        "## Missing Real Inputs",
        "",
    ]
    for missing in audit["missing_real_inputs"]:
        lines.append(f"- {missing}")
    lines.extend(["", "## Remaining Runtime Blockers", ""])
    for blocker in audit["remaining_runtime_blockers"]:
        lines.append(f"- {blocker}")
    lines.extend(["", "## Boundary", "", audit["claim_boundary"], ""])
    return "\n".join(lines)