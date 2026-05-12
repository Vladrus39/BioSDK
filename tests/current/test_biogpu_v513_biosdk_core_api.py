from __future__ import annotations

import json
from pathlib import Path

from biogpu.benchmarks.biogpu_v513_biosdk_core_api import run
from biogpu.llm.agent_bridge_v54 import BioComputeAgentRequestV54
from biogpu.sdk.core_v513 import BioSDKClientV513, build_biosdk_phase_gate_v513, run_biosdk_reference_flow_v513, write_biosdk_core_outputs_v513


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
    _write_json(root, "outputs/v51_dataset_expansion/V51_DATASET_EXPANSION_SUMMARY.json", {"probes": [{"probe": "a"}, {"probe": "b"}, {"probe": "c"}, {"probe": "d"}], "gate": {"nwb_available": False}})
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
    _write_json(root, "outputs/v54_llm_agent_bridge/V54_LLM_AGENT_BRIDGE_SUMMARY.json", {"tool_count": 8, "gate": {"safe_replay_agent_request_approved": True, "live_shadow_requires_or_has_approval": True, "direct_actuation_blocked": True, "nsi_manifest_emitted_for_safe_requests": True}})
    _write_json(root, "outputs/v55_control_plane_queue/V55_CONTROL_PLANE_QUEUE_SUMMARY.json", {"queued_job_count": 2, "safe_replay_admitted": True, "blocked_actuation_rejected": True})
    _write_json(root, "outputs/v56_raw_hdf5_structure/V56_RAW_HDF5_STRUCTURE_SUMMARY.json", {"valid_file_count": 42, "files_with_events": 22})
    _write_json(root, "outputs/v57_raw_preprocessed_alignment/V57_RAW_PREPROCESSED_ALIGNMENT_SUMMARY.json", {"exact_recording_match_count": 0})
    _write_json(root, "outputs/v58_raw_native_benchmark/V58_RAW_NATIVE_FEATURE_SUMMARY.json", {"feature_row_count": 352})
    _write_json(root, "outputs/v59_raw_native_stability_audit/V59_RAW_NATIVE_STABILITY_SUMMARY.json", {"split_half_repeatability_status": "split_half_repeatability_available", "split_half_cosine_median": 0.99998, "target_readout_signal_status": "not_supported"})
    _write_json(root, "outputs/v510_project_alignment_claim_audit/V510_PROJECT_ALIGNMENT_SUMMARY.json", {"overall_status": "on_mission_with_claim_boundaries", "direct_answer": {"did_we_drift_from_project_meaning": "no", "is_the_code_globally_unique_proven": "no_local_tests_cannot_prove_global_uniqueness"}})
    _write_json(root, "outputs/v511_bic_os_boot_readiness/V511_BIC_OS_BOOT_READINESS_SUMMARY.json", {"product_name": "BiC OS", "offline_runtime_kernel_bootable": True, "production_os_ready": False})


def test_v513_phase_gate_keeps_biosdk_active_and_bic_os_locked(tmp_path):
    _write_supported_artifacts(tmp_path)

    gate = build_biosdk_phase_gate_v513(tmp_path)

    assert gate["overall_status"] == "biosdk_core_api_active_bic_os_locked"
    assert gate["active_phase"] == "biosdk_public_core"
    assert gate["bic_os_phase_locked"] is True
    assert "durable_scheduler_worker" in gate["allowed_next_builds"]
    assert "production_bic_os_claim" in gate["blocked_next_builds"]


def test_v513_client_builds_valid_replay_manifest(tmp_path):
    _write_supported_artifacts(tmp_path)
    client = BioSDKClientV513(tmp_path)

    request = client.build_replay_request("safe", "Run a safe replay job")
    response = client.review_agent_task(request)

    assert response["status"] == "approved"
    assert response["nsi_task_manifest"] is not None
    assert client.validate_nsi_payload("BioComputeTaskManifest", response["nsi_task_manifest"])["valid"] is True


def test_v513_reference_flow_queues_safe_replay_and_locks_os(tmp_path):
    _write_supported_artifacts(tmp_path)

    flow = run_biosdk_reference_flow_v513(tmp_path)

    assert flow["phase_gate"]["bic_os_phase_locked"] is True
    assert flow["agent_response"]["status"] == "approved"
    assert flow["nsi_manifest_valid"] is True
    assert flow["queue_admission_accepted"] is True
    assert flow["job_status"] == "queued"


def test_v513_blocks_unsafe_actuation_through_facade(tmp_path):
    _write_supported_artifacts(tmp_path)
    client = BioSDKClientV513(tmp_path)
    request = BioComputeAgentRequestV54(
        request_id="unsafe",
        agent_id="agent",
        user_goal="try unsafe actuation",
        requested_tool="biocompute.request_approved_actuation",
        mode="approved_actuation",
        inputs={"operation": "live_stimulation"},
    )

    response = client.review_agent_task(request)
    submission = client.submit_agent_task(request)

    assert response["status"] == "blocked"
    assert submission["admission"]["accepted"] is False
    assert submission["job"] is None


def test_v513_write_outputs(tmp_path):
    _write_supported_artifacts(tmp_path)
    flow = run_biosdk_reference_flow_v513(tmp_path)

    paths = write_biosdk_core_outputs_v513(flow, tmp_path / "out")

    assert Path(paths["summary_json"]).exists()
    assert Path(paths["phase_gate_json"]).exists()
    assert Path(paths["reference_flow_json"]).exists()
    report = Path(paths["markdown_report"]).read_text(encoding="utf-8")
    assert "BioSDK Core API" in report


def test_v513_runner_writes_summary(tmp_path):
    _write_supported_artifacts(tmp_path)

    result = run(root=tmp_path, out_dir=tmp_path / "out")

    assert result["summary"]["active_phase"] == "biosdk_public_core"
    assert result["summary"]["bic_os_phase_locked"] is True
    assert (tmp_path / "out" / "V513_BIOSDK_CORE_API_SUMMARY.json").exists()
