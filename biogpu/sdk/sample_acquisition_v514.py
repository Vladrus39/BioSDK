"""BioSDK sample acquisition and proof gate, v5.14."""
from __future__ import annotations

import csv
import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from biogpu.data_ingest.dandi_discovery import candidates_as_dict
from biogpu.data_ingest.dandi_nwb import inspect_nwb_units
from biogpu.sdk.core_v513 import build_biosdk_phase_gate_v513


DEFAULT_OUT = Path("outputs/v514_sample_acquisition_gate")


@dataclass(frozen=True)
class BioSDKSampleRequirementV514:
    sample_id: str
    source_family: str
    sample_kind: str
    priority: str
    status: str
    required_for: tuple[str, ...]
    local_paths: tuple[str, ...] = tuple()
    file_count: int = 0
    total_bytes: int = 0
    validation_evidence: tuple[str, ...] = tuple()
    download_hint: str = ""
    recommended_command: str = ""
    blockers: tuple[str, ...] = tuple()
    claim_boundary: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def _files(root: Path, *patterns: str) -> list[Path]:
    found: list[Path] = []
    for pattern in patterns:
        found.extend(path for path in root.glob(pattern) if path.is_file())
    return sorted(set(found))


def _stats(paths: list[Path], root: Path) -> tuple[tuple[str, ...], int, int]:
    rel_paths = tuple(str(path.relative_to(root)).replace("\\", "/") for path in paths[:20])
    total_bytes = sum(path.stat().st_size for path in paths if path.exists())
    return rel_paths, len(paths), total_bytes


def _artifact_exists(root: Path, relative_path: str) -> bool:
    return (root / relative_path).exists()


def _preprocessed_requirement(root: Path) -> BioSDKSampleRequirementV514:
    paths = _files(root, "data/external/Pre_processed_MEA_data.zip")
    rel, count, total = _stats(paths, root)
    v50_present = _artifact_exists(root, "outputs/v50_pc_validation_bundle/V50_PC_VALIDATION_BUNDLE_SUMMARY.json")
    status = "validated_present" if count and v50_present else "present_needs_v50_gate" if count else "missing_download_required"
    blockers = tuple() if status == "validated_present" else ("download Pre_processed_MEA_data.zip", "run v50 PC validation bundle")
    return BioSDKSampleRequirementV514(
        sample_id="zenodo_14363732_preprocessed",
        source_family="zenodo_14363732",
        sample_kind="public_archive_preprocessed_mea",
        priority="P0",
        status=status,
        required_for=("PC validation", "BioSDK replay examples", "evidence bundle baseline"),
        local_paths=rel,
        file_count=count,
        total_bytes=total,
        validation_evidence=("outputs/v50_pc_validation_bundle/V50_PC_VALIDATION_BUNDLE_SUMMARY.json",) if v50_present else tuple(),
        download_hint="Download Pre_processed_MEA_data.zip from Zenodo record 14363732 into data/external/.",
        blockers=blockers,
        claim_boundary="Supports software replay evidence only; not live BioGPU or full BioSDK proof by itself.",
    )


def _raw_hdf5_requirement(root: Path) -> BioSDKSampleRequirementV514:
    zip_paths = _files(root, "data/external/Raw_data_MEA_data.zip")
    h5_paths = _files(root, "data/external/raw_hdf5/**/*.h5", "data/external/raw_hdf5/**/*.hdf5")
    rel, count, total = _stats(zip_paths + h5_paths, root)
    v56_present = _artifact_exists(root, "outputs/v56_raw_hdf5_structure/V56_RAW_HDF5_STRUCTURE_SUMMARY.json")
    v58_present = _artifact_exists(root, "outputs/v58_raw_native_benchmark/V58_RAW_NATIVE_FEATURE_SUMMARY.json")
    v59_present = _artifact_exists(root, "outputs/v59_raw_native_stability_audit/V59_RAW_NATIVE_STABILITY_SUMMARY.json")
    if h5_paths and v56_present and v58_present and v59_present:
        status = "validated_present_partial_proof"
        blockers = ("resolve exact raw-to-v15 coverage", "increase repeated-target raw coverage")
    elif h5_paths:
        status = "present_needs_raw_gates"
        blockers = ("run v56/v58/v59 raw gates",)
    elif zip_paths:
        status = "archive_present_needs_extract"
        blockers = ("extract Raw_data_MEA_data.zip into data/external/raw_hdf5",)
    else:
        status = "missing_download_required"
        blockers = ("download Raw_data_MEA_data.zip",)
    evidence = tuple(
        rel_path
        for rel_path, present in (
            ("outputs/v56_raw_hdf5_structure/V56_RAW_HDF5_STRUCTURE_SUMMARY.json", v56_present),
            ("outputs/v58_raw_native_benchmark/V58_RAW_NATIVE_FEATURE_SUMMARY.json", v58_present),
            ("outputs/v59_raw_native_stability_audit/V59_RAW_NATIVE_STABILITY_SUMMARY.json", v59_present),
        )
        if present
    )
    return BioSDKSampleRequirementV514(
        sample_id="zenodo_14363732_raw_hdf5",
        source_family="zenodo_14363732",
        sample_kind="public_archive_raw_mea_hdf5",
        priority="P0",
        status=status,
        required_for=("raw reconstruction", "raw native benchmark", "BioSDK data proof"),
        local_paths=rel,
        file_count=count,
        total_bytes=total,
        validation_evidence=evidence,
        download_hint="Run scripts/download_zenodo_raw_hdf5.ps1, then extract Raw_data_MEA_data.zip into data/external/raw_hdf5/.",
        blockers=blockers,
        claim_boundary="Raw HDF5 supports raw-event feature extraction; current local subset still does not prove v15/v50 exact raw equivalence or target-ID decoding.",
    )


