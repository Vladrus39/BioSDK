from __future__ import annotations

import json, shutil
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Literal

from biogpu.runtime.engineering_v19 import build_prototype_plan_v19

Stage = Literal['now','power_pc','licensed_lab','future']

@dataclass(frozen=True)
class BioGPUVisualElement:
    name: str
    description: str
    live_appearance: str
    purpose: str
    stage: Stage
    def to_dict(self): return asdict(self)

@dataclass(frozen=True)
class BioGPUConnectionStep:
    order: int
    component: str
    connects_to: str
    signal_type: str
    purpose: str
    stage: Stage
    def to_dict(self): return asdict(self)

@dataclass(frozen=True)
class BioGPULabBoundary:
    category: str
    allowed_in_project: list[str] = field(default_factory=list)
    not_included_here: list[str] = field(default_factory=list)
    reason: str = ''
    required_real_world_dependency: list[str] = field(default_factory=list)
    def to_dict(self): return asdict(self)

@dataclass(frozen=True)
class BioGPUPrototypeStack:
    version: str
    goal: str
    first_real_form: str
    visual_spec: list[BioGPUVisualElement]
    connection_map: list[BioGPUConnectionStep]
    boundaries: list[BioGPULabBoundary]
    coding_next_steps: list[str]
    power_pc_next_steps: list[str]
    lab_next_steps: list[str]
    def to_dict(self):
        d = asdict(self)
        d['visual_spec'] = [x.to_dict() for x in self.visual_spec]
        d['connection_map'] = [x.to_dict() for x in self.connection_map]
        d['boundaries'] = [x.to_dict() for x in self.boundaries]
        return d


def build_visual_spec_v20() -> list[BioGPUVisualElement]:
    return [
        BioGPUVisualElement(
            name='Living neural cartridge',
            description='A small transparent cartridge or dish containing a living neuronal network on a MEA/HD-MEA substrate.',
            live_appearance='From the outside: a compact clear chamber with fluid; from the inside under magnification: a thin branching network of neurons spread over an electrode grid.',
            purpose='Primary biological computing substrate for BioGPU.',
            stage='now'
        ),
        BioGPUVisualElement(
            name='MEA/HD-MEA interface chip',
            description='A glass/silicon chip with many microelectrodes for recording and stimulation.',
            live_appearance='Dark or gold grid at the bottom of the chamber, often visible as metallic tracks or pads.',
            purpose='Electrical I/O between controller electronics and living neural substrate.',
            stage='now'
        ),
        BioGPUVisualElement(
            name='Environmental control shell',
            description='A sealed or stage-top environment that maintains a stable state for the living substrate.',
            live_appearance='An enclosure or incubated stage around the cartridge, with sensor lines and controlled environment.',
            purpose='Keep the biological substrate stable enough for repeatable operation.',
            stage='licensed_lab'
        ),
        BioGPUVisualElement(
            name='Acquisition and stimulation electronics',
            description='Amplifier/stimulator layer that talks to the MEA/HD-MEA and to the BioGPU controller.',
            live_appearance='External rack or compact device connected by cables to the MEA platform.',
            purpose='Generate safe patterns and acquire responses.',
            stage='now'
        ),
        BioGPUVisualElement(
            name='BioGPU controller workstation',
            description='The host computer running BioGPU runtime, encoder, scheduler, feature extraction and readout.',
            live_appearance='A workstation or server connected to electronics and storage.',
            purpose='Software control plane for running jobs, collecting traces and evaluating benchmarks.',
            stage='now'
        ),
    ]


def build_connection_map_v20() -> list[BioGPUConnectionStep]:
    return [
        BioGPUConnectionStep(1, 'BioGPU task input', 'Encoder', 'digital task payload', 'Convert benchmark/task input into a substrate-facing pattern request.', 'now'),
        BioGPUConnectionStep(2, 'Encoder', 'Stimulus planner', 'software stimulation request', 'Prepare safe high-level stimulation intent and channel targets.', 'now'),
        BioGPUConnectionStep(3, 'Stimulus planner', 'Acquisition/stimulation electronics', 'vendor API command', 'Pass a validated command to the hardware control layer.', 'licensed_lab'),
        BioGPUConnectionStep(4, 'Acquisition/stimulation electronics', 'MEA/HD-MEA chip', 'electrical stimulation and acquisition control', 'Drive and read the electrode array.', 'licensed_lab'),
        BioGPUConnectionStep(5, 'MEA/HD-MEA chip', 'Living neuronal network', 'extracellular stimulation/readout interface', 'Couple the electronics to the biological substrate.', 'licensed_lab'),
        BioGPUConnectionStep(6, 'Living neuronal network', 'MEA/HD-MEA chip', 'biological spike responses', 'Return neuronal activity back to the array.', 'licensed_lab'),
        BioGPUConnectionStep(7, 'MEA/HD-MEA chip', 'Acquisition/stimulation electronics', 'digitized recordings', 'Bring measured activity into the digital stack.', 'licensed_lab'),
        BioGPUConnectionStep(8, 'Acquisition/stimulation electronics', 'BioGPU runtime', 'recording stream / files', 'Collect timestamps, channels, traces and metadata.', 'now'),
        BioGPUConnectionStep(9, 'BioGPU runtime', 'Feature extraction / readout', 'BioGPUTrace', 'Build feature vectors and decode result.', 'now'),
        BioGPUConnectionStep(10, 'Feature extraction / readout', 'Benchmark harness / controller', 'BioGPUResult', 'Score the task and optionally schedule the next closed-loop step.', 'now'),
    ]


