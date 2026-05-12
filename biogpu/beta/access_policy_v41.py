from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
import csv
import json

VERSION = "4.1.0"

SAFE_SOFTWARE_CAPABILITIES = [
    "install_sdk",
    "run_docker",
    "run_cli",
    "use_python_api",
    "run_replay_benchmarks",
    "upload_or_import_own_data",
    "use_curated_datasets",
    "run_lineage_strict_splits",
    "run_shuffle_controls_with_quota",
    "run_bootstrap_with_quota",
    "use_all_safe_decoders",
    "use_feature_ablations",
    "export_result_bundle",
    "inspect_audit_logs",
    "use_biollm_tool_interface",
    "use_mock_external_api_clients",
    "use_read_only_external_api_clients",
    "run_powerpc_scripts_when_local_resources_allow",
]

LIVE_CONTROL_CAPABILITIES = [
    "live_stimulation",
    "electrode_actuation",
    "closed_loop_write_control",
    "media_or_environment_control",
    "vendor_driver_write_mode",
]

UNSAFE_FIELDS = [
    "voltage",
    "amplitude",
    "current",
    "pulse_width",
    "frequency",
    "charge_density",
    "pinout",
    "wiring",
    "media_recipe",
    "culturing_recipe",
    "incubation_formula",
    "unreviewed_stimulation",
    "free_form_electrode_command",
]

@dataclass(frozen=True)
class AccessTierV41:
    tier_id: str
    name: str
    intended_users: str
    commercial_stage: str
    delivery: List[str]
    allowed_capabilities: List[str]
    external_api_modes: List[str]
    compute_policy: str
    data_policy: str
    support_policy: str
    blocked_capabilities: List[str]
    approval_required_for: List[str]
    upgrade_path: str

@dataclass(frozen=True)
class AccessDecisionV41:
    tier_id: str
    requested_capability: str
    allowed: bool
    reason: str
    required_gate: Optional[str] = None

@dataclass(frozen=True)
class RemainingWorkItemV41:
    item_id: str
    category: str
    title: str
    status: str
    can_finish_in_this_environment: bool
    next_environment: str
    why_it_matters: str
    deliverables: List[str]