def _dandi_requirement(root: Path) -> BioSDKSampleRequirementV514:
    nwb_paths = _files(root, "data/external/nwb/**/*.nwb", "data/external/dandi/**/*.nwb")
    rel, count, total = _stats(nwb_paths, root)
    v515_present = _artifact_exists(root, "outputs/v515_dandi_nwb_task_validation/V515_DANDI_NWB_TASK_VALIDATION_SUMMARY.json")
    v516_present = _artifact_exists(root, "outputs/v516_dandi_nwb_task_benchmark/V516_DANDI_NWB_TASK_BENCHMARK_SUMMARY.json")
    inspected = []
    for path in nwb_paths[:3]:
        try:
            inspected.append(inspect_nwb_units(path))
        except Exception as exc:
            inspected.append({"path": str(path), "exists": True, "error": str(exc)})
    has_units = any(item.get("has_units") is True for item in inspected)
    if has_units:
        status = "validated_present"
        blockers = tuple()
    elif nwb_paths:
        status = "present_needs_units_or_task_gate"
        blockers = ("choose an NWB with /units spike_times", "map intervals/trials/stimulus metadata")
    else:
        status = "missing_download_required"
        blockers = ("download one capped DANDI NWB sample", "run NWB units/task inspection")
    return BioSDKSampleRequirementV514(
        sample_id="dandi_nwb_task_sample",
        source_family="dandi_public_nwb",
        sample_kind="public_archive_task_aligned_nwb",
        priority="P1",
        status=status,
        required_for=("independent public dataset proof", "NSI dataset import examples", "BioSDK full data proof"),
        local_paths=rel,
        file_count=count,
        total_bytes=total,
        validation_evidence=tuple(
            item
            for item, present in (
                ("/units spike_times inspected", has_units),
                ("outputs/v515_dandi_nwb_task_validation/V515_DANDI_NWB_TASK_VALIDATION_SUMMARY.json", v515_present),
                ("outputs/v516_dandi_nwb_task_benchmark/V516_DANDI_NWB_TASK_BENCHMARK_SUMMARY.json", v516_present),
            )
            if present
        ),
        download_hint="Prefer a single small NWB asset from DANDI 000469 before any full dandiset/cache download.",
        recommended_command="powershell -ExecutionPolicy Bypass -File scripts/download_dandi_nwb_sample_v514.ps1 -DandisetId 000469 -MaxMB 512",
        blockers=blockers,
        claim_boundary="A DANDI NWB sample can prove parser portability only after local units and task metadata inspection passes.",
    )


