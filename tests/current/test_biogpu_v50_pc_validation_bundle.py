import json
import zipfile
from pathlib import Path

import pytest

from biogpu.release.pc_validation_bundle_v50 import (
    BundleArtifactV50,
    build_pc_validation_bundle_v50,
    collect_bundle_artifacts_v50,
)


def write_file(root: Path, relative_path: str, content: str) -> Path:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def test_v50_pc_validation_bundle_packages_manifest_and_artifacts(tmp_path):
    artifacts = (
        BundleArtifactV50("README.md", "project_entry"),
        BundleArtifactV50("outputs/example_summary.json", "validation_output"),
    )
    write_file(tmp_path, "README.md", "# example\n")
    write_file(tmp_path, "outputs/example_summary.json", json.dumps({"status": "ok"}))

    summary = build_pc_validation_bundle_v50(
        tmp_path,
        Path("outputs/v50_pc_validation_bundle"),
        artifacts=artifacts,
    )

    assert summary["status"] == "ok"
    assert summary["artifact_count"] == 2
    assert summary["bundle_sha256"]

    bundle_path = tmp_path / summary["bundle"]
    manifest_path = tmp_path / summary["manifest"]
    assert bundle_path.exists()
    assert manifest_path.exists()

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["bundle_id"] == "BIOGPU_CORE_V50_PC_VALIDATION_BUNDLE"
    assert manifest["artifact_count"] == 2
    assert manifest["artifacts"][0]["sha256"]

    with zipfile.ZipFile(bundle_path) as bundle_zip:
        names = set(bundle_zip.namelist())
    assert "V50_PC_VALIDATION_BUNDLE_MANIFEST.json" in names
    assert "artifacts/README.md" in names
    assert "artifacts/outputs/example_summary.json" in names


def test_v50_pc_validation_bundle_requires_declared_artifacts(tmp_path):
    artifacts = (BundleArtifactV50("missing.json", "validation_output"),)
    with pytest.raises(FileNotFoundError):
        collect_bundle_artifacts_v50(tmp_path, artifacts)


def test_v50_pc_validation_bundle_allows_missing_optional_artifacts(tmp_path):
    artifacts = (
        BundleArtifactV50("README.md", "project_entry"),
        BundleArtifactV50("outputs/optional.json", "extended_methods_output", required=False),
    )
    write_file(tmp_path, "README.md", "# example\n")

    records, missing_optional = collect_bundle_artifacts_v50(tmp_path, artifacts)

    assert len(records) == 1
    assert missing_optional == ["outputs/optional.json"]


def test_v50_pc_validation_bundle_reads_powershell_bom_json(tmp_path):
    artifacts = (
        BundleArtifactV50("README.md", "project_entry"),
        BundleArtifactV50("outputs/powerpc_full_shuffle_1000/v36_summary.json", "full_shuffle_output"),
        BundleArtifactV50("outputs/powerpc_full_shuffle_1000/WINDOWS_FULL_SHUFFLE_1000_RUN_SUMMARY.json", "full_shuffle_output"),
    )
    write_file(tmp_path, "README.md", "# example\n")
    write_file(
        tmp_path,
        "outputs/powerpc_full_shuffle_1000/v36_summary.json",
        json.dumps({"best_run": {"balanced_accuracy": 0.9}, "sweep_run_count": 1}),
    )
    run_summary_path = tmp_path / "outputs/powerpc_full_shuffle_1000/WINDOWS_FULL_SHUFFLE_1000_RUN_SUMMARY.json"
    run_summary_path.parent.mkdir(parents=True, exist_ok=True)
    run_summary_path.write_text('\ufeff{"status":"ok"}', encoding="utf-8")

    summary = build_pc_validation_bundle_v50(
        tmp_path,
        Path("outputs/v50_pc_validation_bundle"),
        artifacts=artifacts,
    )
    manifest_path = tmp_path / summary["manifest"]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert manifest["evidence_highlights"]["full_shuffle_status"] == "ok"
    assert manifest["evidence_highlights"]["best_balanced_accuracy"] == 0.9