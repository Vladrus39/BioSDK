
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional
import csv
import json

VERSION = "4.0.0"

@dataclass(frozen=True)
class ReleaseChannelV40:
    channel_id: str
    name: str
    audience: str
    delivery: str
    primary_use: str
    data_location: str
    monetization: str
    allowed_modes: List[str]
    blocked_modes: List[str]
    required_gates: List[str]

@dataclass(frozen=True)
class DatasetExpansionItemV40:
    dataset_id: str
    name: str
    source_type: str
    priority: int
    adapter_status: str
    reason: str
    required_work: List[str]
    power_pc_required: bool
    beta_relevance: str

@dataclass(frozen=True)
class APISourceItemV40:
    api_id: str
    name: str
    access_stage: str
    adapter_status: str
    first_safe_mode: str
    enterprise_value: str
    blocked_until_approval: List[str]

@dataclass(frozen=True)
class ValidationGateV40:
    gate_id: str
    name: str
    purpose: str
    pass_criteria: List[str]
    output_artifacts: List[str]

@dataclass(frozen=True)
class DeferredWorkItemV40:
    item_id: str
    phase: str
    title: str
    why_deferred: str
    execution_environment: str
    required_inputs: List[str]
    deliverables: List[str]
    exit_criteria: List[str]


@dataclass(frozen=True)
class RoadmapMilestoneV40:
    version: str
    title: str
    purpose: str
    deliverables: List[str]
    exit_criteria: List[str]


def release_channels_v40() -> List[ReleaseChannelV40]:
    return [
        ReleaseChannelV40(
            channel_id="private_github_sdk",
            name="Private GitHub / Private Package SDK",
            audience="labs, enterprise engineers, early technical partners",
            delivery="private repository, wheel package, Docker image, examples, docs",
            primary_use="developer evaluation and on-prem reproducible runs",
            data_location="customer/local environment",
            monetization="developer evaluation; paid enterprise license after trial",
            allowed_modes=["mock", "replay", "read_only_import", "local_dataset_validation"],
            blocked_modes=["unapproved_live_stimulation", "wet_lab_protocols", "vendor_pinout_commands"],
            required_gates=["license_check", "safety_boundary", "audit_logging"],
        ),
        ReleaseChannelV40(
            channel_id="hosted_biogpu_server",
            name="Hosted BioGPU Server",
            audience="non-infra beta users, investors, labs needing quick demos",
            delivery="web UI + REST API + job queue + result-bundle downloads",
            primary_use="fast beta access without installing the full stack",
            data_location="hosted sandbox or temporary uploaded datasets",
            monetization="subscription, paid job credits, enterprise workspaces",
            allowed_modes=["mock", "replay", "read_only_uploaded_data", "curated_dataset_runs"],
            blocked_modes=["live_actuation", "unapproved_external_api_write", "unsafe_lab_fields"],
            required_gates=["account_role", "api_key", "quota", "data_retention_policy", "safety_boundary"],
        ),
        ReleaseChannelV40(
            channel_id="enterprise_onprem_docker",
            name="Enterprise On-Prem Docker",
            audience="companies and regulated labs that cannot upload data externally",
            delivery="Docker image, docker-compose, offline license file, admin guide",
            primary_use="private deployment inside customer infrastructure",
            data_location="customer infrastructure only",
            monetization="annual enterprise license + support/SLA package",
            allowed_modes=["mock", "replay", "read_only_import", "internal_api_read_only", "power_pc_sweeps"],
            blocked_modes=["closed_loop_live_control_without_lab_approval"],
            required_gates=["offline_license", "admin_audit", "safety_boundary", "deployment_acceptance_test"],
        ),
        ReleaseChannelV40(
            channel_id="lab_approved_live_addon",
            name="Lab-Approved Live Add-on",
            audience="approved laboratories or vendor platforms with operator oversight",
            delivery="separate paid module, protocol-bound adapter, operator checklist",
            primary_use="live-data shadow mode first; controlled closed-loop later",
            data_location="partner lab/vendor environment",
            monetization="high-value add-on, milestone fees, support contract",
            allowed_modes=["metadata", "read_only_live", "live_shadow", "approved_protocol_closed_loop"],
            blocked_modes=["unreviewed_stimulation", "free-form_electrode_commands", "home_wetlab_use"],
            required_gates=["human_operator", "lab_protocol_id", "vendor_approval", "safety_boundary", "run_manifest", "audit_bundle"],
        ),
    ]


