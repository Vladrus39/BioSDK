from __future__ import annotations

from pathlib import Path

from biogpu.benchmarks.biogpu_v542_signed_artifact_provenance import run
from biogpu.evidence.ledger_v53 import sha256_file
from biogpu.sdk.artifact_provenance_v542 import (
    build_artifact_manifest_v542,
    build_artifact_provenance_policy_v542,
    build_provenance_statement_v542,
    run_provenance_tamper_probe_v542,
    run_signed_artifact_provenance_workflow_v542,
    sign_provenance_statement_v542,
    validate_signature_envelope_v542,
    write_signed_artifact_provenance_outputs_v542,
)


def _fake_v541_audit(tmp_path: Path) -> dict[str, object]:
    wheel = tmp_path / "biogpu_core-5.0.0-py3-none-any.whl"
    wheel.write_bytes(b"fake wheel bytes for v542 contract tests")
    digest = sha256_file(wheel)
    return {
        "overall_status": "clean_room_install_report_contract_ready_external_not_claimed",
        "clean_room_install_report_contract_ready": True,
        "local_clean_room_install_probe_ready": True,
        "clean_room_audit_sha256": "a" * 64,
        "local_install_probe": {
            "wheel_path": str(wheel),
            "probe_sha256": "b" * 64,
            "wheel_manifest": {
                "wheel_inspection_ready": True,
                "wheel_name": wheel.name,
                "wheel_sha256": digest,
                "file_count": 1,
            },
        },
    }


def test_v542_policy_keeps_external_signature_blocked():
    policy = build_artifact_provenance_policy_v542()

    assert policy["policy_ready"] is True
    assert policy["policy"]["local_signature_required"] is True
    assert policy["policy"]["trusted_external_signature_ready"] is False
    assert policy["transparency_log_ready"] is False
    assert policy["full_biosdk_ready"] is False


def test_v542_artifact_manifest_uses_wheel_digest(tmp_path):
    audit = _fake_v541_audit(tmp_path)
    manifest = build_artifact_manifest_v542(Path.cwd(), audit)

    assert manifest["artifact_manifest_ready"] is True
    assert manifest["artifact_kind"] == "wheel"
    assert manifest["artifact_sha256"] == audit["local_install_probe"]["wheel_manifest"]["wheel_sha256"]
    assert manifest["errors"] == []


def test_v542_local_signature_validates_and_tamper_fails(tmp_path):
    audit = _fake_v541_audit(tmp_path)
    manifest = build_artifact_manifest_v542(Path.cwd(), audit)
    statement = build_provenance_statement_v542(Path.cwd(), manifest, audit)
    envelope = sign_provenance_statement_v542(statement)
    validation = validate_signature_envelope_v542(envelope)
    tamper_probe = run_provenance_tamper_probe_v542(envelope)

    assert validation["signature_validation_ready"] is True
    assert validation["payload_hash_valid"] is True
    assert validation["local_signature_valid"] is True
    assert tamper_probe["tamper_detection_ready"] is True


def test_v542_external_signature_claim_is_rejected(tmp_path):
    audit = _fake_v541_audit(tmp_path)
    manifest = build_artifact_manifest_v542(Path.cwd(), audit)
    statement = build_provenance_statement_v542(Path.cwd(), manifest, audit)
    envelope = sign_provenance_statement_v542(statement)
    envelope["trusted_external_signature_ready"] = True
    validation = validate_signature_envelope_v542(envelope)

    assert validation["signature_validation_ready"] is False
    assert "trusted_external_signature_must_not_be_claimed" in validation["boundary_errors"]


def test_v542_workflow_ready_without_claiming_full_sdk(tmp_path):
    audit = run_signed_artifact_provenance_workflow_v542(Path.cwd(), tmp_path / "out")

    assert audit["overall_status"] == "signed_artifact_provenance_contract_ready_external_not_claimed"
    assert audit["signed_artifact_provenance_contract_ready"] is True
    assert audit["v541_dependency_ready"] is True
    assert audit["local_signature_ready"] is True
    assert audit["signature_validation_ready"] is True
    assert audit["tamper_detection_ready"] is True
    assert audit["trusted_external_signature_ready"] is False
    assert audit["full_biosdk_ready"] is False
    assert audit["bic_os_phase_locked"] is True


def test_v542_outputs_are_written(tmp_path):
    audit = run_signed_artifact_provenance_workflow_v542(Path.cwd(), tmp_path / "workflow")
    paths = write_signed_artifact_provenance_outputs_v542(audit, tmp_path / "out")

    assert Path(paths["summary_json"]).exists()
    assert Path(paths["policy_json"]).exists()
    assert Path(paths["artifact_manifest_json"]).exists()
    assert Path(paths["provenance_statement_json"]).exists()
    assert Path(paths["signature_envelope_json"]).exists()
    assert Path(paths["signature_validation_json"]).exists()
    assert Path(paths["tamper_probe_json"]).exists()
    assert Path(paths["materials_csv"]).exists()
    assert "Signed Artifact Provenance Contract" in Path(paths["markdown_report"]).read_text(encoding="utf-8")


def test_v542_runner_writes_summary(tmp_path):
    result = run(root=Path.cwd(), out_dir=tmp_path / "out")

    assert result["summary"]["signed_artifact_provenance_contract_ready"] is True
    assert (tmp_path / "out" / "V542_SIGNED_ARTIFACT_PROVENANCE_SUMMARY.json").exists()