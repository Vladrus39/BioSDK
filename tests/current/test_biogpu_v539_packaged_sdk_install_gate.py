from __future__ import annotations

from pathlib import Path

from biogpu.benchmarks.biogpu_v539_packaged_sdk_install_gate import run
from biogpu.sdk.package_install_gate_v539 import (
    build_distribution_manifest_v539,
    build_package_metadata_contract_v539,
    discover_packages_v539,
    run_packaged_sdk_install_gate_workflow_v539,
    validate_entrypoint_contracts_v539,
    write_packaged_sdk_install_gate_outputs_v539,
)


def test_v539_package_metadata_contract_is_ready():
    contract = build_package_metadata_contract_v539(Path.cwd())

    assert contract["package_metadata_contract_ready"] is True
    assert contract["metadata"]["name"] == "biogpu-core"
    assert contract["metadata"]["script_count"] >= 35
    assert contract["metadata"]["full_biosdk_ready"] is False


def test_v539_package_discovery_and_entrypoints_are_ready():
    packages = discover_packages_v539(Path.cwd())
    entrypoints = validate_entrypoint_contracts_v539(Path.cwd())

    assert packages["package_discovery_ready"] is True
    assert packages["package_count"] >= 10
    assert entrypoints["entrypoint_contract_ready"] is True
    assert entrypoints["missing_critical_entrypoints"] == []


def test_v539_distribution_manifest_keeps_full_biosdk_locked():
    metadata = build_package_metadata_contract_v539(Path.cwd())
    packages = discover_packages_v539(Path.cwd())
    entrypoints = validate_entrypoint_contracts_v539(Path.cwd())
    manifest = build_distribution_manifest_v539(Path.cwd(), metadata, packages, entrypoints, {"overall_status": "storage_retention_contract_proof_ready_runtime_not_claimed", "storage_retention_contract_ready": True})

    assert manifest["expected_wheel_name"] == "biogpu_core-5.0.0-py3-none-any.whl"
    assert len(manifest["manifest_sha256"]) == 64
    assert manifest["full_biosdk_ready"] is False


def test_v539_workflow_ready_without_claiming_full_sdk(tmp_path):
    audit = run_packaged_sdk_install_gate_workflow_v539(Path.cwd(), tmp_path / "out", build_distribution=False, require_wheel_build=False)

    assert audit["overall_status"] == "packaged_sdk_install_gate_ready_full_sdk_not_claimed"
    assert audit["packaged_sdk_install_gate_ready"] is True
    assert audit["package_metadata_contract_ready"] is True
    assert audit["entrypoint_contract_ready"] is True
    assert audit["local_wheel_build_ready"] is False
    assert audit["full_biosdk_ready"] is False
    assert audit["production_biocompute_runtime_ready"] is False
    assert audit["bic_os_phase_locked"] is True


def test_v539_outputs_are_written(tmp_path):
    audit = run_packaged_sdk_install_gate_workflow_v539(Path.cwd(), tmp_path / "workflow", build_distribution=False, require_wheel_build=False)

    paths = write_packaged_sdk_install_gate_outputs_v539(audit, tmp_path / "out")
    assert Path(paths["summary_json"]).exists()
    assert Path(paths["metadata_json"]).exists()
    assert Path(paths["packages_json"]).exists()
    assert Path(paths["entrypoints_json"]).exists()
    assert Path(paths["distribution_manifest_json"]).exists()
    assert Path(paths["entrypoints_csv"]).exists()
    assert "Packaged SDK Install Gate" in Path(paths["markdown_report"]).read_text(encoding="utf-8")


def test_v539_runner_writes_summary(tmp_path):
    result = run(root=Path.cwd(), out_dir=tmp_path / "out", build_distribution=False, require_wheel_build=False)

    assert result["summary"]["packaged_sdk_install_gate_ready"] is True
    assert (tmp_path / "out" / "V539_PACKAGED_SDK_INSTALL_GATE_SUMMARY.json").exists()


def test_v539_reports_missing_real_distribution_inputs(tmp_path):
    audit = run_packaged_sdk_install_gate_workflow_v539(Path.cwd(), tmp_path / "out", build_distribution=False, require_wheel_build=False)

    assert audit["direct_answer"]["is_full_biosdk_ready"] == "no"
    assert len(audit["missing_real_inputs"]) >= 5