from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List
import csv
import json

VERSION = "4.5.0"

@dataclass(frozen=True)
class RoadmapItem:
    id: str
    phase: str
    title: str
    status: str
    owner_environment: str
    deliverable: str
    gate: str

@dataclass(frozen=True)
class AccessTier:
    tier: str
    purpose: str
    allowed: List[str]
    blocked: List[str]
    commercial_note: str

@dataclass(frozen=True)
class DatasetSource:
    id: str
    priority: str
    source_type: str
    purpose: str
    required_before_beta: bool
    power_pc_required: bool

@dataclass(frozen=True)
class CleanupItem:
    category: str
    problem: str
    action: str
    risk_if_ignored: str


def roadmap_items() -> List[RoadmapItem]:
    return [
        RoadmapItem("R0", "completed_local", "Real-data replay baseline from Zenodo preprocessed MEA data", "done", "current_environment", "v1.2-v3.3 reports and result bundles", "repeatable smoke tests pass"),
        RoadmapItem("R1", "completed_local", "Runtime/SDK core: adapters, encoder, readout, closed-loop, energy model", "done", "current_environment", "v2.4-v3.1 SDK modules", "py_compile and targeted tests pass"),
        RoadmapItem("R2", "completed_local", "Real sklearn readouts and release hygiene", "done", "current_environment", "v3.5", "real LogisticRegression/LinearSVC available"),
        RoadmapItem("R3", "completed_local", "Lineage-strict split and bootstrap scaffold", "done", "current_environment", "v3.6", "base lineage is kept either train-only or test-only"),
        RoadmapItem("R4", "completed_local", "External API/BioSDK skeleton", "done", "current_environment", "v3.7", "read-only/mock clients available"),
        RoadmapItem("R5", "completed_local", "BioLLM tool interface", "done", "current_environment", "v3.8", "LLM tool returns structured result"),
        RoadmapItem("R6", "completed_local", "Enterprise packaging and licensing", "done", "current_environment", "v3.9", "commercial tiers documented"),
        RoadmapItem("R7", "completed_local", "Beta architecture and maximum safe access policy", "done", "current_environment", "v4.0-v4.1", "early testers get broad software access, live actuation gated"),
        RoadmapItem("R8", "completed_local", "Dataset registry/import skeleton and hosted server/job model", "done", "current_environment", "v4.2-v4.3", "dataset registry and job model tests pass"),
        RoadmapItem("R9", "completed_local", "Private beta docs and sample manifests", "included_in_v45", "current_environment", "beta/ quickstart/checklists/sample manifests", "external tester can run smoke workflow"),
        RoadmapItem("R10", "completed_local", "Single master plan and repository cleanup audit", "done", "current_environment", "MASTER_PROJECT_PLAN_V45.md and cleanup audit", "single source of truth exists"),
        RoadmapItem("P0", "power_pc", "Re-run v3.5/v3.6 smoke checks on workstation", "pending", "power_pc", "POWERPC_SMOKE_RESULT_BUNDLE", "all smoke tests pass on target machine"),
        RoadmapItem("P1", "power_pc", "full_shuffle_1000 lineage-strict validation", "pending", "power_pc", "paper_table_full_shuffle_1000.csv", "stable signal above shuffled controls or honest negative result"),
        RoadmapItem("P2", "power_pc", "extended_methods_5000 supplementary sweep", "pending", "power_pc_or_server", "extended_methods_result_bundle", "supplementary methods table complete"),
        RoadmapItem("P3", "power_pc", "Bootstrap confidence intervals and calibration curves", "pending", "power_pc", "bootstrap_ci_tables and calibration plots", "95% CI and calibration reported for each claim"),
        RoadmapItem("D1", "dataset_expansion", "Zenodo raw HDF5 / TTL reconstruction", "pending", "power_pc", "raw_hdf5_pulse_windows.csv", "raw-derived windows match or supersede preprocessed windows"),
        RoadmapItem("D2", "dataset_expansion", "DANDI/NWB discovery and task-aligned parser", "pending", "power_pc_or_server", "NWB task-aligned benchmark bundle", "units+intervals/trials/stimulus parsed"),
        RoadmapItem("D3", "dataset_expansion", "AllenSDK visual coding/orientation benchmark", "pending", "power_pc_or_server", "Allen orientation benchmark report", "stimulus presentations and spikes parsed"),
        RoadmapItem("A1", "external_api", "FinalSpark read-only credential validation", "pending", "partner_api", "FinalSpark read-only trace bundle", "metadata and read-only trace import works"),
        RoadmapItem("A2", "external_api", "3Brain/Axion/MCS exported-data validation", "pending", "partner_or_user_data", "vendor export BioGPUTrace bundles", "vendor data converted without unsafe commands"),
        RoadmapItem("S1", "hosted_beta", "Hosted BioGPU server with auth, quotas, job queue", "pending", "server", "hosted beta deployment", "safe jobs run and unsafe jobs rejected"),
        RoadmapItem("S2", "private_beta", "Private beta with selected labs/enterprises", "pending", "server_and_private_repo", "beta feedback reports", "3+ external testers complete acceptance checklist"),
        RoadmapItem("E1", "enterprise", "Enterprise pilot package and legal/security review", "pending", "commercial", "pilot MSA/SLA/security pack", "pilot partner accepts data handling and access boundaries"),
        RoadmapItem("L1", "lab_validation", "First approved live BioGPU experiment", "pending", "approved_lab", "live BioGPU result bundle", "approved protocol, audit log, readout result, latency/energy report"),
    ]


