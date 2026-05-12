"""BiC OS boot readiness kernel, v5.11."""
from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


DEFAULT_OUT = Path("outputs/v511_bic_os_boot_readiness")
PRODUCT_NAME = "BiC OS"


@dataclass(frozen=True)
class BiCOSSubsystemV511:
    subsystem_id: str
    title: str
    layer: str
    status: str
    boot_required: bool
    production_required: bool
    evidence: tuple[str, ...]
    gaps: tuple[str, ...]
    next_action: str
    allowed_statement: str
    forbidden_statement: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _artifact_map(root: Path) -> dict[str, dict[str, Any]]:
    paths = {
        "v43_job_model": "biogpu/beta/job_model_v43.py",
        "v49_blueprint": "biogpu/os/blueprint_v49.py",
        "v52_nsi": "outputs/v52_nsi_interface/V52_NSI_INTERFACE_SUMMARY.json",
        "v53_evidence_ledger": "outputs/v53_evidence_ledger/V53_EVIDENCE_LEDGER_SUMMARY.json",
        "v54_agent_bridge": "outputs/v54_llm_agent_bridge/V54_LLM_AGENT_BRIDGE_SUMMARY.json",
        "v55_control_plane": "outputs/v55_control_plane_queue/V55_CONTROL_PLANE_QUEUE_SUMMARY.json",
        "v58_raw_native": "outputs/v58_raw_native_benchmark/V58_RAW_NATIVE_FEATURE_SUMMARY.json",
        "v59_stability": "outputs/v59_raw_native_stability_audit/V59_RAW_NATIVE_STABILITY_SUMMARY.json",
        "v510_claim_audit": "outputs/v510_project_alignment_claim_audit/V510_PROJECT_ALIGNMENT_SUMMARY.json",
        "master_plan": "docs/MASTER_PROJECT_PLAN_V50.md",
        "first_mover_strategy": "docs/BIC_OS_FIRST_MOVER_STRATEGY_V50.md",
    }
    artifacts: dict[str, dict[str, Any]] = {}
    for key, relative_path in paths.items():
        path = root / relative_path
        artifacts[key] = {
            "path": relative_path,
            "exists": path.exists(),
            "json": _read_json(path) if path.suffix.lower() == ".json" else {},
        }
    return artifacts


def _evidence_for(artifacts: dict[str, dict[str, Any]], *keys: str) -> tuple[str, ...]:
    return tuple(str(artifacts[key]["path"]) for key in keys if artifacts.get(key, {}).get("exists"))


def _missing_for(artifacts: dict[str, dict[str, Any]], *keys: str) -> tuple[str, ...]:
    return tuple(str(artifacts[key]["path"]) for key in keys if not artifacts.get(key, {}).get("exists"))


def _gate(data: dict[str, Any], key: str) -> bool:
    gate = data.get("gate")
    return isinstance(gate, dict) and bool(gate.get(key))


def _int_value(data: dict[str, Any], key: str) -> int:
    try:
        return int(data.get(key, 0))
    except (TypeError, ValueError):
        return 0


def _float_value(data: dict[str, Any], key: str) -> float:
    try:
        return float(data.get(key, 0.0))
    except (TypeError, ValueError):
        return 0.0


def _nsi_ready(summary: dict[str, Any]) -> bool:
    return (
        summary.get("schema_status") == "frozen_interface_profile"
        and _int_value(summary, "schema_count") >= 7
        and _gate(summary, "nsi_schemas_frozen")
        and _gate(summary, "adapter_conformance_passed")
        and _gate(summary, "result_bundle_validator_passed")
        and _gate(summary, "claim_annotation_available")
    )


def _evidence_ready(summary: dict[str, Any]) -> bool:
    return bool(summary.get("ledger_chain_valid")) and bool(summary.get("reference_bundle_valid")) and _gate(summary, "local_signatures_present")


def _agent_ready(summary: dict[str, Any]) -> bool:
    return (
        _int_value(summary, "tool_count") >= 8
        and _gate(summary, "safe_replay_agent_request_approved")
        and _gate(summary, "live_shadow_requires_or_has_approval")
        and _gate(summary, "direct_actuation_blocked")
        and _gate(summary, "nsi_manifest_emitted_for_safe_requests")
    )


