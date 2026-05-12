"""Safe user-upload fixture workflow, v5.23."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from biogpu.sdk.cross_dataset_evidence_v521 import DEFAULT_OUT as V521_OUT
from biogpu.sdk.cross_dataset_evidence_v521 import build_cross_dataset_evidence_pack_v521, write_cross_dataset_evidence_outputs_v521
from biogpu.sdk.public_examples_v522 import DEFAULT_OUT as V522_OUT
from biogpu.sdk.public_examples_v522 import build_biosdk_public_examples_gate_v522, write_biosdk_public_examples_outputs_v522
from biogpu.sdk.sample_acquisition_v514 import DEFAULT_OUT as V514_OUT
from biogpu.sdk.sample_acquisition_v514 import build_sample_acquisition_gate_v514, write_sample_acquisition_outputs_v514
from biogpu.sdk.vendor_upload_v519 import DEFAULT_OUT as V519_OUT
from biogpu.sdk.vendor_upload_v519 import build_vendor_upload_gate_v519, validate_vendor_upload_sample_v519, write_vendor_upload_outputs_v519


DEFAULT_OUT = Path("outputs/v523_user_upload_fixture")
DEFAULT_FIXTURE_PATH = Path("data/external/user_upload_samples/biosdk_v523_safe_user_fixture.json")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def build_safe_user_upload_fixture_payload_v523(root: str | Path = ".") -> dict[str, Any]:
    project_root = Path(root)
    dandi = _read_json(project_root / "outputs/v516_dandi_nwb_task_benchmark/V516_DANDI_NWB_TASK_BENCHMARK_SUMMARY.json")
    allen = _read_json(project_root / "outputs/v520_allen_orientation_benchmark/V520_ALLEN_ORIENTATION_BENCHMARK_SUMMARY.json")
    cross = _read_json(project_root / "outputs/v521_cross_dataset_evidence_pack/V521_CROSS_DATASET_EVIDENCE_SUMMARY.json")
    return {
        "fixture_id": "biosdk_v523_safe_user_upload_fixture",
        "schema_id": "biosdk_safe_user_upload_v1",
        "mode": "read_only_replay",
        "created_by_gate": "v5.23",
        "origin": {
            "kind": "derived_public_evidence_fixture",
            "source_versions": ["v5.16", "v5.20", "v5.21"],
            "source_artifacts": [
                "outputs/v516_dandi_nwb_task_benchmark/V516_DANDI_NWB_TASK_BENCHMARK_SUMMARY.json",
                "outputs/v520_allen_orientation_benchmark/V520_ALLEN_ORIENTATION_BENCHMARK_SUMMARY.json",
                "outputs/v521_cross_dataset_evidence_pack/V521_CROSS_DATASET_EVIDENCE_SUMMARY.json",
            ],
        },
        "summary": {
            "record_count": 6,
            "source_count": 2,
            "dandi_rows": int(dandi.get("sample_count", 0) or 0),
            "dandi_units": int(dandi.get("unit_count", 0) or 0),
            "allen_rows": int(allen.get("sample_count", 0) or 0),
            "allen_units_used": int(allen.get("selected_unit_count", 0) or 0),
            "public_cross_dataset_ready": bool(cross.get("public_cross_dataset_evidence_ready")),
            "full_biosdk_ready": False,
            "bic_os_ready": False,
        },
        "records": [
            {"row_id": "dandi_demo_001", "source_id": "dandi_nwb_task", "label": "1", "channels": [1, 2, 3], "spike_times_s": [0.012, 0.048, 0.087]},
            {"row_id": "dandi_demo_002", "source_id": "dandi_nwb_task", "label": "2", "channels": [2, 4, 5], "spike_times_s": [0.019, 0.055, 0.091]},
            {"row_id": "dandi_demo_003", "source_id": "dandi_nwb_task", "label": "3", "channels": [1, 5, 6], "spike_times_s": [0.023, 0.061, 0.099]},
            {"row_id": "allen_demo_001", "source_id": "allen_visual_coding_orientation", "label": "0", "channels": [10, 11, 12], "spike_times_s": [0.015, 0.044, 0.076]},
            {"row_id": "allen_demo_002", "source_id": "allen_visual_coding_orientation", "label": "45", "channels": [11, 13, 14], "spike_times_s": [0.018, 0.052, 0.083]},
            {"row_id": "allen_demo_003", "source_id": "allen_visual_coding_orientation", "label": "90", "channels": [10, 14, 15], "spike_times_s": [0.021, 0.057, 0.096]},
        ],
        "claim_boundary": "This fixture validates the read-only user-upload path only. It is not a vendor export, a real external API sample, full BioSDK readiness or BiC OS readiness.",
    }


def write_safe_user_upload_fixture_v523(root: str | Path = ".", fixture_path: str | Path = DEFAULT_FIXTURE_PATH, overwrite: bool = True) -> Path:
    project_root = Path(root)
    target = project_root / fixture_path
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and not overwrite:
        return target
    payload = build_safe_user_upload_fixture_payload_v523(project_root)
    target.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True), encoding="utf-8")
    return target


def run_user_upload_fixture_workflow_v523(root: str | Path = ".", fixture_path: str | Path = DEFAULT_FIXTURE_PATH, overwrite: bool = True) -> dict[str, Any]:
    project_root = Path(root)
    fixture = write_safe_user_upload_fixture_v523(project_root, fixture_path=fixture_path, overwrite=overwrite)
    validation_report = validate_vendor_upload_sample_v519(fixture, project_root)["report"]
    v519_paths = write_vendor_upload_outputs_v519(project_root, project_root / V519_OUT)
    v519_summary = build_vendor_upload_gate_v519(project_root)
    v514_gate = build_sample_acquisition_gate_v514(project_root)
    v514_paths = write_sample_acquisition_outputs_v514(v514_gate, project_root / V514_OUT)
    v521_audit = build_cross_dataset_evidence_pack_v521(project_root)
    v521_paths = write_cross_dataset_evidence_outputs_v521(v521_audit, project_root / V521_OUT)
    v522_gate = build_biosdk_public_examples_gate_v522(project_root)
    v522_paths = write_biosdk_public_examples_outputs_v522(v522_gate, project_root / V522_OUT)
    user_upload_ready = bool(v519_summary.get("user_upload_validated")) and validation_report.get("gate_status") == "readonly_sample_validated"
    external_ready = bool(v521_audit.get("external_partner_evidence_ready"))
    return {
        "version": "v5.23",
        "phase": "safe_user_upload_fixture_proof",
        "overall_status": "safe_user_upload_fixture_validated_external_api_ready" if user_upload_ready and external_ready else "safe_user_upload_fixture_validated_external_api_still_blocked" if user_upload_ready else "safe_user_upload_fixture_incomplete",
        "active_phase": "biosdk_public_core",
        "bic_os_phase_locked": True,
        "fixture_path": str(fixture.relative_to(project_root)).replace("\\", "/") if fixture.is_relative_to(project_root) else str(fixture),
        "fixture_size_bytes": fixture.stat().st_size if fixture.exists() else 0,
        "fixture_validation_status": validation_report.get("gate_status"),
        "fixture_sha256": validation_report.get("sha256"),
        "fixture_schema_hint": validation_report.get("schema_hint"),
        "safety_scan_passed": bool(validation_report.get("safety_scan_passed")),
        "forbidden_terms": validation_report.get("forbidden_terms", []),
        "user_upload_validated": bool(v519_summary.get("user_upload_validated")),
        "vendor_export_validated": bool(v519_summary.get("vendor_export_validated")),
        "external_partner_evidence_ready": external_ready,
        "vendor_user_evidence_ready": bool(v521_audit.get("vendor_user_evidence_ready")),
        "full_sample_proof_ready": bool(v514_gate.get("full_sample_proof_ready")),
        "full_biosdk_ready": False,
        "downstream_status": {
            "v519_overall_status": v519_summary.get("overall_status"),
            "v514_overall_status": v514_gate.get("overall_status"),
            "v521_overall_status": v521_audit.get("overall_status"),
            "v522_overall_status": v522_gate.get("overall_status"),
        },
        "refreshed_outputs": {
            "v519": v519_paths,
            "v514": v514_paths,
            "v521": v521_paths,
            "v522": v522_paths,
        },
        "direct_answer": {
            "did_we_close_user_upload_blocker": "yes" if user_upload_ready else "not_yet",
            "did_we_close_vendor_export_blocker": "no",
            "did_we_close_real_external_api_blocker": "yes_readonly_export_only" if external_ready else "no",
            "is_full_biosdk_proven": "no",
            "is_bic_os_ready": "no",
            "next_best_build_step": "package SDK release-candidate docs with public, user-upload and read-only external export evidence" if external_ready else "obtain one real external read-only export/token; vendor export remains optional but user-upload path is now validated",
        },
        "claim_boundary": "v5.23 validates a safe read-only user-upload fixture and refreshes downstream proof reports. It does not prove vendor exports, real external APIs, production BioSDK or BiC OS readiness.",
    }


def write_user_upload_fixture_outputs_v523(audit: dict[str, Any], out_dir: str | Path = DEFAULT_OUT) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary_json": out / "V523_USER_UPLOAD_FIXTURE_SUMMARY.json",
        "workflow_json": out / "V523_USER_UPLOAD_FIXTURE_WORKFLOW.json",
        "markdown_report": out / "BIOGPU_V523_USER_UPLOAD_FIXTURE_REPORT.md",
    }
    summary = {key: value for key, value in audit.items() if key not in {"refreshed_outputs"}}
    paths["summary_json"].write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["workflow_json"].write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["markdown_report"].write_text(_markdown_report(audit), encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}


def _markdown_report(audit: dict[str, Any]) -> str:
    answer = audit["direct_answer"]
    return "\n".join(
        [
            "# BioGPU-Core v5.23 Safe User-Upload Fixture",
            "",
            f"- Overall status: `{audit['overall_status']}`",
            f"- Fixture: `{audit['fixture_path']}`",
            f"- Fixture validation: `{audit['fixture_validation_status']}`",
            f"- User upload validated: `{audit['user_upload_validated']}`",
            f"- External partner evidence ready: `{audit['external_partner_evidence_ready']}`",
            f"- Full sample proof ready: `{audit['full_sample_proof_ready']}`",
            f"- BiC OS locked: `{audit['bic_os_phase_locked']}`",
            "",
            "## Direct Answer",
            "",
            f"- User-upload blocker closed: `{answer['did_we_close_user_upload_blocker']}`",
            f"- Vendor export blocker closed: `{answer['did_we_close_vendor_export_blocker']}`",
            f"- Real external API blocker closed: `{answer['did_we_close_real_external_api_blocker']}`",
            f"- Next best build step: {answer['next_best_build_step']}",
            "",
            "## Boundary",
            "",
            audit["claim_boundary"],
            "",
        ]
    )