def _allen_requirement(root: Path) -> BioSDKSampleRequirementV514:
    paths = _files(root, "data/external/allen/**/*.nwb", "data/external/allen/**/*manifest*.json")
    rel, count, total = _stats(paths, root)
    v518_summary = _read_json(root / "outputs/v518_allen_orientation_gate/V518_ALLEN_ORIENTATION_GATE_SUMMARY.json")
    v518_status = str(v518_summary.get("overall_status") or "")
    if v518_status == "allen_orientation_sample_validated":
        status = "validated_present"
        blockers = tuple()
    elif paths and v518_status:
        status = "present_validation_incomplete"
        blockers = ("select visual-coding sessions", "run orientation stimulus/spike extraction")
    elif paths:
        status = "present_needs_allen_orientation_gate"
        blockers = ("run v5.18 Allen orientation gate",)
    else:
        status = "missing_download_required"
        blockers = ("select a small Allen visual-coding session", "place NWB/cache manifest under data/external/allen", "run v5.18 Allen orientation gate")
    return BioSDKSampleRequirementV514(
        sample_id="allen_visual_coding_orientation_sample",
        source_family="allen_visual_coding",
        sample_kind="public_archive_orientation_neurophysiology",
        priority="P1",
        status=status,
        required_for=("second independent public dataset", "orientation benchmark externalization"),
        local_paths=rel,
        file_count=count,
        total_bytes=total,
        validation_evidence=("outputs/v518_allen_orientation_gate/V518_ALLEN_ORIENTATION_GATE_SUMMARY.json",) if v518_status else tuple(),
        download_hint="Do not download the full Allen cache by default. Select a small session/cache slice for orientation benchmark validation.",
        blockers=blockers,
        claim_boundary="Synthetic orientation data is not enough for full external neurophysiology proof; an Allen/real public sample is still needed.",
    )


def _external_api_requirement(root: Path) -> BioSDKSampleRequirementV514:
    configured = [name for name in ("FINALSPARK_TOKEN", "THREEBRAIN_TOKEN", "AXION_TOKEN", "MCS_TOKEN") if os.environ.get(name)]
    trace_paths = _files(root, "data/external/api_exports/**/*", "data/external/finalspark/**/*")
    v517_present = _artifact_exists(root, "outputs/v517_external_readonly_api_gate/V517_EXTERNAL_READONLY_API_SUMMARY.json")
    v517_summary = _read_json(root / "outputs/v517_external_readonly_api_gate/V517_EXTERNAL_READONLY_API_SUMMARY.json")
    v524_summary = _read_json(root / "outputs/v524_external_export_validation/V524_EXTERNAL_EXPORT_VALIDATION_SUMMARY.json")
    real_ready = bool(v517_summary.get("real_external_ready") or v524_summary.get("real_external_ready"))
    rel, count, total = _stats(trace_paths, root)
    if real_ready:
        status = "validated_present"
        blockers = tuple()
    elif configured and trace_paths:
        status = "credential_and_export_present_needs_validation"
        blockers = ("run read-only adapter validation",)
    elif configured:
        status = "credential_configured_needs_readonly_trace"
        blockers = ("fetch/read one metadata or trace export without actuation",)
    elif trace_paths:
        status = "export_present_needs_adapter_validation"
        blockers = ("map export to read-only API adapter",)
    else:
        status = "credential_or_export_required"
        blockers = ("obtain read-only partner/API credential or export",)
    return BioSDKSampleRequirementV514(
        sample_id="external_readonly_api_or_export_sample",
        source_family="external_readonly_api_or_vendor_export",
        sample_kind="read_only_partner_api_or_export",
        priority="P1",
        status=status,
        required_for=("external wetware read-only proof", "BioCompute Runtime beta", "stronger SDK proof"),
        local_paths=rel,
        file_count=count,
        total_bytes=total,
        validation_evidence=tuple(
            [*(f"env:{name}" for name in configured)]
            + (["outputs/v517_external_readonly_api_gate/V517_EXTERNAL_READONLY_API_SUMMARY.json"] if v517_present else [])
            + (["outputs/v524_external_export_validation/V524_EXTERNAL_EXPORT_VALIDATION_SUMMARY.json"] if v524_summary else [])
        ),
        download_hint="Needs a read-only token/export from a partner platform or vendor. Live actuation remains blocked.",
        blockers=blockers,
        claim_boundary="External API/export proof must remain metadata/read-only/live-shadow; no closed-loop or live control claim is allowed here.",
    )


def _vendor_upload_requirement(root: Path) -> BioSDKSampleRequirementV514:
    paths = _files(root, "data/external/vendor_exports/**/*", "data/external/user_upload_samples/**/*")
    rel, count, total = _stats(paths, root)
    v519_summary = _read_json(root / "outputs/v519_vendor_user_upload_gate/V519_VENDOR_USER_UPLOAD_GATE_SUMMARY.json")
    v519_status = str(v519_summary.get("overall_status") or "")
    if v519_status == "vendor_user_upload_readonly_samples_validated":
        status = "validated_present"
        blockers = tuple()
    elif paths and v519_status:
        status = "present_validation_incomplete"
        blockers = ("inspect v5.19 blocked sample reports", "provide safe read-only export fixtures")
    elif paths:
        status = "present_needs_import_validation"
        blockers = ("run v5.19 vendor/user-upload gate",)
    else:
        status = "missing_sample_required"
        blockers = ("collect MCS/3Brain/Axion export samples or user-upload fixtures", "run schema detection and safety scan")
    return BioSDKSampleRequirementV514(
        sample_id="vendor_or_user_upload_sample",
        source_family="vendor_export_or_private_upload",
        sample_kind="vendor_export_or_private_beta_upload",
        priority="P2",
        status=status,
        required_for=("private beta", "enterprise portability", "user-upload validation"),
        local_paths=rel,
        file_count=count,
        total_bytes=total,
        validation_evidence=("outputs/v519_vendor_user_upload_gate/V519_VENDOR_USER_UPLOAD_GATE_SUMMARY.json",) if v519_status else tuple(),
        download_hint="Collect read-only sample exports or user-upload fixtures; do not include live-control vendor settings.",
        blockers=blockers,
        claim_boundary="Vendor/private upload samples prove portability only after read-only safety scan and schema mapping.",
    )


