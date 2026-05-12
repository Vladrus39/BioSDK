from __future__ import annotations

import json
from pathlib import Path

from biogpu.benchmarks.biogpu_v523_user_upload_fixture import run
from biogpu.sdk.user_upload_fixture_v523 import build_safe_user_upload_fixture_payload_v523, run_user_upload_fixture_workflow_v523, write_safe_user_upload_fixture_v523, write_user_upload_fixture_outputs_v523
from biogpu.sdk.vendor_upload_v519 import validate_vendor_upload_sample_v519


def _write_json(root: Path, relative_path: str, payload: dict) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _write_text(root: Path, relative_path: str, content: str = "ok") -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_public_artifacts(root: Path) -> None:
    for relative_path in (
        "examples/biosdk_v513_minimal_flow.py",
        "examples/biosdk_v516_dandi_task_benchmark.py",
        "examples/biosdk_v517_external_readonly_gate.py",
        "examples/biosdk_v519_vendor_user_upload_gate.py",
        "examples/biosdk_v520_allen_orientation_benchmark.py",
        "examples/biosdk_v521_cross_dataset_evidence.py",
        "examples/biosdk_v522_public_examples.py",
    ):
        _write_text(root, relative_path)
    _write_json(root, "outputs/v513_biosdk_core_api/V513_BIOSDK_CORE_API_SUMMARY.json", {"overall_status": "biosdk_core_api_active_bic_os_locked"})
    _write_json(root, "outputs/v514_sample_acquisition_gate/V514_SAMPLE_ACQUISITION_SUMMARY.json", {"full_sample_proof_ready": False, "missing_required_sample_ids": ["external_readonly_api_or_export_sample", "vendor_or_user_upload_sample"]})
    _write_json(root, "outputs/v56_raw_hdf5_structure/V56_RAW_HDF5_STRUCTURE_SUMMARY.json", {"overall_status": "raw_hdf5_events_available", "files_with_events": 22})
    _write_json(root, "outputs/v58_raw_native_benchmark/V58_RAW_NATIVE_FEATURE_SUMMARY.json", {"overall_status": "raw_native_features_available", "feature_row_count": 352, "feature_count": 236})
    _write_json(root, "outputs/v59_raw_native_stability_audit/V59_RAW_NATIVE_STABILITY_SUMMARY.json", {"split_half_repeatability_status": "split_half_repeatability_available", "split_half_cosine_median": 0.9999, "target_readout_signal_status": "not_supported"})
    _write_json(root, "outputs/v515_dandi_nwb_task_validation/V515_DANDI_NWB_TASK_VALIDATION_SUMMARY.json", {"overall_status": "dandi_nwb_task_sample_validated", "total_exported_window_count": 135, "total_unit_count": 5})
    _write_json(root, "outputs/v516_dandi_nwb_task_benchmark/V516_DANDI_NWB_TASK_BENCHMARK_SUMMARY.json", {"overall_status": "dandi_nwb_sdk_task_benchmark_available", "sample_count": 135, "unit_count": 5, "feature_count": 10, "observed": {"balanced_accuracy": 0.49}, "label_shuffle_baseline": {"balanced_accuracy_median": 0.33, "p_value_balanced_accuracy_gt_shuffle": 0.01}})
    _write_json(root, "outputs/v518_allen_orientation_gate/V518_ALLEN_ORIENTATION_GATE_SUMMARY.json", {"overall_status": "allen_orientation_sample_validated", "validated_sample_count": 1})
    _write_json(root, "outputs/v520_allen_orientation_benchmark/V520_ALLEN_ORIENTATION_BENCHMARK_SUMMARY.json", {"overall_status": "allen_orientation_sdk_benchmark_available", "sample_count": 598, "selected_unit_count": 64, "feature_count": 128, "observed": {"balanced_accuracy": 0.39}, "label_shuffle_baseline": {"balanced_accuracy_median": 0.12, "p_value_balanced_accuracy_gt_shuffle": 0.01}})
    _write_json(root, "outputs/v517_external_readonly_api_gate/V517_EXTERNAL_READONLY_API_SUMMARY.json", {"overall_status": "mock_readonly_contract_passed_real_external_required", "all_mock_contracts_passed": True, "real_external_ready": False, "real_export_file_count": 0})
    _write_json(root, "outputs/v519_vendor_user_upload_gate/V519_VENDOR_USER_UPLOAD_GATE_SUMMARY.json", {"overall_status": "vendor_user_upload_sample_missing_required", "validated_sample_count": 0})
    _write_json(root, "outputs/v521_cross_dataset_evidence_pack/V521_CROSS_DATASET_EVIDENCE_SUMMARY.json", {"overall_status": "cross_dataset_public_evidence_ready_external_vendor_blocked", "public_cross_dataset_evidence_ready": True})


def test_v523_payload_is_safe_and_traceable(tmp_path):
    _write_public_artifacts(tmp_path)

    payload = build_safe_user_upload_fixture_payload_v523(tmp_path)

    text = json.dumps(payload, sort_keys=True)
    assert "voltage" not in text
    assert payload["mode"] == "read_only_replay"
    assert payload["origin"]["source_versions"] == ["v5.16", "v5.20", "v5.21"]


def test_v523_written_fixture_validates_with_v519(tmp_path):
    _write_public_artifacts(tmp_path)

    fixture = write_safe_user_upload_fixture_v523(tmp_path)
    report = validate_vendor_upload_sample_v519(fixture, tmp_path)["report"]

    assert report["gate_status"] == "readonly_sample_validated"
    assert report["sample_family"] == "user_upload"
    assert report["safety_scan_passed"] is True
    assert report["forbidden_terms"] == ()


def test_v523_workflow_closes_user_upload_not_external(tmp_path):
    _write_public_artifacts(tmp_path)

    audit = run_user_upload_fixture_workflow_v523(tmp_path)

    assert audit["overall_status"] == "safe_user_upload_fixture_validated_external_api_still_blocked"
    assert audit["user_upload_validated"] is True
    assert audit["vendor_user_evidence_ready"] is True
    assert audit["external_partner_evidence_ready"] is False
    assert audit["full_sample_proof_ready"] is False


def test_v523_write_outputs(tmp_path):
    _write_public_artifacts(tmp_path)
    audit = run_user_upload_fixture_workflow_v523(tmp_path)

    paths = write_user_upload_fixture_outputs_v523(audit, tmp_path / "out")

    assert Path(paths["summary_json"]).exists()
    assert Path(paths["workflow_json"]).exists()
    assert "Safe User-Upload Fixture" in Path(paths["markdown_report"]).read_text(encoding="utf-8")


def test_v523_runner_writes_summary(tmp_path):
    _write_public_artifacts(tmp_path)

    result = run(root=tmp_path, out_dir=tmp_path / "out")

    assert result["summary"]["user_upload_validated"] is True
    assert (tmp_path / "out" / "V523_USER_UPLOAD_FIXTURE_SUMMARY.json").exists()