def access_tiers() -> List[AccessTier]:
    safe_allowed = [
        "local SDK install", "Docker/on-prem run", "sample datasets", "own data upload/import", "replay benchmarks",
        "lineage-strict split", "shuffle controls within quota", "bootstrap scaffold", "BioLLM tool interface",
        "read-only/mock external API", "result bundle export", "audit logs", "power-PC runner scripts"
    ]
    blocked = [
        "unapproved live stimulation", "electrode actuation", "vendor write commands", "unsafe stimulation fields",
        "pinout/wiring instructions", "wet-lab environment/media control", "uncontrolled closed-loop"
    ]
    return [
        AccessTier("Developer Evaluation", "Fast local evaluation by engineers", safe_allowed[:8], blocked, "free or low-cost, limited quotas and non-commercial use"),
        AccessTier("Research/Lab Evaluation", "Maximum safe technical evaluation by selected labs", safe_allowed, blocked, "pilot/free for strategic labs or paid research pilot"),
        AccessTier("Enterprise Read-Only BioSDK", "Commercial read-only/replay/on-prem deployment", safe_allowed, blocked, "first primary paid product"),
        AccessTier("Enterprise Live Shadow", "Live read-only stream with predictions but no actuation", safe_allowed + ["live read-only stream", "shadow predictions"], blocked, "premium paid add-on"),
        AccessTier("Lab-Approved Closed Loop", "Approved live actuation only under vendor/lab protocol", safe_allowed + ["allowlisted actuation schema", "operator approval workflow"], ["free-form unsafe commands", "unapproved stimulation", "wet-lab recipe automation"], "highest-value future module; separate contract and approval"),
    ]


def dataset_sources() -> List[DatasetSource]:
    return [
        DatasetSource("zenodo_14363732_preprocessed", "P0", "existing_realdata", "current smoke/replay baseline", True, False),
        DatasetSource("zenodo_14363732_raw_hdf5", "P0", "raw_hdf5", "TTL/stimulus reconstruction and raw-vs-preprocessed validation", True, True),
        DatasetSource("dandi_nwb_discovery", "P1", "NWB/API", "task-aligned neural benchmarks", True, True),
        DatasetSource("allen_visual_coding_orientation", "P1", "AllenSDK", "orientation/visual coding benchmark", True, True),
        DatasetSource("finalspark_readonly_export", "P2", "external_api_or_export", "remote wetware read-only validation", False, False),
        DatasetSource("vendor_exports_mcs_3brain_axion", "P2", "vendor_export", "enterprise/lab data compatibility", False, False),
        DatasetSource("user_uploaded_neural_data", "P0", "private_upload", "beta tester data import", True, False),
    ]


