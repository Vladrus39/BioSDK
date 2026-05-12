"""BioSDK evidence pack and readiness audit, v5.12."""
from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


DEFAULT_OUT = Path("outputs/v512_biosdk_evidence_pack")
SDK_NAME = "BioSDK / Living Compute SDK"


@dataclass(frozen=True)
class BioSDKCapabilityV512:
    capability_id: str
    title: str
    sdk_layer: str
    status: str
    proof_level: str
    public_api: tuple[str, ...]
    cli_entrypoints: tuple[str, ...]
    evidence: tuple[str, ...]
    gaps: tuple[str, ...]
    next_action: str
    why_it_matters: str
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
        "pyproject": "pyproject.toml",
        "readme": "README.md",
        "cli": "biogpu/cli.py",
        "v50_bundle": "outputs/v50_pc_validation_bundle/V50_PC_VALIDATION_BUNDLE_SUMMARY.json",
        "v51_dataset": "outputs/v51_dataset_expansion/V51_DATASET_EXPANSION_SUMMARY.json",
        "v52_nsi": "outputs/v52_nsi_interface/V52_NSI_INTERFACE_SUMMARY.json",
        "v53_ledger": "outputs/v53_evidence_ledger/V53_EVIDENCE_LEDGER_SUMMARY.json",
        "v54_agent": "outputs/v54_llm_agent_bridge/V54_LLM_AGENT_BRIDGE_SUMMARY.json",
        "v55_queue": "outputs/v55_control_plane_queue/V55_CONTROL_PLANE_QUEUE_SUMMARY.json",
        "v56_raw_structure": "outputs/v56_raw_hdf5_structure/V56_RAW_HDF5_STRUCTURE_SUMMARY.json",
        "v57_alignment": "outputs/v57_raw_preprocessed_alignment/V57_RAW_PREPROCESSED_ALIGNMENT_SUMMARY.json",
        "v58_raw_native": "outputs/v58_raw_native_benchmark/V58_RAW_NATIVE_FEATURE_SUMMARY.json",
        "v59_stability": "outputs/v59_raw_native_stability_audit/V59_RAW_NATIVE_STABILITY_SUMMARY.json",
        "v510_claim": "outputs/v510_project_alignment_claim_audit/V510_PROJECT_ALIGNMENT_SUMMARY.json",
        "v511_boot": "outputs/v511_bic_os_boot_readiness/V511_BIC_OS_BOOT_READINESS_SUMMARY.json",
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


def _v50_ready(data: dict[str, Any]) -> bool:
    return data.get("status") == "ok" and _int_value(data, "artifact_count") >= 1 and bool(data.get("bundle_sha256"))


def _v52_ready(data: dict[str, Any]) -> bool:
    return (
        data.get("schema_status") == "frozen_interface_profile"
        and _int_value(data, "schema_count") >= 7
        and _gate(data, "nsi_schemas_frozen")
        and _gate(data, "adapter_conformance_passed")
        and _gate(data, "result_bundle_validator_passed")
        and _gate(data, "claim_annotation_available")
    )


def _v53_ready(data: dict[str, Any]) -> bool:
    return bool(data.get("ledger_chain_valid")) and bool(data.get("reference_bundle_valid")) and _gate(data, "local_signatures_present")


def _v54_ready(data: dict[str, Any]) -> bool:
    return (
        _int_value(data, "tool_count") >= 8
        and _gate(data, "safe_replay_agent_request_approved")
        and _gate(data, "live_shadow_requires_or_has_approval")
        and _gate(data, "direct_actuation_blocked")
        and _gate(data, "nsi_manifest_emitted_for_safe_requests")
    )


def _v55_ready(data: dict[str, Any]) -> bool:
    return bool(data.get("safe_replay_admitted")) and bool(data.get("blocked_actuation_rejected")) and _int_value(data, "queued_job_count") >= 1