def build_sample_requirements_v514(root: str | Path = ".") -> list[BioSDKSampleRequirementV514]:
    project_root = Path(root).resolve()
    return [
        _preprocessed_requirement(project_root),
        _raw_hdf5_requirement(project_root),
        _dandi_requirement(project_root),
        _allen_requirement(project_root),
        _external_api_requirement(project_root),
        _vendor_upload_requirement(project_root),
    ]


def build_sample_acquisition_gate_v514(root: str | Path = ".") -> dict[str, Any]:
    project_root = Path(root).resolve()
    requirements = build_sample_requirements_v514(project_root)
    phase_gate = build_biosdk_phase_gate_v513(project_root)
    status_by_id = {item.sample_id: item.status for item in requirements}
    available_families = sorted(
        {
            item.source_family
            for item in requirements
            if item.status in {"validated_present", "validated_present_partial_proof", "present_needs_import_validation", "credential_and_export_present_needs_validation"}
        }
    )
    missing_required = [
        item.sample_id
        for item in requirements
        if item.status in {"missing_download_required", "credential_or_export_required", "missing_sample_required"}
    ]
    dandi_ready = status_by_id.get("dandi_nwb_task_sample") == "validated_present"
    external_ready = status_by_id.get("external_readonly_api_or_export_sample") in {
        "validated_present",
        "credential_and_export_present_needs_validation",
        "export_present_needs_adapter_validation",
    }
    independent_source_target = 3
    full_sample_proof_ready = len(available_families) >= independent_source_target and dandi_ready and external_ready
    overall_status = "sample_proof_gate_ready_for_external_downloads" if not full_sample_proof_ready else "sample_proof_gate_complete_review_required"
    next_best_steps = []
    if not dandi_ready:
        next_best_steps.extend(
            [
                "run selective capped DANDI NWB sample download",
                "inspect the downloaded NWB for /units and task/stimulus metadata",
            ]
        )
    elif _artifact_exists(project_root, "outputs/v516_dandi_nwb_task_benchmark/V516_DANDI_NWB_TASK_BENCHMARK_SUMMARY.json"):
        next_best_steps.append("extend DANDI/NWB benchmark to a second public sample or package it into the installable SDK examples")
    else:
        next_best_steps.append("extend DANDI/NWB validation to a second sample or convert exported task windows into SDK examples")
    if not external_ready:
        next_best_steps.append("add one external read-only API/export validation path")
    if status_by_id.get("allen_visual_coding_orientation_sample") == "missing_download_required":
        next_best_steps.append("add one Allen/public orientation sample without downloading a full cache")
    if status_by_id.get("vendor_or_user_upload_sample") == "missing_sample_required":
        next_best_steps.append("collect one read-only vendor export or user-upload fixture")
    next_best_steps.append("expand BioSDK examples for each validated sample path")
    return {
        "version": "v5.14",
        "phase": "biosdk_sample_acquisition_and_data_proof",
        "overall_status": overall_status,
        "active_phase": phase_gate.get("active_phase", "biosdk_public_core"),
        "bic_os_phase_locked": True,
        "sample_requirement_count": len(requirements),
        "locally_available_independent_source_count": len(available_families),
        "independent_source_target": independent_source_target,
        "locally_available_source_families": available_families,
        "missing_required_sample_ids": missing_required,
        "dandi_nwb_validated": dandi_ready,
        "external_readonly_validated_or_present": external_ready,
        "full_sample_proof_ready": full_sample_proof_ready,
        "requirements": [item.to_dict() for item in requirements],
        "dandi_curated_candidates": candidates_as_dict(),
        "download_manifest": build_download_manifest_v514(),
        "next_best_steps": next_best_steps,
        "claim_boundary": "v5.14 prepares and audits sample acquisition for BioSDK proof; it does not claim full BioSDK, production runtime or BiC OS readiness.",
    }


