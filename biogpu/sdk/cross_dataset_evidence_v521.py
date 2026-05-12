"""Cross-dataset BioSDK evidence pack, v5.21."""
from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


DEFAULT_OUT = Path("outputs/v521_cross_dataset_evidence_pack")
SDK_NAME = "BioSDK / Living Compute SDK"


@dataclass(frozen=True)
class CrossDatasetEvidenceSourceV521:
    source_id: str
    title: str
    source_family: str
    source_scope: str
    status: str
    proof_level: str
    sample_count: int
    unit_count: int | None
    feature_count: int | None
    observed_metric_name: str | None
    observed_metric: float | None
    shuffle_baseline_metric: float | None
    shuffle_p_value: float | None
    evidence_artifacts: tuple[str, ...]
    blockers: tuple[str, ...]
    next_action: str
    allowed_statement: str
    forbidden_statement: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _artifact(root: Path, relative_path: str) -> tuple[str, dict[str, Any], bool]:
    path = root / relative_path
    return relative_path, _read_json(path), path.exists()


def _present(paths: tuple[tuple[str, dict[str, Any], bool], ...]) -> tuple[str, ...]:
    return tuple(relative_path for relative_path, _, exists in paths if exists)


def _int_value(data: dict[str, Any], key: str, default: int = 0) -> int:
    try:
        return int(data.get(key, default))
    except (TypeError, ValueError):
        return default


def _float_value(data: dict[str, Any] | None, key: str, default: float | None = None) -> float | None:
    if not isinstance(data, dict):
        return default
    try:
        value = data.get(key, default)
        return None if value is None else float(value)
    except (TypeError, ValueError):
        return default


def _metric(summary: dict[str, Any]) -> float | None:
    return _float_value(summary.get("observed"), "balanced_accuracy")


def _shuffle_median(summary: dict[str, Any]) -> float | None:
    return _float_value(summary.get("label_shuffle_baseline") or summary.get("condition_readout_shuffle_baseline"), "balanced_accuracy_median")


def _shuffle_p(summary: dict[str, Any]) -> float | None:
    return _float_value(summary.get("label_shuffle_baseline") or summary.get("condition_readout_shuffle_baseline"), "p_value_balanced_accuracy_gt_shuffle")


def _is_benchmark(status: str) -> bool:
    return status in {
        "benchmark_available",
        "validated_benchmark_available",
        "raw_benchmark_available",
    }


def _is_ready_source(status: str) -> bool:
    return status in {
        "benchmark_available",
        "validated_benchmark_available",
        "raw_benchmark_available",
        "validated_readonly_samples",
        "real_external_ready",
    }


def _zenodo_raw_source(root: Path) -> CrossDatasetEvidenceSourceV521:
    v56 = _artifact(root, "outputs/v56_raw_hdf5_structure/V56_RAW_HDF5_STRUCTURE_SUMMARY.json")
    v58 = _artifact(root, "outputs/v58_raw_native_benchmark/V58_RAW_NATIVE_FEATURE_SUMMARY.json")
    v59 = _artifact(root, "outputs/v59_raw_native_stability_audit/V59_RAW_NATIVE_STABILITY_SUMMARY.json")
    v56_json, v58_json, v59_json = v56[1], v58[1], v59[1]
    ready = (
        v56_json.get("overall_status") == "raw_hdf5_events_available"
        and v58_json.get("overall_status") == "raw_native_features_available"
        and v59_json.get("split_half_repeatability_status") == "split_half_repeatability_available"
    )
    blockers: list[str] = []
    if not ready:
        blockers.append("raw HDF5 structure, feature extraction or repeatability artifacts are missing/incomplete")
    if v59_json.get("target_readout_signal_status") == "not_supported":
        blockers.append("target-level decoding signal is explicitly not supported on the current sparse repeated-target subset")
    return CrossDatasetEvidenceSourceV521(
        source_id="zenodo_raw_mea",
        title="Zenodo raw MEA HDF5 event-window runtime",
        source_family="zenodo_public_raw_hdf5",
        source_scope="public_neurophysiology",
        status="raw_benchmark_available" if ready else "missing_or_incomplete",
        proof_level="raw_hdf5_structure_features_repeatability" if ready else "missing_artifact",
        sample_count=_int_value(v58_json, "feature_row_count"),
        unit_count=None,
        feature_count=_int_value(v58_json, "feature_count") if v58_json else None,
        observed_metric_name="split_half_cosine_median" if ready else None,
        observed_metric=_float_value(v59_json, "split_half_cosine_median"),
        shuffle_baseline_metric=None,
        shuffle_p_value=None,
        evidence_artifacts=_present((v56, v58, v59)),
        blockers=tuple(blockers),
        next_action="Acquire stronger repeated-target raw coverage or exact raw/preprocessed overlap before any target-decoding claim.",
        allowed_statement="BioSDK has raw public MEA HDF5 inspection, event-window features and repeatability evidence.",
        forbidden_statement="The raw Zenodo path proves live biology, GPU replacement, energy advantage or target-ID decoding.",
    )


