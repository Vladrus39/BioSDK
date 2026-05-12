from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


SAFETY_BOUNDARY_V50 = [
    "offline public-data replay only",
    "no live biological actuation",
    "no wet-lab protocol or culturing recipe",
    "no vendor pinout/wiring procedure",
    "no GPU replacement or energy superiority claim",
]


@dataclass(frozen=True)
class BundleArtifactV50:
    path: str
    category: str
    required: bool = True


DEFAULT_BUNDLE_ARTIFACTS_V50: tuple[BundleArtifactV50, ...] = (
    BundleArtifactV50("README.md", "project_entry"),
    BundleArtifactV50("docs/MASTER_PROJECT_PLAN_V50.md", "project_plan"),
    BundleArtifactV50("docs/V43_TO_V50_CONSOLIDATION.md", "project_plan"),
    BundleArtifactV50("RUN_RESULTS_REALDATA_V50.md", "evidence_report"),
    BundleArtifactV50("PROJECT_INVENTORY_V50.md", "inventory"),
    BundleArtifactV50("data/assets/zenodo_14363732_preprocessed.asset.json", "dataset_manifest"),
    BundleArtifactV50("data/assets/zenodo_14363732_preprocessed_sample.asset.json", "dataset_manifest"),
    BundleArtifactV50("scripts/run_biogpu_v50_pc_validation_smoke.ps1", "runner"),
    BundleArtifactV50("scripts/run_biogpu_v50_dataset_asset_validation.ps1", "runner"),
    BundleArtifactV50("scripts/run_biogpu_v50_pc_validation_compact.ps1", "runner"),
    BundleArtifactV50("scripts/run_biogpu_v50_pc_validation_full_shuffle.ps1", "runner"),
    BundleArtifactV50("outputs/v50_pc_validation_smoke/windows_pc_validation_smoke_summary.json", "validation_output"),
    BundleArtifactV50("outputs/v50_pc_validation_compact/windows_pc_validation_compact_summary.json", "validation_output"),
    BundleArtifactV50("outputs/v50_dataset_asset_validation/v46_clean_release_summary.json", "validation_output"),
    BundleArtifactV50("outputs/powerpc_full_shuffle_1000/RUN_MANIFEST_FULL_SHUFFLE_1000_WINDOWS.json", "full_shuffle_output"),
    BundleArtifactV50("outputs/powerpc_full_shuffle_1000/WINDOWS_FULL_SHUFFLE_1000_RUN_SUMMARY.json", "full_shuffle_output"),
    BundleArtifactV50("outputs/powerpc_full_shuffle_1000/v36_summary.json", "full_shuffle_output"),
    BundleArtifactV50("outputs/powerpc_full_shuffle_1000/v36_config.json", "full_shuffle_output"),
    BundleArtifactV50("outputs/powerpc_full_shuffle_1000/v36_system_info.json", "full_shuffle_output"),
    BundleArtifactV50("outputs/powerpc_full_shuffle_1000/v36_lineage_audit.csv", "full_shuffle_output"),
    BundleArtifactV50("outputs/powerpc_full_shuffle_1000/v36_lineage_splits.csv", "full_shuffle_output"),
    BundleArtifactV50("outputs/powerpc_full_shuffle_1000/v36_lineage_sweep_results.csv", "full_shuffle_output"),
    BundleArtifactV50("outputs/powerpc_full_shuffle_1000/v36_lineage_shuffle_controls.csv", "full_shuffle_output"),
    BundleArtifactV50("outputs/powerpc_full_shuffle_1000/v36_bootstrap_ci_by_decoder.csv", "full_shuffle_output"),
    BundleArtifactV50("outputs/powerpc_full_shuffle_1000/v36_bootstrap_ci_by_ablation.csv", "full_shuffle_output"),
    BundleArtifactV50("outputs/powerpc_full_shuffle_1000/BIOGPU_V36_LINEAGE_BOOTSTRAP_REPORT.md", "full_shuffle_output"),
    BundleArtifactV50("outputs/powerpc_full_shuffle_1000/biogpu_v36_lineage_bootstrap_bundle.zip", "nested_result_bundle"),
    BundleArtifactV50("scripts/run_biogpu_v50_pc_validation_extended_methods.ps1", "runner", required=False),
    BundleArtifactV50("outputs/powerpc_extended_methods_5000/RUN_MANIFEST_EXTENDED_METHODS_5000_WINDOWS.json", "extended_methods_output", required=False),
    BundleArtifactV50("outputs/powerpc_extended_methods_5000/WINDOWS_EXTENDED_METHODS_5000_RUN_SUMMARY.json", "extended_methods_output", required=False),
    BundleArtifactV50("outputs/powerpc_extended_methods_5000/v36_summary.json", "extended_methods_output", required=False),
    BundleArtifactV50("outputs/powerpc_extended_methods_5000/v36_config.json", "extended_methods_output", required=False),
    BundleArtifactV50("outputs/powerpc_extended_methods_5000/v36_system_info.json", "extended_methods_output", required=False),
    BundleArtifactV50("outputs/powerpc_extended_methods_5000/v36_lineage_audit.csv", "extended_methods_output", required=False),
    BundleArtifactV50("outputs/powerpc_extended_methods_5000/v36_lineage_splits.csv", "extended_methods_output", required=False),
    BundleArtifactV50("outputs/powerpc_extended_methods_5000/v36_lineage_sweep_results.csv", "extended_methods_output", required=False),
    BundleArtifactV50("outputs/powerpc_extended_methods_5000/v36_lineage_shuffle_controls.csv", "extended_methods_output", required=False),
    BundleArtifactV50("outputs/powerpc_extended_methods_5000/v36_bootstrap_ci_by_decoder.csv", "extended_methods_output", required=False),
    BundleArtifactV50("outputs/powerpc_extended_methods_5000/v36_bootstrap_ci_by_ablation.csv", "extended_methods_output", required=False),
    BundleArtifactV50("outputs/powerpc_extended_methods_5000/BIOGPU_V36_LINEAGE_BOOTSTRAP_REPORT.md", "extended_methods_output", required=False),
    BundleArtifactV50("outputs/powerpc_extended_methods_5000/biogpu_v36_lineage_bootstrap_bundle.zip", "nested_result_bundle", required=False),
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _artifact_record(project_root: Path, artifact: BundleArtifactV50) -> dict[str, Any]:
    path = project_root / artifact.path
    return {
        "path": artifact.path.replace("\\", "/"),
        "category": artifact.category,
        "required": artifact.required,
        "size_bytes": path.stat().st_size,
        "sha256": _sha256(path),
    }


def collect_bundle_artifacts_v50(
    project_root: Path,
    artifacts: Iterable[BundleArtifactV50] = DEFAULT_BUNDLE_ARTIFACTS_V50,
) -> tuple[list[dict[str, Any]], list[str]]:
    project_root = project_root.resolve()
    records: list[dict[str, Any]] = []
    missing_optional: list[str] = []
    missing_required: list[str] = []
    for artifact in artifacts:
        path = project_root / artifact.path
        if path.is_file():
            records.append(_artifact_record(project_root, artifact))
        elif artifact.required:
            missing_required.append(artifact.path)
        else:
            missing_optional.append(artifact.path)
    if missing_required:
        joined = ", ".join(missing_required)
        raise FileNotFoundError(f"Missing required v5.0 bundle artifacts: {joined}")
    return records, missing_optional


def _evidence_highlights(project_root: Path) -> dict[str, Any]:
    full_shuffle = _load_json(project_root / "outputs/powerpc_full_shuffle_1000/v36_summary.json") or {}
    extended = _load_json(project_root / "outputs/powerpc_extended_methods_5000/v36_summary.json") or {}
    dataset = _load_json(project_root / "outputs/v50_dataset_asset_validation/v46_clean_release_summary.json") or {}
    run_summary = _load_json(project_root / "outputs/powerpc_full_shuffle_1000/WINDOWS_FULL_SHUFFLE_1000_RUN_SUMMARY.json") or {}
    extended_run_summary = _load_json(project_root / "outputs/powerpc_extended_methods_5000/WINDOWS_EXTENDED_METHODS_5000_RUN_SUMMARY.json") or {}
    best = full_shuffle.get("best_run", {})
    extended_best = extended.get("best_run", {})
    full_dataset = dataset.get("full_dataset_validation", {})
    full_profile = full_dataset.get("profile", {})
    extracted_dataset = dataset.get("extracted_dataset_validation", {})
    extracted_profile = extracted_dataset.get("profile", {})
    return {
        "data_gate_status": dataset.get("data_gate_status"),
        "official_zip_valid": full_dataset.get("valid"),
        "official_zip_sha256": full_profile.get("sha256"),
        "official_zip_recording_count": full_profile.get("recording_count"),
        "extracted_dataset_valid": extracted_dataset.get("valid"),
        "extracted_dataset_validation_level": extracted_dataset.get("validation_level"),
        "extracted_dataset_file_count": extracted_profile.get("file_count"),
        "full_shuffle_status": run_summary.get("status"),
        "full_shuffle_elapsed_seconds": run_summary.get("elapsed_seconds"),
        "full_shuffle_sweep_rows": full_shuffle.get("sweep_run_count"),
        "full_shuffle_shuffle_count": full_shuffle.get("config", {}).get("shuffle_count"),
        "full_shuffle_bootstrap_iterations": full_shuffle.get("config", {}).get("bootstrap_iterations"),
        "best_split": best.get("split_id"),
        "best_decoder": best.get("decoder_id"),
        "best_ablation": best.get("ablation_id"),
        "best_accuracy": best.get("accuracy"),
        "best_balanced_accuracy": best.get("balanced_accuracy"),
        "best_empirical_p_value": best.get("empirical_p_value_shuffled_ge_real"),
        "best_improvement_vs_shuffle_mean": best.get("improvement_vs_shuffle_mean"),
        "extended_methods_status": extended_run_summary.get("status"),
        "extended_methods_profile": extended_run_summary.get("profile"),
        "extended_methods_elapsed_seconds": extended_run_summary.get("elapsed_seconds"),
        "extended_methods_sweep_rows": extended.get("sweep_run_count"),
        "extended_methods_shuffle_count": extended.get("config", {}).get("shuffle_count"),
        "extended_methods_bootstrap_iterations": extended.get("config", {}).get("bootstrap_iterations"),
        "extended_methods_best_balanced_accuracy": extended_best.get("balanced_accuracy"),
        "extended_methods_best_empirical_p_value": extended_best.get("empirical_p_value_shuffled_ge_real"),
    }


def build_manifest_v50(
    project_root: Path,
    artifact_records: list[dict[str, Any]],
    missing_optional: list[str],
) -> dict[str, Any]:
    return {
        "bundle_id": "BIOGPU_CORE_V50_PC_VALIDATION_BUNDLE",
        "version": "v5.0",
        "created_utc": _utc_now(),
        "project_root_name": project_root.resolve().name,
        "safety_boundary": SAFETY_BOUNDARY_V50,
        "evidence_highlights": _evidence_highlights(project_root.resolve()),
        "artifact_count": len(artifact_records),
        "missing_optional_artifacts": missing_optional,
        "artifacts": artifact_records,
    }


def build_pc_validation_bundle_v50(
    project_root: Path,
    out_dir: Path,
    bundle_name: str = "biogpu_v50_pc_validation_bundle.zip",
    artifacts: Iterable[BundleArtifactV50] = DEFAULT_BUNDLE_ARTIFACTS_V50,
) -> dict[str, Any]:
    project_root = project_root.resolve()
    out_dir = out_dir if out_dir.is_absolute() else project_root / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    artifact_records, missing_optional = collect_bundle_artifacts_v50(project_root, artifacts)
    manifest = build_manifest_v50(project_root, artifact_records, missing_optional)
    manifest_path = out_dir / "V50_PC_VALIDATION_BUNDLE_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    bundle_path = out_dir / bundle_name
    with zipfile.ZipFile(bundle_path, "w", zipfile.ZIP_DEFLATED) as bundle_zip:
        bundle_zip.write(manifest_path, arcname=manifest_path.name)
        for record in artifact_records:
            source = project_root / record["path"]
            bundle_zip.write(source, arcname="artifacts/" + record["path"])
    bundle_sha256 = _sha256(bundle_path)
    summary = {
        "status": "ok",
        "bundle": str(bundle_path.relative_to(project_root)).replace("\\", "/"),
        "manifest": str(manifest_path.relative_to(project_root)).replace("\\", "/"),
        "bundle_size_bytes": bundle_path.stat().st_size,
        "bundle_sha256": bundle_sha256,
        "artifact_count": len(artifact_records),
        "created_utc": _utc_now(),
    }
    summary_path = out_dir / "V50_PC_VALIDATION_BUNDLE_SUMMARY.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Package BioGPU-Core v5.0 PC validation evidence bundle")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--out-dir", default="outputs/v50_pc_validation_bundle")
    parser.add_argument("--bundle-name", default="biogpu_v50_pc_validation_bundle.zip")
    args = parser.parse_args()
    summary = build_pc_validation_bundle_v50(Path(args.project_root), Path(args.out_dir), args.bundle_name)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()