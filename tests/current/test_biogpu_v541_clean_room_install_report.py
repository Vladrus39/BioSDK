from __future__ import annotations

from pathlib import Path

from biogpu.benchmarks.biogpu_v541_clean_room_install_report import run
from biogpu.sdk.clean_room_install_report_v541 import (
    build_clean_room_environment_contract_v541,
    build_clean_room_report_fixture_v541,
    build_clean_room_report_sections_v541,
    run_clean_room_install_report_workflow_v541,
    validate_clean_room_report_completeness_v541,
    write_clean_room_install_report_outputs_v541,
)


def test_v541_environment_contract_is_local_only():
    contract = build_clean_room_environment_contract_v541(Path.cwd())

    assert contract["environment_contract_ready"] is True
    assert contract["contract"]["network_required_for_install"] is False
    assert contract["contract"]["global_site_packages_allowed"] is False
    assert contract["external_clean_room_report_ready"] is False
    assert contract["full_biosdk_ready"] is False


def test_v541_report_sections_require_external_evidence_without_claiming_it():
    sections = build_clean_room_report_sections_v541()
    required = [section for section in sections if section["required"]]
    external_required = [section for section in sections if section["external_evidence_required"]]

    assert len(required) == 7
    assert len(external_required) >= 5
    assert all(section["local_contract_ready"] for section in required)
    assert not any(section["production_ready"] for section in sections)


def test_v541_report_fixture_completeness_keeps_external_report_false():
    sections = build_clean_room_report_sections_v541()
    report = build_clean_room_report_fixture_v541()
    completeness = validate_clean_room_report_completeness_v541(report, sections)

    assert completeness["report_completeness_ready"] is True
    assert report["external_clean_room_report_ready"] is False
    assert report["live_actuation_enabled"] is False
    assert len(report["report_sha256"]) == 64


def test_v541_workflow_ready_without_local_probe_when_not_required(tmp_path):
    audit = run_clean_room_install_report_workflow_v541(Path.cwd(), tmp_path / "out", run_local_install_probe=False, require_local_install_probe=False)

    assert audit["overall_status"] == "clean_room_install_report_contract_ready_external_not_claimed"
    assert audit["clean_room_install_report_contract_ready"] is True
    assert audit["v540_dependency_ready"] is True
    assert audit["report_completeness_ready"] is True
    assert audit["local_clean_room_install_probe_ready"] is False
    assert audit["external_clean_room_report_ready"] is False
    assert audit["full_biosdk_ready"] is False
    assert audit["bic_os_phase_locked"] is True


def test_v541_workflow_requires_probe_when_requested(tmp_path):
    audit = run_clean_room_install_report_workflow_v541(Path.cwd(), tmp_path / "out", run_local_install_probe=False, require_local_install_probe=True)

    assert audit["clean_room_install_report_contract_ready"] is False
    assert audit["overall_status"] == "clean_room_install_report_contract_incomplete"
    assert audit["local_install_probe_required_for_gate"] is True


def test_v541_outputs_are_written(tmp_path):
    audit = run_clean_room_install_report_workflow_v541(Path.cwd(), tmp_path / "workflow", run_local_install_probe=False, require_local_install_probe=False)
    paths = write_clean_room_install_report_outputs_v541(audit, tmp_path / "out")

    assert Path(paths["summary_json"]).exists()
    assert Path(paths["environment_contract_json"]).exists()
    assert Path(paths["report_sections_json"]).exists()
    assert Path(paths["local_probe_json"]).exists()
    assert Path(paths["report_fixture_json"]).exists()
    assert Path(paths["completeness_json"]).exists()
    assert Path(paths["sections_csv"]).exists()
    assert "Clean-Room Install Report Contract" in Path(paths["markdown_report"]).read_text(encoding="utf-8")


def test_v541_runner_writes_summary(tmp_path):
    result = run(root=Path.cwd(), out_dir=tmp_path / "out", run_local_install_probe=False, require_local_install_probe=False)

    assert result["summary"]["clean_room_install_report_contract_ready"] is True
    assert (tmp_path / "out" / "V541_CLEAN_ROOM_INSTALL_REPORT_SUMMARY.json").exists()