def dataset_expansion_v40() -> List[DatasetExpansionItemV40]:
    return [
        DatasetExpansionItemV40(
            dataset_id="zenodo_14363732_raw_hdf5",
            name="Zenodo 14363732 raw HDF5 MEA dataset",
            source_type="raw_hdf5",
            priority=1,
            adapter_status="planned_v4_1",
            reason="Validate preprocessed spike windows against raw recordings; search TTL/stimulus markers.",
            required_work=["download raw archive on power PC", "inspect HDF5 tree", "locate TTL/stimulus channels", "derive raw pulse windows", "compare raw-derived features with v1.5/v3.6 features"],
            power_pc_required=True,
            beta_relevance="required before strong claims about pulse-level benchmark quality",
        ),
        DatasetExpansionItemV40(
            dataset_id="dandi_nwb_discovery_pack",
            name="DANDI NWB task-aligned discovery pack",
            source_type="nwb_api",
            priority=2,
            adapter_status="existing_seed_plus_planned_expansion",
            reason="Find datasets with units + intervals/trials/stimulus to validate task-aligned BioGPUTrace pipeline.",
            required_work=["DANDI API search", "filter by NWB units and stimulus/trials", "download small sample files", "build stimulus_windows.csv", "run task-aligned readout"],
            power_pc_required=False,
            beta_relevance="broadens SDK beyond one MEA dataset",
        ),
        DatasetExpansionItemV40(
            dataset_id="allen_brain_observatory_visual_coding",
            name="Allen Brain Observatory / AllenSDK visual coding adapter",
            source_type="allen_sdk",
            priority=3,
            adapter_status="planned_v4_1",
            reason="Orientation/drifting-grating tasks are strong analogs for BioGPU encoding/readout benchmarks.",
            required_work=["install AllenSDK on power/dev PC", "download small Neuropixels/visual-coding sample", "extract stimulus presentations", "extract spike/unit responses", "build orientation benchmark"],
            power_pc_required=True,
            beta_relevance="adds a recognized neuroscience benchmark family",
        ),
        DatasetExpansionItemV40(
            dataset_id="finalspark_read_only_live_hdf5",
            name="FinalSpark read-only/live HDF5 bridge",
            source_type="external_api",
            priority=4,
            adapter_status="mock_v3_7_then_real_credentials",
            reason="First real remote wetware API path without live actuation.",
            required_work=["obtain platform access/token", "metadata-only smoke test", "read-only spike/live trace capture", "export BioGPUTrace", "run live-shadow result bundle"],
            power_pc_required=False,
            beta_relevance="shows enterprise BioSDK can connect to external wetware platforms",
        ),
        DatasetExpansionItemV40(
            dataset_id="vendor_export_adapters",
            name="3Brain / Axion / MCS exported-data adapters",
            source_type="vendor_export",
            priority=5,
            adapter_status="mock_v3_7_then_partner_samples",
            reason="Enterprise labs often start with exported files before allowing live SDK access.",
            required_work=["collect sample exports", "write schema mappers", "convert to BioGPUTrace", "run read-only benchmark", "generate compatibility report"],
            power_pc_required=False,
            beta_relevance="makes SDK useful to real MEA labs before live integration",
        ),
    ]