def _raw_ready(v56: dict[str, Any], v58: dict[str, Any], v59: dict[str, Any]) -> bool:
    return (
        _int_value(v56, "valid_file_count") > 0
        and _int_value(v56, "files_with_events") > 0
        and _int_value(v58, "feature_row_count") > 0
        and v59.get("split_half_repeatability_status") == "split_half_repeatability_available"
        and _float_value(v59, "split_half_cosine_median") >= 0.95
    )


def _claim_ready(data: dict[str, Any]) -> bool:
    return (
        data.get("overall_status") == "on_mission_with_claim_boundaries"
        and data.get("direct_answer", {}).get("did_we_drift_from_project_meaning") == "no"
        and data.get("direct_answer", {}).get("is_the_code_globally_unique_proven") == "no_local_tests_cannot_prove_global_uniqueness"
    )


def _boot_ready(data: dict[str, Any]) -> bool:
    return data.get("product_name") == "BiC OS" and bool(data.get("offline_runtime_kernel_bootable")) and data.get("production_os_ready") is False


def build_biosdk_capabilities_v512(root: str | Path = ".") -> tuple[BioSDKCapabilityV512, ...]:
    project_root = Path(root)
    artifacts = _artifact_map(project_root)
    v50 = artifacts["v50_bundle"]["json"]
    v51 = artifacts["v51_dataset"]["json"]
    v52 = artifacts["v52_nsi"]["json"]
    v53 = artifacts["v53_ledger"]["json"]
    v54 = artifacts["v54_agent"]["json"]
    v55 = artifacts["v55_queue"]["json"]
    v56 = artifacts["v56_raw_structure"]["json"]
    v57 = artifacts["v57_alignment"]["json"]
    v58 = artifacts["v58_raw_native"]["json"]
    v59 = artifacts["v59_stability"]["json"]
    v510 = artifacts["v510_claim"]["json"]
    v511 = artifacts["v511_boot"]["json"]

    dataset_probe_count = len(v51.get("probes", [])) if isinstance(v51.get("probes"), list) else 0
    dataset_status = "partially_proven" if dataset_probe_count >= 4 else "missing"
    if dataset_status == "partially_proven" and bool(v51.get("gate", {}).get("nwb_available")):
        dataset_status = "locally_proven"

    raw_status = "locally_proven" if _raw_ready(v56, v58, v59) else "partial_or_missing"
    raw_gaps = []
    if _int_value(v57, "exact_recording_match_count") == 0:
        raw_gaps.append("Exact raw/preprocessed overlap for v15/v50 PC rows is not proven.")
    if v59.get("target_readout_signal_status") == "not_supported":
        raw_gaps.append("Target-ID decoding is not supported on the current sparse repeated-target raw subset.")

    return (
        BioSDKCapabilityV512(
            capability_id="pc_evidence_bundle",
            title="PC Validation Evidence Bundle",
            sdk_layer="evidence_foundation",
            status="locally_proven" if _v50_ready(v50) else "missing",
            proof_level="local_reproducible_bundle" if _v50_ready(v50) else "missing_artifact",
            public_api=("biogpu.release.pc_validation_bundle_v50",),
            cli_entrypoints=("scripts/package_biogpu_v50_pc_validation_bundle.ps1",),
            evidence=_evidence_for(artifacts, "v50_bundle"),
            gaps=tuple() if _v50_ready(v50) else _missing_for(artifacts, "v50_bundle") + ("PC validation bundle summary is missing or invalid.",),
            next_action="Keep bundle checksums and full-shuffle artifacts in every SDK release candidate.",
            why_it_matters="A wanted BioSDK must ship evidence, not only code.",
            allowed_statement="BioSDK has a local reproducible PC validation evidence bundle.",
            forbidden_statement="The PC bundle proves live BioGPU or GPU replacement.",
        ),
        BioSDKCapabilityV512(
            capability_id="dataset_import_layer",
            title="Dataset and Adapter Import Layer",
            sdk_layer="data_sdk",
            status=dataset_status,
            proof_level="local_multi_probe_partial" if dataset_status == "partially_proven" else "local_multi_probe",
            public_api=("biogpu.data_ingest", "biogpu.datasets", "biogpu.substrates"),
            cli_entrypoints=("biogpu.cli public-data", "scripts/run_biogpu_v51_dataset_api_expansion.ps1"),
            evidence=_evidence_for(artifacts, "v51_dataset", "v56_raw_structure"),
            gaps=("DANDI/NWB real file gate is not yet downloaded/validated.", "External read-only API credentials are not validated."),
            next_action="Add at least one real NWB/DANDI file gate and one external read-only adapter validation.",
            why_it_matters="Labs will want an SDK that accepts many real data sources without vendor lock-in.",
            allowed_statement="BioSDK has local dataset/importer probes and raw HDF5 availability, with NWB/external API gaps visible.",
            forbidden_statement="BioSDK has proven all target external dataset/API integrations.",
        ),
        BioSDKCapabilityV512(
            capability_id="nsi_contract",
            title="NSI-1.0 Contract and Validators",
            sdk_layer="interface_sdk",
            status="locally_proven" if _v52_ready(v52) else "missing",
            proof_level="local_schema_conformance" if _v52_ready(v52) else "missing_artifact",
            public_api=("biogpu.standards.nsi_v10", "biogpu.standards.nsi_conformance_v52"),
            cli_entrypoints=("biogpu-validate-nsi", "python -m biogpu.cli validate-nsi"),
            evidence=_evidence_for(artifacts, "v52_nsi"),
            gaps=tuple() if _v52_ready(v52) else _missing_for(artifacts, "v52_nsi") + ("NSI gates are not all true.",),
            next_action="Publish stable SDK examples for every NSI schema.",
            why_it_matters="A real SDK needs stable contracts that third parties can implement.",
            allowed_statement="BioSDK has a frozen local NSI-1.0 interface profile and validators.",
            forbidden_statement="NSI is already an externally adopted universal standard.",
        ),
        BioSDKCapabilityV512(
            capability_id="evidence_ledger",
            title="Evidence Ledger and Bundle Validator",
            sdk_layer="evidence_sdk",
            status="locally_proven" if _v53_ready(v53) else "missing",
            proof_level="local_chain_and_signature" if _v53_ready(v53) else "missing_artifact",
            public_api=("biogpu.evidence.ledger_v53",),
            cli_entrypoints=("biogpu-v53-evidence-ledger", "scripts/run_biogpu_v53_evidence_ledger.ps1"),
            evidence=_evidence_for(artifacts, "v53_ledger"),
            gaps=tuple() if _v53_ready(v53) else _missing_for(artifacts, "v53_ledger") + ("Ledger gates are not all true.",),
            next_action="Add external identity/notarization and retention policy.",
            why_it_matters="Users will trust the tool if every result can be audited and reproduced.",
            allowed_statement="BioSDK has local evidence-ledger validation and local integrity signatures.",
            forbidden_statement="The ledger is a production external notarization network.",
        ),
        BioSDKCapabilityV512(
            capability_id="agent_tool_bridge",
            title="LLM/Agent Tool Bridge",
            sdk_layer="agent_sdk",
            status="locally_proven" if _v54_ready(v54) else "missing",
            proof_level="local_policy_and_manifest_gate" if _v54_ready(v54) else "missing_artifact",
            public_api=("biogpu.llm.agent_bridge_v54",),
            cli_entrypoints=("biogpu-v54-llm-agent-bridge", "scripts/run_biogpu_v54_llm_agent_bridge.ps1"),
            evidence=_evidence_for(artifacts, "v54_agent"),
            gaps=tuple() if _v54_ready(v54) else _missing_for(artifacts, "v54_agent") + ("Agent bridge gates are not all true.",),
            next_action="Expose agent tools through a durable service or MCP-compatible wrapper.",
            why_it_matters="Agent-native biological compute is a major adoption wedge if it stays safe and auditable.",
            allowed_statement="BioSDK can turn approved agent requests into safe NSI task manifests.",
            forbidden_statement="LLM agents can directly actuate live biological systems.",
        ),
        BioSDKCapabilityV512(
            capability_id="control_plane_admission",
            title="Control Plane Admission",
            sdk_layer="runtime_sdk",
            status="locally_proven" if _v55_ready(v55) else "missing",
            proof_level="local_queue_admission_gate" if _v55_ready(v55) else "missing_artifact",
            public_api=("biogpu.beta.control_plane_v55", "biogpu.beta.job_model_v43"),
            cli_entrypoints=("biogpu-v55-control-plane-queue", "scripts/run_biogpu_v55_control_plane_queue.ps1"),
            evidence=_evidence_for(artifacts, "v55_queue"),
            gaps=("Queue is still in-memory/offline; durable scheduler workers are not implemented.",),
            next_action="Implement durable scheduler, persisted jobs and worker lifecycle.",
            why_it_matters="A working tool must move from library calls to governed jobs users can run repeatedly.",
            allowed_statement="BioSDK has safe offline job admission from approved agent/NSI manifests.",
            forbidden_statement="BioSDK has a production scheduler daemon today.",
        ),
        BioSDKCapabilityV512(
            capability_id="raw_data_runtime",
            title="Raw Data Runtime and Audits",
            sdk_layer="neural_data_sdk",
            status=raw_status,
            proof_level="local_raw_hdf5_repeatability" if raw_status == "locally_proven" else "partial_or_missing",
            public_api=("biogpu.data_ingest.zenodo_raw_hdf5_v56", "biogpu.data_ingest.raw_native_benchmark_v58", "biogpu.analysis.raw_native_stability_v59"),
            cli_entrypoints=("biogpu-v56-raw-hdf5-structure", "biogpu-v58-raw-native-benchmark", "biogpu-v59-raw-native-stability-audit"),
            evidence=_evidence_for(artifacts, "v56_raw_structure", "v57_alignment", "v58_raw_native", "v59_stability"),
            gaps=tuple(raw_gaps),
            next_action="Acquire stronger repeated-target raw coverage or exact raw/preprocessed overlap.",
            why_it_matters="The SDK becomes serious when it handles real raw neural recordings, not only preprocessed tables.",
            allowed_statement="BioSDK has raw HDF5 inspection, event-window feature extraction and repeatability evidence.",
            forbidden_statement="The raw runtime proves target-ID decoding, live compute or v15/v50 raw equivalence.",
        ),
        BioSDKCapabilityV512(
            capability_id="claim_supervisor",
            title="Claim Supervisor",
            sdk_layer="governance_sdk",
            status="locally_proven" if _claim_ready(v510) else "missing",
            proof_level="local_claim_boundary_gate" if _claim_ready(v510) else "missing_artifact",
            public_api=("biogpu.claims.project_alignment_v510",),
            cli_entrypoints=("biogpu-v510-project-alignment-claim-audit",),
            evidence=_evidence_for(artifacts, "v510_claim", "master_plan", "first_mover_strategy"),
            gaps=tuple() if _claim_ready(v510) else _missing_for(artifacts, "v510_claim") + ("Claim audit is not on-mission with boundaries.",),
            next_action="Attach claim levels to every SDK result object and report.",
            why_it_matters="A project people trust must block overclaims automatically.",
            allowed_statement="BioSDK separates locally supported claims from blocked claims.",
            forbidden_statement="BioSDK has proven global uniqueness, first biological computer or GPU replacement claims.",
        ),
        BioSDKCapabilityV512(
            capability_id="bic_os_boot_bridge",
            title="BiC OS Boot Bridge",
            sdk_layer="os_bridge",
            status="locally_proven" if _boot_ready(v511) else "missing",
            proof_level="local_offline_runtime_kernel" if _boot_ready(v511) else "missing_artifact",
            public_api=("biogpu.os.boot_readiness_v511",),
            cli_entrypoints=("biogpu-v511-bic-os-boot-readiness",),
            evidence=_evidence_for(artifacts, "v511_boot"),
            gaps=("Production OS blockers remain: daemon, auth, plugins, dashboard, live telemetry/lab gateway.",),
            next_action="Do not claim BiC OS production readiness until BioSDK proof gates and runtime services are complete.",
            why_it_matters="The SDK must be the proven bridge into BiC OS, not a shortcut around evidence.",
            allowed_statement="BioSDK can feed an offline BiC OS runtime-kernel boot manifest.",
            forbidden_statement="BiC OS is production-ready or globally unique today.",
        ),
    )


