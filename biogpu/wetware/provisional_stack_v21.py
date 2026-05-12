from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Literal

Readiness = Literal['provisional_design','requires_vendor_protocol','requires_lab_validation','future']

@dataclass(frozen=True)
class WetwareComponent:
    layer: str
    ideal_choice: str
    role: str
    why_this_choice: list[str]
    possible_alternatives: list[str] = field(default_factory=list)
    what_can_change_it: list[str] = field(default_factory=list)
    readiness: Readiness = 'provisional_design'
    def to_dict(self): return asdict(self)

@dataclass(frozen=True)
class WetwareAcceptanceCriterion:
    metric: str
    desired_direction: str
    measurement_channel: str
    why_it_matters: str
    stage: Literal['software_now','power_pc','lab']
    def to_dict(self): return asdict(self)

@dataclass(frozen=True)
class WetwareStackSpec:
    version: str
    selected_path: str
    plain_language_summary: str
    components: list[WetwareComponent]
    acceptance_criteria: list[WetwareAcceptanceCriterion]
    explicit_non_protocol_boundary: list[str]
    def to_dict(self):
        d = asdict(self)
        d['components'] = [x.to_dict() for x in self.components]
        d['acceptance_criteria'] = [x.to_dict() for x in self.acceptance_criteria]
        return d


