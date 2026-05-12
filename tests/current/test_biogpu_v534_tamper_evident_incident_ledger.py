from __future__ import annotations

from pathlib import Path

from biogpu.benchmarks.biogpu_v534_tamper_evident_incident_ledger import run
from biogpu.runtime.incident_ledger_v534 import (
    build_incident_ledger_v534,
    run_incident_ledger_tamper_probe_v534,
    run_tamper_evident_incident_ledger_workflow_v534,
    validate_incident_ledger_chain_v534,
    write_tamper_evident_incident_ledger_outputs_v534,
)


def _minimal_v533_audit() -> dict:
    return {
        "version": "v5.33",
        "overall_status": "operator_incident_retention_proof_ready_runtime_not_claimed",
        "operator_incident_retention_ready": True,
        "active_incident_id": "incident-test",
        "timeline": {
            "opened_incident": {"incident_id": "incident-test", "status": "open", "summary": "opened"},
            "acknowledgement_action": {"action_id": "ack-test", "incident_id": "incident-test", "action": "acknowledge", "accepted": True, "note": "ack"},
            "resolution_action": {"action_id": "res-test", "incident_id": "incident-test", "action": "resolve", "accepted": True, "note": "resolved"},
            "incidents": [{"incident_id": "incident-test", "status": "resolved"}],
            "actions": [],
        },
        "retention_manifest": {"manifest_sha256": "retention-test-sha", "non_destructive_full_export": True},
        "incident_audit_bundle": {"bundle_sha256": "bundle-test-sha", "bundle_ready": True},
        "production_incident_retention_ready": False,
    }


def test_v534_builds_valid_incident_ledger_chain():
    ledger = build_incident_ledger_v534(_minimal_v533_audit())
    validation = validate_incident_ledger_chain_v534(ledger)

    assert ledger["entry_count"] == 5
    assert validation["valid"] is True
    assert validation["retention_manifest_anchored"] is True
    assert validation["local_signature_validation_ready"] is True


def test_v534_tamper_probe_detects_payload_mutation():
    ledger = build_incident_ledger_v534(_minimal_v533_audit())
    probe = run_incident_ledger_tamper_probe_v534(ledger)

    assert probe["tamper_probe_ready"] is True
    assert probe["tampered_validation_valid"] is False
    assert probe["detected_issue_count"] >= 1


def test_v534_workflow_ready_but_not_production_incident_ledger(tmp_path):
    audit = run_tamper_evident_incident_ledger_workflow_v534(tmp_path)

    assert audit["overall_status"] == "tamper_evident_incident_ledger_proof_ready_runtime_not_claimed"
    assert audit["tamper_evident_incident_ledger_ready"] is True
    assert audit["incident_ledger_chain_valid"] is True
    assert audit["retention_manifest_anchored"] is True
    assert audit["tamper_detection_passed"] is True
    assert audit["production_incident_ledger_ready"] is False
    assert audit["production_biocompute_runtime_ready"] is False
    assert audit["bic_os_phase_locked"] is True


def test_v534_write_outputs(tmp_path):
    audit = run_tamper_evident_incident_ledger_workflow_v534(tmp_path)

    paths = write_tamper_evident_incident_ledger_outputs_v534(audit, tmp_path / "out")
    assert Path(paths["summary_json"]).exists()
    assert Path(paths["ledger_json"]).exists()
    assert Path(paths["validation_json"]).exists()
    assert Path(paths["tamper_probe_json"]).exists()
    assert Path(paths["entries_csv"]).exists()
    assert "Tamper-Evident" in Path(paths["markdown_report"]).read_text(encoding="utf-8")


def test_v534_runner_writes_summary(tmp_path):
    result = run(root=tmp_path, out_dir=tmp_path / "out")

    assert result["summary"]["tamper_evident_incident_ledger_ready"] is True
    assert (tmp_path / "out" / "V534_TAMPER_EVIDENT_INCIDENT_LEDGER_SUMMARY.json").exists()