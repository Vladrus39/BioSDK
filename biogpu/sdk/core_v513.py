"""BioSDK public core facade and phase gate, v5.13."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from biogpu.beta.control_plane_v55 import default_control_plane_contexts_v55, submit_agent_request_to_queue_v55
from biogpu.beta.job_model_v43 import InMemoryJobStoreV43
from biogpu.llm.agent_bridge_v54 import BioComputeAgentRequestV54, build_agent_response_v54
from biogpu.sdk.evidence_pack_v512 import build_biosdk_evidence_pack_v512
from biogpu.standards.nsi_v10 import reference_nsi_objects, validate_nsi_object


DEFAULT_OUT = Path("outputs/v513_biosdk_core_api")


@dataclass(frozen=True)
class BioSDKPhaseV513:
    phase_id: str
    status: str
    reason: str
    required_before_unlock: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_biosdk_phase_gate_v513(root: str | Path = ".") -> dict[str, Any]:
    evidence = build_biosdk_evidence_pack_v512(root)
    biosdk_kernel_ready = bool(evidence.get("biosdk_evidence_kernel_ready"))
    full_biosdk_ready = bool(evidence.get("full_biosdk_ready"))
    capability_gap_ids = tuple(str(item.get("capability_id")) for item in evidence.get("capability_gaps", []))
    phases = (
        BioSDKPhaseV513(
            phase_id="biogpu_core_kernel",
            status="available",
            reason="Core package, benchmark code, evidence bundles and current tests exist locally.",
            required_before_unlock=tuple(),
        ),
        BioSDKPhaseV513(
            phase_id="biosdk_public_core",
            status="active" if biosdk_kernel_ready else "blocked",
            reason="This is the correct active phase: expose stable SDK calls over NSI, agent review, queue admission, evidence and claim boundaries.",
            required_before_unlock=tuple() if biosdk_kernel_ready else ("restore v5.12 BioSDK evidence-kernel gates",),
        ),
        BioSDKPhaseV513(
            phase_id="biocompute_runtime",
            status="blocked_until_biosdk_core_examples_and_scheduler",
            reason="Runtime should follow SDK facade, public examples, real data validation and durable scheduling.",
            required_before_unlock=("public SDK examples", "durable scheduler/workers", "real NWB/DANDI or external read-only adapter gate"),
        ),
        BioSDKPhaseV513(
            phase_id="bio_compute_control_plane",
            status="blocked_until_runtime_persistence",
            reason="Control plane should not outrun runtime persistence, user/API-key model, uploads/storage and result retention.",
            required_before_unlock=("persistent jobs", "API keys", "dataset upload/storage", "result-bundle retention"),
        ),
        BioSDKPhaseV513(
            phase_id="bic_os",
            status="locked" if not full_biosdk_ready else "review_only",
            reason="BiC OS remains the end target, not the current implementation phase.",
            required_before_unlock=(
                "complete production BioSDK claim",
                "durable runtime daemon and scheduler",
                "permission/identity system",
                "plugin manager",
                "dashboard",
                "live telemetry and lab approval workflow",
                "external prior-art review before global uniqueness claims",
            ),
        ),
    )
    return {
        "version": "v5.13",
        "active_phase": "biosdk_public_core",
        "overall_status": "biosdk_core_api_active_bic_os_locked" if biosdk_kernel_ready and not full_biosdk_ready else "biosdk_core_api_needs_evidence_repair",
        "biosdk_evidence_kernel_ready": biosdk_kernel_ready,
        "full_biosdk_ready": full_biosdk_ready,
        "bic_os_phase_locked": not full_biosdk_ready,
        "capability_gap_ids": list(capability_gap_ids),
        "phase_order": [phase.to_dict() for phase in phases],
        "allowed_next_builds": [
            "biosdk_public_examples",
            "real_nwb_dandi_validation_gate",
            "external_read_only_adapter_validation",
            "durable_scheduler_worker",
            "installable_sdk_release_candidate",
        ],
        "blocked_next_builds": [
            "production_bic_os_claim",
            "global_uniqueness_claim",
            "live_biogpu_claim",
            "gpu_replacement_claim",
            "energy_superiority_claim",
            "lab_closed_loop_module_without_external_approval",
        ],
        "claim_boundary": "v5.13 makes BioSDK public core the active phase and keeps BiC OS locked until SDK/data/runtime evidence gates are complete.",
    }


class BioSDKClientV513:
    """Small public-facing facade over the proven local BioSDK building blocks."""

    def __init__(self, root: str | Path = ".", context_name: str = "researcher") -> None:
        self.root = Path(root)
        self.context_name = context_name
        contexts = default_control_plane_contexts_v55()
        if context_name not in contexts:
            raise ValueError(f"unknown BioSDK context: {context_name}")
        self.context = contexts[context_name]
        self.store = InMemoryJobStoreV43()

    def phase_gate(self) -> dict[str, Any]:
        return build_biosdk_phase_gate_v513(self.root)

    def evidence_pack(self) -> dict[str, Any]:
        return build_biosdk_evidence_pack_v512(self.root)

    def capabilities(self) -> list[dict[str, Any]]:
        return list(self.evidence_pack().get("capabilities", []))

    def validate_nsi_payload(self, schema_name: str, payload: dict[str, Any]) -> dict[str, Any]:
        return validate_nsi_object(schema_name, payload).to_dict()

    def reference_nsi_payloads(self) -> dict[str, Any]:
        return reference_nsi_objects()

    def build_replay_request(
        self,
        request_id: str,
        user_goal: str,
        dataset_ref: str = "zenodo_14363732_preprocessed",
        task_ref: str = "pulse_window_readout",
        decoder_id: str = "centroid",
    ) -> BioComputeAgentRequestV54:
        return BioComputeAgentRequestV54(
            request_id=request_id,
            agent_id="biosdk_v513_client",
            user_goal=user_goal,
            requested_tool="biocompute.run_replay_benchmark",
            mode="replay",
            dataset_ref=dataset_ref,
            task_ref=task_ref,
            decoder_id=decoder_id,
            inputs={"source": "BioSDKClientV513"},
        )

    def review_agent_task(self, request: BioComputeAgentRequestV54) -> dict[str, Any]:
        return build_agent_response_v54(request).to_dict()

    def submit_agent_task(self, request: BioComputeAgentRequestV54) -> dict[str, Any]:
        submission = submit_agent_request_to_queue_v55(request, self.context, self.store)
        return submission.to_dict()


def run_biosdk_reference_flow_v513(root: str | Path = ".") -> dict[str, Any]:
    client = BioSDKClientV513(root=root, context_name="researcher")
    phase_gate = client.phase_gate()
    request = client.build_replay_request(
        request_id="v513_reference_replay",
        user_goal="Run a safe replay benchmark through the BioSDK public facade and keep BiC OS locked.",
    )
    response = client.review_agent_task(request)
    manifest = response.get("nsi_task_manifest")
    nsi_validation = client.validate_nsi_payload("BioComputeTaskManifest", manifest) if isinstance(manifest, dict) else {"valid": False}
    submission = client.submit_agent_task(request)
    return {
        "version": "v5.13",
        "phase_gate": phase_gate,
        "request": request.to_dict(),
        "agent_response": response,
        "nsi_manifest_valid": bool(nsi_validation.get("valid")),
        "nsi_validation": nsi_validation,
        "queue_submission": submission,
        "queue_admission_accepted": bool(submission.get("admission", {}).get("accepted")),
        "job_status": None if submission.get("job") is None else submission["job"].get("status"),
        "direct_answer": {
            "current_correct_phase": "BioSDK public core",
            "bic_os_locked": phase_gate["bic_os_phase_locked"],
            "why": "BioSDK/data/runtime proof gates are not complete, so BiC OS remains the long-term target.",
        },
        "claim_boundary": "Reference flow demonstrates a safe SDK replay path only; it does not claim full BioSDK, production runtime or BiC OS readiness.",
    }


def write_biosdk_core_outputs_v513(flow: dict[str, Any], out_dir: str | Path = DEFAULT_OUT) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary_json": out / "V513_BIOSDK_CORE_API_SUMMARY.json",
        "phase_gate_json": out / "V513_BIOSDK_PHASE_GATE.json",
        "reference_flow_json": out / "V513_BIOSDK_REFERENCE_FLOW.json",
        "markdown_report": out / "BIOGPU_V513_BIOSDK_CORE_API_REPORT.md",
    }
    summary = {
        "version": flow["version"],
        "overall_status": flow["phase_gate"]["overall_status"],
        "active_phase": flow["phase_gate"]["active_phase"],
        "biosdk_evidence_kernel_ready": flow["phase_gate"]["biosdk_evidence_kernel_ready"],
        "full_biosdk_ready": flow["phase_gate"]["full_biosdk_ready"],
        "bic_os_phase_locked": flow["phase_gate"]["bic_os_phase_locked"],
        "nsi_manifest_valid": flow["nsi_manifest_valid"],
        "queue_admission_accepted": flow["queue_admission_accepted"],
        "job_status": flow["job_status"],
        "allowed_next_builds": flow["phase_gate"]["allowed_next_builds"],
        "blocked_next_builds": flow["phase_gate"]["blocked_next_builds"],
        "claim_boundary": flow["claim_boundary"],
    }
    paths["summary_json"].write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["phase_gate_json"].write_text(json.dumps(flow["phase_gate"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["reference_flow_json"].write_text(json.dumps(flow, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["markdown_report"].write_text(_markdown_report(flow), encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}


def _markdown_report(flow: dict[str, Any]) -> str:
    gate = flow["phase_gate"]
    lines = [
        "# BioGPU-Core v5.13 BioSDK Core API Report",
        "",
        "## Phase Gate",
        "",
        f"- Active phase: `{gate['active_phase']}`",
        f"- Overall status: `{gate['overall_status']}`",
        f"- BiC OS locked: `{gate['bic_os_phase_locked']}`",
        "",
        "## Reference Flow",
        "",
        f"- NSI manifest valid: `{flow['nsi_manifest_valid']}`",
        f"- Queue admission accepted: `{flow['queue_admission_accepted']}`",
        f"- Job status: `{flow['job_status']}`",
        "",
        "## Allowed Next Builds",
        "",
    ]
    for item in gate["allowed_next_builds"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Blocked Next Builds", ""])
    for item in gate["blocked_next_builds"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Boundary", "", flow["claim_boundary"], ""])
    return "\n".join(lines)
