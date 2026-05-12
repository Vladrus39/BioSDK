from __future__ import annotations

import json

from biogpu.benchmarks.biogpu_v55_control_plane_queue import run
from biogpu.beta.control_plane_v55 import (
    default_control_plane_contexts_v55,
    reference_queue_demo_v55,
    submit_agent_request_to_queue_v55,
)
from biogpu.beta.job_model_v43 import InMemoryJobStoreV43, JobStatus
from biogpu.llm.agent_bridge_v54 import BioComputeAgentRequestV54, reference_agent_requests_v54


def test_v55_safe_replay_agent_request_enters_queue():
    contexts = default_control_plane_contexts_v55()
    request = reference_agent_requests_v54()["safe_replay"]
    store = InMemoryJobStoreV43()
    submission = submit_agent_request_to_queue_v55(request, contexts["researcher"], store)
    assert submission.admission.accepted is True
    assert submission.job is not None
    assert submission.job["status"] == JobStatus.QUEUED.value
    assert submission.admission.job_type == "benchmark_run"
    assert len(store.list_jobs()) == 1


def test_v55_blocked_agent_request_is_not_queued():
    contexts = default_control_plane_contexts_v55()
    request = reference_agent_requests_v54()["blocked_actuation"]
    store = InMemoryJobStoreV43()
    submission = submit_agent_request_to_queue_v55(request, contexts["researcher"], store)
    assert submission.admission.accepted is False
    assert submission.job is None
    assert any(error.startswith("agent_request_not_approved") for error in submission.admission.errors)
    assert len(store.list_jobs()) == 0


def test_v55_unapproved_live_shadow_is_not_queued():
    contexts = default_control_plane_contexts_v55()
    request = BioComputeAgentRequestV54(
        request_id="shadow_no_approval_queue",
        agent_id="agent",
        user_goal="read live stream without approval",
        requested_tool="biocompute.request_live_shadow_session",
        mode="live_shadow",
    )
    submission = submit_agent_request_to_queue_v55(request, contexts["enterprise_live_shadow"], InMemoryJobStoreV43())
    assert submission.admission.accepted is False
    assert "missing_nsi_task_manifest" in submission.admission.errors


def test_v55_live_shadow_requires_enterprise_live_shadow_tier():
    contexts = default_control_plane_contexts_v55()
    request = reference_agent_requests_v54()["live_shadow_with_approval"]
    denied = submit_agent_request_to_queue_v55(request, contexts["developer"], InMemoryJobStoreV43())
    allowed = submit_agent_request_to_queue_v55(request, contexts["enterprise_live_shadow"], InMemoryJobStoreV43())
    assert denied.admission.accepted is False
    assert "live_shadow_not_allowed_for_tier:developer_evaluation" in denied.admission.errors
    assert allowed.admission.accepted is True
    assert allowed.admission.job_type == "api_readonly_validation"


def test_v55_viewer_role_cannot_queue_safe_agent_job():
    contexts = default_control_plane_contexts_v55()
    viewer_context = contexts["developer"]
    viewer_context.role = viewer_context.role.VIEWER
    request = reference_agent_requests_v54()["safe_replay"]
    submission = submit_agent_request_to_queue_v55(request, viewer_context, InMemoryJobStoreV43())
    assert submission.admission.accepted is True
    assert submission.job is not None
    assert submission.job["status"] == JobStatus.FAILED.value
    assert "job_type_not_allowed_for_role:benchmark_run:viewer" in submission.job["validation_errors"]


def test_v55_reference_demo_has_expected_safety_outcomes():
    demo = reference_queue_demo_v55()
    assert demo["queued_job_count"] == 2
    assert demo["safe_replay"]["admission"]["accepted"] is True
    assert demo["live_shadow_allowed"]["admission"]["accepted"] is True
    assert demo["live_shadow_denied_tier"]["admission"]["accepted"] is False
    assert demo["blocked_actuation"]["admission"]["accepted"] is False


def test_v55_runner_writes_outputs(tmp_path):
    summary = run(tmp_path)
    assert summary["version"] == "v5.5"
    assert summary["safe_replay_admitted"] is True
    assert summary["blocked_actuation_rejected"] is True
    assert (tmp_path / "V55_CONTROL_PLANE_QUEUE_SUMMARY.json").exists()
    loaded = json.loads((tmp_path / "V55_CONTROL_PLANE_QUEUE_SUMMARY.json").read_text(encoding="utf-8"))
    assert loaded["component"] == "BioCompute Control Plane Queue Bridge"
