from __future__ import annotations

import json
from pathlib import Path

from biogpu.benchmarks.biogpu_v511_bic_os_boot_readiness import run
from biogpu.os.boot_readiness_v511 import build_bic_os_boot_readiness_v511, build_bic_os_subsystems_v511, write_bic_os_boot_outputs_v511


def _write_json(root: Path, relative_path: str, payload: dict) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _write_text(root: Path, relative_path: str, content: str = "ok") -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_supported_artifacts(root: Path) -> None:
    _write_text(root, "biogpu/beta/job_model_v43.py", "job model")
    _write_text(root, "biogpu/os/blueprint_v49.py", "blueprint")
    _write_text(root, "docs/MASTER_PROJECT_PLAN_V50.md", "BiC OS plan")
    _write_text(root, "docs/BIC_OS_FIRST_MOVER_STRATEGY_V50.md", "BiC OS strategy")
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
    _write_json(
        root,
        "outputs/v53_evidence_ledger/V53_EVIDENCE_LEDGER_SUMMARY.json",
        {
            "ledger_chain_valid": True,
            "reference_bundle_valid": True,
            "gate": {"local_signatures_present": True},
        },
    )
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
    _write_json(
        root,
        "outputs/v55_control_plane_queue/V55_CONTROL_PLANE_QUEUE_SUMMARY.json",
        {
            "queued_job_count": 2,
            "safe_replay_admitted": True,
            "live_shadow_developer_rejected": True,
            "blocked_actuation_rejected": True,
        },
    )
    _write_json(root, "outputs/v58_raw_native_benchmark/V58_RAW_NATIVE_FEATURE_SUMMARY.json", {"feature_row_count": 352})
    _write_json(
        root,
        "outputs/v59_raw_native_stability_audit/V59_RAW_NATIVE_STABILITY_SUMMARY.json",
        {
            "split_half_repeatability_status": "split_half_repeatability_available",
            "split_half_cosine_median": 0.99998,
            "split_vs_cross_median_margin": 0.42,
        },
    )
    _write_json(
        root,
        "outputs/v510_project_alignment_claim_audit/V510_PROJECT_ALIGNMENT_SUMMARY.json",
        {
            "overall_status": "on_mission_with_claim_boundaries",
            "direct_answer": {
                "did_we_drift_from_project_meaning": "no",
                "is_the_code_globally_unique_proven": "no_local_tests_cannot_prove_global_uniqueness",
            },
        },
    )


def test_v511_bic_os_boot_manifest_ready_but_not_full_os(tmp_path):
    _write_supported_artifacts(tmp_path)

    audit = build_bic_os_boot_readiness_v511(tmp_path)

    assert audit["product_name"] == "BiC OS"
    assert audit["overall_status"] == "bic_os_offline_runtime_kernel_boot_ready_production_os_not_claimed"
    assert audit["offline_runtime_kernel_bootable"] is True
    assert audit["production_os_ready"] is False
    assert audit["direct_answer"]["can_we_claim_full_unique_os_now"] == "no"


def test_v511_missing_core_artifacts_not_bootable(tmp_path):
    _write_text(tmp_path, "docs/MASTER_PROJECT_PLAN_V50.md", "BiC OS plan")

    audit = build_bic_os_boot_readiness_v511(tmp_path)

    assert audit["overall_status"] == "bic_os_boot_readiness_incomplete"
    assert audit["offline_runtime_kernel_bootable"] is False
    assert "missing" in audit["status_counts"]


def test_v511_subsystems_preserve_production_blockers(tmp_path):
    _write_supported_artifacts(tmp_path)

    subsystems = {item.subsystem_id: item for item in build_bic_os_subsystems_v511(tmp_path)}

    assert subsystems["scheduler_worker_daemon"].status == "degraded"
    assert subsystems["permission_identity_system"].status == "degraded"
    assert subsystems["dashboard_control_plane"].status == "missing"
    assert subsystems["live_telemetry_lab_gateway"].status == "blocked_for_production"


def test_v511_write_outputs(tmp_path):
    _write_supported_artifacts(tmp_path)
    audit = build_bic_os_boot_readiness_v511(tmp_path)

    paths = write_bic_os_boot_outputs_v511(audit, tmp_path / "out")

    assert Path(paths["summary_json"]).exists()
    assert Path(paths["boot_manifest_json"]).exists()
    assert Path(paths["subsystem_csv"]).exists()
    report = Path(paths["markdown_report"]).read_text(encoding="utf-8")
    assert "BiC OS Boot Readiness" in report
    summary = json.loads(Path(paths["summary_json"]).read_text(encoding="utf-8"))
    assert "dashboard_control_plane" in summary["production_blocker_ids"]


def test_v511_runner_writes_summary(tmp_path):
    _write_supported_artifacts(tmp_path)

    result = run(root=tmp_path, out_dir=tmp_path / "out")

    assert result["summary"]["product_name"] == "BiC OS"
    assert result["summary"]["offline_runtime_kernel_bootable"] is True
    assert (tmp_path / "out" / "V511_BIC_OS_BOOT_READINESS_SUMMARY.json").exists()