def api_sources_v40() -> List[APISourceItemV40]:
    return [
        APISourceItemV40("finalspark", "FinalSpark NeuroPlatform class", "read_only_first", "mock_client_v3_7", "metadata_then_read_only_trace", "remote wetware validation and live-shadow demo", ["stimulation", "media_control", "free_form_closed_loop"]),
        APISourceItemV40("threebrain", "3Brain HD-MEA class", "export_first", "mock_client_v3_7", "exported_data_import", "HD-MEA compatibility and high-channel-count roadmap", ["driver_write", "electrode_command", "pinout"]),
        APISourceItemV40("axion", "Axion Maestro class", "export_or_automation_read_first", "mock_client_v3_7", "exported_data_or_read_only_metadata", "multiwell enterprise screening path", ["dosing", "media_change", "stimulation"]),
        APISourceItemV40("mcs", "MCS MEA2100 class", "export_ttl_bridge_first", "mock_client_v3_7", "exported_data_and_ttl_metadata", "bridge to current Zenodo/MEA2100 lineage", ["live_stimulus_generator", "physical_wiring", "pinout"]),
    ]


def validation_gates_v40() -> List[ValidationGateV40]:
    return [
        ValidationGateV40(
            gate_id="G1_release_install",
            name="Install and smoke-test gate",
            purpose="Ensure beta user can install SDK or run Docker without hidden manual steps.",
            pass_criteria=["pip or Docker install succeeds", "health check passes", "sample manifest runs", "result bundle is created"],
            output_artifacts=["install_log.txt", "health.json", "sample_result_bundle.zip"],
        ),
        ValidationGateV40(
            gate_id="G2_dataset_replay",
            name="Dataset replay gate",
            purpose="Verify SDK can run at least one curated dataset end-to-end.",
            pass_criteria=["dataset registry resolves source", "features are generated or loaded", "readout runs", "shuffle baseline is reported"],
            output_artifacts=["run_manifest.json", "readout_summary.json", "shuffle_controls.csv", "audit_log.jsonl"],
        ),
        ValidationGateV40(
            gate_id="G3_lineage_statistics",
            name="Lineage-strict statistics gate",
            purpose="Prevent overclaiming from culture/DIV leakage before external beta.",
            pass_criteria=["lineage parser runs", "train/test lineage overlap is zero", "bootstrap CI is generated", "claim level remains honest"],
            output_artifacts=["lineage_split_summary.json", "bootstrap_ci.csv", "claim_ladder.md"],
        ),
        ValidationGateV40(
            gate_id="G4_api_read_only",
            name="External API read-only gate",
            purpose="Allow enterprise/API validation without live actuation.",
            pass_criteria=["metadata call succeeds", "write commands are denied", "BioGPUTrace export succeeds", "audit shows read-only mode"],
            output_artifacts=["api_metadata.json", "write_denial_report.json", "biogpu_trace.json", "api_audit_log.jsonl"],
        ),
        ValidationGateV40(
            gate_id="G5_powerpc_full_validation",
            name="Power-PC full validation gate",
            purpose="Run heavy sweeps before commercial/private beta claims.",
            pass_criteria=["full_shuffle_1000 completed", "extended_methods_5000 optional", "aggregate paper tables built", "no unreviewed GPU advantage claim"],
            output_artifacts=["global_results.csv", "aggregate_by_dataset.csv", "bootstrap_summary.csv", "validation_report.md"],
        ),
    ]


