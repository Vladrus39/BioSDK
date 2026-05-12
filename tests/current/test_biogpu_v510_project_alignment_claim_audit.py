from __future__ import annotations

import json
from pathlib import Path

from biogpu.benchmarks.biogpu_v510_project_alignment_claim_audit import run
from biogpu.claims.project_alignment_v510 import build_project_alignment_audit_v510, build_claim_register_v510, write_project_alignment_outputs_v510


def _write_json(root: Path, relative_path: str, payload: dict) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _write_text(root: Path, relative_path: str, content: str = "ok") -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_supported_artifacts(root: Path) -> None:
    _write_text(root, "docs/BIC_OS_FIRST_MOVER_STRATEGY_V50.md", "not first biological computer")
    _write_text(root, "docs/MASTER_PROJECT_PLAN_V50.md", "claims policy")
    _write_json(root, "outputs/v50_pc_validation_bundle/V50_PC_VALIDATION_BUNDLE_SUMMARY.json", {"status": "ok"})
    _write_json(root, "outputs/v52_nsi_interface/V52_NSI_INTERFACE_SUMMARY.json", {"status": "ok"})
    _write_json(root, "outputs/v53_evidence_ledger/V53_EVIDENCE_LEDGER_SUMMARY.json", {"status": "ok"})
    _write_json(root, "outputs/v54_llm_agent_bridge/V54_LLM_AGENT_BRIDGE_SUMMARY.json", {"status": "ok"})
    _write_json(root, "outputs/v55_control_plane_queue/V55_CONTROL_PLANE_QUEUE_SUMMARY.json", {"status": "ok"})
    _write_json(root, "outputs/v56_raw_hdf5_structure/V56_RAW_HDF5_STRUCTURE_SUMMARY.json", {"files_with_events": 22})
    _write_json(root, "outputs/v57_raw_preprocessed_alignment/V57_RAW_PREPROCESSED_ALIGNMENT_SUMMARY.json", {"exact_recording_match_count": 0})
    _write_json(root, "outputs/v58_raw_native_benchmark/V58_RAW_NATIVE_FEATURE_SUMMARY.json", {"feature_row_count": 352})
    _write_json(
        root,
        "outputs/v59_raw_native_stability_audit/V59_RAW_NATIVE_STABILITY_SUMMARY.json",
        {
            "split_half_cosine_median": 0.99998,
            "split_vs_cross_median_margin": 0.42,
            "target_readout_signal_status": "not_supported",
            "target_fingerprint_signal_status": "not_supported",
        },
    )


def test_v510_claim_register_blocks_global_uniqueness(tmp_path):
    _write_supported_artifacts(tmp_path)

    register = {item.claim_id: item for item in build_claim_register_v510(tmp_path)}

    assert register["project_meaning_alignment"].status == "supported"
    assert register["global_uniqueness_proof"].status == "not_provable_locally"
    assert register["first_biological_computer"].status == "blocked"
    assert register["target_id_decoding"].status == "not_supported"


def test_v510_project_alignment_audit_answers_user_question(tmp_path):
    _write_supported_artifacts(tmp_path)

    audit = build_project_alignment_audit_v510(tmp_path)

    assert audit["overall_status"] == "on_mission_with_claim_boundaries"
    assert audit["direct_answer"]["did_we_drift_from_project_meaning"] == "no"
    assert audit["direct_answer"]["is_the_code_globally_unique_proven"] == "no_local_tests_cannot_prove_global_uniqueness"


def test_v510_missing_artifacts_reduce_alignment_to_partial(tmp_path):
    _write_text(tmp_path, "docs/MASTER_PROJECT_PLAN_V50.md", "claims policy")

    audit = build_project_alignment_audit_v510(tmp_path)
    register = {row["claim_id"]: row for row in audit["claim_register"]}

    assert audit["overall_status"] == "on_mission_with_claim_boundaries"
    assert register["project_meaning_alignment"]["status"] == "partially_supported"
    assert register["raw_native_extraction_repeatability"]["status"] == "not_supported"


def test_v510_write_outputs(tmp_path):
    _write_supported_artifacts(tmp_path)
    audit = build_project_alignment_audit_v510(tmp_path)

    paths = write_project_alignment_outputs_v510(audit, tmp_path / "out")

    assert Path(paths["summary_json"]).exists()
    assert Path(paths["claim_register_csv"]).exists()
    report = Path(paths["markdown_report"]).read_text(encoding="utf-8")
    assert "Is global uniqueness proven" in report


def test_v510_runner_writes_summary(tmp_path):
    _write_supported_artifacts(tmp_path)

    result = run(root=tmp_path, out_dir=tmp_path / "out")

    assert result["summary"]["overall_status"] == "on_mission_with_claim_boundaries"
    assert (tmp_path / "out" / "V510_PROJECT_ALIGNMENT_SUMMARY.json").exists()
