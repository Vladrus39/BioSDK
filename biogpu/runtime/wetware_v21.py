from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Literal

Stage = Literal['ideal_v1','vendor_sop_required','lab_validation_required','future']

@dataclass(frozen=True)
class WetwareComponent:
    layer: str
    component: str
    ideal_choice: str
    role: str
    repeatability_reason: str
    may_change_if: list[str] = field(default_factory=list)
    stage: Stage = 'ideal_v1'
    def to_dict(self): return asdict(self)

@dataclass(frozen=True)
class GeometrySpec:
    name: str
    ideal_value: str
    reason: str
    formula_or_rule: str
    may_change_if: list[str] = field(default_factory=list)
    stage: Stage = 'ideal_v1'
    def to_dict(self): return asdict(self)

@dataclass(frozen=True)
class ConnectionSpec:
    order: int
    from_block: str
    to_block: str
    physical_or_logical_link: str
    signal: str
    exact_detail_status: str
    notes: str
    def to_dict(self): return asdict(self)

@dataclass(frozen=True)
class FormulaSpec:
    formula_id: str
    title: str
    formula: str
    variables: dict[str, str]
    use_in_project: str
    safety_note: str = ''
    def to_dict(self): return asdict(self)

@dataclass(frozen=True)
class IdealBioGPUWetwareStack:
    version: str
    title: str
    intended_physical_object: str
    core_material_statement: str
    components: list[WetwareComponent]
    geometry: list[GeometrySpec]
    connections: list[ConnectionSpec]
    formulas: list[FormulaSpec]
    change_rules: list[str]
    boundary_note: str
    def to_dict(self):
        d = asdict(self)
        d['components'] = [x.to_dict() for x in self.components]
        d['geometry'] = [x.to_dict() for x in self.geometry]
        d['connections'] = [x.to_dict() for x in self.connections]
        d['formulas'] = [x.to_dict() for x in self.formulas]
        return d


def build_v21_components() -> list[WetwareComponent]:
    return [
        WetwareComponent('biological_cells','Primary choice: human iPSC-derived mixed cortical-like neurons','Commercial or lab-derived excitatory/inhibitory neuronal population with optional glial support','Living nonlinear adaptive reservoir','More repeatable and ethically cleaner than ad-hoc animal primary cultures when sourced through standard providers',['supplier availability','lab preference for rodent primary neurons','ethics approval route','maturation speed requirements']),
        WetwareComponent('biological_support','Astrocyte or astrocyte-conditioned support layer/co-culture','Low-fraction supportive glial component or validated commercial support protocol','Improve viability, synapse formation and network stability','Mixed neural cultures often provide more stable long-term activity than neuron-only cultures',['chosen cell line already includes support cells','lab SOP forbids co-culture','MEA optical clarity requirements']),
        WetwareComponent('surface_adhesion','Poly-D-lysine or PEI base layer + laminin/fibronectin extracellular matrix class','Vendor/SOP-selected cationic adhesion layer plus ECM cue','Make neurons attach, extend neurites and couple to electrodes','This is a standard conceptual stack for neuronal adhesion on glass/MEA surfaces',['MEA manufacturer requires different coating','cell supplier provides optimized coating','electrode impedance changes too much'],'vendor_sop_required'),
        WetwareComponent('basal_medium','BrainPhys or Neurobasal Plus class neuronal basal medium','BrainPhys for activity-preserving electrophysiology; Neurobasal Plus + B-27 Plus for robust survival/maturation route','Keep neurons alive and electrophysiologically active','Both are real commercial neuronal media classes used for hPSC/primary neuronal culture workflows',['cell supplier recommends specific medium','network activity is unstable','long-term survival beats electrophysiological activity in priority'],'vendor_sop_required'),
        WetwareComponent('supplements','B-27 Plus / N2 / SM1-like supplement class depending on basal medium','Serum-free neuronal supplement package chosen by supplier/SOP','Provide nutrients, antioxidants and support factors','Repeatability comes from commercial matched media systems rather than hand-mixed unknown recipes',['basal medium choice changes','cell type changes','supplier protocol specifies alternate supplement'],'vendor_sop_required'),
        WetwareComponent('interface_chip','HD-MEA preferred; 60-channel MEA acceptable for first low-cost prototype','MEA/HD-MEA with extracellular recording and stimulation and vendor SDK','Electrical input/output to living network','Same software contract can work on 60-electrode data now and HD-MEA later',['budget','availability','vendor API access','channel count needed']),
        WetwareComponent('environment','Sealed cartridge or stage-top incubated chamber','37 C class thermal control, controlled gas/humidity/medium stability via lab hardware','Keep substrate stable for repeatable compute sessions','Without stable environment, BioGPU results cannot be compared to GPU baselines',['room-temperature recording platform','short acute tests only','vendor cartridge has built-in environment'],'lab_validation_required'),
    ]