def _queue_ready(summary: dict[str, Any]) -> bool:
    return (
        bool(summary.get("safe_replay_admitted"))
        and bool(summary.get("live_shadow_developer_rejected"))
        and bool(summary.get("blocked_actuation_rejected"))
        and _int_value(summary, "queued_job_count") >= 1
    )


def _raw_runtime_ready(v58: dict[str, Any], v59: dict[str, Any]) -> bool:
    return (
        _int_value(v58, "feature_row_count") > 0
        and v59.get("split_half_repeatability_status") == "split_half_repeatability_available"
        and _float_value(v59, "split_half_cosine_median") >= 0.95
        and _float_value(v59, "split_vs_cross_median_margin") > 0.1
    )


def _claim_supervisor_ready(summary: dict[str, Any]) -> bool:
    return (
        summary.get("overall_status") == "on_mission_with_claim_boundaries"
        and summary.get("direct_answer", {}).get("did_we_drift_from_project_meaning") == "no"
        and summary.get("direct_answer", {}).get("is_the_code_globally_unique_proven") == "no_local_tests_cannot_prove_global_uniqueness"
    )


def build_bic_os_subsystems_v511(root: str | Path = ".") -> tuple[BiCOSSubsystemV511, ...]:
    project_root = Path(root)
    artifacts = _artifact_map(project_root)
    v52 = artifacts["v52_nsi"]["json"]
    v53 = artifacts["v53_evidence_ledger"]["json"]
    v54 = artifacts["v54_agent_bridge"]["json"]
    v55 = artifacts["v55_control_plane"]["json"]
    v58 = artifacts["v58_raw_native"]["json"]
    v59 = artifacts["v59_stability"]["json"]
    v510 = artifacts["v510_claim_audit"]["json"]

    nsi_ready = _nsi_ready(v52)
    evidence_ready = _evidence_ready(v53)
    agent_ready = _agent_ready(v54)
    queue_ready = _queue_ready(v55)
    raw_ready = _raw_runtime_ready(v58, v59)
    claim_ready = _claim_supervisor_ready(v510)
    safety_ready = nsi_ready and agent_ready and queue_ready and claim_ready

    return (
        BiCOSSubsystemV511(
            subsystem_id="nsi_kernel",
            title="NSI Kernel",
            layer="interface_kernel",
            status="boot_ready" if nsi_ready else "missing",
            boot_required=True,
            production_required=True,
            evidence=_evidence_for(artifacts, "v52_nsi"),
            gaps=tuple() if nsi_ready else _missing_for(artifacts, "v52_nsi") + ("NSI schema freeze/conformance/result-bundle gates are not all true.",),
            next_action="Expand NSI adapter certification beyond local skeletons.",
            allowed_statement="BiC OS has a local vendor-neutral NSI kernel profile with conformance and result-bundle checks.",
            forbidden_statement="NSI is already an externally adopted universal standard.",
        ),
        BiCOSSubsystemV511(
            subsystem_id="evidence_ledger",
            title="Evidence Ledger",
            layer="evidence_kernel",
            status="boot_ready" if evidence_ready else "missing",
            boot_required=True,
            production_required=True,
            evidence=_evidence_for(artifacts, "v53_evidence_ledger"),
            gaps=tuple() if evidence_ready else _missing_for(artifacts, "v53_evidence_ledger") + ("Ledger chain/reference bundle/local signature gates are not all true.",),
            next_action="Add external identity/notarization and retention policy.",
            allowed_statement="BiC OS has a local evidence ledger for reproducible result bundles.",
            forbidden_statement="The ledger is a production external notarization service today.",
        ),
        BiCOSSubsystemV511(
            subsystem_id="llm_agent_bridge",
            title="LLM/Agent Bridge",
            layer="agent_control",
            status="boot_ready" if agent_ready else "missing",
            boot_required=True,
            production_required=True,
            evidence=_evidence_for(artifacts, "v54_agent_bridge"),
            gaps=tuple() if agent_ready else _missing_for(artifacts, "v54_agent_bridge") + ("Agent bridge safe replay/live-shadow/direct-actuation gates are not all true.",),
            next_action="Expose the bridge through a durable service or MCP-compatible endpoint.",
            allowed_statement="BiC OS can translate approved agent requests into safe NSI task manifests.",
            forbidden_statement="Agents can directly control live biological actuation.",
        ),
        BiCOSSubsystemV511(
            subsystem_id="control_plane_queue",
            title="Control Plane Queue",
            layer="runtime_orchestration",
            status="boot_ready" if queue_ready else "missing",
            boot_required=True,
            production_required=True,
            evidence=_evidence_for(artifacts, "v55_control_plane", "v43_job_model"),
            gaps=tuple() if queue_ready else _missing_for(artifacts, "v55_control_plane", "v43_job_model") + ("Queue admission gates are not all true.",),
            next_action="Replace the in-memory queue with durable persistence and workers.",
            allowed_statement="BiC OS has an offline queue admission path for approved NSI/agent jobs.",
            forbidden_statement="The queue is already a production scheduler/worker daemon.",
        ),
        BiCOSSubsystemV511(
            subsystem_id="safety_supervisor",
            title="Safety Supervisor",
            layer="safety_kernel",
            status="boot_ready" if safety_ready else "missing",
            boot_required=True,
            production_required=True,
            evidence=_evidence_for(artifacts, "v52_nsi", "v54_agent_bridge", "v55_control_plane", "v510_claim_audit"),
            gaps=tuple() if safety_ready else _missing_for(artifacts, "v52_nsi", "v54_agent_bridge", "v55_control_plane", "v510_claim_audit") + ("Safety and claim-boundary gates are not all true.",),
            next_action="Add signed lab allowlists and operator approval workflow.",
            allowed_statement="BiC OS blocks unsafe live actuation by default and preserves claim boundaries.",
            forbidden_statement="BiC OS currently enables unrestricted closed-loop stimulation.",
        ),
        BiCOSSubsystemV511(
            subsystem_id="raw_data_runtime",
            title="Raw Data Runtime",
            layer="data_runtime",
            status="boot_ready" if raw_ready else "degraded",
            boot_required=True,
            production_required=False,
            evidence=_evidence_for(artifacts, "v58_raw_native", "v59_stability"),
            gaps=("Target-ID decoding and v15/v50 raw equivalence remain unsupported.",) if raw_ready else _missing_for(artifacts, "v58_raw_native", "v59_stability") + ("Raw feature rows or repeatability gates are not available.",),
            next_action="Acquire stronger repeated-target raw coverage or exact raw/preprocessed overlap.",
            allowed_statement="BiC OS can boot a raw-data replay/audit runtime with repeatable event-window features.",
            forbidden_statement="The current raw runtime proves live compute, target-ID decoding or raw equivalence.",
        ),
        BiCOSSubsystemV511(
            subsystem_id="claim_supervisor",
            title="Claim Supervisor",
            layer="governance_kernel",
            status="boot_ready" if claim_ready else "missing",
            boot_required=True,
            production_required=True,
            evidence=_evidence_for(artifacts, "v510_claim_audit", "master_plan", "first_mover_strategy"),
            gaps=tuple() if claim_ready else _missing_for(artifacts, "v510_claim_audit", "master_plan", "first_mover_strategy") + ("v5.10 claim audit is not on-mission with claim boundaries.",),
            next_action="Keep claim register updated for each OS subsystem release.",
            allowed_statement="BiC OS has a local claim supervisor that separates supported claims from blocked claims.",
            forbidden_statement="BiC OS has proven global uniqueness or first-biological-computer status.",
        ),
        BiCOSSubsystemV511(
            subsystem_id="scheduler_worker_daemon",
            title="Scheduler and Worker Daemon",
            layer="production_runtime",
            status="degraded" if queue_ready else "missing",
            boot_required=False,
            production_required=True,
            evidence=_evidence_for(artifacts, "v55_control_plane", "v43_job_model"),
            gaps=("Only offline/in-memory queue admission exists; no persistent daemon, worker pool or recovery loop.",),
            next_action="Implement durable job store, worker lifecycle, retries and resumable execution.",
            allowed_statement="BiC OS has an offline scheduler scaffold through queue admission.",
            forbidden_statement="BiC OS already has a production scheduler daemon.",
        ),
        BiCOSSubsystemV511(
            subsystem_id="permission_identity_system",
            title="Permission and Identity System",
            layer="production_governance",
            status="degraded" if artifacts["v43_job_model"]["exists"] else "missing",
            boot_required=False,
            production_required=True,
            evidence=_evidence_for(artifacts, "v43_job_model", "v55_control_plane"),
            gaps=("Roles, tiers and quotas exist as local models; API keys, auth, tenancy and signed approvals are not production-ready.",),
            next_action="Add API-key auth, workspace tenancy, signed approval refs and policy persistence.",
            allowed_statement="BiC OS has local roles, tiers and quota models.",
            forbidden_statement="BiC OS has production-grade identity, auth and lab approval today.",
        ),
        BiCOSSubsystemV511(
            subsystem_id="adapter_plugin_manager",
            title="Adapter Plugin Manager",
            layer="extension_runtime",
            status="degraded" if nsi_ready else "missing",
            boot_required=False,
            production_required=True,
            evidence=_evidence_for(artifacts, "v52_nsi", "v49_blueprint"),
            gaps=("Adapter conformance exists, but plugin packaging, registry, versioning and certification workflow are not implemented.",),
            next_action="Implement plugin manifest, local registry and adapter certification runner.",
            allowed_statement="BiC OS has adapter conformance foundations.",
            forbidden_statement="BiC OS already has a production adapter marketplace.",
        ),
        BiCOSSubsystemV511(
            subsystem_id="dashboard_control_plane",
            title="Dashboard Control Plane",
            layer="operator_interface",
            status="missing",
            boot_required=False,
            production_required=True,
            evidence=_evidence_for(artifacts, "v49_blueprint"),
            gaps=("No production dashboard/backend UI for datasets, jobs, approvals, telemetry and bundles.",),
            next_action="Build a minimal local operator dashboard backed by the v5.11 boot manifest and queue state.",
            allowed_statement="BiC OS dashboard is specified as a required OS layer.",
            forbidden_statement="BiC OS already ships a production dashboard.",
        ),
        BiCOSSubsystemV511(
            subsystem_id="live_telemetry_lab_gateway",
            title="Live Telemetry and Lab Gateway",
            layer="live_lab_runtime",
            status="blocked_for_production",
            boot_required=False,
            production_required=True,
            evidence=_evidence_for(artifacts, "first_mover_strategy", "v510_claim_audit"),
            gaps=("No partner live stream, live-shadow telemetry bundle, lab approval workflow or approved actuation evidence exists.",),
            next_action="Validate read-only/live-shadow partner API credentials before any closed-loop module.",
            allowed_statement="BiC OS keeps live telemetry and lab control as a gated future layer.",
            forbidden_statement="BiC OS has proven live biological compute or lab-approved closed loop.",
        ),
    )


