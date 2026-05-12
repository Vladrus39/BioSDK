"""BioCompute Control Plane queue bridge, v5.5.

This module connects the v5.4 LLM/Agent Bridge to the older v4.3 hosted beta
job model. It accepts only approved NSI task manifests and turns them into
safe hosted queue jobs with role, tier and live-shadow checks.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from biogpu.beta.job_model_v43 import (
    AccessTier,
    BioGPUJobRecordV43,
    BioGPUJobSpecV43,
    DEFAULT_QUOTAS,
    InMemoryJobStoreV43,
    JobType,
    UserContextV43,
    UserRole,
)
from biogpu.llm.agent_bridge_v54 import (
    BioComputeAgentRequestV54,
    AgentToolResponseV54,
    build_agent_response_v54,
)
from biogpu.standards.nsi_v10 import validate_nsi_object


TOOL_TO_JOB_TYPE_V55: dict[str, JobType] = {
    "biocompute.validate_dataset": JobType.DATASET_IMPORT,
    "biocompute.run_replay_benchmark": JobType.BENCHMARK_RUN,
    "biocompute.run_lineage_sweep": JobType.BENCHMARK_RUN,
    "biocompute.compare_shuffle_baseline": JobType.BENCHMARK_RUN,
    "biocompute.import_nwb": JobType.DATASET_IMPORT,
    "biocompute.import_vendor_export": JobType.DATASET_IMPORT,
    "biocompute.package_result_bundle": JobType.RESULT_BUNDLE_EXPORT,
    "biocompute.request_live_shadow_session": JobType.API_READONLY_VALIDATION,
}


@dataclass(frozen=True)
class ControlPlaneAdmissionV55:
    accepted: bool
    status: str
    errors: tuple[str, ...]
    job_type: str | None
    manifest_id: str | None
    dataset_id: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ControlPlaneSubmissionV55:
    admission: ControlPlaneAdmissionV55
    job: dict[str, Any] | None
    agent_response: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def default_control_plane_contexts_v55() -> dict[str, UserContextV43]:
    return {
        "developer": UserContextV43("dev_user", "dev_workspace", UserRole.DEVELOPER, AccessTier.DEVELOPER_EVALUATION),
        "researcher": UserContextV43("research_user", "research_workspace", UserRole.RESEARCHER, AccessTier.RESEARCH_PILOT),
        "enterprise_readonly": UserContextV43(
            "enterprise_user",
            "enterprise_workspace",
            UserRole.OPERATOR,
            AccessTier.ENTERPRISE_READ_ONLY,
        ),
        "enterprise_live_shadow": UserContextV43(
            "shadow_operator",
            "shadow_workspace",
            UserRole.OPERATOR,
            AccessTier.ENTERPRISE_LIVE_SHADOW,
        ),
    }


def _agent_response_dict(response: AgentToolResponseV54 | dict[str, Any]) -> dict[str, Any]:
    if isinstance(response, AgentToolResponseV54):
        return response.to_dict()
    return dict(response)


def _dataset_id_from_manifest(manifest: dict[str, Any] | None) -> str | None:
    if not manifest:
        return None
    dataset = manifest.get("dataset")
    if not isinstance(dataset, dict):
        return None
    return str(dataset.get("dataset_ref") or dataset.get("dataset_id") or "") or None


def _requested_tool_from_manifest(manifest: dict[str, Any] | None) -> str | None:
    if not manifest:
        return None
    task = manifest.get("task")
    if not isinstance(task, dict):
        return None
    tool = task.get("requested_tool")
    return str(tool) if tool else None


def review_control_plane_admission_v55(
    response: AgentToolResponseV54 | dict[str, Any],
    context: UserContextV43,
) -> ControlPlaneAdmissionV55:
    response_dict = _agent_response_dict(response)
    errors: list[str] = []
    policy = response_dict.get("policy_review")
    if not isinstance(policy, dict):
        errors.append("missing_policy_review")
    elif not bool(policy.get("approved")):
        errors.append(f"agent_request_not_approved:{response_dict.get('status')}")

    manifest = response_dict.get("nsi_task_manifest")
    if not isinstance(manifest, dict):
        errors.append("missing_nsi_task_manifest")
        manifest = None
    else:
        report = validate_nsi_object("BioComputeTaskManifest", manifest)
        if not report.valid:
            errors.append("invalid_nsi_task_manifest")

    requested_tool = _requested_tool_from_manifest(manifest)
    job_type = TOOL_TO_JOB_TYPE_V55.get(requested_tool or "")
    if requested_tool and job_type is None:
        errors.append(f"unsupported_agent_tool_for_queue:{requested_tool}")

    mode = str(manifest.get("mode") if manifest else "")
    if mode == "approved_actuation":
        errors.append("approved_actuation_not_enabled_in_v55_control_plane")
    if mode == "live_shadow" and not DEFAULT_QUOTAS[context.tier].allow_live_shadow:
        errors.append(f"live_shadow_not_allowed_for_tier:{context.tier.value}")

    accepted = not errors
    return ControlPlaneAdmissionV55(
        accepted=accepted,
        status="accepted" if accepted else "rejected",
        errors=tuple(errors),
        job_type=job_type.value if job_type else None,
        manifest_id=str(manifest.get("manifest_id")) if manifest else None,
        dataset_id=_dataset_id_from_manifest(manifest),
    )


def submit_agent_response_to_queue_v55(
    response: AgentToolResponseV54 | dict[str, Any],
    context: UserContextV43,
    store: InMemoryJobStoreV43 | None = None,
) -> ControlPlaneSubmissionV55:
    store = store or InMemoryJobStoreV43()
    response_dict = _agent_response_dict(response)
    admission = review_control_plane_admission_v55(response_dict, context)
    if not admission.accepted:
        return ControlPlaneSubmissionV55(admission=admission, job=None, agent_response=response_dict)

    manifest = response_dict["nsi_task_manifest"]
    job_type = JobType(admission.job_type)
    spec = BioGPUJobSpecV43(
        job_type=job_type,
        manifest=manifest,
        dataset_id=admission.dataset_id,
        requested_result_bundle=True,
        metadata={
            "source": "v55_control_plane_queue",
            "agent_request_id": response_dict.get("request_id"),
            "claim_level": response_dict.get("claim_annotation", {}).get("claim_level"),
            "required_evidence": response_dict.get("result_contract", {}).get("required_evidence", []),
        },
    )
    job = store.create_job(context, spec)
    job.add_event("agent_response_admitted", manifest_id=admission.manifest_id, job_type=admission.job_type)
    return ControlPlaneSubmissionV55(admission=admission, job=job.to_dict(), agent_response=response_dict)


def submit_agent_request_to_queue_v55(
    request: BioComputeAgentRequestV54,
    context: UserContextV43,
    store: InMemoryJobStoreV43 | None = None,
) -> ControlPlaneSubmissionV55:
    return submit_agent_response_to_queue_v55(build_agent_response_v54(request), context, store)


def reference_queue_demo_v55() -> dict[str, Any]:
    from biogpu.llm.agent_bridge_v54 import reference_agent_requests_v54

    contexts = default_control_plane_contexts_v55()
    requests = reference_agent_requests_v54()
    store = InMemoryJobStoreV43()
    safe_replay = submit_agent_request_to_queue_v55(requests["safe_replay"], contexts["researcher"], store)
    live_shadow_allowed = submit_agent_request_to_queue_v55(
        requests["live_shadow_with_approval"],
        contexts["enterprise_live_shadow"],
        store,
    )
    live_shadow_denied_tier = submit_agent_request_to_queue_v55(
        requests["live_shadow_with_approval"],
        contexts["developer"],
        store,
    )
    blocked_actuation = submit_agent_request_to_queue_v55(requests["blocked_actuation"], contexts["researcher"], store)
    return {
        "safe_replay": safe_replay.to_dict(),
        "live_shadow_allowed": live_shadow_allowed.to_dict(),
        "live_shadow_denied_tier": live_shadow_denied_tier.to_dict(),
        "blocked_actuation": blocked_actuation.to_dict(),
        "queued_job_count": len(store.list_jobs()),
    }


def control_plane_summary_v55() -> dict[str, Any]:
    demo = reference_queue_demo_v55()
    return {
        "version": "v5.5",
        "component": "BioCompute Control Plane Queue Bridge",
        "tool_mappings": {tool: job_type.value for tool, job_type in TOOL_TO_JOB_TYPE_V55.items()},
        "queued_job_count": demo["queued_job_count"],
        "safe_replay_admitted": demo["safe_replay"]["admission"]["accepted"],
        "live_shadow_enterprise_admitted": demo["live_shadow_allowed"]["admission"]["accepted"],
        "live_shadow_developer_rejected": not demo["live_shadow_denied_tier"]["admission"]["accepted"],
        "blocked_actuation_rejected": not demo["blocked_actuation"]["admission"]["accepted"],
    }