def _dandi_source(root: Path) -> CrossDatasetEvidenceSourceV521:
    v515 = _artifact(root, "outputs/v515_dandi_nwb_task_validation/V515_DANDI_NWB_TASK_VALIDATION_SUMMARY.json")
    v516 = _artifact(root, "outputs/v516_dandi_nwb_task_benchmark/V516_DANDI_NWB_TASK_BENCHMARK_SUMMARY.json")
    validation, benchmark = v515[1], v516[1]
    ready = benchmark.get("overall_status") == "dandi_nwb_sdk_task_benchmark_available"
    validated = validation.get("overall_status") == "dandi_nwb_task_sample_validated"
    status = "benchmark_available" if ready else "validated_sample_no_benchmark" if validated else "missing_or_incomplete"
    blockers: list[str] = []
    if not ready:
        blockers.append("DANDI/NWB task benchmark artifact is missing or incomplete")
    blockers.append("single public DANDI NWB task sample only; not multi-dandiset proof")
    return CrossDatasetEvidenceSourceV521(
        source_id="dandi_nwb_task",
        title="DANDI NWB task-window benchmark",
        source_family="dandi_public_nwb",
        source_scope="public_neurophysiology",
        status=status,
        proof_level="single_sample_task_window_readout" if ready else "validated_sample" if validated else "missing_artifact",
        sample_count=_int_value(benchmark, "sample_count", _int_value(validation, "total_exported_window_count")),
        unit_count=_int_value(benchmark, "unit_count", _int_value(validation, "total_unit_count")) if (benchmark or validation) else None,
        feature_count=_int_value(benchmark, "feature_count") if benchmark else None,
        observed_metric_name="balanced_accuracy" if ready else None,
        observed_metric=_metric(benchmark),
        shuffle_baseline_metric=_shuffle_median(benchmark),
        shuffle_p_value=_shuffle_p(benchmark),
        evidence_artifacts=_present((v515, v516)),
        blockers=tuple(blockers),
        next_action="Add a second public NWB task source or promote the DANDI flow into installable SDK examples.",
        allowed_statement="BioSDK can validate one public DANDI/NWB task sample and run a bounded task readout.",
        forbidden_statement="The DANDI path proves all NWB datasets, all wetware APIs or full BioSDK readiness.",
    )


def _allen_source(root: Path) -> CrossDatasetEvidenceSourceV521:
    v518 = _artifact(root, "outputs/v518_allen_orientation_gate/V518_ALLEN_ORIENTATION_GATE_SUMMARY.json")
    v520 = _artifact(root, "outputs/v520_allen_orientation_benchmark/V520_ALLEN_ORIENTATION_BENCHMARK_SUMMARY.json")
    validation, benchmark = v518[1], v520[1]
    ready = benchmark.get("overall_status") == "allen_orientation_sdk_benchmark_available"
    validated = validation.get("overall_status") == "allen_orientation_sample_validated"
    status = "benchmark_available" if ready else "validated_sample_no_benchmark" if validated else "missing_or_incomplete"
    blockers: list[str] = []
    if not ready:
        blockers.append("Allen orientation benchmark artifact is missing or incomplete")
    blockers.append("single Allen visual-coding session only; not full Allen cache or multi-session proof")
    return CrossDatasetEvidenceSourceV521(
        source_id="allen_visual_coding_orientation",
        title="Allen visual-coding orientation benchmark",
        source_family="allen_public_visual_coding_nwb",
        source_scope="public_neurophysiology",
        status=status,
        proof_level="single_session_orientation_readout" if ready else "validated_orientation_sample" if validated else "missing_artifact",
        sample_count=_int_value(benchmark, "sample_count", _int_value(validation, "validated_sample_count")),
        unit_count=_int_value(benchmark, "selected_unit_count") if benchmark else _int_value(validation, "validated_sample_count") if validation else None,
        feature_count=_int_value(benchmark, "feature_count") if benchmark else None,
        observed_metric_name="balanced_accuracy" if ready else None,
        observed_metric=_metric(benchmark),
        shuffle_baseline_metric=_shuffle_median(benchmark),
        shuffle_p_value=_shuffle_p(benchmark),
        evidence_artifacts=_present((v518, v520)),
        blockers=tuple(blockers),
        next_action="Add a second Allen session only if public multi-session evidence becomes the next bottleneck.",
        allowed_statement="BioSDK can validate one public Allen visual-coding session and run an orientation readout.",
        forbidden_statement="The Allen path proves the full Allen cache, all visual coding experiments or BiC OS readiness.",
    )