def build_biosdk_evidence_pack_v512(root: str | Path = ".") -> dict[str, Any]:
    project_root = Path(root)
    artifacts = _artifact_map(project_root)
    capabilities = build_biosdk_capabilities_v512(project_root)
    status_counts: dict[str, int] = {}
    for capability in capabilities:
        status_counts[capability.status] = status_counts.get(capability.status, 0) + 1

    proof_ready_ids = {
        "pc_evidence_bundle",
        "nsi_contract",
        "evidence_ledger",
        "agent_tool_bridge",
        "control_plane_admission",
        "raw_data_runtime",
        "claim_supervisor",
        "bic_os_boot_bridge",
    }
    proof_ready = all(capability.status == "locally_proven" for capability in capabilities if capability.capability_id in proof_ready_ids)
    full_sdk_ready = all(capability.status == "locally_proven" for capability in capabilities) and False
    overall_status = "biosdk_evidence_kernel_ready_full_sdk_not_claimed" if proof_ready else "biosdk_evidence_kernel_incomplete"

    capability_gaps = [
        {
            "capability_id": capability.capability_id,
            "status": capability.status,
            "gaps": list(capability.gaps),
            "next_action": capability.next_action,
        }
        for capability in capabilities
        if capability.gaps or capability.status != "locally_proven"
    ]
    return {
        "version": "v5.12",
        "sdk_name": SDK_NAME,
        "overall_status": overall_status,
        "biosdk_evidence_kernel_ready": proof_ready,
        "full_biosdk_ready": full_sdk_ready,
        "status_counts": dict(sorted(status_counts.items())),
        "locally_proven_capability_count": status_counts.get("locally_proven", 0),
        "capability_count": len(capabilities),
        "capability_gap_count": len(capability_gaps),
        "capability_gaps": capability_gaps,
        "artifact_presence": {key: {"path": value["path"], "exists": bool(value["exists"])} for key, value in sorted(artifacts.items())},
        "capabilities": [capability.to_dict() for capability in capabilities],
        "what_makes_it_a_real_tool": [
            "stable public SDK contracts and CLI gates",
            "multi-source data import with real raw neural data support",
            "reproducible evidence bundles and ledger validation",
            "agent-native tasking with blocked-by-default live actuation",
            "safe job admission and future durable scheduler",
            "claim supervisor that prevents marketing from outrunning evidence",
            "developer docs, examples, tests and acceptance gates for every capability",
        ],
        "what_can_make_it_unique_and_desired": [
            "vendor-neutral living-compute SDK instead of one closed wetware device",
            "evidence-first result bundles as the default product behavior",
            "LLM-agent integration that can plan biological compute jobs without unsafe actuation",
            "raw-data plus replay plus read-only API path in one runtime",
            "adapter conformance and future plugin certification for labs and vendors",
            "clear path from BioSDK to BiC OS without overclaiming production readiness",
        ],
        "direct_answer": {
            "should_bic_os_wait_for_proven_biosdk": "yes",
            "is_biosdk_evidence_kernel_ready": "yes" if proof_ready else "not_yet",
            "is_full_biosdk_proven": "no",
            "is_global_uniqueness_proven": "no_local_tests_cannot_prove_global_uniqueness",
            "next_best_build_step": "durable scheduler plus public SDK examples and external adapter validation",
        },
        "claim_boundary": "v5.12 validates BioSDK evidence-kernel readiness from local artifacts. It does not claim a complete production BioSDK, global uniqueness, production BiC OS, live BioGPU proof, GPU replacement or energy superiority.",
    }