def deferred_work_items_v40() -> List[DeferredWorkItemV40]:
    """Items intentionally deferred earlier because they require a workstation, external API access, or lab approval.

    This is the bridge between the research backlog and the beta release plan.
    v4.0 must keep these visible so the project does not jump to external users before
    the proof/validation stack is complete.
    """
    return [
        DeferredWorkItemV40(
            item_id="D0_reproduce_v35_v36_smoke",
            phase="before_power_pc_full",
            title="Reproduce v3.5/v3.6 smoke checks on the target workstation",
            why_deferred="The beta machine must prove that the same package, sklearn readouts and lineage split run outside this chat environment.",
            execution_environment="power_pc_or_server",
            required_inputs=["v3.6/v4.0 archive", "Python environment", "local outputs directory"],
            deliverables=["install_log.txt", "v35_smoke_result.json", "v36_lineage_smoke_result.json"],
            exit_criteria=["all smoke tests pass", "no missing modules", "lineage overlap is zero"],
        ),
        DeferredWorkItemV40(
            item_id="D1_full_shuffle_1000",
            phase="power_pc_validation",
            title="Full shuffled-label validation",
            why_deferred="Hundreds of thousands of fit/evaluation operations are too heavy for this environment.",
            execution_environment="power_pc_or_server",
            required_inputs=["pulse_feature_matrix.npz", "pulse_feature_metadata.csv", "v3.6 lineage split logic"],
            deliverables=["full_shuffle_1000_results.csv", "shuffle_pvalue_summary.csv", "global_readout_summary.json"],
            exit_criteria=["1000 shuffles complete for approved splits/decoders", "empirical p-values reported", "failures logged not hidden"],
        ),
        DeferredWorkItemV40(
            item_id="D2_extended_methods_5000",
            phase="power_pc_validation",
            title="Extended methods and ablation sweep",
            why_deferred="Millions of compact model fits require workstation/server runtime.",
            execution_environment="power_pc_or_server",
            required_inputs=["v3.5 sklearn readouts", "v3.6 lineage split", "feature ablation registry"],
            deliverables=["extended_methods_5000.csv", "best_by_dataset_decoder_ablation.csv", "failure_modes.md"],
            exit_criteria=["all planned decoders compared", "all feature ablations summarized", "claim level updated"],
        ),
        DeferredWorkItemV40(
            item_id="D3_bootstrap_confidence_intervals",
            phase="power_pc_validation",
            title="Bootstrap confidence intervals and calibration tables",
            why_deferred="Enough resampling must be done to make paper/beta claims statistically defensible.",
            execution_environment="power_pc_or_server",
            required_inputs=["prediction tables", "split summaries", "shuffle summaries"],
            deliverables=["bootstrap_ci.csv", "calibration_curve.csv", "paper_table_statistics.csv"],
            exit_criteria=["95% CI reported", "calibration quality reported", "negative controls included"],
        ),
        DeferredWorkItemV40(
            item_id="D4_zenodo_raw_hdf5_ttl",
            phase="dataset_expansion",
            title="Zenodo raw HDF5 / TTL / stimulus reconstruction",
            why_deferred="Raw archive is large and needs local storage, HDF5 inspection and possibly long parsing.",
            execution_environment="power_pc_or_server",
            required_inputs=["Raw_data_MEA_data.zip", "HDF5 reader", "preprocessed spike windows for comparison"],
            deliverables=["hdf5_tree_report.md", "ttl_channel_candidates.csv", "raw_stimulus_windows.csv", "raw_vs_preprocessed_comparison.md"],
            exit_criteria=["raw structure mapped", "TTL/stimulus presence or absence stated", "raw-derived windows compared to v1.5/v3.6"],
        ),
        DeferredWorkItemV40(
            item_id="D5_dandi_nwb_task_aligned",
            phase="dataset_expansion",
            title="DANDI/NWB task-aligned dataset discovery and parser",
            why_deferred="Needs online dataset search/download and multiple file schema checks.",
            execution_environment="dev_pc_or_power_pc",
            required_inputs=["DANDI API/client", "NWB files with units + intervals/trials/stimulus"],
            deliverables=["dandi_dataset_registry.csv", "nwb_task_windows.csv", "task_aligned_readout_report.md"],
            exit_criteria=["at least 3 candidate Dandisets profiled", "one task-aligned benchmark runs end-to-end"],
        ),
        DeferredWorkItemV40(
            item_id="D6_allen_visual_coding_adapter",
            phase="dataset_expansion",
            title="Allen Brain Observatory / AllenSDK orientation benchmark",
            why_deferred="Allen downloads and SDK setup are better done on a workstation.",
            execution_environment="dev_pc_or_power_pc",
            required_inputs=["AllenSDK", "visual coding / Neuropixels sample", "stimulus presentation tables"],
            deliverables=["allen_orientation_dataset_profile.json", "orientation_readout_report.md", "allen_result_bundle.zip"],
            exit_criteria=["orientation task extracted", "readout and shuffle baseline run", "dataset added to registry"],
        ),
        DeferredWorkItemV40(
            item_id="D7_energy_latency_measurement",
            phase="power_pc_and_future_lab",
            title="Measured energy/latency accounting",
            why_deferred="Current v2.9 is a model; real energy requires measured host/electronics/lab boundaries.",
            execution_environment="power_pc_first_then_lab",
            required_inputs=["power meter or host telemetry", "fixed benchmark manifest", "task count and latency logs"],
            deliverables=["measured_energy_report.csv", "latency_breakdown.csv", "energy_claim_boundary.md"],
            exit_criteria=["measured not only estimated", "system boundary stated", "no GPU advantage claim without matched baseline"],
        ),
        DeferredWorkItemV40(
            item_id="D8_external_api_credentials",
            phase="api_validation",
            title="External API read-only credential tests",
            why_deferred="Requires partner/platform access tokens and terms of use.",
            execution_environment="dev_pc_or_partner_environment",
            required_inputs=["FinalSpark or vendor API credentials", "read-only API config", "safety boundary"],
            deliverables=["api_metadata_result.json", "read_only_trace_sample.json", "write_denial_report.json"],
            exit_criteria=["metadata read works", "unsafe write is blocked", "BioGPUTrace export works"],
        ),
        DeferredWorkItemV40(
            item_id="D9_hosted_server_beta",
            phase="beta_platform",
            title="Hosted BioGPU Server beta deployment",
            why_deferred="Only valuable after dataset expansion and validation gates exist.",
            execution_environment="cloud_server_or_onprem_server",
            required_inputs=["FastAPI beta server", "job queue", "auth/API keys", "dataset registry", "storage"],
            deliverables=["hosted_beta_url_or_local_deploy", "user_role_tests.json", "job_queue_demo_bundle.zip"],
            exit_criteria=["two users can run sandbox jobs", "quotas and audit logs work", "unsafe modes blocked"],
        ),
        DeferredWorkItemV40(
            item_id="D10_lab_live_validation",
            phase="future_lab",
            title="First approved live BioGPU experiment",
            why_deferred="Requires partner lab/vendor platform, operator approval, protocol ID and biosafety/ethics boundaries.",
            execution_environment="approved_lab_or_vendor_platform",
            required_inputs=["approved protocol", "operator", "vendor/lab adapter", "run manifest", "audit plan"],
            deliverables=["live_shadow_or_closed_loop_bundle.zip", "operator_log.md", "live_validation_report.md"],
            exit_criteria=["live read-only/shadow validated first", "closed-loop only if approved", "all results auditable"],
        ),
    ]


