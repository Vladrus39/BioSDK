from __future__ import annotations

from pathlib import Path

from biogpu.benchmarks.biogpu_v551_partner_dataroom_review_packet import run
from biogpu.sdk.partner_dataroom_review_packet_v551 import (
    build_external_review_blocker_register_v551,
    build_external_review_packet_v551,
    build_partner_dataroom_audit_bundle_v551,
    build_partner_dataroom_manifest_v551,
    build_partner_dataroom_policy_v551,
    default_dataroom_manifest_item_fixtures_v551,
    default_external_review_gate_fixtures_v551,
    evaluate_dataroom_manifest_item_v551,
    evaluate_external_review_gate_v551,
    run_external_review_gate_v551,
    run_partner_dataroom_review_packet_workflow_v551,
    write_partner_dataroom_review_packet_outputs_v551,
)


def _fake_v550_dependency() -> dict[str, object]:
    return {
        "external_acceptance_intake_contract_ready": True,
        "external_acceptance_intake_audit_sha256": "c" * 64,
        "external_acceptance_packet_record_count": 10,
        "real_acceptance_ready_count": 0,
        "real_pilot_intake_blocker_count": 19,
        "artifact_name": "biogpu_core-5.0.0-py3-none-any.whl",
        "artifact_sha256": "a" * 64,
        "real_external_pilot_ready": False,
        "production_ready": False,
        "full_biosdk_ready": False,
        "bic_os_phase_locked": True,
    }


def test_v551_policy_is_local_only():
    policy = build_partner_dataroom_policy_v551()

    assert policy["partner_dataroom_policy_ready"] is True
    assert policy["policy"]["requires_v550_external_acceptance_intake"] is True
    assert len(policy["policy"]["required_dataroom_items"]) == 12
    assert len(policy["policy"]["external_review_packet_sections"]) == 8
    assert policy["real_external_review_ready"] is False
    assert policy["bic_os_phase_locked"] is True


def test_v551_manifest_validates_local_items_but_blocks_real_dataroom():
    dependency = _fake_v550_dependency()
    manifest = build_partner_dataroom_manifest_v551(dependency, default_dataroom_manifest_item_fixtures_v551())

    assert manifest["partner_dataroom_manifest_ready"] is True
    assert manifest["manifest_item_count"] == 12
    assert manifest["local_manifest_item_ready_count"] == 12
    assert manifest["real_dataroom_item_ready_count"] == 0
    assert "real_partner_dataroom_upload_missing" in manifest["reason_codes"]
    assert "external_reviewer_access_missing" in manifest["reason_codes"]
    assert "real_external_review_not_ready" in manifest["reason_codes"]
    assert "real_external_pilot_not_ready" in manifest["reason_codes"]
    assert "production_release_not_allowed" in manifest["reason_codes"]
    assert "bic_os_unlock_not_allowed" in manifest["reason_codes"]


def test_v551_manifest_item_blocks_external_review_request():
    dependency = _fake_v550_dependency()
    fixture = [item for item in default_dataroom_manifest_item_fixtures_v551() if item.requests_real_external_review][0]
    decision = evaluate_dataroom_manifest_item_v551(fixture, dependency)

    assert decision.local_manifest_item_ready is True
    assert decision.real_dataroom_item_ready is False
    assert "real_external_review_not_ready" in decision.reason_codes
    assert decision.real_external_review_ready is False


def test_v551_review_packet_gate_blockers_and_bundle_are_ready():
    dependency = _fake_v550_dependency()
    policy = build_partner_dataroom_policy_v551()
    manifest = build_partner_dataroom_manifest_v551(dependency)
    review_packet = build_external_review_packet_v551(dependency, manifest)
    review_gate = run_external_review_gate_v551(dependency, manifest, review_packet)
    blocker_register = build_external_review_blocker_register_v551(manifest, review_gate)
    bundle = build_partner_dataroom_audit_bundle_v551(policy, manifest, review_packet, review_gate, blocker_register)

    assert review_packet["external_review_packet_ready"] is True
    assert review_packet["packet_section_count"] == 8
    assert review_packet["external_review_completed_count"] == 0
    assert review_gate["external_review_gate_ready"] is True
    assert review_gate["accepted_local_review_stage_count"] == 3
    assert review_gate["denied_external_review_gate_count"] == 9
    assert blocker_register["external_review_blocker_register_ready"] is True
    assert blocker_register["blocker_count"] == 21
    assert bundle["partner_dataroom_audit_bundle_ready"] is True
    assert bundle["real_external_review_ready"] is False


def test_v551_review_gate_denies_external_review_with_open_blockers():
    dependency = _fake_v550_dependency()
    manifest = build_partner_dataroom_manifest_v551(dependency)
    review_packet = build_external_review_packet_v551(dependency, manifest)
    fixture = [item for item in default_external_review_gate_fixtures_v551() if item.gate_id == "external-review-with-open-blockers"][0]
    decision = evaluate_external_review_gate_v551(fixture, dependency, manifest, review_packet)

    assert decision.accepted_for_local_review_stage is False
    assert "intake_blockers_still_open" in decision.reason_codes
    assert "real_external_review_not_ready" in decision.reason_codes
    assert decision.real_external_review_ready is False


def test_v551_workflow_ready_without_external_review_or_production_claim(tmp_path):
    audit = run_partner_dataroom_review_packet_workflow_v551(Path.cwd(), tmp_path / "out")

    assert audit["overall_status"] == "partner_dataroom_review_packet_contract_ready_review_not_claimed"
    assert audit["partner_dataroom_review_packet_contract_ready"] is True
    assert audit["v550_dependency_ready"] is True
    assert audit["partner_dataroom_manifest_ready"] is True
    assert audit["external_review_packet_ready"] is True
    assert audit["real_dataroom_item_ready_count"] == 0
    assert audit["external_review_completed_count"] == 0
    assert audit["direct_answer"]["is_real_external_review_ready"] == "no"
    assert audit["real_external_review_ready"] is False
    assert audit["real_external_pilot_ready"] is False
    assert audit["production_ready"] is False
    assert audit["full_biosdk_ready"] is False
    assert audit["bic_os_phase_locked"] is True


def test_v551_outputs_are_written(tmp_path):
    audit = run_partner_dataroom_review_packet_workflow_v551(Path.cwd(), tmp_path / "workflow")
    paths = write_partner_dataroom_review_packet_outputs_v551(audit, tmp_path / "out")

    assert Path(paths["summary_json"]).exists()
    assert Path(paths["policy_json"]).exists()
    assert Path(paths["manifest_json"]).exists()
    assert Path(paths["review_packet_json"]).exists()
    assert Path(paths["review_gate_json"]).exists()
    assert Path(paths["blocker_register_json"]).exists()
    assert Path(paths["audit_bundle_json"]).exists()
    assert Path(paths["manifest_csv"]).exists()
    assert Path(paths["review_gate_csv"]).exists()
    assert "Partner Data-Room Review Packet Contract" in Path(paths["markdown_report"]).read_text(encoding="utf-8")


def test_v551_runner_writes_summary(tmp_path):
    result = run(root=Path.cwd(), out_dir=tmp_path / "out")

    assert result["summary"]["partner_dataroom_review_packet_contract_ready"] is True
    assert (tmp_path / "out" / "V551_PARTNER_DATAROOM_REVIEW_PACKET_SUMMARY.json").exists()