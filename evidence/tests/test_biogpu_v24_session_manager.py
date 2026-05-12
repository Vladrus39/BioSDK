
import json
import zipfile
from pathlib import Path

from biogpu.runtime.session_manager_v24 import (
    BioGPUAuditLog,
    build_v24_manifest,
    validate_manifest,
    write_v24_session_outputs,
)


def test_v24_manifest_has_modes_and_goal():
    manifest = build_v24_manifest("dry_run")
    assert manifest.version == "v2.4"
    assert manifest.run_mode == "dry_run"
    assert "BioGPU" in manifest.project_goal
    assert manifest.benchmark_ids


def test_v24_manifest_validates_with_v23_registry():
    manifest = build_v24_manifest("replay", ["B0_target_vs_random_electrode"])
    assert validate_manifest(manifest) == []


def test_v24_rejects_unknown_benchmark():
    manifest = build_v24_manifest("dry_run", ["missing_task"])
    errors = validate_manifest(manifest)
    assert any("unknown benchmark_id" in e for e in errors)


def test_v24_audit_log_jsonl():
    audit = BioGPUAuditLog()
    audit.add("created", "ok", a=1)
    audit.add("validated", "ok")
    text = audit.to_jsonl()
    assert text.count("\n") == 2
    assert "created" in text


def test_v24_outputs_and_bundle(tmp_path: Path):
    summary = write_v24_session_outputs(tmp_path, run_mode="dry_run")
    assert summary["run_mode"] == "dry_run"
    assert summary["validation_errors"] == []
    assert (tmp_path / "run_manifest.json").exists()
    assert (tmp_path / "audit_log.jsonl").exists()
    assert (tmp_path / "session_summary.json").exists()
    bundle = tmp_path / "biogpu_v24_result_bundle.zip"
    assert bundle.exists()
    with zipfile.ZipFile(bundle) as z:
        names = set(z.namelist())
    assert "run_manifest.json" in names
    assert "audit_log.jsonl" in names
    assert "session_summary.json" in names


def test_v24_summary_is_json_serializable(tmp_path: Path):
    summary = write_v24_session_outputs(tmp_path, run_mode="power_pc", hardware_profile="8c_32gb")
    loaded = json.loads((tmp_path / "session_summary.json").read_text())
    assert loaded["session_id"] == summary["session_id"]
    assert loaded["run_mode"] == "power_pc"
    assert loaded["result_bundle_sha256"]