def roadmap_v40() -> List[RoadmapMilestoneV40]:
    return [
        RoadmapMilestoneV40("v4.0", "Beta Release Architecture", "Define how SDK is delivered, governed, tested and monetized.", ["release channels", "hosted/on-prem/GitHub model", "roles", "license gates", "dataset/API expansion plan"], ["architecture manifest generated", "docs complete", "tests pass"]),
        RoadmapMilestoneV40("v4.1", "Dataset Expansion Pack", "Expand beyond one preprocessed Zenodo dataset.", ["Zenodo raw HDF5 adapter plan", "DANDI discovery adapter", "AllenSDK adapter", "dataset registry", "download manifests"], ["at least 3 dataset families registered", "sample import tests pass"]),
        RoadmapMilestoneV40("v4.2", "Power-PC Validation Suite", "Run serious statistics and large shuffles on workstation/server.", ["full_shuffle_1000", "extended_methods_5000", "bootstrap CI", "lineage-strict reporting", "global paper tables"], ["large result bundle produced", "claim ladder updated"]),
        RoadmapMilestoneV40("v4.3", "Hosted BioGPU Server", "Make beta usable without local install.", ["FastAPI server", "job queue", "users/API keys", "dataset upload", "run manifest endpoint", "bundle download"], ["two demo users can run sandbox jobs", "admin can inspect audit logs"]),
        RoadmapMilestoneV40("v4.4", "Private Beta SDK", "Give controlled external access to technical partners.", ["private repo/wheel", "Docker image", "quickstart", "examples", "license file", "support docs"], ["partner onboarding checklist completed", "beta feedback form ready"]),
        RoadmapMilestoneV40("v4.5", "Enterprise Pilot Package", "Convert beta into paid pilots.", ["enterprise onboarding", "security checklist", "DPA/data handling notes", "SLA boundaries", "commercial offer template", "pilot success criteria"], ["pilot package complete", "pricing assumptions approved"]),
    ]