def build_download_manifest_v514() -> dict[str, Any]:
    return {
        "version": "v5.14",
        "network_policy": {
            "default_max_mb": 512,
            "full_dandiset_download_default": False,
            "full_allensdk_cache_download_default": False,
            "reason": "Use selective capped samples first to preserve bandwidth and keep evidence traceable.",
        },
        "commands": [
            {
                "sample_id": "dandi_nwb_task_sample",
                "purpose": "Download one small NWB sample from DANDI 000469 when available under the size cap.",
                "powershell": "powershell -ExecutionPolicy Bypass -File scripts/download_dandi_nwb_sample_v514.ps1 -DandisetId 000469 -MaxMB 512",
                "plan_only": "powershell -ExecutionPolicy Bypass -File scripts/download_dandi_nwb_sample_v514.ps1 -DandisetId 000469 -MaxMB 512 -PlanOnly",
            },
            {
                "sample_id": "zenodo_14363732_raw_hdf5",
                "purpose": "Resume/verify the already-used raw HDF5 archive if it must be restored.",
                "powershell": "powershell -ExecutionPolicy Bypass -File scripts/download_zenodo_raw_hdf5.ps1",
            },
        ],
    }


def write_sample_acquisition_outputs_v514(gate: dict[str, Any], out_dir: str | Path = DEFAULT_OUT) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary_json": out / "V514_SAMPLE_ACQUISITION_SUMMARY.json",
        "sample_matrix_json": out / "V514_SAMPLE_REQUIREMENT_MATRIX.json",
        "sample_matrix_csv": out / "V514_SAMPLE_REQUIREMENT_MATRIX.csv",
        "download_manifest_json": out / "V514_DOWNLOAD_MANIFEST.json",
        "markdown_report": out / "BIOGPU_V514_SAMPLE_ACQUISITION_REPORT.md",
    }
    summary = {
        "version": gate["version"],
        "overall_status": gate["overall_status"],
        "active_phase": gate["active_phase"],
        "bic_os_phase_locked": gate["bic_os_phase_locked"],
        "locally_available_independent_source_count": gate["locally_available_independent_source_count"],
        "independent_source_target": gate["independent_source_target"],
        "missing_required_sample_ids": gate["missing_required_sample_ids"],
        "dandi_nwb_validated": gate["dandi_nwb_validated"],
        "external_readonly_validated_or_present": gate["external_readonly_validated_or_present"],
        "full_sample_proof_ready": gate["full_sample_proof_ready"],
        "claim_boundary": gate["claim_boundary"],
    }
    paths["summary_json"].write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["sample_matrix_json"].write_text(json.dumps({"requirements": gate["requirements"]}, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["download_manifest_json"].write_text(json.dumps(gate["download_manifest"], indent=2, ensure_ascii=False), encoding="utf-8")
    _write_sample_csv(paths["sample_matrix_csv"], gate["requirements"])
    paths["markdown_report"].write_text(_markdown_report(gate), encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}


def _write_sample_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = [
        "sample_id",
        "source_family",
        "sample_kind",
        "priority",
        "status",
        "file_count",
        "total_bytes",
        "required_for",
        "blockers",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "sample_id": row["sample_id"],
                    "source_family": row["source_family"],
                    "sample_kind": row["sample_kind"],
                    "priority": row["priority"],
                    "status": row["status"],
                    "file_count": row["file_count"],
                    "total_bytes": row["total_bytes"],
                    "required_for": ";".join(row["required_for"]),
                    "blockers": ";".join(row["blockers"]),
                }
            )


def _markdown_report(gate: dict[str, Any]) -> str:
    lines = [
        "# BioGPU-Core v5.14 Sample Acquisition Gate",
        "",
        f"- Overall status: `{gate['overall_status']}`",
        f"- Active phase: `{gate['active_phase']}`",
        f"- BiC OS locked: `{gate['bic_os_phase_locked']}`",
        f"- Local independent sources: `{gate['locally_available_independent_source_count']}/{gate['independent_source_target']}`",
        f"- Full sample proof ready: `{gate['full_sample_proof_ready']}`",
        "",
        "## Requirements",
        "",
    ]
    for item in gate["requirements"]:
        lines.append(f"- `{item['sample_id']}`: `{item['status']}`")
    lines.extend(["", "## Next Best Steps", ""])
    for step in gate["next_best_steps"]:
        lines.append(f"- {step}")
    lines.extend(["", "## Boundary", "", gate["claim_boundary"], ""])
    return "\n".join(lines)
