from __future__ import annotations

import json

from biogpu.beta.access_policy_v41 import (
    access_tiers_v41,
    build_v41_access_audit,
    decide_access_v41,
    write_v41_outputs,
)


def test_v41_research_pilot_has_maximum_safe_software_access():
    tiers = {t.tier_id: t for t in access_tiers_v41()}
    pilot = tiers["research_pilot_max_safe"]
    assert "run_replay_benchmarks" in pilot.allowed_capabilities
    assert "upload_or_import_own_data" in pilot.allowed_capabilities
    assert "use_read_only_external_api_clients" in pilot.allowed_capabilities
    assert "use_biollm_tool_interface" in pilot.allowed_capabilities
    assert "live_stimulation" in pilot.blocked_capabilities


def test_v41_access_decision_blocks_live_stimulation_before_lab_approval():
    d = decide_access_v41("research_pilot_max_safe", "live_stimulation")
    assert d.allowed is False
    assert d.required_gate == "upgrade_and_safety_approval"
    ok = decide_access_v41("research_pilot_max_safe", "export_result_bundle")
    assert ok.allowed is True


def test_v41_lab_addon_allows_only_approved_protocol_closed_loop_not_free_form():
    ok = decide_access_v41("lab_approved_closed_loop_addon", "approved_protocol_closed_loop")
    assert ok.allowed is True
    bad = decide_access_v41("lab_approved_closed_loop_addon", "free_form_electrode_command")
    assert bad.allowed is False
    assert bad.required_gate == "lab_vendor_protocol_approval"


def test_v41_remaining_work_separates_local_from_powerpc_api_lab():
    audit = build_v41_access_audit()
    local_ids = {x["item_id"] for x in audit["still_possible_in_this_environment"]}
    external_ids = {x["item_id"] for x in audit["must_move_elsewhere"]}
    assert "E2_dataset_registry_skeleton" in local_ids
    assert "E3_hosted_server_scaffold" in local_ids
    assert "P2_full_shuffle_1000" in external_ids
    assert "A2_vendor_api_credentials" in external_ids
    assert "L1_live_lab_validation" in external_ids


def test_v41_outputs_are_written(tmp_path):
    written = write_v41_outputs(tmp_path)
    assert (tmp_path / "v41_access_audit.json").exists()
    assert (tmp_path / "v41_access_tiers.csv").exists()
    assert (tmp_path / "v41_remaining_work_items.csv").exists()
    data = json.loads((tmp_path / "v41_summary.json").read_text(encoding="utf-8"))
    assert data["access_tier_count"] >= 5
    assert data["still_possible_in_this_environment_count"] >= 4