def build_beta_release_architecture_v40() -> Dict[str, Any]:
    return {
        "version": VERSION,
        "project_positioning": "BioGPU-Core Enterprise BioSDK for living neural compute: SDK + hosted server + on-prem deployment, with read-only/replay beta before approved live-lab modules.",
        "release_channels": [asdict(x) for x in release_channels_v40()],
        "dataset_expansion": [asdict(x) for x in dataset_expansion_v40()],
        "api_sources": [asdict(x) for x in api_sources_v40()],
        "validation_gates": [asdict(x) for x in validation_gates_v40()],
        "deferred_work_items": [asdict(x) for x in deferred_work_items_v40()],
        "roadmap": [asdict(x) for x in roadmap_v40()],
        "beta_rules": {
            "first_external_access": "mock/replay/read-only only",
            "full_access_policy": "separate paid lab-approved module after safety, operator and protocol gates",
            "commercial_default": "Enterprise Read-Only BioSDK is the first paid product",
            "no_go_claims": ["GPU replacement proven", "live BioGPU proven", "unrestricted wetware control"],
        },
        "recommended_next_actions": [
            "Before external beta: reproduce v3.5/v3.6 smoke checks on the target workstation",
            "Run D1-D4 power-PC validation backlog: full_shuffle_1000, extended_methods_5000, bootstrap CI, raw HDF5/TTL inspection",
            "Implement v4.1 dataset registry and adapters for Zenodo raw, DANDI/NWB and AllenSDK",
            "Run v4.2 power-PC validation before public claims or investor material",
            "Build v4.3 hosted server only after basic dataset expansion and safety gates work",
            "Offer v4.4 private beta to technical partners under read-only terms",
            "Keep v4.5 enterprise pilot separate from future lab-approved live control",
        ],
    }


def _write_csv(path: Path, rows: List[Dict[str, Any]], fieldnames: Optional[List[str]] = None) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    if fieldnames is None:
        fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: (json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v) for k, v in row.items()})