def access_tiers_v41() -> List[AccessTierV41]:
    """Commercial access tiers after correcting the v4.0 beta access strategy.

    The principle is maximum *software* access for serious early testers, while unsafe
    live biological actuation remains approval-gated. This is less restrictive than a
    tiny demo, but still safe enough for labs and enterprise review.
    """
    common_safe = list(SAFE_SOFTWARE_CAPABILITIES)
    common_blocks = list(LIVE_CONTROL_CAPABILITIES) + list(UNSAFE_FIELDS)
    return [
        AccessTierV41(
            tier_id="developer_evaluation",
            name="Developer Evaluation BioSDK",
            intended_users="individual developers, technical reviewers, early evaluators",
            commercial_stage="free_or_low_cost_trial",
            delivery=["public/private package", "sample Docker", "sample datasets", "quickstart docs"],
            allowed_capabilities=[
                "install_sdk", "run_docker", "run_cli", "use_python_api",
                "run_replay_benchmarks", "use_curated_datasets", "use_all_safe_decoders",
                "export_result_bundle", "inspect_audit_logs", "use_biollm_tool_interface",
                "use_mock_external_api_clients",
            ],
            external_api_modes=["mock", "metadata_template_only"],
            compute_policy="local only; small sample jobs; shuffle/bootstrap quotas are intentionally low",
            data_policy="sample data and user-provided local data; no hosted private-data retention by default",
            support_policy="community/docs only",
            blocked_capabilities=common_blocks,
            approval_required_for=["real external API credentials", "hosted private workspace", "live-shadow", "any live biological actuation"],
            upgrade_path="Research Pilot or Enterprise Read-Only",
        ),
        AccessTierV41(
            tier_id="research_pilot_max_safe",
            name="Research Pilot — Maximum Safe Software Access",
            intended_users="selected labs, serious technical partners, early scientific validators",
            commercial_stage="pilot_fee_or_strategic_free_access",
            delivery=["private repo", "full SDK", "Docker/on-prem", "power-PC scripts", "dataset/API adapters", "result-bundle tooling"],
            allowed_capabilities=common_safe,
            external_api_modes=["mock", "metadata", "read_only", "exported_data_import", "live_shadow_read_only_if_partner_approved"],
            compute_policy="local/on-prem full software access; heavy jobs allowed on partner hardware; hosted quotas optional",
            data_policy="partner data stays local unless explicitly uploaded; result bundles are exportable",
            support_policy="pilot support, onboarding call, issue triage, compatibility feedback",
            blocked_capabilities=common_blocks,
            approval_required_for=["closed_loop_write_control", "electrode_actuation", "vendor_driver_write_mode", "wetware environment control"],
            upgrade_path="Enterprise Read-Only / Live Shadow or Lab-Control Add-on",
        ),
        AccessTierV41(
            tier_id="enterprise_read_only",
            name="Enterprise Read-Only BioSDK",
            intended_users="companies, MEA labs, pharma/neurotech groups needing production-grade analysis",
            commercial_stage="paid_core_product",
            delivery=["private package", "licensed Docker", "hosted workspace optional", "admin docs", "audit bundle"],
            allowed_capabilities=common_safe + ["team_workspaces", "private_dataset_registry", "enterprise_audit_exports"],
            external_api_modes=["metadata", "read_only", "exported_data_import"],
            compute_policy="paid quotas or on-prem unlimited depending on contract; no live write control",
            data_policy="customer-controlled data handling; optional hosted retention rules",
            support_policy="business support, SLA boundaries, security questionnaire support",
            blocked_capabilities=common_blocks,
            approval_required_for=["live_shadow", "approved closed-loop", "vendor write adapters"],
            upgrade_path="Enterprise Live Shadow",
        ),
        AccessTierV41(
            tier_id="enterprise_live_shadow",
            name="Enterprise Live Shadow BioSDK",
            intended_users="labs and enterprise partners with approved read-only live data streams",
            commercial_stage="premium_paid_product",
            delivery=["on-prem/hosted hybrid", "read-only live connector", "operator dashboard", "live audit logs"],
            allowed_capabilities=common_safe + ["read_only_live_stream", "online_feature_extraction", "shadow_predictions", "operator_dashboard"],
            external_api_modes=["metadata", "read_only", "live_shadow_read_only"],
            compute_policy="premium quotas; live stream read-only processing; no write-back to the biological system",
            data_policy="live traces remain in partner environment unless explicitly exported",
            support_policy="premium support, integration support, validation package",
            blocked_capabilities=common_blocks,
            approval_required_for=["any command that changes stimulation/environment/electrode state"],
            upgrade_path="Lab-Approved Closed Loop Add-on",
        ),
        AccessTierV41(
            tier_id="lab_approved_closed_loop_addon",
            name="Lab-Approved Closed Loop Add-on",
            intended_users="approved laboratories/vendor platforms with operator oversight and written protocol",
            commercial_stage="highest_value_addon",
            delivery=["separate module", "allowlisted command schema", "operator checklist", "protocol-bound adapter", "full audit"],
            allowed_capabilities=common_safe + [
                "approved_protocol_closed_loop", "allowlisted_write_commands", "operator_confirmation", "protocol_id_required"
            ],
            external_api_modes=["metadata", "read_only", "live_shadow", "approved_closed_loop"],
            compute_policy="contract-specific; every live-control run must be manifest-bound and auditable",
            data_policy="lab/vendor controlled; exports only through approved bundle policy",
            support_policy="direct technical support, change-control, safety review, milestone fees",
            blocked_capabilities=["free_form_electrode_command", "unreviewed_stimulation", "home_wetlab_use", "unsafe_fields_without_allowlist"],
            approval_required_for=["every new protocol", "every new vendor write backend", "every change to allowlisted command schema"],
            upgrade_path="custom enterprise/lab contract",
        ),
    ]


