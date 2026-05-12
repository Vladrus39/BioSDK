"""BiC OS / BioCompute OS differentiation blueprint.

The blueprint defines what must exist before BioGPU-Core can honestly move
from SDK/runtime to OS-like control plane for living neural compute.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List


@dataclass(frozen=True)
class OSModule:
    name: str
    purpose: str
    differentiator: str
    status: str
    next_deliverables: List[str]


@dataclass(frozen=True)
class LLMWorkflow:
    name: str
    description: str
    safe_default: str
    future_upgrade: str


@dataclass(frozen=True)
class FirstMoverAxis:
    axis: str
    what_exists_elsewhere: str
    our_angle: str
    evidence_needed: str


OS_MODULES: List[OSModule] = [
    OSModule(
        name="NSI Kernel",
        purpose="Schema and conformance layer for traces, manifests, feature batches, readout results, bundles, safety profiles and adapters.",
        differentiator="Vendor-neutral profile above NWB/HDF5/vendor exports/API streams.",
        status="draft in v4.8/v4.9",
        next_deliverables=["JSON Schema/Pydantic models", "adapter conformance tests", "versioned NSI-1.0 spec"],
    ),
    OSModule(
        name="LLM/Agent Bridge",
        purpose="Expose BioCompute tasks as safe tools for LLM planners and research agents.",
        differentiator="LLM can request replay/read-only/live-shadow analyses and receive structured result bundles with claim levels.",
        status="BioLLM tool interface prototype exists",
        next_deliverables=["tool schema", "agent approval policy", "prompt/result audit", "MCP-compatible wrapper candidate"],
    ),
    OSModule(
        name="Experiment Orchestrator",
        purpose="Run manifests across datasets, adapters, decoders, shuffles, bootstraps and result packaging.",
        differentiator="Turns wetware/neural data experiments into reproducible compute jobs.",
        status="runtime/benchmark scaffolds exist; power-PC validation pending",
        next_deliverables=["persistent job state", "resumable sweeps", "distributed workers", "failure recovery"],
    ),
    OSModule(
        name="Safety Supervisor",
        purpose="Central permission gate for replay, read-only, live-shadow and approved actuation modes.",
        differentiator="Allows maximum software access while blocking unsafe biological actuation by default.",
        status="boundary modules exist",
        next_deliverables=["policy-as-code", "operator approvals", "signed allowlists", "protocol-bound live permissions"],
    ),
    OSModule(
        name="Adapter Marketplace / Plugin Layer",
        purpose="Let labs/vendors add adapters for NWB, DANDI, Allen, FinalSpark, MCS, 3Brain, Axion, CL-like APIs and private data.",
        differentiator="A cross-vendor ecosystem rather than one vertical wetware device.",
        status="mock/read-only adapter skeleton exists",
        next_deliverables=["plugin packaging", "adapter certification", "adapter test harness", "credential vault"],
    ),
    OSModule(
        name="Evidence Ledger",
        purpose="Keep every run reproducible through checksums, manifests, metrics, plots, logs and software versions.",
        differentiator="Turns speculative biological compute claims into auditable evidence bundles.",
        status="result bundle discipline exists in evidence pack",
        next_deliverables=["bundle signing", "immutability option", "comparison dashboard", "paper/investor export"],
    ),
    OSModule(
        name="BioCompute Dashboard",
        purpose="UI for researchers, enterprise users and operators: datasets, jobs, adapters, metrics, bundles, approvals and telemetry.",
        differentiator="Human-readable control plane for hybrid biological/AI workflows.",
        status="server scaffold exists; production UI missing",
        next_deliverables=["FastAPI production backend", "worker queue", "Postgres", "object storage", "React dashboard"],
    ),
    OSModule(
        name="Live Lab Gateway",
        purpose="Future lab/vendor-approved path from live streams to live-shadow and then controlled closed-loop.",
        differentiator="A staged governance workflow rather than uncontrolled stimulation.",
        status="roadmap only",
        next_deliverables=["read-only credential tests", "live-shadow telemetry", "protocol approval workflow", "lab pilot result bundle"],
    ),
]

LLM_WORKFLOWS: List[LLMWorkflow] = [
    LLMWorkflow(
        name="BioCompute Tool Call",
        description="LLM turns a research question into a BioComputeTaskManifest and receives a structured result with confidence, baseline and claim level.",
        safe_default="replay/read-only only",
        future_upgrade="live-shadow after partner API approval",
    ),
    LLMWorkflow(
        name="Autonomous Benchmark Agent",
        description="Agent proposes decoder/ablation/split experiments, runs approved jobs and summarizes evidence without touching live actuation.",
        safe_default="bounded job templates and quotas",
        future_upgrade="operator-approved experimental plans",
    ),
    LLMWorkflow(
        name="Lab Copilot",
        description="LLM helps interpret run bundles, flag anomalies, produce reports and prepare next experiment manifests.",
        safe_default="analysis/reporting only",
        future_upgrade="protocol-bound suggestions reviewed by human operator",
    ),
    LLMWorkflow(
        name="Enterprise Evidence Assistant",
        description="LLM assembles reproducibility packs, audit summaries, partner reports and pilot acceptance evidence.",
        safe_default="result-bundle-grounded generation",
        future_upgrade="customer-specific governance and approval workflows",
    ),
]

FIRST_MOVER_AXES: List[FirstMoverAxis] = [
    FirstMoverAxis(
        axis="Vendor neutrality",
        what_exists_elsewhere="Vertical wetware platforms and vendor-specific APIs exist.",
        our_angle="Define a neutral runtime/interface across replay datasets, NWB/DANDI/Allen, vendor exports and remote wetware APIs.",
        evidence_needed="At least 3 independent adapter families passing NSI conformance tests.",
    ),
    FirstMoverAxis(
        axis="Result-bundle evidence standard",
        what_exists_elsewhere="Many platforms provide data or experiments, but reproducible cross-platform evidence bundles are fragmented.",
        our_angle="Every claim is tied to manifest, data checksum, split policy, baseline, metrics, logs and claim level.",
        evidence_needed="Power-PC full shuffle/CI bundles and at least one external dataset/API bundle.",
    ),
    FirstMoverAxis(
        axis="LLM-native biological compute tooling",
        what_exists_elsewhere="LLM agents and wetware systems exist mostly as separate stacks.",
        our_angle="Expose biological compute as safe LLM tools with safety profiles, audit trails and structured outputs.",
        evidence_needed="BioLLM workflows running on replay + read-only partner data.",
    ),
    FirstMoverAxis(
        axis="Maximum safe beta access",
        what_exists_elsewhere="Products often choose either demo-only or closed vendor control.",
        our_angle="Give early testers full software/replay/read-only access while blocking unsafe live actuation by default.",
        evidence_needed="Private beta pilots with upload, replay, read-only adapters and result bundles.",
    ),
    FirstMoverAxis(
        axis="Path from SDK to OS",
        what_exists_elsewhere="SDKs/control tools exist for electrophysiology and some wetware platforms.",
        our_angle="Unify SDK, runtime, scheduler, safety supervisor, adapter marketplace, evidence ledger and LLM bridge into an OS-like control plane.",
        evidence_needed="Production server, plugin manager, permissions, job queue and live-shadow validation.",
    ),
]


def bic_os_blueprint() -> Dict[str, object]:
    return {
        "version": "4.9",
        "working_name": "BiC OS",
        "long_form": "BioCompute OS / Biological Interface Compute OS",
        "status": "roadmap codename, not legally cleared",
        "one_line": "An OS-like control plane for living neural compute, LLM agents, replay datasets, wetware APIs, experiments and auditable result bundles.",
        "default_safety_posture": "maximum software access; no unsafe live actuation by default",
        "modules": [asdict(x) for x in OS_MODULES],
        "llm_workflows": [asdict(x) for x in LLM_WORKFLOWS],
        "first_mover_axes": [asdict(x) for x in FIRST_MOVER_AXES],
        "must_exist_before_os_claim": [
            "persistent daemon/service",
            "scheduler and worker queue",
            "permission and approval system",
            "adapter plugin manager",
            "production storage/database",
            "dashboard/control plane",
            "NSI-1.0 conformance tests",
            "at least one read-only/live-shadow external API validation",
            "power-PC evidence bundles",
            "safety supervisor with blocked-by-default live actuation",
        ],
    }


def assert_bic_os_blueprint_complete() -> None:
    data = bic_os_blueprint()
    assert data["working_name"] == "BiC OS"
    module_names = {m["name"] for m in data["modules"]}
    assert "LLM/Agent Bridge" in module_names
    assert "Safety Supervisor" in module_names
    assert "Evidence Ledger" in module_names
    assert len(data["first_mover_axes"]) >= 5