def build_v21_geometry() -> list[GeometrySpec]:
    return [
        GeometrySpec(
            'reference_device_envelope',
            'BioGPU-A1 engineering target: 90 mm x 90 mm x 25 mm external dry electronics/cartridge envelope, excluding host PC and incubator shell',
            'A compact module size keeps the first prototype bench-top and microscope-stage compatible while leaving room for cables and shielding.',
            'Envelope = cartridge_holder + headstage_clearance + cable_bend_radius',
            ['selected vendor holder is larger','environmental shell is integrated','shielding/noise tests require larger enclosure']
        ),
        GeometrySpec(
            'cartridge_outer_form',
            'Target replaceable wet cartridge/dish class: <= 60 mm x 60 mm x 15 mm; exact footprint from MEA vendor',
            'This separates the replaceable biological cartridge from reusable acquisition/stimulation electronics.',
            'Cartridge footprint = vendor MEA substrate + chamber wall + gasket/seal margin',
            ['chosen vendor cartridge dimensions','open dish instead of sealed cartridge','microfluidic module added']
        ),
        GeometrySpec(
            'active_electrode_area',
            'Nominal design target: 4 mm x 4 mm active neural/electrode field = 16 mm^2; bridge prototype may use vendor 60-electrode active area',
            'A few-mm active field is large enough for local network dynamics but small enough for controlled stimulation/readout.',
            'A_active = active_width_mm * active_height_mm',
            ['HD-MEA layout','60-electrode ring/grid layout','desired spatial coverage']
        ),
        GeometrySpec(
            'electrode_count',
            'Bridge: 59-60 recording channels for Zenodo continuity; target BioGPU-A1: >=1024 addressable channels; stretch: 4096+ channels',
            'v1.x evidence used 59 electrodes, but a real accelerator needs denser I/O for spatial encoding and parallel readout.',
            'N_channels = N_recording + N_stim + N_reference as vendor defines',
            ['budget','SDK access','task complexity','live stimulation capability']
        ),
        GeometrySpec(
            'electrode_pitch',
            'Nominal HD-MEA target: 50 um pitch class; acceptable planning range 20-200 um depending on vendor chip',
            'Pitch controls how finely BioGPU can address and read local network regions.',
            'pitch_um = active_width_um / (N_x - 1) for square-grid approximation',
            ['vendor MEA design','desired spatial resolution','electrode impedance/noise']
        ),
        GeometrySpec(
            'electrode_geometry',
            'Nominal planning variable: electrode diameter/side length 10-30 um for HD-MEA class; use vendor exact electrode area for charge-density audit',
            'Charge-density and coupling calculations require actual electrode area, not guesswork.',
            'A_electrode = vendor_defined_effective_area',
            ['vendor material','electrode coating','stimulation mode'],
            'vendor_sop_required'
        ),
        GeometrySpec(
            'medium_volume',
            'Engineering target variable: chamber liquid volume in the 0.05-2 mL cartridge class; exact volume from chamber geometry/vendor SOP',
            'Volume affects thermal stability, diffusion and session duration. It is a hardware design value, not a culture recipe.',
            'V_medium = A_chamber * h_medium + reservoir_volume',
            ['chamber height','perfusion design','sealed vs open dish','long-duration session needs'],
            'lab_validation_required'
        ),
        GeometrySpec(
            'cell_planning_density',
            'Planning only: connected network over active field; use N_cells = rho_cells * A_growth with rho_cells from supplier/lab SOP',
            'Too sparse gives no network; too dense may detach or over-synchronize. The project tracks the variable but does not invent a universal density.',
            'N_cells_planned = rho_cells * A_growth_surface',
            ['cell line','coating','MEA surface','target maturity'],
            'vendor_sop_required'
        ),
        GeometrySpec(
            'recording_sampling',
            'Nominal extracellular recording target: 20 kHz sampling rate class; acceptable range from vendor hardware, commonly 10-25+ kHz for spikes',
            'Spike timing and feature extraction need a fixed sampling contract.',
            'N_samples = f_s * T_window',
            ['vendor hardware','spike sorting method','storage bandwidth']
        ),
        GeometrySpec(
            'bio_response_window',
            'Initial benchmark target: pre-window 0.5 s, post-window 0.5 s, exact-window tied to stimulus event duration; final timing selected per task',
            'Keeps the live benchmark compatible with the pulse-aligned replay logic already built in v1.3-v1.7.',
            'T_window_total = T_pre + T_exact + T_post',
            ['task requires fast latency','network response is delayed','vendor stimulus timestamps differ']
        ),
        GeometrySpec(
            'environment_telemetry',
            'Log temperature/gas/humidity/medium-state variables as session metadata; target stable cell-culture environment, exact setpoints from lab SOP',
            'BioGPU cannot claim reproducible compute without environmental metadata.',
            'SessionMetadata = {T_env, gas_state, humidity_state, medium_state, time_since_medium_change}',
            ['sealed cartridge','perfusion system','short recording-only sessions'],
            'lab_validation_required'
        ),
    ]