def cleanup_items() -> List[CleanupItem]:
    return [
        CleanupItem("documentation", "Roadmap and strategy are spread across many versioned docs", "Use docs/MASTER_PROJECT_PLAN_V45.md as single source of truth; treat older docs as historical evidence", "testers and partners cannot understand current direction"),
        CleanupItem("repository", "Many PROJECT_INVENTORY_V*.md and RUN_RESULTS_REALDATA_V*.md files clutter root", "Before beta, move historical inventories/results into archive/history or generated_reports", "root looks unprofessional and confusing"),
        CleanupItem("outputs", "Multiple outputs/realdata_* folders accumulate generated artifacts", "Keep latest beta outputs; archive old generated outputs outside source tree", "zip grows and hides important files"),
        CleanupItem("docs", "Wetware/blueprint docs mix current safe SDK with speculative/live lab notes", "Add docs/DOCUMENT_INDEX_V45.md and mark documents as current/reference/legacy/restricted", "safety and commercial story becomes unclear"),
        CleanupItem("packaging", "Some previous generated zips were missing from local file list or based on older archive", "Use release manifest and zip integrity check for every release", "users may receive inconsistent packages"),
        CleanupItem("tests", "Targeted tests exist, but no single beta acceptance test suite", "Add beta acceptance checklist and smoke workflow", "external testers may test different things"),
        CleanupItem("data", "Only a small preprocessed real dataset has been run locally", "Power-PC validation must add raw HDF5, DANDI/NWB, AllenSDK, and user uploads", "claims remain too narrow"),
    ]


def to_rows(items):
    return [asdict(i) for i in items]


