from __future__ import annotations

import json
from pathlib import Path

from biogpu.benchmarks.biogpu_v512_biosdk_evidence_pack import run
from biogpu.sdk.evidence_pack_v512 import build_biosdk_capabilities_v512, build_biosdk_evidence_pack_v512, write_biosdk_evidence_pack_outputs_v512


def _write_json(root: Path, relative_path: str, payload: dict) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _write_text(root: Path, relative_path: str, content: str = "ok") -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_supported_artifacts(root: Path) -> None:
    _write_text(root, "pyproject.toml", "project")
    _write_text(root, "README.md", "readme")
    _write_text(root, "biogpu/cli.py", "cli")
    _write_text(root, "docs/MASTER_PROJECT_PLAN_V50.md", "plan")
    _write_text(root, "docs/BIC_OS_FIRST_MOVER_STRATEGY_V50.md", "strategy")
    _write_json(root, "outputs/v50_pc_validation_bundle/V50_PC_VALIDATION_BUNDLE_SUMMARY.json", {"status": "ok", "artifact_count": 41, "bundle_sha256": "abc"})
    _write_json(
        root,
        "outputs/v51_dataset_expansion/V51_DATASET_EXPANSION_SUMMARY.json",
        {"probes": [{"probe": "a"}, {"probe": "b"}, {"probe": "c"}, {"probe": "d"}], "gate": {"nwb_available": False}},
    )
    _write_json(
        root,
        "outputs/v52_nsi_interface/V52_NSI_INTERFACE_SUMMARY.json",
        {
            "schema_status": "frozen_interface_profile",
            "schema_count": 7,
            "gate": {
                "nsi_schemas_frozen": True,
                "adapter_conformance_passed": True,
                "result_bundle_validator_passed": True,
                "claim_annotation_available": True,
            },
        },
    )
    _write_json(root, "outputs/v53_evidence_ledger/V53_EVIDENCE_LEDGER_SUMMARY.json", {"ledger_chain_valid": True, "reference_bundle_valid": True, "gate": {"local_signatures_present": True}})
    _write_json(
        root,
        "outputs/v54_llm_agent_bridge/V54_LLM_AGENT_BRIDGE_SUMMARY.json",
        {
            "tool_count": 8,
            "gate": {
                "safe_replay_agent_request_approved": True,
                "live_shadow_requires_or_has_approval": True,
                "direct_actuation_blocked": True,
                "nsi_manifest_emitted_for_safe_requests": True,
            },
        },
    )
    _write_json(root, "outputs/v55_control_plane_queue/V55_CONTROL_PLANE_QUEUE_SUMMARY.json", {"queued_job_count": 2, "safe_replay_admitted": True, "blocked_actuation_rejected": True})
    _write_json(root, "outputs/v56_raw_hdf5_structure/V56_RAW_HDF5_STRUCTURE_SUMMARY.json", {"valid_file_count": 42, "files_with_events": 22})
    _write_json(root, "outputs/v57_raw_preprocessed_alignment/V57_RAW_PREPROCESSED_ALIGNMENT_SUMMARY.json", {"exact_recording_match_count": 0})
    _write_json(root, "outputs/v58_raw_native_benchmark/V58_RAW_NATIVE_FEATURE_SUMMARY.json", {"feature_row_count": 352})
    _write_json(
        root,
        "outputs/v59_raw_native_stability_audit/V59_RAW_NATIVE_STABILITY_SUMMARY.json",
        {"split_half_repeatability_status": "split_half_repeatability_available", "split_half_cosine_median": 0.99998, "target_readout_signal_status": "not_supported"},
    )
    _write_json(
        root,
        "outputs/v510_project_alignment_claim_audit/V510_PROJECT_ALIGNMENT_SUMMARY.json",
        {"overall_status": "on_mission_with_claim_boundaries", "direct_answer": {"did_we_drift_from_project_meaning": "no", "is_the_code_globally_unique_proven": "no_local_tests_cannot_prove_global_uniqueness"}},
    )
    _write_json(
        root,
        "outputs/v511_bic_os_boot_readiness/V511_BIC_OS_BOOT_READINESS_SUMMARY.json",
        {"product_name": "BiC OS", "offline_runtime_kernel_bootable": True, "production_os_ready": False},
    )


def test_v512_evidence_kernel_ready_but_full_sdk_not_claimed(tmp_path):
    _write_supported_artifacts(tmp_path)

    audit = build_biosdk_evidence_pack_v512(tmp_path)

    assert audit["overall_status"] == "biosdk_evidence_kernel_ready_full_sdk_not_claimed"
    assert audit["biosdk_evidence_kernel_ready"] is True
    assert audit["full_biosdk_ready"] is False
    assert audit["direct_answer"]["should_bic_os_wait_for_proven_biosdk"] == "yes"


def test_v512_capabilities_include_usefulness_and_uniqueness_thesis(tmp_path):
    _write_supported_artifacts(tmp_path)

    audit = build_biosdk_evidence_pack_v512(tmp_path)
    capabilities = {item["capability_id"]: item for item in audit["capabilities"]}

    assert capabilities["nsi_contract"]["status"] == "locally_proven"
    assert capabilities["dataset_import_layer"]["status"] == "partially_proven"
    assert "evidence-first result bundles" in " ".join(audit["what_can_make_it_unique_and_desired"])
    assert audit["direct_answer"]["is_global_uniqueness_proven"] == "no_local_tests_cannot_prove_global_uniqueness"


def test_v512_missing_core_artifacts_incomplete(tmp_path):
    _write_text(tmp_path, "README.md", "readme")

    audit = build_biosdk_evidence_pack_v512(tmp_path)

    assert audit["overall_status"] == "biosdk_evidence_kernel_incomplete"
    assert audit["biosdk_evidence_kernel_ready"] is False
    assert audit["locally_proven_capability_count"] == 0


def test_v512_write_outputs(tmp_path):
    _write_supported_artifacts(tmp_path)
    audit = build_biosdk_evidence_pack_v512(tmp_path)

    paths = write_biosdk_evidence_pack_outputs_v512(audit, tmp_path / "out")

    assert Path(paths["summary_json"]).exists()
    assert Path(paths["capability_matrix_json"]).exists()
    assert Path(paths["capability_matrix_csv"]).exists()
    report = Path(paths["markdown_report"]).read_text(encoding="utf-8")
    assert "BioSDK Evidence Pack" in report
    summary = json.loads(Path(paths["summary_json"]).read_text(encoding="utf-8"))
    assert "dataset_import_layer" in summary["capability_gap_ids"]


def test_v512_runner_writes_summary(tmp_path):
    _write_supported_artifacts(tmp_path)

    result = run(root=tmp_path, out_dir=tmp_path / "out")

    assert result["summary"]["sdk_name"] == "BioSDK / Living Compute SDK"
    assert result["summary"]["biosdk_evidence_kernel_ready"] is True
    assert (tmp_path / "out" / "V512_BIOSDK_EVIDENCE_PACK_SUMMARY.json").exists()