def write_biosdk_evidence_pack_outputs_v512(audit: dict[str, Any], out_dir: str | Path = DEFAULT_OUT) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary_json": out / "V512_BIOSDK_EVIDENCE_PACK_SUMMARY.json",
        "capability_matrix_json": out / "V512_BIOSDK_CAPABILITY_MATRIX.json",
        "capability_matrix_csv": out / "V512_BIOSDK_CAPABILITY_MATRIX.csv",
        "markdown_report": out / "BIOGPU_V512_BIOSDK_EVIDENCE_PACK_REPORT.md",
    }
    summary = {key: value for key, value in audit.items() if key not in {"capabilities", "capability_gaps"}}
    summary["capability_gap_ids"] = [item["capability_id"] for item in audit["capability_gaps"]]
    paths["summary_json"].write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["capability_matrix_json"].write_text(json.dumps(audit["capabilities"], indent=2, ensure_ascii=False), encoding="utf-8")
    _write_capability_csv(paths["capability_matrix_csv"], audit["capabilities"])
    paths["markdown_report"].write_text(_markdown_report(audit), encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}


def _write_capability_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = ["capability_id", "title", "sdk_layer", "status", "proof_level", "next_action", "public_api", "cli_entrypoints", "evidence", "gaps"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({
                "capability_id": row["capability_id"],
                "title": row["title"],
                "sdk_layer": row["sdk_layer"],
                "status": row["status"],
                "proof_level": row["proof_level"],
                "next_action": row["next_action"],
                "public_api": " | ".join(str(value) for value in row.get("public_api", [])),
                "cli_entrypoints": " | ".join(str(value) for value in row.get("cli_entrypoints", [])),
                "evidence": " | ".join(str(value) for value in row.get("evidence", [])),
                "gaps": " | ".join(str(value) for value in row.get("gaps", [])),
            })


def _markdown_report(audit: dict[str, Any]) -> str:
    answer = audit["direct_answer"]
    lines = [
        "# BioGPU-Core v5.12 BioSDK Evidence Pack Report",
        "",
        "## Direct Answer",
        "",
        f"- Should BiC OS wait for proven BioSDK: `{answer['should_bic_os_wait_for_proven_biosdk']}`",
        f"- BioSDK evidence kernel ready: `{answer['is_biosdk_evidence_kernel_ready']}`",
        f"- Full BioSDK proven: `{answer['is_full_biosdk_proven']}`",
        f"- Global uniqueness proven: `{answer['is_global_uniqueness_proven']}`",
        f"- Next best build step: {answer['next_best_build_step']}",
        "",
        "## Overall Status",
        "",
        f"`{audit['overall_status']}`",
        "",
        "## Capability Matrix",
        "",
        "| Capability | Status | Proof | Next Action |",
        "| --- | --- | --- | --- |",
    ]
    for row in audit["capabilities"]:
        lines.append(f"| `{row['capability_id']}` | `{row['status']}` | `{row['proof_level']}` | {row['next_action']} |")
    lines.extend([
        "",
        "## What Makes This A Real Tool",
        "",
    ])
    for item in audit["what_makes_it_a_real_tool"]:
        lines.append(f"- {item}")
    lines.extend([
        "",
        "## What Can Make It Unique And Wanted",
        "",
    ])
    for item in audit["what_can_make_it_unique_and_desired"]:
        lines.append(f"- {item}")
    lines.extend([
        "",
        "## Boundary",
        "",
        audit["claim_boundary"],
        "",
    ])
    return "\n".join(lines)