def allowed_capabilities_by_tier_v41() -> Dict[str, List[str]]:
    return {tier.tier_id: tier.allowed_capabilities for tier in access_tiers_v41()}


def decide_access_v41(tier_id: str, requested_capability: str) -> AccessDecisionV41:
    tiers = {t.tier_id: t for t in access_tiers_v41()}
    if tier_id not in tiers:
        return AccessDecisionV41(tier_id, requested_capability, False, "unknown tier", "valid_license_tier")
    tier = tiers[tier_id]
    cap = requested_capability.strip()
    if cap in tier.allowed_capabilities:
        return AccessDecisionV41(tier_id, cap, True, "allowed by tier")
    if cap in tier.blocked_capabilities or cap in LIVE_CONTROL_CAPABILITIES or cap in UNSAFE_FIELDS:
        gate = "lab_vendor_protocol_approval" if tier_id == "lab_approved_closed_loop_addon" else "upgrade_and_safety_approval"
        return AccessDecisionV41(tier_id, cap, False, "blocked because it can affect a live biological or lab system", gate)
    return AccessDecisionV41(tier_id, cap, False, "not included in this tier or not recognized", "commercial_or_admin_approval")


def remaining_work_items_v41() -> List[RemainingWorkItemV41]:
    """Audit of what remains open, separated by what can still be done here vs elsewhere."""
    return [
        RemainingWorkItemV41(
            "E1_access_policy_patch", "this_environment", "Maximum safe access policy for beta testers", "closed_in_v4_1", True, "this environment",
            "Corrects the commercial strategy: early testers get real software access, not a crippled demo.",
            ["access matrix", "tier policy", "tests", "docs"],
        ),
        RemainingWorkItemV41(
            "E2_dataset_registry_skeleton", "this_environment", "Dataset registry skeleton for Zenodo/DANDI/Allen/vendor exports", "open", True, "this environment",
            "Needed before external beta so users can select/import datasets through one manifest format.",
            ["dataset_registry.py", "dataset_manifest_template.json", "download/import plan", "tests"],
        ),
        RemainingWorkItemV41(
            "E3_hosted_server_scaffold", "this_environment", "Hosted BioGPU Server scaffold", "open", True, "this environment",
            "We can build routes, job model, roles, quotas, and bundle endpoints even before deploying to cloud.",
            ["FastAPI routes", "job schema", "user role policy", "mock queue", "tests"],
        ),
        RemainingWorkItemV41(
            "E4_private_beta_docs", "this_environment", "Private beta onboarding docs and quickstart", "open", True, "this environment",
            "A tester needs a 15-minute path from zip/Docker to first result bundle.",
            ["QUICKSTART_BETA.md", "PARTNER_ONBOARDING.md", "sample manifests", "support checklist"],
        ),
        RemainingWorkItemV41(
            "E5_security_data_policy", "this_environment", "Security, privacy and data-retention policy drafts", "open", True, "this environment",
            "Enterprise testers will ask how uploaded neural data, logs and result bundles are handled.",
            ["DATA_HANDLING.md", "SECURITY_MODEL.md", "DPA notes", "retention defaults"],
        ),
        RemainingWorkItemV41(
            "P1_powerpc_smoke_repro", "power_pc", "Reproduce v3.5/v3.6/v4.x smoke checks on target workstation", "open", False, "power PC/server",
            "Proves the same archive works outside this environment.",
            ["install logs", "smoke result bundles", "environment report"],
        ),
        RemainingWorkItemV41(
            "P2_full_shuffle_1000", "power_pc", "Full shuffled baseline validation", "open", False, "power PC/server",
            "Needed for defensible statistical claims before external beta or investor material.",
            ["full_shuffle_1000_results.csv", "p-value summary", "failure log"],
        ),
        RemainingWorkItemV41(
            "P3_extended_methods_5000", "power_pc", "Extended decoder/ablation sweep", "open", False, "power PC/server",
            "Checks that the result is not a one-decoder/one-split accident.",
            ["extended_methods_5000.csv", "best-by-decoder tables", "claim update"],
        ),
        RemainingWorkItemV41(
            "P4_raw_hdf5_ttl", "power_pc", "Zenodo raw HDF5 / TTL reconstruction", "open", False, "power PC/server",
            "Needed to verify whether pulse-level windows can be reconstructed from raw data, not only preprocessed spikes.",
            ["hdf5 tree report", "ttl candidates", "raw windows", "raw-vs-preprocessed comparison"],
        ),
        RemainingWorkItemV41(
            "P5_measured_energy_latency", "power_pc_then_lab", "Measured energy and latency", "open", False, "power PC first, lab later",
            "v2.9 is a model; claims need measured host/electronics/task boundaries.",
            ["power telemetry", "latency breakdown", "energy claim boundary"],
        ),
        RemainingWorkItemV41(
            "A1_dandi_allen_real_downloads", "external_data", "DANDI/Allen real downloads and schema validation", "open", False, "dev PC/power PC with internet/storage",
            "Expands proof beyond one MEA dataset.",
            ["candidate dataset registry", "NWB parser results", "Allen orientation benchmark"],
        ),
        RemainingWorkItemV41(
            "A2_vendor_api_credentials", "external_api", "FinalSpark/vendor read-only credentials", "open", False, "partner/API environment",
            "Turns mock v3.7 clients into real read-only API validation.",
            ["metadata read", "read-only trace", "write denial report", "BioGPUTrace export"],
        ),
        RemainingWorkItemV41(
            "L1_live_lab_validation", "lab", "First approved live BioGPU experiment", "open", False, "approved lab/vendor platform",
            "Only this can prove live BioGPU behavior; everything before is replay/API/software validation.",
            ["approved protocol", "operator log", "live result bundle", "validation report"],
        ),
    ]


