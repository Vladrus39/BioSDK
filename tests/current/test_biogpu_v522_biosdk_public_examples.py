from __future__ import annotations

import json
from pathlib import Path

from biogpu.benchmarks.biogpu_v522_biosdk_public_examples import run
from biogpu.sdk.public_examples_v522 import build_biosdk_public_examples_gate_v522, build_biosdk_public_examples_v522, write_biosdk_public_examples_outputs_v522


def _write_json(root: Path, relative_path: str, payload: dict) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _write_text(root: Path, relative_path: str, content: str = "ok") -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_example_files(root: Path) -> None:
    for path in (
        "examples/biosdk_v513_minimal_flow.py",
        "examples/biosdk_v516_dandi_task_benchmark.py",
        "examples/biosdk_v520_allen_orientation_benchmark.py",
        "examples/biosdk_v521_cross_dataset_evidence.py",
        "examples/biosdk_v522_public_examples.py",
        "examples/biosdk_v517_external_readonly_gate.py",
        "examples/biosdk_v519_vendor_user_upload_gate.py",
    ):
        _write_text(root, path)


def _write_supported_artifacts(root: Path) -> None:
    _write_json(root, "outputs/v56_raw_hdf5_structure/V56_RAW_HDF5_STRUCTURE_SUMMARY.json", {"overall_status": "raw_hdf5_events_available", "files_with_events": 22})
    _write_json(root, "outputs/v58_raw_native_benchmark/V58_RAW_NATIVE_FEATURE_SUMMARY.json", {"overall_status": "raw_native_features_available", "feature_row_count": 352, "feature_count": 236})
    _write_json(root, "outputs/v59_raw_native_stability_audit/V59_RAW_NATIVE_STABILITY_SUMMARY.json", {"split_half_repeatability_status": "split_half_repeatability_available", "split_half_cosine_median": 0.9999, "target_readout_signal_status": "not_supported"})
    _write_json(root, "outputs/v515_dandi_nwb_task_validation/V515_DANDI_NWB_TASK_VALIDATION_SUMMARY.json", {"overall_status": "dandi_nwb_task_sample_validated", "total_exported_window_count": 135, "total_unit_count": 5})
    _write_json(root, "outputs/v516_dandi_nwb_task_benchmark/V516_DANDI_NWB_TASK_BENCHMARK_SUMMARY.json", {"overall_status": "dandi_nwb_sdk_task_benchmark_available", "sample_count": 135, "unit_count": 5, "feature_count": 10, "observed": {"balanced_accuracy": 0.49}, "label_shuffle_baseline": {"balanced_accuracy_median": 0.33, "p_value_balanced_accuracy_gt_shuffle": 0.01}})
    _write_json(root, "outputs/v518_allen_orientation_gate/V518_ALLEN_ORIENTATION_GATE_SUMMARY.json", {"overall_status": "allen_orientation_sample_validated", "validated_sample_count": 1})
    _write_json(root, "outputs/v520_allen_orientation_benchmark/V520_ALLEN_ORIENTATION_BENCHMARK_SUMMARY.json", {"overall_status": "allen_orientation_sdk_benchmark_available", "sample_count": 598, "selected_unit_count": 64, "feature_count": 128, "observed": {"balanced_accuracy": 0.39}, "label_shuffle_baseline": {"balanced_accuracy_median": 0.12, "p_value_balanced_accuracy_gt_shuffle": 0.01}})
    _write_json(root, "outputs/v517_external_readonly_api_gate/V517_EXTERNAL_READONLY_API_SUMMARY.json", {"overall_status": "mock_readonly_contract_passed_real_external_required", "all_mock_contracts_passed": True, "real_external_ready": False, "real_export_file_count": 0})
    _write_json(root, "outputs/v519_vendor_user_upload_gate/V519_VENDOR_USER_UPLOAD_GATE_SUMMARY.json", {"overall_status": "vendor_user_upload_sample_missing_required", "validated_sample_count": 0})
    _write_json(root, "outputs/v514_sample_acquisition_gate/V514_SAMPLE_ACQUISITION_SUMMARY.json", {"overall_status": "sample_proof_gate_ready_for_external_downloads", "missing_required_sample_ids": ["external_readonly_api_or_export_sample", "vendor_or_user_upload_sample"], "full_sample_proof_ready": False})


def test_v522_public_examples_ready_external_vendor_blocked(tmp_path):
    _write_example_files(tmp_path)
    _write_supported_artifacts(tmp_path)

    audit = build_biosdk_public_examples_gate_v522(tmp_path)

    assert audit["overall_status"] == "biosdk_public_examples_ready_external_vendor_blocked"
    assert audit["public_examples_ready"] is True
    assert audit["ready_required_public_example_count"] == audit["required_public_example_count"] == 5
    assert audit["external_partner_evidence_ready"] is False
    assert audit["vendor_user_evidence_ready"] is False
    assert audit["bic_os_phase_locked"] is True


def test_v522_catalog_tracks_blocked_handoff_examples(tmp_path):
    _write_example_files(tmp_path)
    _write_supported_artifacts(tmp_path)

    examples = {example.example_id: example for example in build_biosdk_public_examples_v522(tmp_path)}

    assert examples["cross_dataset_evidence_example"].status == "ready"
    assert examples["external_readonly_handoff_example"].status == "blocked_waiting_for_real_external_material"
    assert examples["vendor_user_upload_handoff_example"].status == "blocked_waiting_for_safe_vendor_or_user_sample"


def test_v522_missing_public_example_blocks_public_examples(tmp_path):
    _write_example_files(tmp_path)
    _write_supported_artifacts(tmp_path)
    (tmp_path / "examples/biosdk_v520_allen_orientation_benchmark.py").unlink()

    audit = build_biosdk_public_examples_gate_v522(tmp_path)

    assert audit["overall_status"] == "biosdk_public_examples_incomplete"
    assert audit["public_examples_ready"] is False
    blocked = {example["example_id"]: example for example in audit["examples"] if example["status"] != "ready"}
    assert "allen_orientation_benchmark_example" in blocked


def test_v522_write_outputs(tmp_path):
    _write_example_files(tmp_path)
    _write_supported_artifacts(tmp_path)
    audit = build_biosdk_public_examples_gate_v522(tmp_path)

    paths = write_biosdk_public_examples_outputs_v522(audit, tmp_path / "out")

    assert Path(paths["summary_json"]).exists()
    assert Path(paths["example_catalog_json"]).exists()
    assert Path(paths["example_catalog_csv"]).exists()
    assert Path(paths["runbook_json"]).exists()
    report = Path(paths["markdown_report"]).read_text(encoding="utf-8")
    assert "BioSDK Public Examples" in report


def test_v522_runner_writes_summary(tmp_path):
    _write_example_files(tmp_path)
    _write_supported_artifacts(tmp_path)

    result = run(root=tmp_path, out_dir=tmp_path / "out")

    assert result["summary"]["public_examples_ready"] is True
    assert (tmp_path / "out" / "V522_BIOSDK_PUBLIC_EXAMPLES_SUMMARY.json").exists()