def build_lab_boundaries_v20() -> list[BioGPULabBoundary]:
    return [
        BioGPULabBoundary(
            category='Safe project scope in this repository',
            allowed_in_project=[
                'High-level material specification and visual description',
                'Architecture, interfaces, benchmark design and runtime contracts',
                'Replay-substrate development on public datasets',
                'Vendor-neutral connection architecture at system level',
                'Checklists for what a qualified lab or vendor backend must provide',
            ],
            not_included_here=[
                'Step-by-step wet-lab culturing protocol',
                'Exact media recipes, concentrations or incubation formulas',
                'Exact stimulation limits or electrode safety settings for live tissue',
                'Operational troubleshooting for growing or manipulating live neuronal cultures',
                'Detailed wiring/pinout instructions for any specific MEA vendor system',
            ],
            reason='These details require qualified biosafety oversight, approved laboratory SOPs and vendor documentation; they are outside the safe scope of this coding/research repository.',
            required_real_world_dependency=['licensed lab', 'approved SOPs', 'biosafety/ethics review as applicable', 'vendor manuals/SDKs', 'trained personnel']
        ),
        BioGPULabBoundary(
            category='What to prepare before live prototype work',
            allowed_in_project=[
                'Define acceptance criteria for a first prototype',
                'Specify required telemetry and audit logging',
                'Define data contracts for stimulation requests and response traces',
                'Design dry-run and replay modes before hardware integration',
            ],
            not_included_here=[
                'Executing live biological experiments',
                'Purchasing or handling regulated biological materials',
            ],
            reason='Project can prepare software and systems engineering now, while live work happens later in an appropriate facility.',
            required_real_world_dependency=['facility selection', 'procurement process', 'lab partner or in-house capability']
        )
    ]


def build_prototype_stack_v20() -> BioGPUPrototypeStack:
    plan = build_prototype_plan_v19()
    return BioGPUPrototypeStack(
        version='v2.0',
        goal=plan.main_goal,
        first_real_form='A living neuronal network grown on a MEA/HD-MEA cartridge, controlled by external electronics and the BioGPU software runtime.',
        visual_spec=build_visual_spec_v20(),
        connection_map=build_connection_map_v20(),
        boundaries=build_lab_boundaries_v20(),
        coding_next_steps=[
            'Strengthen live adapter contracts and session schemas.',
            'Add benchmark registry with standard input/output contracts.',
            'Add result bundle/export for power-PC and future lab runs.',
            'Add deterministic replay traces for regression tests.',
        ],
        power_pc_next_steps=[
            'Run 100-1000 label-shuffle permutations.',
            'Run multi-seed negative sampling sweeps.',
            'Expand comparison across linear readouts and feature ablations.',
            'Add DANDI/Allen dataset execution.',
        ],
        lab_next_steps=[
            'Select a concrete MEA/HD-MEA platform and SDK.',
            'Map vendor backend onto the LiveMEASubstrateAdapter contract.',
            'Establish qualified lab SOPs and approval paths.',
            'Measure stability, latency and repeatability on live hardware.',
        ]
    )


def render_v20_report(stack: BioGPUPrototypeStack) -> str:
    vis = '\n'.join(f"- **{x.name}** ({x.stage}) — {x.description}" for x in stack.visual_spec)
    conn = '\n'.join(f"{x.order}. **{x.component} → {x.connects_to}** — {x.signal_type}: {x.purpose}" for x in stack.connection_map)
    bnd = '\n\n'.join(
        f"### {b.category}\nAllowed in project:\n" + '\n'.join(f"- {a}" for a in b.allowed_in_project) +
        "\nNot included here:\n" + '\n'.join(f"- {n}" for n in b.not_included_here) +
        f"\nReason: {b.reason}\nRequired dependency:\n" + '\n'.join(f"- {r}" for r in b.required_real_world_dependency)
        for b in stack.boundaries
    )
    return f'''# BioGPU v2.0 — Prototype Stack and Lab Boundaries

## Goal

{stack.goal}

## First real form

{stack.first_real_form}

## Visual specification

{vis}

## High-level connection architecture

{conn}

## Lab boundaries

{bnd}

## Coding next steps

{chr(10).join('- ' + x for x in stack.coding_next_steps)}

## Power-PC next steps

{chr(10).join('- ' + x for x in stack.power_pc_next_steps)}

## Lab next steps

{chr(10).join('- ' + x for x in stack.lab_next_steps)}
'''


def write_v20_outputs(out_dir: str | Path, image_path: str | Path | None = None) -> dict:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    stack = build_prototype_stack_v20()
    summary = {
        'version': stack.version,
        'goal': stack.goal,
        'first_real_form': stack.first_real_form,
        'visual_elements': len(stack.visual_spec),
        'connection_steps': len(stack.connection_map),
        'coding_next_steps': stack.coding_next_steps,
        'power_pc_next_steps': stack.power_pc_next_steps,
        'lab_next_steps': stack.lab_next_steps,
    }
    (out/'v20_prototype_stack.json').write_text(json.dumps(stack.to_dict(), indent=2, ensure_ascii=False), encoding='utf-8')
    (out/'v20_summary.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding='utf-8')
    (out/'BIOGPU_V20_PROTOTYPE_REPORT.md').write_text(render_v20_report(stack), encoding='utf-8')
    if image_path and Path(image_path).exists():
        shutil.copy2(Path(image_path), out/'biogpu_material_visualization.png')
    return summary