def _external_readonly_source(root: Path) -> CrossDatasetEvidenceSourceV521:
    v517 = _artifact(root, "outputs/v517_external_readonly_api_gate/V517_EXTERNAL_READONLY_API_SUMMARY.json")
    v524 = _artifact(root, "outputs/v524_external_export_validation/V524_EXTERNAL_EXPORT_VALIDATION_SUMMARY.json")
    summary = v517[1]
    validation = v524[1]
    real_ready = bool(summary.get("real_external_ready") or validation.get("real_external_ready"))
    mock_ready = bool(summary.get("all_mock_contracts_passed"))
    status = "real_external_ready" if real_ready else "mock_contract_only_real_required" if mock_ready else "missing_or_incomplete"
    blockers = tuple(str(item) for item in summary.get("required_real_external_next_steps", [])) or ("obtain one non-secret read-only token/export from a real external platform",)
    return CrossDatasetEvidenceSourceV521(
        source_id="external_readonly_api_or_export",
        title="External read-only API/export contract",
        source_family="external_readonly_api_or_vendor_export",
        source_scope="external_partner_or_vendor",
        status=status,
        proof_level="real_readonly_export" if real_ready else "mock_readonly_contract_write_denial" if mock_ready else "missing_artifact",
        sample_count=_int_value(validation, "validated_export_count", _int_value(summary, "real_export_file_count")),
        unit_count=None,
        feature_count=None,
        observed_metric_name=None,
        observed_metric=None,
        shuffle_baseline_metric=None,
        shuffle_p_value=None,
        evidence_artifacts=_present((v517, v524)),
        blockers=blockers if not real_ready else tuple(),
        next_action="Keep the validated export attached to SDK proof; live API/token proof remains separate." if real_ready else "Obtain one non-secret read-only token or export and rerun the v5.17/v5.24 gates without storing secrets.",
        allowed_statement="BioSDK has one validated non-secret read-only external export plus mock adapter write-denial contracts." if real_ready else "BioSDK has mock read-only adapter contracts and write-denial behavior for external platform shapes.",
        forbidden_statement="BioSDK has proven live external wetware/API control, closed-loop writes or BiC OS readiness from a read-only export.",
    )


def _vendor_upload_source(root: Path) -> CrossDatasetEvidenceSourceV521:
    v519 = _artifact(root, "outputs/v519_vendor_user_upload_gate/V519_VENDOR_USER_UPLOAD_GATE_SUMMARY.json")
    summary = v519[1]
    ready = summary.get("overall_status") == "vendor_user_upload_readonly_samples_validated"
    blockers = tuple(str(item) for item in summary.get("required_next_steps", [])) or ("place one safe read-only vendor export or user-upload fixture under data/external",)
    return CrossDatasetEvidenceSourceV521(
        source_id="vendor_user_upload_sample",
        title="Vendor/user-upload read-only sample intake",
        source_family="private_vendor_or_user_upload",
        source_scope="private_beta_or_user_supplied",
        status="validated_readonly_samples" if ready else summary.get("overall_status", "missing_or_incomplete"),
        proof_level="safe_readonly_upload_sample" if ready else "intake_contract_only",
        sample_count=_int_value(summary, "validated_sample_count"),
        unit_count=None,
        feature_count=None,
        observed_metric_name=None,
        observed_metric=None,
        shuffle_baseline_metric=None,
        shuffle_p_value=None,
        evidence_artifacts=_present((v519,)),
        blockers=tuple() if ready else blockers,
        next_action="Add one safe read-only vendor export or user fixture and rerun v5.19.",
        allowed_statement="BioSDK has a scanner and routing contract for safe read-only vendor/user files.",
        forbidden_statement="BioSDK has proven private/vendor portability without at least one real safe sample.",
    )


