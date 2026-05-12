from __future__ import annotations

import json

from biogpu.benchmarks.biogpu_v54_llm_agent_bridge import run
from biogpu.llm.agent_bridge_v54 import (
    BioComputeAgentRequestV54,
    agent_tool_catalog_v54,
    build_agent_response_v54,
    reference_agent_requests_v54,
    review_agent_request_v54,
)
from biogpu.standards.nsi_v10 import validate_nsi_object


def test_v54_tool_catalog_has_expected_safe_tools():
    catalog = agent_tool_catalog_v54()
    assert "biocompute.validate_dataset" in catalog
    assert "biocompute.run_replay_benchmark" in catalog
    assert "biocompute.package_result_bundle" in catalog
    assert "biocompute.request_live_shadow_session" in catalog
    assert all("approved_actuation" not in spec.allowed_modes for spec in catalog.values())


def test_v54_safe_replay_request_is_approved_and_emits_nsi_manifest():
    request = reference_agent_requests_v54()["safe_replay"]
    response = build_agent_response_v54(request)
    assert response.status == "approved"
    assert response.nsi_task_manifest is not None
    assert validate_nsi_object("BioComputeTaskManifest", response.nsi_task_manifest).valid is True
    assert response.claim_annotation["claim_level"] == "software_replay_only"


def test_v54_unsafe_live_field_blocks_request():
    request = BioComputeAgentRequestV54(
        request_id="unsafe_voltage",
        agent_id="agent",
        user_goal="unsafe",
        requested_tool="biocompute.run_replay_benchmark",
        mode="replay",
        inputs={"voltage": 1.0},
    )
    review = review_agent_request_v54(request)
    assert review.approved is False
    assert review.status == "blocked"
    assert any("Unsafe live-lab field" in issue for issue in review.issues)


def test_v54_direct_actuation_is_blocked():
    request = reference_agent_requests_v54()["blocked_actuation"]
    response = build_agent_response_v54(request)
    assert response.status == "blocked"
    assert response.nsi_task_manifest is None
    assert "approved_actuation" in response.policy_review["blocked_operations"]


def test_v54_live_shadow_without_approval_is_gated():
    request = BioComputeAgentRequestV54(
        request_id="shadow_no_approval",
        agent_id="agent",
        user_goal="read live stream without approval",
        requested_tool="biocompute.request_live_shadow_session",
        mode="live_shadow",
    )
    response = build_agent_response_v54(request)
    assert response.status == "needs_human_or_partner_approval"
    assert response.nsi_task_manifest is None
    assert response.policy_review["requires_human_approval"] is True
    assert response.claim_annotation["claim_level"] == "software_replay_only"


def test_v54_live_shadow_with_approval_emits_manifest():
    request = reference_agent_requests_v54()["live_shadow_with_approval"]
    response = build_agent_response_v54(request)
    assert response.status == "approved"
    assert response.nsi_task_manifest is not None
    assert response.nsi_task_manifest["mode"] == "live_shadow"
    assert response.policy_review["requires_human_approval"] is True


def test_v54_unknown_tool_is_blocked():
    request = BioComputeAgentRequestV54(
        request_id="unknown_tool",
        agent_id="agent",
        user_goal="call unknown",
        requested_tool="biocompute.unknown_tool",
    )
    review = review_agent_request_v54(request)
    assert review.status == "blocked"
    assert any("unknown agent tool" in issue for issue in review.issues)


def test_v54_live_shadow_protocol_id_alone_is_not_approval():
    request = BioComputeAgentRequestV54(
        request_id="shadow_protocol_only",
        agent_id="agent",
        user_goal="read live stream with protocol id only",
        requested_tool="biocompute.request_live_shadow_session",
        mode="live_shadow",
        approval_refs={"protocol_id": "readonly-shadow-protocol"},
    )
    response = build_agent_response_v54(request)
    assert response.status == "needs_human_or_partner_approval"
    assert response.nsi_task_manifest is None


def test_v54_unsafe_live_shadow_is_blocked_before_approval_gate():
    request = BioComputeAgentRequestV54(
        request_id="shadow_unsafe_payload",
        agent_id="agent",
        user_goal="unsafe live stream request",
        requested_tool="biocompute.request_live_shadow_session",
        mode="live_shadow",
        inputs={"voltage": 1.0},
    )
    response = build_agent_response_v54(request)
    assert response.status == "blocked"
    assert response.nsi_task_manifest is None


def test_v54_runner_writes_outputs(tmp_path):
    summary = run(tmp_path)
    assert summary["milestone"] == "v5.4"
    assert summary["gate"]["safe_replay_agent_request_approved"] is True
    assert summary["gate"]["direct_actuation_blocked"] is True
    assert (tmp_path / "V54_AGENT_TOOL_CATALOG.json").exists()
    assert json.loads((tmp_path / "V54_LLM_AGENT_BRIDGE_SUMMARY.json").read_text(encoding="utf-8"))["phase"] == "llm_agent_bridge"
