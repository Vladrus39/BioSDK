from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Literal

Stage = Literal["now", "power_pc", "licensed_lab", "future"]
Criticality = Literal["required", "recommended", "optional", "future"]


@dataclass(frozen=True)
class HardwareComponent:
    id: str
    name: str
    layer: str
    role: str
    stage: Stage
    criticality: Criticality
    target_spec: str
    bridge_options: list[str] = field(default_factory=list)
    target_options: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class HardwareConnection:
    order: int
    source: str
    target: str
    signal_type: str
    interface: str
    purpose: str
    stage: Stage
    safety_boundary: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class HardwareFormula:
    id: str
    expression: str
    meaning: str
    used_for: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class HardwareBlueprint:
    version: str
    name: str
    goal: str
    boundary_note: str
    components: list[HardwareComponent]
    connections: list[HardwareConnection]
    formulas: list[HardwareFormula]
    implementation_stages: dict[str, list[str]]

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "name": self.name,
            "goal": self.goal,
            "boundary_note": self.boundary_note,
            "components": [c.to_dict() for c in self.components],
            "connections": [c.to_dict() for c in self.connections],
            "formulas": [f.to_dict() for f in self.formulas],
            "implementation_stages": self.implementation_stages,
        }


def build_biogpu_a1_hardware_blueprint_v22() -> HardwareBlueprint:
    components = [
        HardwareComponent(
            id="wet_cartridge",
            name="Replaceable living neural cartridge",
            layer="wetware",
            role="Physical living substrate chamber containing neuronal culture over MEA/HD-MEA.",
            stage="licensed_lab",
            criticality="required",
            target_spec="Transparent sealed/controlled cartridge; first target 2D neuronal network over electrode array; final geometry depends on selected MEA vendor.",
            bridge_options=["60/120/256 electrode MEA cartridge/dish class", "single-well MEA cartridge"],
            target_options=["4096+ channel HD-MEA single-well cartridge", "future 3D organoid/neurosphere cartridge"],
            notes=[
                "Not a standalone biological protocol; live use requires SOP, sterility plan, and facility controls.",
                "Must expose stable electrical contact to the acquisition/stimulation electronics through vendor-approved docking.",
            ],
        ),
        HardwareComponent(
            id="mea_chip",
            name="MEA/HD-MEA electrode chip",
            layer="bioelectronic_interface",
            role="Bidirectional interface: stimulate selected sites and record extracellular activity.",
            stage="licensed_lab",
            criticality="required",
            target_spec="Bridge: 59-256 electrode MEA. Target: 1024-4096+ addressable HD-MEA channels. Planning pitch class 20-200 µm.",
            bridge_options=["MCS MEA2100-compatible 60/120/256 electrode MEA", "Axion Maestro-compatible MEA plate"],
            target_options=["3Brain CorePlate/BioCAM-class 4096 electrode HD-MEA", "future higher-density HD-MEA"],
            notes=[
                "Exact electrode count, pitch, contact material and well geometry are vendor-specific.",
                "All stimulation and safety limits are delegated to vendor manuals and approved lab SOP.",
            ],
        ),
        HardwareComponent(
            id="headstage_stimulator",
            name="Headstage, amplifier and stimulator",
            layer="electronics",
            role="Low-noise acquisition, ADC, stimulation command execution, timestamping.",
            stage="licensed_lab",
            criticality="required",
            target_spec="Bidirectional acquisition/stimulation system with API/SDK access, timestamping, and export of raw traces/spikes.",
            bridge_options=["MCS MEA2100 headstage/stimulator", "Axion Maestro-class acquisition/stimulation backend"],
            target_options=["3Brain BioCAM/BioCAM DupleX-class HD-MEA backend", "Intan RHS-class research controller where appropriate"],
            notes=[
                "BioGPU runtime must talk to this through an adapter, not through hard-coded pinouts.",
                "Dry-run mode must validate patterns before any live output is allowed.",
            ],
        ),
        HardwareComponent(
            id="environment_control",
            name="Environmental control module",
            layer="life_support",
            role="Maintain stable conditions around the living substrate.",
            stage="licensed_lab",
            criticality="required",
            target_spec="Temperature, CO2, humidity, vibration/noise isolation, and sensor telemetry suited to selected wetware platform.",
            bridge_options=["built-in MEA stage-top temperature control", "integrated incubated multiwell MEA chamber"],
            target_options=["closed cartridge environment with telemetry export", "long-run incubated HD-MEA setup"],
            notes=[
                "This is part of the BioGPU system energy budget.",
                "Exact values are SOP-dependent and intentionally not specified here as an operational protocol.",
            ],
        ),
        HardwareComponent(
            id="microfluidics",
            name="Microfluidics / media maintenance module",
            layer="life_support",
            role="Support long-running wetware operation through medium handling and monitoring.",
            stage="future",
            criticality="recommended",
            target_spec="Perfusion/media exchange capability or vendor-supported maintenance mode, with logging and alarms.",
            bridge_options=["manual/vender-SOP maintenance for short bridge runs"],
            target_options=["closed-loop microfluidic cartridge", "remote-access wetware platform model"],
            notes=[
                "Optional for short software dry-runs; important for live long-duration BioGPU experiments.",
                "Must be handled by qualified lab procedures, not by this repository.",
            ],
        ),
        HardwareComponent(
            id="host_pc",
            name="BioGPU controller workstation",
            layer="compute",
            role="Runs BioGPU runtime, adapters, feature extraction, readout, benchmark orchestration and logging.",
            stage="now",
            criticality="required",
            target_spec="Minimum: 8 cores, 32 GB RAM, 1 TB SSD for full local runs. Better: 16+ cores, 64 GB RAM, 2+ TB SSD.",
            bridge_options=["Ubuntu workstation", "lab PC attached to vendor acquisition system"],
            target_options=["dedicated acquisition PC + analysis workstation pair", "server with NAS for long recordings"],
            notes=[
                "GPU is optional for current Zenodo/replay benchmarks; CPU and fast storage matter more now.",
                "Live closed-loop latency depends on vendor SDK path, OS scheduling and network isolation.",
            ],
        ),
        HardwareComponent(
            id="storage",
            name="Data storage and result bundle store",
            layer="compute",
            role="Stores raw traces, spikes, BioGPUTrace, BioGPUResult, logs, reports and audit manifests.",
            stage="now",
            criticality="required",
            target_spec="SSD/NVMe for active runs; external or NAS backup for raw traces and long experiments.",
            bridge_options=["local SSD for replay datasets", "USB/NAS backup"],
            target_options=["RAID/NAS storage with immutable run bundles"],
            notes=[
                "Result bundles must include run manifest, version, hardware config, adapter mode and data hashes.",
            ],
        ),
        HardwareComponent(
            id="runtime",
            name="BioGPU runtime software",
            layer="software",
            role="Defines BioGPUJob → substrate adapter → BioGPUTrace → readout → BioGPUResult.",
            stage="now",
            criticality="required",
            target_spec="Same job contract must run in replay, dry-run and live modes.",
            bridge_options=["RealDataReplayBioGPUSubstrate", "dry-run vendor adapter"],
            target_options=["LiveMEA adapter with vendor backends"],
            notes=[
                "This is the part we can fully develop in this environment.",
                "The runtime must never assume a single vendor or electrode geometry.",
            ],
        ),
        HardwareComponent(
            id="visual_monitoring",
            name="Optional microscope / camera monitoring",
            layer="monitoring",
            role="Provides visual QC of cartridge condition and experiment state.",
            stage="future",
            criticality="optional",
            target_spec="Optional microscope/camera stream linked to run logs.",
            bridge_options=["manual microscope QC"],
            target_options=["integrated imaging with timestamps"],
            notes=["Useful for troubleshooting and publication evidence; not required for replay benchmarks."],
        ),
        HardwareComponent(
            id="power_ups",
            name="Power, UPS and telemetry",
            layer="infrastructure",
            role="Stabilizes long-running experiments and tracks power for energy-per-task calculations.",
            stage="power_pc",
            criticality="recommended",
            target_spec="UPS, watt meter, per-device power logging where possible.",
            bridge_options=["external watt meter for host + electronics"],
            target_options=["per-module telemetry feed into BioGPU metrics"],
            notes=["Energy-per-task claims require measured power, not estimated power only."],
        ),
        HardwareComponent(
            id="sop_safety",
            name="Lab SOP, ethics and biosafety boundary",
            layer="governance",
            role="Defines what can be done live, by whom, and with which vendor/lab-approved procedures.",
            stage="licensed_lab",
            criticality="required",
            target_spec="Approved SOPs, vendor manuals, trained personnel, facility approval as applicable.",
            bridge_options=["no live culture work in software-only environment"],
            target_options=["qualified lab deployment package"],
            notes=[
                "The repository stores engineering contracts and checklists, not executable live-culture recipes.",
                "All live stimulation settings must be validated in a lab-specific safety gate.",
            ],
        ),
    ]

    connections = [
        HardwareConnection(1, "runtime", "host_pc", "software process", "local OS / Python", "Start BioGPU job, load manifest, select replay/dry/live backend.", "now"),
        HardwareConnection(2, "runtime", "headstage_stimulator", "validated command", "vendor SDK/API adapter", "Send validated stimulation/acquisition request to vendor backend.", "licensed_lab", "dry-run gate before live output"),
        HardwareConnection(3, "headstage_stimulator", "mea_chip", "electrical I/O", "vendor-approved connector/dock", "Drive stimulation and receive electrode signals.", "licensed_lab", "vendor manuals only"),
        HardwareConnection(4, "mea_chip", "wet_cartridge", "extracellular interface", "culture-on-chip contact field", "Couple the living network to the electrode array.", "licensed_lab", "lab SOP only"),
        HardwareConnection(5, "wet_cartridge", "mea_chip", "biological spike response", "extracellular readout", "Return neural response to electrode field.", "licensed_lab", "non-invasive extracellular recording path"),
        HardwareConnection(6, "mea_chip", "headstage_stimulator", "analog/digitized acquisition", "vendor acquisition path", "Amplify, digitize, timestamp and stream/store recordings.", "licensed_lab"),
        HardwareConnection(7, "headstage_stimulator", "runtime", "recording stream/files", "vendor SDK/export files", "Create BioGPUTrace inputs for feature extraction.", "now"),
        HardwareConnection(8, "runtime", "storage", "run bundle", "filesystem", "Persist BioGPUJob, BioGPUTrace, BioGPUResult, hardware manifest and logs.", "now"),
        HardwareConnection(9, "environment_control", "wet_cartridge", "environmental support", "stage/incubator/cartridge control", "Keep substrate in vendor/lab-approved operating envelope.", "licensed_lab", "SOP-controlled"),
        HardwareConnection(10, "microfluidics", "wet_cartridge", "media/perfusion support", "lab/vender-approved fluidic path", "Support longer wetware experiments.", "future", "SOP-controlled"),
        HardwareConnection(11, "visual_monitoring", "storage", "image/video metadata", "timestamped files", "Attach visual QC evidence to result bundle.", "future"),
        HardwareConnection(12, "power_ups", "runtime", "power telemetry", "meter/API/manual log", "Feed measured power into energy-per-task estimates.", "power_pc"),
    ]

    formulas = [
        HardwareFormula("samples_per_window", "N_samples = N_channels * f_s * T_window", "Number of sampled values per acquisition window.", "RAM and storage planning"),
        HardwareFormula("bytes_per_window", "B_window = N_channels * f_s * T_window * bytes_per_sample", "Bytes generated for one raw trace window.", "per-task storage estimate"),
        HardwareFormula("stream_rate", "R_Bps = N_channels * f_s * bytes_per_sample", "Raw stream bandwidth in bytes per second.", "DAQ/storage planning"),
        HardwareFormula("storage_per_day", "S_day_GB = R_Bps * 86400 / 1e9", "Approximate continuous raw storage per day.", "long-run experiment planning"),
        HardwareFormula("loop_latency", "T_loop = T_encode + T_stim + T_bio + T_acq + T_decode", "Closed-loop runtime latency.", "control-loop feasibility"),
        HardwareFormula("energy_per_task", "E_task = (P_host + P_electronics + P_environment) * T_run / N_tasks", "Energy per completed task, requiring measured power for real claims.", "GPU/CPU/BioGPU comparison"),
        HardwareFormula("channel_density", "D_ch = N_channels / A_active", "Electrode/channel density over active area.", "MEA vs HD-MEA comparison"),
    ]

    stages = {
        "software_now": [
            "Keep replay substrate and BioGPU runtime vendor-neutral.",
            "Generate hardware manifests and result bundles without live hardware.",
            "Run Zenodo/replay benchmarks and power-PC scripts.",
        ],
        "power_pc": [
            "Run 100-1000 shuffle and multi-seed sweeps.",
            "Add measured host power for replay compute energy estimates.",
            "Prepare NAS/backup and reproducible result bundle storage.",
        ],
        "licensed_lab_bridge": [
            "Select one bridge platform: MCS/Axion-class MEA or equivalent.",
            "Map vendor SDK into LiveMEA adapter without changing BioGPUJob contract.",
            "Validate dry-run pattern logs before any live command.",
        ],
        "hd_mea_target": [
            "Move to 1024-4096+ channel HD-MEA platform.",
            "Measure latency, stability, repeatability and energy.",
            "Compare live BioGPU tasks against CPU/GPU/neuromorphic baselines.",
        ],
    }

    return HardwareBlueprint(
        version="v2.2",
        name="BioGPU-A1 Hardware Blueprint",
        goal="Turn BioGPU-A1 from software/wetware concept into a modular hardware system map ready for replay, dry-run and future live MEA/HD-MEA implementation.",
        boundary_note=(
            "This blueprint is an engineering system design. It is not a wet-lab protocol, "
            "not a vendor pinout manual, and not a live stimulation safety document. "
            "Live implementation requires selected platform documentation, qualified lab SOPs and trained personnel."
        ),
        components=components,
        connections=connections,
        formulas=formulas,
        implementation_stages=stages,
    )