def build_cross_dataset_evidence_sources_v521(root: str | Path = ".") -> tuple[CrossDatasetEvidenceSourceV521, ...]:
    project_root = Path(root)
    return (
        _zenodo_raw_source(project_root),
        _dandi_source(project_root),
        _allen_source(project_root),
        _external_readonly_source(project_root),
        _vendor_upload_source(project_root),
    )


def build_cross_dataset_evidence_pack_v521(root: str | Path = ".") -> dict[str, Any]:
    project_root = Path(root)
    sources = build_cross_dataset_evidence_sources_v521(project_root)
    sample_gate = _artifact(project_root, "outputs/v514_sample_acquisition_gate/V514_SAMPLE_ACQUISITION_SUMMARY.json")[1]
    public_sources = [source for source in sources if source.source_scope == "public_neurophysiology"]
    public_benchmarks = [source for source in public_sources if _is_benchmark(source.status)]
    external_ready = any(source.source_id == "external_readonly_api_or_export" and source.status == "real_external_ready" for source in sources)
    vendor_ready = any(source.source_id == "vendor_user_upload_sample" and source.status == "validated_readonly_samples" for source in sources)
    blocker_rows = [
        {"source_id": source.source_id, "status": source.status, "blockers": list(source.blockers), "next_action": source.next_action}
        for source in sources
        if source.blockers or not _is_ready_source(source.status)
    ]
    public_ready = len(public_benchmarks) >= 3
    full_sample_proof_ready = bool(sample_gate.get("full_sample_proof_ready"))
    if public_ready and external_ready and vendor_ready:
        overall_status = "cross_dataset_sample_evidence_ready_full_biosdk_not_claimed"
    elif public_ready and vendor_ready and not external_ready:
        overall_status = "cross_dataset_public_and_user_upload_evidence_ready_external_blocked"
    elif public_ready and external_ready and not vendor_ready:
        overall_status = "cross_dataset_public_and_external_evidence_ready_vendor_blocked"
    elif public_ready:
        overall_status = "cross_dataset_public_evidence_ready_external_vendor_blocked"
    else:
        overall_status = "cross_dataset_evidence_incomplete"
    if external_ready and vendor_ready:
        next_best_build_step = "package the validated sample layer into SDK release-candidate docs while keeping full BioSDK/runtime claims blocked"
    elif vendor_ready and not external_ready:
        next_best_build_step = "close the real external read-only export/token blocker; user-upload evidence is now validated"
    elif external_ready and not vendor_ready:
        next_best_build_step = "add one safe vendor/user-upload sample; external read-only evidence is already present"
    else:
        next_best_build_step = "close the real external read-only export/token blocker or add one safe vendor/user-upload sample, then package v5.21 as public SDK examples"
    return {
        "version": "v5.21",
        "sdk_name": SDK_NAME,
        "phase": "cross_dataset_biosdk_evidence_pack",
        "overall_status": overall_status,
        "active_phase": "biosdk_public_core",
        "bic_os_phase_locked": True,
        "public_cross_dataset_evidence_ready": public_ready,
        "public_benchmark_source_count": len(public_benchmarks),
        "public_source_target": 3,
        "external_partner_evidence_ready": external_ready,
        "vendor_user_evidence_ready": vendor_ready,
        "full_sample_proof_ready": full_sample_proof_ready,
        "full_biosdk_ready": False,
        "source_count": len(sources),
        "blocker_count": len(blocker_rows),
        "missing_required_sample_ids": sample_gate.get("missing_required_sample_ids", []),
        "source_status_counts": _status_counts(sources),
        "source_ids": [source.source_id for source in sources],
        "sources": [source.to_dict() for source in sources],
        "blockers": blocker_rows,
        "direct_answer": {
            "is_public_biosdk_evidence_layer_ready": "yes" if public_ready else "not_yet",
            "is_full_biosdk_proven": "no",
            "is_bic_os_ready": "no",
            "should_download_full_public_datasets_now": "no_capped_representative_samples_are_enough_for_current_proof",
            "next_best_build_step": next_best_build_step,
        },
        "claim_boundary": "v5.21 aggregates validated local public neurophysiology evidence across Zenodo raw HDF5, DANDI NWB and Allen visual coding. It does not claim full BioSDK readiness, real external platform integration, private vendor portability or BiC OS readiness until the remaining blockers pass.",
    }