def build_v41_access_audit() -> Dict[str, Any]:
    tiers = [asdict(t) for t in access_tiers_v41()]
    remaining = [asdict(x) for x in remaining_work_items_v41()]
    return {
        "version": VERSION,
        "principle": "Give early testers maximum safe software access; gate only capabilities that can affect live biological/lab systems.",
        "access_tiers": tiers,
        "unsafe_fields": UNSAFE_FIELDS,
        "live_control_capabilities": LIVE_CONTROL_CAPABILITIES,
        "remaining_work_items": remaining,
        "closed_in_this_environment_count": len([x for x in remaining if x["status"] == "closed_in_v4_1"]),
        "still_possible_in_this_environment": [x for x in remaining if x["can_finish_in_this_environment"] and x["status"] != "closed_in_v4_1"],
        "must_move_elsewhere": [x for x in remaining if not x["can_finish_in_this_environment"]],
        "recommended_next_versions": [
            {"version": "v4.2", "title": "Dataset Registry + Import Skeleton", "environment": "this environment"},
            {"version": "v4.3", "title": "Hosted Server Scaffold + Job Model", "environment": "this environment"},
            {"version": "v4.4", "title": "Private Beta Docs + Sample Manifests", "environment": "this environment"},
            {"version": "v4.5", "title": "Security/Data Handling + Enterprise Pilot Pack", "environment": "this environment"},
            {"version": "v4.6", "title": "Power-PC Validation Execution", "environment": "power PC/server"},
        ],
    }


def _write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v for k, v in row.items()})