def render_markdown_report(blueprint: HardwareBlueprint) -> str:
    comp_lines = []
    for c in blueprint.components:
        comp_lines.append(
            f"### {c.id} — {c.name}\n\n"
            f"- Layer: `{c.layer}`\n"
            f"- Stage: `{c.stage}`\n"
            f"- Criticality: `{c.criticality}`\n"
            f"- Role: {c.role}\n"
            f"- Target spec: {c.target_spec}\n"
            f"- Bridge options: {', '.join(c.bridge_options) if c.bridge_options else 'n/a'}\n"
            f"- Target options: {', '.join(c.target_options) if c.target_options else 'n/a'}\n"
            f"- Notes:\n" + "\n".join(f"  - {n}" for n in c.notes) + "\n"
        )
    conn_lines = "\n".join(
        f"| {x.order} | `{x.source}` | `{x.target}` | {x.signal_type} | {x.interface} | {x.purpose} | {x.stage} |"
        for x in blueprint.connections
    )
    formula_lines = "\n".join(f"- `{f.expression}` — {f.meaning} Used for: {f.used_for}." for f in blueprint.formulas)
    stage_lines = "\n".join(
        f"### {stage}\n" + "\n".join(f"- {item}" for item in items)
        for stage, items in blueprint.implementation_stages.items()
    )
    mermaid = """```mermaid
flowchart LR
  Job[BioGPUJob] --> Runtime[BioGPU runtime]
  Runtime --> Adapter[Vendor adapter / SDK]
  Adapter --> HW[Headstage / stimulator / amplifier]
  HW --> MEA[MEA / HD-MEA chip]
  MEA --> Living[Living neural cartridge]
  Living --> MEA
  MEA --> HW
  HW --> Trace[BioGPUTrace]
  Trace --> Readout[Feature extraction / readout]
  Readout --> Result[BioGPUResult]
  Env[Environment control] --> Living
  Fluidics[Microfluidics / media support] --> Living
  Power[Power telemetry] --> Runtime
  Runtime --> Store[Result bundle store]
```"""
    return f"""# {blueprint.name}

Version: `{blueprint.version}`

## Goal

{blueprint.goal}

## Boundary

{blueprint.boundary_note}

## System signal chain

{mermaid}

## Hardware components

{chr(10).join(comp_lines)}

## Connection table

| # | Source | Target | Signal | Interface | Purpose | Stage |
|---:|---|---|---|---|---|---|
{conn_lines}

## Engineering formulas

{formula_lines}

## Implementation stages

{stage_lines}
"""