def render_markdown_report_v40(architecture: Optional[Dict[str, Any]] = None) -> str:
    arch = architecture or build_beta_release_architecture_v40()
    lines = []
    lines.append("# BioGPU-Core v4.0 — Beta Release Architecture + Dataset/API Expansion Plan")
    lines.append("")
    lines.append("## Positioning")
    lines.append(arch["project_positioning"])
    lines.append("")
    lines.append("## Delivery channels")
    for ch in arch["release_channels"]:
        lines.append(f"### {ch['name']}")
        lines.append(f"- Audience: {ch['audience']}")
        lines.append(f"- Delivery: {ch['delivery']}")
        lines.append(f"- Use: {ch['primary_use']}")
        lines.append(f"- Monetization: {ch['monetization']}")
        lines.append(f"- Allowed modes: {', '.join(ch['allowed_modes'])}")
        lines.append(f"- Blocked modes: {', '.join(ch['blocked_modes'])}")
        lines.append("")
    lines.append("## Dataset/API expansion")
    for ds in arch["dataset_expansion"]:
        lines.append(f"### P{ds['priority']} — {ds['name']}")
        lines.append(f"- ID: `{ds['dataset_id']}`")
        lines.append(f"- Type: {ds['source_type']}")
        lines.append(f"- Adapter status: {ds['adapter_status']}")
        lines.append(f"- Why: {ds['reason']}")
        lines.append(f"- Required work: {', '.join(ds['required_work'])}")
        lines.append(f"- Power-PC required: {ds['power_pc_required']}")
        lines.append("")
    lines.append("## Validation gates before beta")
    for gate in arch["validation_gates"]:
        lines.append(f"### {gate['gate_id']} — {gate['name']}")
        lines.append(f"- Purpose: {gate['purpose']}")
        lines.append(f"- Pass criteria: {', '.join(gate['pass_criteria'])}")
        lines.append(f"- Artifacts: {', '.join(gate['output_artifacts'])}")
        lines.append("")
    lines.append("## Deferred backlog from earlier phases")
    lines.append("These items were deliberately postponed until a power-PC/server, external API credentials, or a lab environment is available. They must remain in the project plan before external beta claims.")
    lines.append("")
    for item in arch["deferred_work_items"]:
        lines.append(f"### {item['item_id']} — {item['title']}")
        lines.append(f"- Phase: {item['phase']}")
        lines.append(f"- Why deferred: {item['why_deferred']}")
        lines.append(f"- Environment: {item['execution_environment']}")
        lines.append(f"- Required inputs: {', '.join(item['required_inputs'])}")
        lines.append(f"- Deliverables: {', '.join(item['deliverables'])}")
        lines.append(f"- Exit criteria: {', '.join(item['exit_criteria'])}")
        lines.append("")
    lines.append("## Roadmap to external test access")
    for step in arch["roadmap"]:
        lines.append(f"### {step['version']} — {step['title']}")
        lines.append(f"- Purpose: {step['purpose']}")
        lines.append(f"- Deliverables: {', '.join(step['deliverables'])}")
        lines.append(f"- Exit criteria: {', '.join(step['exit_criteria'])}")
        lines.append("")
    lines.append("## Beta rules")
    for k, v in arch["beta_rules"].items():
        lines.append(f"- **{k}**: {json.dumps(v, ensure_ascii=False) if isinstance(v, list) else v}")
    lines.append("")
    return "\n".join(lines)


def write_beta_release_outputs_v40(output_dir: str | Path) -> Dict[str, str]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    arch = build_beta_release_architecture_v40()
    paths: Dict[str, str] = {}
    p = out / "v40_beta_release_architecture.json"
    p.write_text(json.dumps(arch, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["architecture_json"] = str(p)

    p = out / "BIOGPU_V40_BETA_RELEASE_ARCHITECTURE.md"
    p.write_text(render_markdown_report_v40(arch), encoding="utf-8")
    paths["report_md"] = str(p)

    tables = {
        "v40_release_channels.csv": arch["release_channels"],
        "v40_dataset_expansion.csv": arch["dataset_expansion"],
        "v40_api_sources.csv": arch["api_sources"],
        "v40_validation_gates.csv": arch["validation_gates"],
        "v40_deferred_work_items.csv": arch["deferred_work_items"],
        "v40_roadmap.csv": arch["roadmap"],
    }
    for name, rows in tables.items():
        p = out / name
        _write_csv(p, rows)
        paths[name] = str(p)

    summary = {
        "version": VERSION,
        "release_channel_count": len(arch["release_channels"]),
        "dataset_expansion_count": len(arch["dataset_expansion"]),
        "api_source_count": len(arch["api_sources"]),
        "validation_gate_count": len(arch["validation_gates"]),
        "deferred_work_count": len(arch["deferred_work_items"]),
        "roadmap_count": len(arch["roadmap"]),
        "first_paid_product": "Enterprise Read-Only BioSDK",
        "live_control_default": "blocked until lab-approved add-on",
    }
    p = out / "v40_summary.json"
    p.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["summary_json"] = str(p)
    return paths


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate BioGPU-Core v4.0 beta release architecture outputs.")
    parser.add_argument("--output", default="outputs/realdata_zenodo_14363732_v40_beta_release")
    args = parser.parse_args()
    written = write_beta_release_outputs_v40(args.output)
    print(json.dumps({"status": "ok", "version": VERSION, "written": written}, indent=2, ensure_ascii=False))