def build_provisional_wetware_stack_v21() -> WetwareStackSpec:
    """Return the current ideal BioGPU wetware hypothesis.

    This is a design/BOM-level specification, not a cell-culture recipe.
    Exact concentrations, timing, passaging, plating densities, medium-change
    schedules and stimulation safety parameters must be imported from the
    chosen cell vendor, MEA vendor, institutional SOPs and lab validation.
    """
    components = [
        WetwareComponent(
            layer='Cellular substrate',
            ideal_choice='Human iPSC-derived mixed cortical-like neurons with excitatory and inhibitory populations; optional astrocyte support/co-culture.',
            role='Living nonlinear adaptive reservoir that transforms stimulation patterns into high-dimensional spike-response states.',
            why_this_choice=['more human-relevant than pure rodent primary cultures','commercially sourceable and more repeatable than freshly dissected primary tissue','mixed excitatory/inhibitory networks should be more stable and computationally richer than a single-cell-type culture'],
            possible_alternatives=['primary rat/mouse cortical neurons for lower-cost first lab proof','pure excitatory iPSC neurons for simpler analysis','3D organoids/neurospheres for later memory-rich substrate'],
            what_can_change_it=['cell availability and budget','ethics and regulatory route','MEA platform compatibility','desired repeatability versus biological richness'],
            readiness='requires_vendor_protocol'
        ),
        WetwareComponent(
            layer='Support cells / trophic support',
            ideal_choice='Astrocyte co-culture or astrocyte-conditioned support strategy; neurotrophic support class such as BDNF/GDNF-family factors where required by the vendor protocol.',
            role='Improve maturation, synaptic stability, viability and long-term electrophysiological activity.',
            why_this_choice=['neural networks on MEA need stable maturation and activity','support cells can improve physiological behavior and robustness','trophic support can reduce culture-to-culture failure risk'],
            possible_alternatives=['defined neuron-only vendor kits','glial feeder strategy','no co-culture for simplest first controlled baseline'],
            what_can_change_it=['chosen cell line','vendor kit requirements','assay duration','lab restrictions'],
            readiness='requires_vendor_protocol'
        ),
        WetwareComponent(
            layer='Electrode-surface adhesion underlayer',
            ideal_choice='MEA-compatible cationic adhesion layer class: PDL or PEI, selected according to the MEA vendor and lab SOP.',
            role='Help neurons attach reliably to the MEA/HD-MEA surface and remain coupled to electrodes.',
            why_this_choice=['widely used for neuronal attachment on MEA surfaces','explicitly appears in MEA vendor protocols/app notes','supports repeatable electrode coupling'],
            possible_alternatives=['poly-L-lysine','vendor pre-coated MEA plates','proprietary surface chemistry'],
            what_can_change_it=['MEA material: glass, silicon, gold, PEDOT, CMOS surface','vendor recommendations','cell type and coating compatibility'],
            readiness='requires_vendor_protocol'
        ),
        WetwareComponent(
            layer='Extracellular matrix / neurite guidance',
            ideal_choice='Laminin-focused ECM layer, optionally with fibronectin depending on cell line and surface.',
            role='Support neurite outgrowth, network formation and local electrode coupling.',
            why_this_choice=['laminin is a standard neuronal ECM component','Axion lists PEI/laminin, PDL and fibronectin as appropriate coating classes','MCS neuronal MEA application notes use PDL/laminin-style coating workflows'],
            possible_alternatives=['Matrigel-class ECM for organoid or 3D work','synthetic peptide coatings','micro-patterned ECM islands'],
            what_can_change_it=['2D versus 3D path','human iPSC versus rodent primary cells','need for patterned input/output zones'],
            readiness='requires_vendor_protocol'
        ),
        WetwareComponent(
            layer='Basal culture medium option A',
            ideal_choice='BrainPhys-class serum-free neuronal medium for functional/electrophysiological assays.',
            role='Maintain more neurophysiological extracellular conditions during recording and stimulation workflows.',
            why_this_choice=['designed for improved neuronal function','supports long-term culture of primary and hPSC-derived neurons','can support functional assays without media switching shock according to vendor description'],
            possible_alternatives=['Neurobasal Plus/B-27 Plus system','vendor-specific iPSC-neuron maintenance medium'],
            what_can_change_it=['cell vendor recommendation','recording stability','cost and availability','comparison against legacy literature'],
            readiness='requires_vendor_protocol'
        ),
        WetwareComponent(
            layer='Basal culture medium option B',
            ideal_choice='Neurobasal Plus + B-27 Plus neuronal culture system or equivalent defined neuronal system.',
            role='Reliable long-term neuronal maintenance and maturation route for primary and iPSC-derived neurons.',
            why_this_choice=['official vendor system for primary rodent and human stem-cell-derived neurons','B-27/Neurobasal lineage is widely used in neuronal culture literature','MEA examples exist with neuronal activity measurements'],
            possible_alternatives=['BrainPhys + neuronal supplements','cell-vendor complete medium'],
            what_can_change_it=['whether the priority is physiological recording medium or maximum survival/maturation','chosen cell line and protocol','supply chain'],
            readiness='requires_vendor_protocol'
        ),
        WetwareComponent(
            layer='Supplement classes',
            ideal_choice='Defined neuronal supplements: B27/SM1/N2-like support, glutamine/GlutaMAX-class support where required, antioxidants and maturation factors according to vendor protocol.',
            role='Provide defined micronutrients, lipid/antioxidant support and metabolic support without serum variability.',
            why_this_choice=['serum-free defined systems improve repeatability','supplements are part of common neuronal culture systems','avoids undefined serum effects in electrophysiology benchmarks'],
            possible_alternatives=['vendor complete supplement packs','minimal defined medium for controlled experiments'],
            what_can_change_it=['cell-line protocol','long-term survival versus strict experimental control','lot-to-lot validation'],
            readiness='requires_vendor_protocol'
        ),
        WetwareComponent(
            layer='Physical interface',
            ideal_choice='HD-MEA/MEA cartridge with bidirectional stimulation/readout, TTL/raw recording and vendor SDK access.',
            role='Bridge BioGPU runtime to the living substrate.',
            why_this_choice=['must support stimulation and recording','must export timestamps/channels/traces','must integrate with Python or a callable vendor backend'],
            possible_alternatives=['classic 60-electrode MEA for first proof','CMOS HD-MEA for scaling','remote organoid platform for early access'],
            what_can_change_it=['budget','vendor access','channel count target','latency target'],
            readiness='provisional_design'
        ),
    ]
    acceptance = [
        WetwareAcceptanceCriterion('Viability and attachment','stable / sufficient for repeated sessions','microscopy + lab QC','Without stable attachment there is no repeatable electrical coupling.','lab'),
        WetwareAcceptanceCriterion('Spontaneous activity','present but not saturated','MEA spike/burst metrics','A silent or constantly saturated network is a poor reservoir.','lab'),
        WetwareAcceptanceCriterion('Stimulus-aligned response','above random-time and random-electrode controls','BioGPU pulse benchmark','This is the first real BioGPU signal gate already shown in replay form.','software_now'),
        WetwareAcceptanceCriterion('Readout separability','above shuffled baseline','BioGPU readout benchmark','Shows the substrate state contains task-relevant information.','power_pc'),
        WetwareAcceptanceCriterion('Session stability','drift measurable and bounded','BioGPU session bundle','Needed before claiming repeatable accelerator behavior.','lab'),
        WetwareAcceptanceCriterion('Energy/task accounting','measured separately for substrate, environment and electronics','power meter + runtime logs','Required before any claim versus GPU/CPU.','lab'),
    ]
    return WetwareStackSpec(
        version='v2.1',
        selected_path='2D human iPSC-derived mixed cortical-like neuronal network on MEA/HD-MEA.',
        plain_language_summary='The first BioGPU wetware should be a real living neuronal network, grown on an engineered electrode array, using vendor/lab-validated neuronal media and coating systems. The repository records the ideal stack and variables, not a substitute wet-lab recipe.',
        components=components,
        acceptance_criteria=acceptance,
        explicit_non_protocol_boundary=[
            'No exact concentrations, plating densities, incubation durations, medium-change schedules or live-stimulation limits are defined here.',
            'Exact values must come from chosen cell-line vendor instructions, MEA vendor protocol, institutional SOP and lab validation.',
            'This repository stores the design hypothesis and evaluation criteria so the future lab protocol can be plugged in without changing BioGPU architecture.'
        ]
    )