def build_v21_connections() -> list[ConnectionSpec]:
    return [
        ConnectionSpec(1,'Host PC / BioGPU runtime','Vendor control SDK','USB/Ethernet/PCIe depending on platform','digital commands and recording stream','vendor-specific','Exact port, driver and API belong to vendor backend.'),
        ConnectionSpec(2,'Vendor control SDK','Stimulator/amplifier headstage','vendor internal control bus','stimulation command + acquisition config','vendor-specific','BioGPU stores only abstract command contract until hardware selected.'),
        ConnectionSpec(3,'Headstage','MEA/HD-MEA cartridge','dock/socket/MEA holder contacts','electrode stimulation and extracellular voltage pickup','vendor-specific','Pinout is not guessed; it must be imported from vendor documentation.'),
        ConnectionSpec(4,'MEA/HD-MEA electrodes','Living neural layer','extracellular bioelectrical coupling','stimulus-induced and spontaneous neural activity','lab-validated','Coupling quality measured by impedance/noise/spike yield, not assumed.'),
        ConnectionSpec(5,'Environmental shell','Cartridge chamber','thermal/gas/medium control lines','environment telemetry','lab-validated','Temperature, gas and medium monitoring become part of BioGPU session metadata.'),
        ConnectionSpec(6,'Acquisition stream','BioGPUTrace builder','file/stream/API callback','timestamps, channel IDs, voltage/spikes/events','software-defined','This is implementable now and vendor-neutral.'),
        ConnectionSpec(7,'BioGPUTrace','Readout / benchmark harness','Python object / npz / csv','feature vector and labels','software-defined','This is already the route used by replay substrate.'),
    ]


def build_v21_formulas() -> list[FormulaSpec]:
    return [
        FormulaSpec('F01_active_area','Active electrode area','A_active = W_active * H_active',{'A_active':'active electrode field area','W_active':'active field width','H_active':'active field height'},'Geometry planning and normalizing cell/electrode density.'),
        FormulaSpec('F02_cell_planning','Cell number planning','N_cells = rho_cells * A_growth',{'N_cells':'planned cell count','rho_cells':'cell density specified by validated SOP','A_growth':'growth surface area'},'Tracks the needed design variable without inventing a universal biological recipe.','rho_cells must be chosen from cell supplier/lab SOP.'),
        FormulaSpec('F03_electrode_pitch','Approximate square-grid pitch','pitch = W_active / (N_x - 1)',{'pitch':'center-to-center electrode spacing','W_active':'active field width','N_x':'number of electrode columns'},'Converts vendor layout into model geometry.'),
        FormulaSpec('F04_sampling','Samples in analysis window','N_samples = f_s * T_window',{'N_samples':'sample count','f_s':'sampling rate','T_window':'window duration'},'Defines acquisition window size for live and replay BioGPUTrace.'),
        FormulaSpec('F05_spike_rate','Spike rate per channel','r_i = N_spikes_i / Delta_t',{'r_i':'spike rate on electrode i','N_spikes_i':'spike count on electrode i','Delta_t':'time window length'},'Core biological response feature.'),
        FormulaSpec('F06_response_delta','Stimulus response delta','Delta r_i = r_i_post - r_i_pre',{'Delta r_i':'evoked change on electrode i','r_i_post':'post-stimulus rate','r_i_pre':'pre-stimulus baseline rate'},'Same real-data signal used in v1.3-v1.7.'),
        FormulaSpec('F07_charge','Stimulus charge bookkeeping','Q = I * t_pulse',{'Q':'charge','I':'stimulation current','t_pulse':'pulse duration'},'Only for audit fields; actual limits come from vendor/lab safety rules.','Do not use without vendor-approved live stimulation limits.'),
        FormulaSpec('F08_charge_density','Electrode charge density','sigma_Q = Q / A_electrode',{'sigma_Q':'charge per electrode area','Q':'charge','A_electrode':'electrode surface area'},'Safety audit placeholder for future live backend.','Maximum safe value is vendor/lab-defined, not guessed here.'),
        FormulaSpec('F09_energy_task','Energy per task','E_task = integral(P_total(t) dt) / N_tasks',{'E_task':'energy per inference/task','P_total':'measured total power','N_tasks':'completed tasks'},'Needed before any BioGPU vs GPU claim.'),
        FormulaSpec('F10_loop_latency','Closed-loop latency','T_loop = T_encode + T_stim + T_bio + T_acq + T_decode',{'T_loop':'end-to-end BioGPU cycle time','T_bio':'biological response interval'},'Compares real-time feasibility across replay/live substrates.'),
        FormulaSpec('F11_readout_auc','Separability metric','AUC = P(score_positive > score_negative)',{'AUC':'ROC area under curve','score_positive':'readout score for true target','score_negative':'score for control'},'Main current separability score.'),
    ]