def build_bic_os_boot_readiness_v511(root: str | Path = ".") -> dict[str, Any]:
    project_root = Path(root)
    artifacts = _artifact_map(project_root)
    subsystems = build_bic_os_subsystems_v511(project_root)
    status_counts: dict[str, int] = {}
    for subsystem in subsystems:
        status_counts[subsystem.status] = status_counts.get(subsystem.status, 0) + 1

    boot_required = [subsystem for subsystem in subsystems if subsystem.boot_required]
    production_required = [subsystem for subsystem in subsystems if subsystem.production_required]
    offline_bootable = all(subsystem.status == "boot_ready" for subsystem in boot_required)
    production_ready = all(subsystem.status == "boot_ready" for subsystem in production_required)
    if offline_bootable and not production_ready:
        overall_status = "bic_os_offline_runtime_kernel_boot_ready_production_os_not_claimed"
    elif offline_bootable and production_ready:
        overall_status = "bic_os_production_ready_review_required"
    else:
        overall_status = "bic_os_boot_readiness_incomplete"

    production_blockers = [
        {
            "subsystem_id": subsystem.subsystem_id,
            "status": subsystem.status,
            "gaps": list(subsystem.gaps),
            "next_action": subsystem.next_action,
        }
        for subsystem in production_required
        if subsystem.status != "boot_ready"
    ]
    boot_sequence = [subsystem.subsystem_id for subsystem in boot_required if subsystem.status == "boot_ready"]
    return {
        "version": "v5.11",
        "product_name": PRODUCT_NAME,
        "boot_profile": "offline_runtime_kernel",
        "overall_status": overall_status,
        "offline_runtime_kernel_bootable": offline_bootable,
        "production_os_ready": production_ready,
        "status_counts": dict(sorted(status_counts.items())),
        "boot_sequence": boot_sequence,
        "production_blocker_count": len(production_blockers),
        "production_blockers": production_blockers,
        "artifact_presence": {key: {"path": value["path"], "exists": bool(value["exists"])} for key, value in sorted(artifacts.items())},
        "subsystems": [subsystem.to_dict() for subsystem in subsystems],
        "direct_answer": {
            "remembered_name": PRODUCT_NAME,
            "are_we_continuing_toward_the_os": "yes",
            "can_we_claim_full_unique_os_now": "no",
            "what_boots_now": "offline BiC OS runtime kernel: NSI, evidence ledger, LLM-agent bridge, queue admission, safety supervisor, raw-data replay/audit runtime and claim supervisor",
            "what_blocks_full_os": "persistent daemon/scheduler, production auth and permissions, plugin manager, dashboard, live telemetry, lab approval workflow and external prior-art evidence for uniqueness",
        },
        "claim_boundary": "v5.11 validates BiC OS offline runtime-kernel boot readiness from local artifacts only. It does not claim a production OS, global uniqueness, live BioGPU proof, GPU replacement or energy superiority.",
    }