def _status_counts(sources: tuple[CrossDatasetEvidenceSourceV521, ...]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for source in sources:
        counts[source.status] = counts.get(source.status, 0) + 1
    return dict(sorted(counts.items()))


def write_cross_dataset_evidence_outputs_v521(audit: dict[str, Any], out_dir: str | Path = DEFAULT_OUT) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary_json": out / "V521_CROSS_DATASET_EVIDENCE_SUMMARY.json",
        "source_matrix_json": out / "V521_CROSS_DATASET_SOURCE_MATRIX.json",
        "source_matrix_csv": out / "V521_CROSS_DATASET_SOURCE_MATRIX.csv",
        "blocker_matrix_json": out / "V521_CROSS_DATASET_BLOCKER_MATRIX.json",
        "markdown_report": out / "BIOGPU_V521_CROSS_DATASET_EVIDENCE_REPORT.md",
    }
    summary = {key: value for key, value in audit.items() if key not in {"sources", "blockers"}}
    summary["blocker_source_ids"] = [row["source_id"] for row in audit["blockers"]]
    paths["summary_json"].write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["source_matrix_json"].write_text(json.dumps(audit["sources"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["blocker_matrix_json"].write_text(json.dumps(audit["blockers"], indent=2, ensure_ascii=False), encoding="utf-8")
    _write_source_csv(paths["source_matrix_csv"], audit["sources"])
    paths["markdown_report"].write_text(_markdown_report(audit), encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}


def _write_source_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "source_id",
        "title",
        "source_family",
        "source_scope",
        "status",
        "proof_level",
        "sample_count",
        "unit_count",
        "feature_count",
        "observed_metric_name",
        "observed_metric",
        "shuffle_baseline_metric",
        "shuffle_p_value",
        "evidence_artifacts",
        "blockers",
        "next_action",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            payload = dict(row)
            payload["evidence_artifacts"] = " | ".join(str(value) for value in row.get("evidence_artifacts", []))
            payload["blockers"] = " | ".join(str(value) for value in row.get("blockers", []))
            writer.writerow({key: payload.get(key) for key in fieldnames})


def _markdown_report(audit: dict[str, Any]) -> str:
    answer = audit["direct_answer"]
    lines = [
        "# BioGPU-Core v5.21 Cross-Dataset Evidence Pack",
        "",
        "## Direct Answer",
        "",
        f"- Public BioSDK evidence layer ready: `{answer['is_public_biosdk_evidence_layer_ready']}`",
        f"- Full BioSDK proven: `{answer['is_full_biosdk_proven']}`",
        f"- BiC OS ready: `{answer['is_bic_os_ready']}`",
        f"- Download full public datasets now: `{answer['should_download_full_public_datasets_now']}`",
        f"- Next best build step: {answer['next_best_build_step']}",
        "",
        "## Overall Status",
        "",
        f"`{audit['overall_status']}`",
        "",
        "## Source Matrix",
        "",
        "| Source | Status | Samples | Features | Metric | Blockers |",
        "| --- | --- | ---: | ---: | --- | --- |",
    ]
    for row in audit["sources"]:
        metric = ""
        if row.get("observed_metric_name") and row.get("observed_metric") is not None:
            metric = f"{row['observed_metric_name']}={row['observed_metric']}"
        blocker_text = "; ".join(str(item) for item in row.get("blockers", []))
        lines.append(f"| `{row['source_id']}` | `{row['status']}` | {row.get('sample_count', 0)} | {row.get('feature_count') or ''} | {metric} | {blocker_text} |")
    lines.extend([
        "",
        "## Boundary",
        "",
        audit["claim_boundary"],
        "",
    ])
    return "\n".join(lines)
