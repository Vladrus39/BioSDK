"""Safe LLM/agent bridge for BioCompute tasks, v5.4."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

from biogpu.safety.boundary_v35 import SafetyViolationV35, assert_no_forbidden_payload_v35
from biogpu.standards.nsi_v10 import (
    BLOCKED_BY_DEFAULT,
    SAFETY_MODES,
    annotate_claim_level,
    validate_nsi_object,
)


@dataclass(frozen=True)
class AgentToolSpecV54:
    tool_name: str
    purpose: str
    allowed_modes: tuple[str, ...]
    requires_approval: bool
    required_evidence: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BioComputeAgentRequestV54:
    request_id: str
    agent_id: str
    user_goal: str
    requested_tool: str
    mode: str = "replay"
    dataset_ref: str = "synthetic_reference"
    task_ref: str = "orientation_decoding"
    decoder_id: str = "centroid"
    split_policy: dict[str, Any] = field(default_factory=lambda: {"policy": "holdout", "seed": 42})
    inputs: dict[str, Any] = field(default_factory=dict)
    constraints: dict[str, Any] = field(default_factory=dict)
    approval_refs: dict[str, str] = field(default_factory=dict)
    output_dir: str = "outputs/v54_llm_agent_bridge"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AgentPolicyReviewV54:
    request_id: str
    approved: bool
    status: str
    normalized_mode: str
    requires_human_approval: bool
    allowed_claim_level: str
    issues: tuple[str, ...]
    blocked_operations: tuple[str, ...]
    required_evidence: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AgentToolResponseV54:
    request_id: str
    status: str
    policy_review: dict[str, Any]
    nsi_task_manifest: dict[str, Any] | None
    nsi_validation: dict[str, Any] | None
    claim_annotation: dict[str, Any]
    result_contract: dict[str, Any]
    audit_events: tuple[dict[str, Any], ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def agent_tool_catalog_v54() -> dict[str, AgentToolSpecV54]:
    return {
        "biocompute.validate_dataset": AgentToolSpecV54(
            tool_name="biocompute.validate_dataset",
            purpose="Validate dataset metadata, local availability and schema safety.",
            allowed_modes=("metadata_only", "read_only", "replay"),
            requires_approval=False,
            required_evidence=("dataset_validation_report", "safety_scan"),
        ),
        "biocompute.run_replay_benchmark": AgentToolSpecV54(
            tool_name="biocompute.run_replay_benchmark",
            purpose="Run replay benchmark jobs against approved local/public data.",
            allowed_modes=("replay",),
            requires_approval=False,
            required_evidence=("run_manifest", "metrics", "result_bundle", "claim_annotation"),
        ),
        "biocompute.run_lineage_sweep": AgentToolSpecV54(
            tool_name="biocompute.run_lineage_sweep",
            purpose="Run lineage-aware replay sweeps with held-out splits.",
            allowed_modes=("replay",),
            requires_approval=False,
            required_evidence=("split_manifest", "shuffle_controls", "result_bundle"),
        ),
        "biocompute.compare_shuffle_baseline": AgentToolSpecV54(
            tool_name="biocompute.compare_shuffle_baseline",
            purpose="Compare real readout metrics to shuffled controls.",
            allowed_modes=("replay",),
            requires_approval=False,
            required_evidence=("shuffle_control_table", "p_value", "result_bundle"),
        ),
        "biocompute.import_nwb": AgentToolSpecV54(
            tool_name="biocompute.import_nwb",
            purpose="Inspect or import NWB data through the NSI trace contract.",
            allowed_modes=("metadata_only", "read_only", "replay"),
            requires_approval=False,
            required_evidence=("nwb_structure_report", "schema_validation"),
        ),
        "biocompute.import_vendor_export": AgentToolSpecV54(
            tool_name="biocompute.import_vendor_export",
            purpose="Inspect read-only vendor-exported data and produce NSI-compatible traces.",
            allowed_modes=("metadata_only", "read_only", "replay"),
            requires_approval=False,
            required_evidence=("vendor_schema_report", "safety_scan"),
        ),
        "biocompute.package_result_bundle": AgentToolSpecV54(
            tool_name="biocompute.package_result_bundle",
            purpose="Package manifests, metrics, checksums and audit logs into an evidence bundle.",
            allowed_modes=("metadata_only", "read_only", "replay", "live_shadow"),
            requires_approval=False,
            required_evidence=("bundle_manifest", "checksums", "ledger_entry"),
        ),
        "biocompute.request_live_shadow_session": AgentToolSpecV54(
            tool_name="biocompute.request_live_shadow_session",
            purpose="Request live read-only shadow access without biological actuation.",
            allowed_modes=("live_shadow",),
            requires_approval=True,
            required_evidence=("partner_api_approval", "read_only_scope", "audit_log", "result_bundle"),
        ),
    }


def _normalize_mode(mode: str) -> str:
    mapping = {
        "api_read_only": "read_only",
        "read_only_replay": "replay",
        "dry_run": "replay",
        "software_replay": "replay",
    }
    return mapping.get(str(mode).strip().lower(), str(mode).strip().lower())


def _flatten_strings(payload: Any) -> list[str]:
    values: list[str] = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            values.append(str(key).lower())
            values.extend(_flatten_strings(value))
    elif isinstance(payload, (list, tuple, set)):
        for item in payload:
            values.extend(_flatten_strings(item))
    elif payload is not None:
        values.append(str(payload).lower())
    return values


def _has_approval(request: BioComputeAgentRequestV54) -> bool:
    return bool(
        request.approval_refs.get("partner_api_approval")
        or request.approval_refs.get("operator_approval")
    )


def _claim_level_for_review(normalized_mode: str, approved: bool) -> str:
    claim_mode = normalized_mode if approved else "replay"
    evidence = {"mode": claim_mode}
    if normalized_mode == "read_only" and approved:
        evidence["read_only_api_validated"] = True
    if normalized_mode == "live_shadow" and approved:
        evidence["live_shadow_validated"] = True
    return str(annotate_claim_level(evidence)["claim_level"])


def review_agent_request_v54(request: BioComputeAgentRequestV54) -> AgentPolicyReviewV54:
    catalog = agent_tool_catalog_v54()
    issues: list[str] = []
    blocked: set[str] = set(BLOCKED_BY_DEFAULT)
    normalized_mode = _normalize_mode(request.mode)
    spec = catalog.get(request.requested_tool)

    try:
        assert_no_forbidden_payload_v35(request.to_dict(), context="BioComputeAgentRequestV54")
    except SafetyViolationV35 as exc:
        issues.append(str(exc))

    flat_values = set(_flatten_strings(request.to_dict()))
    unsafe_values = sorted(set(BLOCKED_BY_DEFAULT).intersection(flat_values))
    if unsafe_values:
        issues.append("unsafe blocked operation requested: " + ", ".join(unsafe_values))
        blocked.update(unsafe_values)

    if spec is None:
        issues.append(f"unknown agent tool: {request.requested_tool}")
        required_evidence: tuple[str, ...] = ()
    else:
        required_evidence = spec.required_evidence
        if normalized_mode not in spec.allowed_modes:
            issues.append(f"mode {normalized_mode} is not allowed for {request.requested_tool}")

    if normalized_mode not in SAFETY_MODES:
        issues.append(f"mode {normalized_mode} is not an NSI safety mode")

    if normalized_mode == "approved_actuation":
        issues.append("LLM/agent bridge cannot directly approve or execute biological actuation")
        blocked.add("approved_actuation")

    requires_approval = bool(spec.requires_approval if spec else False) or normalized_mode == "live_shadow"
    if issues:
        status = "blocked"
    elif requires_approval and not _has_approval(request):
        status = "needs_human_or_partner_approval"
    else:
        status = "approved"

    approved = status == "approved"
    claim_level = _claim_level_for_review(normalized_mode, approved)
    return AgentPolicyReviewV54(
        request_id=request.request_id,
        approved=approved,
        status=status,
        normalized_mode=normalized_mode,
        requires_human_approval=requires_approval,
        allowed_claim_level=claim_level,
        issues=tuple(issues),
        blocked_operations=tuple(sorted(blocked)),
        required_evidence=required_evidence,
    )


def build_nsi_task_manifest_v54(request: BioComputeAgentRequestV54, review: AgentPolicyReviewV54) -> dict[str, Any]:
    if not review.approved:
        raise ValueError(f"agent request is not approved: {review.status}")
    safety_profile = {
        "profile_id": f"{request.request_id}_safety_profile",
        "mode": review.normalized_mode,
        "allowed_operations": _allowed_operations_for_mode(review.normalized_mode),
        "blocked_operations": list(review.blocked_operations),
        "approval_required": bool(review.requires_human_approval),
        "protocol_id": request.approval_refs.get("protocol_id"),
    }
    manifest = {
        "manifest_id": f"agent-{request.request_id}",
        "mode": review.normalized_mode,
        "dataset": {"dataset_ref": request.dataset_ref, "requested_by": request.agent_id},
        "task": {
            "task_ref": request.task_ref,
            "user_goal": request.user_goal,
            "requested_tool": request.requested_tool,
            "inputs": request.inputs,
        },
        "split_policy": request.split_policy,
        "decoder": {"decoder_id": request.decoder_id},
        "safety_profile": safety_profile,
        "output_dir": request.output_dir,
    }
    task_report = validate_nsi_object("BioComputeTaskManifest", manifest)
    safety_report = validate_nsi_object("BioComputeSafetyProfile", safety_profile)
    if not task_report.valid or not safety_report.valid:
        raise ValueError("generated NSI manifest failed validation")
    return manifest


def _allowed_operations_for_mode(mode: str) -> list[str]:
    if mode == "metadata_only":
        return ["metadata_read", "schema_validate"]
    if mode == "replay":
        return ["metadata_read", "trace_read", "benchmark_run", "result_bundle_export"]
    if mode == "read_only":
        return ["metadata_read", "trace_read", "result_bundle_export"]
    if mode == "live_shadow":
        return ["metadata_read", "trace_read", "live_shadow_read", "result_bundle_export"]
    return []


def build_agent_response_v54(request: BioComputeAgentRequestV54) -> AgentToolResponseV54:
    review = review_agent_request_v54(request)
    audit = [
        {"event": "agent_request_received", "timestamp_utc": utc_now(), "request_id": request.request_id},
        {"event": "policy_review_completed", "timestamp_utc": utc_now(), "status": review.status},
    ]
    manifest: dict[str, Any] | None = None
    nsi_validation: dict[str, Any] | None = None
    if review.approved:
        manifest = build_nsi_task_manifest_v54(request, review)
        nsi_validation = validate_nsi_object("BioComputeTaskManifest", manifest).to_dict()
        audit.append({"event": "nsi_manifest_created", "timestamp_utc": utc_now(), "manifest_id": manifest["manifest_id"]})

    claim_mode = review.normalized_mode if review.approved else "replay"
    claim_annotation = annotate_claim_level({
        "mode": claim_mode,
        "read_only_api_validated": review.normalized_mode == "read_only" and review.approved,
        "live_shadow_validated": review.normalized_mode == "live_shadow" and review.approved,
    })
    result_contract = {
        "must_return": ["policy_review", "nsi_task_manifest", "claim_annotation", "result_bundle_or_denial_reason"],
        "required_evidence": list(review.required_evidence),
        "result_bundle_required": review.approved,
        "llm_may_report": review.approved,
        "llm_must_not_claim": claim_annotation["blocked_claims"],
    }
    return AgentToolResponseV54(
        request_id=request.request_id,
        status=review.status,
        policy_review=review.to_dict(),
        nsi_task_manifest=manifest,
        nsi_validation=nsi_validation,
        claim_annotation=claim_annotation,
        result_contract=result_contract,
        audit_events=tuple(audit),
    )


def reference_agent_requests_v54() -> dict[str, BioComputeAgentRequestV54]:
    return {
        "safe_replay": BioComputeAgentRequestV54(
            request_id="v54_safe_replay",
            agent_id="benchmark_agent",
            user_goal="Run an offline replay benchmark and produce an auditable result bundle.",
            requested_tool="biocompute.run_replay_benchmark",
            mode="replay",
            dataset_ref="zenodo_14363732_preprocessed",
            task_ref="pulse_window_readout",
            inputs={"requested_metric": "balanced_accuracy"},
        ),
        "live_shadow_with_approval": BioComputeAgentRequestV54(
            request_id="v54_live_shadow",
            agent_id="lab_copilot",
            user_goal="Request read-only live-shadow monitoring for a partner API session.",
            requested_tool="biocompute.request_live_shadow_session",
            mode="live_shadow",
            dataset_ref="partner_api_readonly_stream",
            task_ref="activity_profile",
            approval_refs={"partner_api_approval": "partner-readonly-scope-v54", "protocol_id": "readonly-shadow-protocol"},
        ),
        "blocked_actuation": BioComputeAgentRequestV54(
            request_id="v54_blocked_actuation",
            agent_id="unsafe_agent",
            user_goal="Try to perform direct biological actuation.",
            requested_tool="biocompute.request_approved_actuation",
            mode="approved_actuation",
            inputs={"operation": "live_stimulation"},
        ),
    }


def catalog_as_dict_v54() -> dict[str, dict[str, Any]]:
    return {name: spec.to_dict() for name, spec in agent_tool_catalog_v54().items()}


def response_to_json_v54(response: AgentToolResponseV54) -> str:
    return json.dumps(response.to_dict(), indent=2, ensure_ascii=False)