def build_ideal_wetware_stack_v21() -> IdealBioGPUWetwareStack:
    return IdealBioGPUWetwareStack(
        version='v2.1',
        title='Ideal repeatable BioGPU wetware/electronics reference design — non-operational SOP draft',
        intended_physical_object='A sealed or stage-top MEA/HD-MEA living-neural cartridge connected to acquisition/stimulation electronics and the BioGPU runtime.',
        core_material_statement='The first real BioGPU should use real living neurons: preferably a 2D mixed cortical-like network from human iPSC-derived neurons, supported by validated adhesion/ECM coating and neuronal medium. The electronics and software are engineered; the computing substrate is biological.',
        components=build_v21_components(),
        geometry=build_v21_geometry(),
        connections=build_v21_connections(),
        formulas=build_v21_formulas(),
        change_rules=[
            'If a specific cell supplier provides a protocol, supplier SOP overrides this provisional stack.',
            'If a specific MEA/HD-MEA vendor is selected, vendor geometry, pinout, SDK and safety limits override all placeholders.',
            'If spontaneous activity is weak, change cell type/support/coating/medium before changing BioGPU readout claims.',
            'If activity is unstable or over-synchronized, treat it as substrate instability, not as a software bug.',
            'If energy advantage is claimed, measure wall power and device power separately and include incubator/environment overhead.',
        ],
        boundary_note='This file is an engineering design specification, not a wet-lab operating protocol. Exact concentrations, timings, seeding density, incubation procedure and live stimulation limits must be supplied by qualified SOPs and vendor manuals.'
    )


def render_wetware_stack_markdown(stack: IdealBioGPUWetwareStack) -> str:
    comps = '\n'.join(f"| {c.layer} | {c.component} | {c.ideal_choice} | {c.stage} |" for c in stack.components)
    geos = '\n'.join(f"| {g.name} | {g.ideal_value} | {g.formula_or_rule} |" for g in stack.geometry)
    conns = '\n'.join(f"| {c.order} | {c.from_block} | {c.to_block} | {c.physical_or_logical_link} | {c.exact_detail_status} |" for c in stack.connections)
    forms = '\n'.join(f"### {f.formula_id} — {f.title}\n\n```text\n{f.formula}\n```\n\nUse: {f.use_in_project}\n\nSafety/limit note: {f.safety_note or 'standard engineering formula'}\n" for f in stack.formulas)
    changes = '\n'.join('- ' + x for x in stack.change_rules)
    return f'''# {stack.title}

## What this is

{stack.core_material_statement}

**Intended physical object:** {stack.intended_physical_object}

## Boundary

{stack.boundary_note}

## Provisional ideal wetware/electronics stack

| Layer | Component | Ideal choice | Status |
|---|---|---|---|
{comps}

## Dimensions and geometry variables

| Name | Ideal value / planning target | Formula or rule |
|---|---|---|
{geos}

## Connection map

| # | From | To | Link | Detail status |
|---:|---|---|---|---|
{conns}

## Formula book

{forms}

## What may change and why

{changes}

## Bottom line

This is the current ideal working reference design for BioGPU. It is meant to be repeatable after selecting a concrete cell supplier, MEA/HD-MEA vendor, lab SOP and hardware SDK. Those concrete choices replace the provisional values above.
'''


def write_v21_outputs(out_dir: str | Path) -> dict:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    stack = build_ideal_wetware_stack_v21()
    (out/'v21_ideal_wetware_stack.json').write_text(json.dumps(stack.to_dict(), indent=2, ensure_ascii=False), encoding='utf-8')
    (out/'BIOGPU_V21_IDEAL_WETWARE_STACK.md').write_text(render_wetware_stack_markdown(stack), encoding='utf-8')
    summary = {
        'version': stack.version,
        'title': stack.title,
        'components': len(stack.components),
        'geometry_specs': len(stack.geometry),
        'connections': len(stack.connections),
        'formulas': len(stack.formulas),
        'boundary_note': stack.boundary_note,
    }
    (out/'v21_summary.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding='utf-8')
    return summary
