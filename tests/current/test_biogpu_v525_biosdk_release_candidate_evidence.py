from __future__ import annotations

import json
from pathlib import Path

from biogpu.benchmarks.biogpu_v525_biosdk_release_candidate_evidence import run
from biogpu.sdk.release_candidate_evidence_v525 import build_biosdk_release_candidate_evidence_v525, build_biosdk_release_candidate_items_v525, write_biosdk_release_candidate_evidence_outputs_v525


def _write_json(root: Path, relative_path: str, payload: dict) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _write_text(root: Path, relative_path: str, content: str = "ok") -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_supported_artifacts(root: Path) -> None:
    _write_json(root, "outputs/v512_biosdk_evidence_pack/V512_BIOSDK_EVIDENCE_PACK_SUMMARY.json", {"overall_status": "biosdk_evidence_kernel_ready_full_sdk_not_claimed", "biosdk_evidence_kernel_ready": True, "full_biosdk_ready": False})
    _write_json(root, "outputs/v513_biosdk_core_api/V513_BIOSDK_CORE_API_SUMMARY.json", {"overall_status": "biosdk_core_api_active_bic_os_locked"})
    _write_json(root, "outputs/v514_sample_acquisition_gate/V514_SAMPLE_ACQUISITION_SUMMARY.json", {"full_sample_proof_ready": True, "missing_required_sample_ids": []})
    _write_json(root, "outputs/v521_cross_dataset_evidence_pack/V521_CROSS_DATASET_EVIDENCE_SUMMARY.json", {"public_cross_dataset_evidence_ready": True, "external_partner_evidence_ready": True, "vendor_user_evidence_ready": True, "full_biosdk_ready": False})
    _write_json(root, "outputs/v522_biosdk_public_examples/V522_BIOSDK_PUBLIC_EXAMPLES_SUMMARY.json", {"public_examples_ready": True, "blocked_example_count": 0, "full_biosdk_ready": False})
    _write_json(root, "outputs/v523_user_upload_fixture/V523_USER_UPLOAD_FIXTURE_SUMMARY.json", {"user_upload_validated": True, "safety_scan_passed": True, "full_biosdk_ready": False})
    _write_json(root, "outputs/v524_external_export_validation/V524_EXTERNAL_EXPORT_VALIDATION_SUMMARY.json", {"real_external_ready": True, "validated_export_count": 1, "full_biosdk_ready": False})
    for relative_path in (
        "README.md",
        "docs/MASTER_PROJECT_PLAN_V50.md",
        "docs/EXTERNAL_EXPORT_VALIDATION_GUIDE_V524.md",
        "docs/BIOSDK_RELEASE_CANDIDATE_EVIDENCE_GUIDE_V525.md",
        "biogpu/sdk/release_candidate_evidence_v525.py",
        "biogpu/benchmarks/biogpu_v525_biosdk_release_candidate_evidence.py",
        "scripts/run_biogpu_v525_biosdk_release_candidate_evidence.ps1",
        "tests/current/test_biogpu_v525_biosdk_release_candidate_evidence.py",
        "examples/biosdk_v525_release_candidate_evidence.py",
    ):
        _write_text(root, relative_path)


def test_v525_rc_evidence_ready_but_full_biosdk_not_claimed(tmp_path):
    _write_supported_artifacts(tmp_path)

    audit = build_biosdk_release_candidate_evidence_v525(tmp_path)

    assert audit["overall_status"] == "biosdk_release_candidate_evidence_ready_full_biosdk_not_claimed"
    assert audit["biosdk_release_candidate_evidence_ready"] is True
    assert audit["ready_required_item_count"] == audit["required_item_count"]
    assert audit["full_biosdk_ready"] is False
    assert audit["bic_os_phase_locked"] is True
    assert audit["direct_answer"]["should_jump_to_bic_os_now"] == "no"


def test_v525_items_track_external_and_user_upload_layers(tmp_path):
    _write_supported_artifacts(tmp_path)

    items = {item.item_id: item for item in build_biosdk_release_candidate_items_v525(tmp_path)}

    assert items["v523_user_upload_fixture"].status == "ready"
    assert items["v524_external_export"].status == "ready"
    assert items["v525_surface"].proof_level == "runner_script_tests_example_present"


def test_v525_missing_external_export_blocks_rc_evidence(tmp_path):
    _write_supported_artifacts(tmp_path)
    (tmp_path / "outputs/v524_external_export_validation/V524_EXTERNAL_EXPORT_VALIDATION_SUMMARY.json").unlink()

    audit = build_biosdk_release_candidate_evidence_v525(tmp_path)

    assert audit["overall_status"] == "biosdk_release_candidate_evidence_incomplete"
    assert audit["biosdk_release_candidate_evidence_ready"] is False
    assert "v524_external_export" in audit["blocked_item_ids"]
    assert audit["full_biosdk_ready"] is False


def test_v525_write_outputs(tmp_path):
    _write_supported_artifacts(tmp_path)
    audit = build_biosdk_release_candidate_evidence_v525(tmp_path)

    paths = write_biosdk_release_candidate_evidence_outputs_v525(audit, tmp_path / "out")

    assert Path(paths["summary_json"]).exists()
    assert Path(paths["checklist_json"]).exists()
    assert Path(paths["checklist_csv"]).exists()
    assert Path(paths["manifest_json"]).exists()
    assert "Release-Candidate Evidence" in Path(paths["markdown_report"]).read_text(encoding="utf-8")


def test_v525_runner_writes_summary(tmp_path):
    _write_supported_artifacts(tmp_path)

    result = run(root=tmp_path, out_dir=tmp_path / "out")

    assert result["summary"]["biosdk_release_candidate_evidence_ready"] is True
    assert (tmp_path / "out" / "V525_BIOSDK_RELEASE_CANDIDATE_EVIDENCE_SUMMARY.json").exists()