def write_connection_csv(blueprint: HardwareBlueprint, path: str | Path) -> None:
    path = Path(path)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["order", "source", "target", "signal_type", "interface", "purpose", "stage", "safety_boundary"],
        )
        w.writeheader()
        for c in blueprint.connections:
            w.writerow(c.to_dict())


def write_bom_csv(blueprint: HardwareBlueprint, path: str | Path) -> None:
    path = Path(path)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["id", "name", "layer", "role", "stage", "criticality", "target_spec", "bridge_options", "target_options", "notes"],
        )
        w.writeheader()
        for c in blueprint.components:
            d = c.to_dict()
            for k in ["bridge_options", "target_options", "notes"]:
                d[k] = " | ".join(d[k])
            w.writerow(d)


def write_v22_outputs(out_dir: str | Path) -> dict:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    blueprint = build_biogpu_a1_hardware_blueprint_v22()
    (out / "biogpu_a1_hardware_blueprint.json").write_text(json.dumps(blueprint.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    (out / "BIOGPU_A1_HARDWARE_REPORT.md").write_text(render_markdown_report(blueprint), encoding="utf-8")
    write_connection_csv(blueprint, out / "BIOGPU_A1_CONNECTION_TABLE.csv")
    write_bom_csv(blueprint, out / "BIOGPU_A1_BOM.csv")
    summary = {
        "version": blueprint.version,
        "components": len(blueprint.components),
        "connections": len(blueprint.connections),
        "formulas": len(blueprint.formulas),
        "required_components": [c.id for c in blueprint.components if c.criticality == "required"],
        "output_files": [
            "biogpu_a1_hardware_blueprint.json",
            "BIOGPU_A1_HARDWARE_REPORT.md",
            "BIOGPU_A1_CONNECTION_TABLE.csv",
            "BIOGPU_A1_BOM.csv",
        ],
    }
    (out / "v22_hardware_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return summary


__all__ = [
    "HardwareComponent",
    "HardwareConnection",
    "HardwareFormula",
    "HardwareBlueprint",
    "build_biogpu_a1_hardware_blueprint_v22",
    "render_markdown_report",
    "write_v22_outputs",
]