def write_bic_os_boot_outputs_v511(audit: dict[str, Any], out_dir: str | Path = DEFAULT_OUT) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary_json": out / "V511_BIC_OS_BOOT_READINESS_SUMMARY.json",
        "boot_manifest_json": out / "V511_BIC_OS_BOOT_MANIFEST.json",
        "subsystem_csv": out / "V511_BIC_OS_SUBSYSTEM_READINESS.csv",
        "markdown_report": out / "BIOGPU_V511_BIC_OS_BOOT_READINESS_REPORT.md",
    }
    summary = {key: value for key, value in audit.items() if key not in {"subsystems", "production_blockers"}}
    summary["production_blocker_ids"] = [item["subsystem_id"] for item in audit["production_blockers"]]
    paths["summary_json"].write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["boot_manifest_json"].write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8")
    _write_subsystem_csv(paths["subsystem_csv"], audit["subsystems"])
    paths["markdown_report"].write_text(_markdown_report(audit), encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}


def _write_subsystem_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = ["subsystem_id", "title", "layer", "status", "boot_required", "production_required", "next_action", "evidence", "gaps"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({
                "subsystem_id": row["subsystem_id"],
                "title": row["title"],
                "layer": row["layer"],
                "status": row["status"],
                "boot_required": row["boot_required"],
                "production_required": row["production_required"],
                "next_action": row["next_action"],
                "evidence": " | ".join(str(value) for value in row.get("evidence", [])),
                "gaps": " | ".join(str(value) for value in row.get("gaps", [])),
            })


def _markdown_report(audit: dict[str, Any]) -> str:
    answer = audit["direct_answer"]
    lines = [
        "# BioGPU-Core v5.11 BiC OS Boot Readiness Report",
        "",
        "## Direct Answer",
        "",
        f"- Name: `{answer['remembered_name']}`",
        f"- Continue toward OS: `{answer['are_we_continuing_toward_the_os']}`",
        f"- Full unique OS claim now: `{answer['can_we_claim_full_unique_os_now']}`",
        f"- What boots now: {answer['what_boots_now']}",
        f"- What blocks full OS: {answer['what_blocks_full_os']}",
        "",
        "## Overall Status",
        "",
        f"`{audit['overall_status']}`",
        "",
        "## Subsystem Readiness",
        "",
        "| Subsystem | Status | Boot Required | Production Required | Next Action |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in audit["subsystems"]:
        lines.append(
            f"| `{row['subsystem_id']}` | `{row['status']}` | `{row['boot_required']}` | `{row['production_required']}` | {row['next_action']} |"
        )
    lines.extend([
        "",
        "## Production Blockers",
        "",
    ])
    if audit["production_blockers"]:
        for blocker in audit["production_blockers"]:
            lines.append(f"- `{blocker['subsystem_id']}`: {blocker['next_action']}")
    else:
        lines.append("- None reported by this local audit.")
    lines.extend([
        "",
        "## Boundary",
        "",
        audit["claim_boundary"],
        "",
    ])
    return "\n".join(lines)
