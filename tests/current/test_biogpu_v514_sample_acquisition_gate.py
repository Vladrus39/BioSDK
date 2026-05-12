from __future__ import annotations

import json
from pathlib import Path

import h5py

from biogpu.benchmarks.biogpu_v514_sample_acquisition_gate import run
from biogpu.sdk.sample_acquisition_v514 import build_sample_acquisition_gate_v514, build_sample_requirements_v514, write_sample_acquisition_outputs_v514


def _write_json(root: Path, relative_path: str, payload: dict) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _write_text(root: Path, relative_path: str, content: str = "ok") -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_minimal_phase_artifacts(root: Path) -> None:
    _write_text(root, "pyproject.toml", "project")
    _write_text(root, "README.md", "readme")
    _write_text(root, "biogpu/cli.py", "cli")
    _write_text(root, "docs/MASTER_PROJECT_PLAN_V50.md", "plan")
    _write_text(root, "docs/BIC_OS_FIRST_MOVER_STRATEGY_V50.md", "strategy")
    _write_json(root, "outputs/v50_pc_validation_bundle/V50_PC_VALIDATION_BUNDLE_SUMMARY.json", {"status": "ok", "artifact_count": 41, "bundle_sha256": "abc"})
    _write_json(root, "outputs/v51_dataset_expansion/V51_DATASET_EXPANSION_SUMMARY.json", {"probes": [{"probe": "a"}, {"probe": "b"}, {"probe": "c"}, {"probe": "d"}], "gate": {"nwb_available": False}})
    _write_json(root, "outputs/v52_nsi_interface/V52_NSI_INTERFACE_SUMMARY.json", {"schema_status": "frozen_interface_profile", "schema_count": 7, "gate": {"nsi_schemas_frozen": True, "adapter_conformance_passed": True, "result_bundle_validator_passed": True, "claim_annotation_available": True}})
    _write_json(root, "outputs/v53_evidence_ledger/V53_EVIDENCE_LEDGER_SUMMARY.json", {"ledger_chain_valid": True, "reference_bundle_valid": True, "gate": {"local_signatures_present": True}})
    _write_json(root, "outputs/v54_llm_agent_bridge/V54_LLM_AGENT_BRIDGE_SUMMARY.json", {"tool_count": 8, "gate": {"safe_replay_agent_request_approved": True, "live_shadow_requires_or_has_approval": True, "direct_actuation_blocked": True, "nsi_manifest_emitted_for_safe_requests": True}})
    _write_json(root, "outputs/v55_control_plane_queue/V55_CONTROL_PLANE_QUEUE_SUMMARY.json", {"queued_job_count": 2, "safe_replay_admitted": True, "blocked_actuation_rejected": True})
    _write_json(root, "outputs/v56_raw_hdf5_structure/V56_RAW_HDF5_STRUCTURE_SUMMARY.json", {"valid_file_count": 2, "files_with_events": 1})
    _write_json(root, "outputs/v57_raw_preprocessed_alignment/V57_RAW_PREPROCESSED_ALIGNMENT_SUMMARY.json", {"exact_recording_match_count": 0})
    _write_json(root, "outputs/v58_raw_native_benchmark/V58_RAW_NATIVE_FEATURE_SUMMARY.json", {"feature_row_count": 12})
    _write_json(root, "outputs/v59_raw_native_stability_audit/V59_RAW_NATIVE_STABILITY_SUMMARY.json", {"split_half_repeatability_status": "split_half_repeatability_available", "target_readout_signal_status": "not_supported"})
    _write_json(root, "outputs/v510_project_alignment_claim_audit/V510_PROJECT_ALIGNMENT_SUMMARY.json", {"overall_status": "on_mission_with_claim_boundaries", "direct_answer": {"did_we_drift_from_project_meaning": "no", "is_the_code_globally_unique_proven": "no_local_tests_cannot_prove_global_uniqueness"}})
    _write_json(root, "outputs/v511_bic_os_boot_readiness/V511_BIC_OS_BOOT_READINESS_SUMMARY.json", {"product_name": "BiC OS", "offline_runtime_kernel_bootable": True, "production_os_ready": False})


def _write_local_zenodo_samples(root: Path) -> None:
    _write_text(root, "data/external/Pre_processed_MEA_data.zip", "zip")
    _write_text(root, "data/external/Raw_data_MEA_data.zip", "zip")
    _write_text(root, "data/external/raw_hdf5/a.h5", "h5")
    _write_text(root, "data/external/raw_hdf5/b.h5", "h5")


def _write_minimal_nwb_units(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with h5py.File(path, "w") as h5:
        units = h5.create_group("units")
        units.create_dataset("spike_times", data=[0.1, 0.2, 0.4])
        units.create_dataset("spike_times_index", data=[2, 3])


def test_v514_reports_local_zenodo_and_missing_external_samples(tmp_path):
    _write_minimal_phase_artifacts(tmp_path)
    _write_local_zenodo_samples(tmp_path)

    gate = build_sample_acquisition_gate_v514(tmp_path)

    assert gate["overall_status"] == "sample_proof_gate_ready_for_external_downloads"
    assert gate["bic_os_phase_locked"] is True
    assert gate["locally_available_independent_source_count"] == 1
    assert "dandi_nwb_task_sample" in gate["missing_required_sample_ids"]
    assert gate["full_sample_proof_ready"] is False


def test_v514_requirements_detect_dandi_nwb_units(tmp_path):
    _write_minimal_phase_artifacts(tmp_path)
    _write_local_zenodo_samples(tmp_path)
    _write_minimal_nwb_units(tmp_path / "data" / "external" / "nwb" / "sample.nwb")

    requirements = {item.sample_id: item for item in build_sample_requirements_v514(tmp_path)}

    assert requirements["dandi_nwb_task_sample"].status == "validated_present"
    assert requirements["dandi_nwb_task_sample"].file_count == 1


def test_v514_download_manifest_is_capped_and_selective(tmp_path):
    _write_minimal_phase_artifacts(tmp_path)
    gate = build_sample_acquisition_gate_v514(tmp_path)

    manifest = gate["download_manifest"]

    assert manifest["network_policy"]["default_max_mb"] == 512
    assert manifest["network_policy"]["full_dandiset_download_default"] is False
    assert any(command["sample_id"] == "dandi_nwb_task_sample" for command in manifest["commands"])


def test_v514_write_outputs(tmp_path):
    _write_minimal_phase_artifacts(tmp_path)
    _write_local_zenodo_samples(tmp_path)
    gate = build_sample_acquisition_gate_v514(tmp_path)

    paths = write_sample_acquisition_outputs_v514(gate, tmp_path / "out")

    assert Path(paths["summary_json"]).exists()
    assert Path(paths["sample_matrix_csv"]).exists()
    assert Path(paths["download_manifest_json"]).exists()
    report = Path(paths["markdown_report"]).read_text(encoding="utf-8")
    assert "Sample Acquisition Gate" in report


def test_v514_runner_writes_summary(tmp_path):
    _write_minimal_phase_artifacts(tmp_path)
    _write_local_zenodo_samples(tmp_path)

    result = run(root=tmp_path, out_dir=tmp_path / "out")

    assert result["summary"]["active_phase"] == "biosdk_public_core"
    assert result["summary"]["bic_os_phase_locked"] is True
    assert (tmp_path / "out" / "V514_SAMPLE_ACQUISITION_SUMMARY.json").exists()