def render_markdown_v41(audit: Optional[Dict[str, Any]] = None) -> str:
    data = audit or build_v41_access_audit()
    lines: List[str] = []
    lines.append("# BioGPU-Core v4.1 — Maximum Safe Access + Remaining Work Audit")
    lines.append("")
    lines.append("## Core correction")
    lines.append(data["principle"])
    lines.append("")
    lines.append("This corrects the beta strategy: early serious testers should not receive a tiny demo. They should receive a real SDK with replay, custom data, read-only/API validation, BioLLM tool mode, Docker/on-prem execution and result bundles. The only hard boundary is uncontrolled live biological/lab actuation.")
    lines.append("")
    lines.append("## Access tiers")
    for tier in data["access_tiers"]:
        lines.append(f"### {tier['name']}")
        lines.append(f"- ID: `{tier['tier_id']}`")
        lines.append(f"- Intended users: {tier['intended_users']}")
        lines.append(f"- Commercial stage: {tier['commercial_stage']}")
        lines.append(f"- Delivery: {', '.join(tier['delivery'])}")
        lines.append(f"- External API modes: {', '.join(tier['external_api_modes'])}")
        lines.append(f"- Compute policy: {tier['compute_policy']}")
        lines.append(f"- Data policy: {tier['data_policy']}")
        lines.append(f"- Blocked capabilities: {', '.join(tier['blocked_capabilities'][:8])}{'...' if len(tier['blocked_capabilities']) > 8 else ''}")
        lines.append(f"- Upgrade path: {tier['upgrade_path']}")
        lines.append("")
    lines.append("## What remains open in this environment")
    possible = data["still_possible_in_this_environment"]
    if possible:
        for item in possible:
            lines.append(f"### {item['item_id']} — {item['title']}")
            lines.append(f"- Why it matters: {item['why_it_matters']}")
            lines.append(f"- Deliverables: {', '.join(item['deliverables'])}")
            lines.append("")
    else:
        lines.append("No remaining local-only items.")
        lines.append("")
    lines.append("## What must move to another environment")
    for item in data["must_move_elsewhere"]:
        lines.append(f"### {item['item_id']} — {item['title']}")
        lines.append(f"- Category: {item['category']}")
        lines.append(f"- Next environment: {item['next_environment']}")
        lines.append(f"- Why it matters: {item['why_it_matters']}")
        lines.append(f"- Deliverables: {', '.join(item['deliverables'])}")
        lines.append("")
    lines.append("## Recommended next versions")
    for step in data["recommended_next_versions"]:
        lines.append(f"- **{step['version']}** — {step['title']} ({step['environment']})")
    lines.append("")
    return "\n".join(lines)


def write_v41_outputs(output_dir: str | Path) -> Dict[str, str]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    audit = build_v41_access_audit()
    paths: Dict[str, str] = {}
    p = out / "v41_access_audit.json"
    p.write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["audit_json"] = str(p)
    p = out / "BIOGPU_V41_MAXIMUM_SAFE_ACCESS_AND_REMAINING_WORK.md"
    p.write_text(render_markdown_v41(audit), encoding="utf-8")
    paths["report_md"] = str(p)
    _write_csv(out / "v41_access_tiers.csv", audit["access_tiers"])
    paths["access_tiers_csv"] = str(out / "v41_access_tiers.csv")
    _write_csv(out / "v41_remaining_work_items.csv", audit["remaining_work_items"])
    paths["remaining_work_csv"] = str(out / "v41_remaining_work_items.csv")
    summary = {
        "version": VERSION,
        "access_tier_count": len(audit["access_tiers"]),
        "remaining_work_count": len(audit["remaining_work_items"]),
        "still_possible_in_this_environment_count": len(audit["still_possible_in_this_environment"]),
        "must_move_elsewhere_count": len(audit["must_move_elsewhere"]),
        "principle": audit["principle"],
        "live_control_default": "blocked unless lab-approved closed-loop add-on",
    }
    p = out / "v41_summary.json"
    p.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["summary_json"] = str(p)
    return paths


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate BioGPU-Core v4.1 maximum safe access policy and remaining work audit outputs.")
    parser.add_argument("--output", default="outputs/realdata_zenodo_14363732_v41_access_audit")
    args = parser.parse_args()
    written = write_v41_outputs(args.output)
    print(json.dumps({"status": "ok", "version": VERSION, "written": written}, indent=2, ensure_ascii=False))