def render_wetware_markdown(spec: WetwareStackSpec) -> str:
    comp = '\n'.join(
        f"### {c.layer}\n\n**Ideal choice:** {c.ideal_choice}\n\n**Role:** {c.role}\n\n**Why:**\n" +
        '\n'.join(f"- {x}" for x in c.why_this_choice) +
        "\n\n**Alternatives:**\n" + '\n'.join(f"- {x}" for x in c.possible_alternatives) +
        "\n\n**What can change it:**\n" + '\n'.join(f"- {x}" for x in c.what_can_change_it) +
        f"\n\n**Readiness:** `{c.readiness}`\n"
        for c in spec.components
    )
    acc = '\n'.join(f"- **{a.metric}** — {a.desired_direction}; channel: {a.measurement_channel}; stage: `{a.stage}`" for a in spec.acceptance_criteria)
    boundary = '\n'.join(f"- {x}" for x in spec.explicit_non_protocol_boundary)
    return f'''# BioGPU v2.1 — Provisional Wetware Stack

## Selected path

{spec.selected_path}

## Summary

{spec.plain_language_summary}

## Non-protocol boundary

{boundary}

## Ideal component stack

{comp}

## Acceptance criteria

{acc}

## Source anchors used for this design

- Thermo Fisher/Gibco: Neurobasal Plus + B-27 Plus neuronal culture system for primary rodent and human stem-cell-derived neurons.
- STEMCELL Technologies: BrainPhys neuronal medium for long-term primary and hPSC-derived neurons and functional assays.
- Axion BioSystems: MEA neural co-culture protocol references MEA plate preparation and coating classes such as PEI/laminin, PDL and fibronectin.
- Multi Channel Systems: neuronal cell culture MEA application notes include complete vendor protocols and PDL/laminin-style coating workflows.
'''


def write_wetware_outputs_v21(out_dir: str | Path) -> dict:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    spec = build_provisional_wetware_stack_v21()
    (out / 'v21_provisional_wetware_stack.json').write_text(json.dumps(spec.to_dict(), indent=2, ensure_ascii=False), encoding='utf-8')
    (out / 'BIOGPU_V21_PROVISIONAL_WETWARE_STACK.md').write_text(render_wetware_markdown(spec), encoding='utf-8')
    return {'version': spec.version, 'selected_path': spec.selected_path, 'components': len(spec.components), 'acceptance_criteria': len(spec.acceptance_criteria)}