def write_csv(path: Path, rows: List[Dict[str, object]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def build_master_markdown() -> str:
    lines = []
    lines.append("# BioGPU-Core v4.5 Master Project Plan\n")
    lines.append("## Current truth\n")
    lines.append("BioGPU-Core is now best described as an enterprise-oriented BioSDK for living neural compute: replay/read-only first, live actuation only after lab/vendor approval. The original GPU-for-LLM replacement idea matured into a safer and more realistic BioSDK/runtime for biological neural signals, wetware APIs, benchmarks, result bundles, and future lab validation.\n")
    lines.append("## Product model\n")
    lines.append("- Private GitHub/private package for technical partners.\n- Hosted BioGPU Server for beta testing and commercial SaaS-style access.\n- Enterprise on-prem Docker for serious customers.\n- Lab-approved closed-loop add-on only after protocol approval.\n")
    lines.append("## Access policy\n")
    lines.append("Early serious testers should receive maximum software-level access: SDK, Docker, own data import, replay, benchmark sweeps, BioLLM tool interface, read-only/mock API, result bundles, and audit logs. Only unsafe live biological actuation remains gated.\n")
    lines.append("## Roadmap\n")
    for item in roadmap_items():
        lines.append(f"- **{item.id} [{item.phase}] {item.title}** — status: `{item.status}`; environment: `{item.owner_environment}`; deliverable: `{item.deliverable}`; gate: `{item.gate}`.")
    lines.append("\n## Datasets/API still required before confident beta claims\n")
    for ds in dataset_sources():
        lines.append(f"- **{ds.id}** ({ds.priority}, {ds.source_type}): {ds.purpose}. Required before beta: `{ds.required_before_beta}`. Power-PC required: `{ds.power_pc_required}`.")
    lines.append("\n## Repository cleanup truth\n")
    lines.append("The project has accumulated historical artifacts. They are useful for audit trail, but they should not be presented as the current entry point. Current entry point is this document plus README_BIOGPU_CORE_V45.md, docs/DOCUMENT_INDEX_V45.md, and beta/PRIVATE_BETA_QUICKSTART.md.\n")
    lines.append("## Claims allowed now\n")
    lines.append("- Allowed: software/replay BioSDK, real-data preprocessed MEA pipeline, lineage-strict split scaffold, read-only/mock API skeleton, hosted server scaffold, enterprise beta packaging.\n")
    lines.append("- Not allowed yet: proven live BioGPU, GPU replacement, LLM replacement, measured live energy advantage, uncontrolled live stimulation.\n")
    return "\n".join(lines) + "\n"


def build_document_index() -> str:
    return """# BioGPU-Core v4.5 Document Index

## Start here
1. `README_BIOGPU_CORE_V45.md` — short orientation.
2. `docs/MASTER_PROJECT_PLAN_V45.md` — single source of truth.
3. `docs/REPOSITORY_CLEANUP_AUDIT_V45.md` — what is legacy/noisy and how to clean it.
4. `beta/PRIVATE_BETA_QUICKSTART.md` — tester entry point.
5. `docs/SECURITY_DATA_HANDLING_V45.md` — enterprise data/safety policy.
6. `docs/POWERPC_VALIDATION_RUNBOOK_V45.md` — heavy validation instructions.

## Current docs
- `docs/MASTER_PROJECT_PLAN_V45.md`
- `docs/V45_SECURITY_DATA_HANDLING_ENTERPRISE_PILOT.md`
- `docs/POWERPC_VALIDATION_RUNBOOK_V45.md`
- `docs/DATASET_API_COMPLETION_CHECKLIST_V45.md`
- `docs/ENTERPRISE_PILOT_PACK_V45.md`

## Historical docs
Older `V12...V44`, `RUN_RESULTS_REALDATA_V*`, and `PROJECT_INVENTORY_V*` documents remain valuable as an audit trail but should be treated as historical unless explicitly referenced by the master plan.
"""


def build_cleanup_md() -> str:
    lines = ["# BioGPU-Core v4.5 Repository Cleanup Audit\n"]
    lines.append("## Direct answer\n")
    lines.append("Yes: before v4.5, the complete plan was spread across many docs and version outputs. This is normal for rapid research iteration, but it is not acceptable for beta/enterprise delivery. v4.5 fixes this by adding one master plan, one document index, one cleanup audit, and one beta/enterprise entry point.\n")
    lines.append("## Cleanup items\n")
    for item in cleanup_items():
        lines.append(f"### {item.category}\n- Problem: {item.problem}\n- Action: {item.action}\n- Risk if ignored: {item.risk_if_ignored}\n")
    lines.append("## Policy\nDo not delete historical artifacts immediately. For beta packaging, hide/archive them from the user-facing root and expose only current docs, sample manifests, scripts, and selected result bundles.\n")
    return "\n".join(lines)


def generate_outputs(output_dir: Path) -> Dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    road = to_rows(roadmap_items())
    access = to_rows(access_tiers())
    datasets = to_rows(dataset_sources())
    cleanup = to_rows(cleanup_items())
    write_csv(output_dir / "v45_master_roadmap.csv", road)
    write_csv(output_dir / "v45_access_tiers.csv", access)
    write_csv(output_dir / "v45_dataset_sources.csv", datasets)
    write_csv(output_dir / "v45_cleanup_audit.csv", cleanup)
    summary = {
        "version": VERSION,
        "single_source_of_truth": "docs/MASTER_PROJECT_PLAN_V45.md",
        "roadmap_items": len(road),
        "access_tiers": len(access),
        "dataset_sources": len(datasets),
        "cleanup_items": len(cleanup),
        "early_tester_policy": "maximum_safe_software_access",
        "live_actuation_default": "blocked_until_lab_vendor_approval",
        "power_pc_required_before_confident_beta_claims": True,
        "ready_for_external_beta_today": False,
        "ready_for_private_technical_preview": True,
    }
    (output_dir / "v45_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return {"summary": str(output_dir / "v45_summary.json")}


if __name__ == "__main__":
    generate_outputs(Path("outputs/realdata_zenodo_14363732_v45_master_plan"))
