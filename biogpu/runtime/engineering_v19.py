from __future__ import annotations

import csv, json, shutil
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal

import numpy as np

from biogpu.runtime.contracts import BioGPUJob, BioGPUObjective, BioGPUResult, BioGPUTrace, build_biogpu_claim_ladder
from biogpu.runtime.replay_runtime import RealDataReplayBioGPUSubstrate

Readiness = Literal['ready_for_design','requires_lab','future']

@dataclass(frozen=True)
class BioGPUMaterialSpec:
    prototype: str
    biological_material: str
    interface_material: str
    natural_or_artificial: str
    live_appearance: str
    why_use_it: list[str]
    main_risks: list[str]
    readiness: Readiness
    def to_dict(self): return asdict(self)

@dataclass(frozen=True)
class BioGPUHardwareLayer:
    name: str
    role: str
    first_prototype_choice: str
    later_upgrade: str
    must_measure: list[str] = field(default_factory=list)
    def to_dict(self): return asdict(self)

@dataclass(frozen=True)
class BioGPUBenchmarkTask:
    task_id: str
    title: str
    purpose: str
    input_encoding: str
    substrate_signal: str
    readout_target: str
    replay_status: str
    live_hardware_status: str
    success_metric: str
    gpu_comparison_note: str
    def to_dict(self): return asdict(self)

@dataclass(frozen=True)
class BioGPUPrototypePlan:
    version: str
    target_object: str
    main_goal: str
    selected_first_material: str
    architecture_flow: list[str]
    material_plan: list[BioGPUMaterialSpec]
    hardware_layers: list[BioGPUHardwareLayer]
    benchmark_tasks: list[BioGPUBenchmarkTask]
    current_evidence: list[str]
    not_yet_proven: list[str]
    power_pc_backlog: list[str]
    lab_backlog: list[str]
    def to_dict(self):
        d=asdict(self)
        d['material_plan']=[x.to_dict() for x in self.material_plan]
        d['hardware_layers']=[x.to_dict() for x in self.hardware_layers]
        d['benchmark_tasks']=[x.to_dict() for x in self.benchmark_tasks]
        return d

@dataclass(frozen=True)
class ClosedLoopDemoStep:
    step_index: int
    job_id: str
    requested_target: int|None
    replayed_target: int|None
    culture: str|None
    recording: str|None
    feature_l2_norm: float
    feature_nonzero_fraction: float
    decision: str
    def to_dict(self): return asdict(self)

def build_material_plan_v19():
    return [
        BioGPUMaterialSpec(
            prototype='Prototype A — first real BioGPU material',
            biological_material='2D dissociated cortical neurons or human iPSC-derived neurons grown as a living network.',
            interface_material='Glass/silicon MEA or HD-MEA chip with extracellular stimulation and recording electrodes.',
            natural_or_artificial='Natural living cells on an engineered chip/chamber/protocol; hybrid living-electronic substrate.',
            live_appearance='Small transparent cartridge/dish with pink-clear culture medium; dark/gold electrode grid on the bottom; under microscope, branching neurons and neurites.',
            why_use_it=['most controllable first material','directly compatible with MEA/HD-MEA stimulation/readout','closest to the Zenodo MEA evidence already used','lower complexity than 3D organoids'],
            main_risks=['culture variability','contamination','limited lifetime without environmental control','ethics/sourcing if human cells are used'],
            readiness='ready_for_design'),
        BioGPUMaterialSpec(
            prototype='Prototype B — organoid/neurosphere BioGPU',
            biological_material='3D neurosphere / brain organoid in vitro.',
            interface_material='MEA/HD-MEA plus microfluidic chamber and stronger environmental control.',
            natural_or_artificial='Living lab-grown self-organizing neural aggregate; not a brain, but a biological tissue-like reservoir.',
            live_appearance='Tiny pale spherical tissue in fluid over/near electrodes.',
            why_use_it=['richer 3D dynamics','possible longer temporal memory','closer to organoid intelligence platforms'],
            main_risks=['harder electrode coupling','harder reproducibility','more complex ethics and maintenance'],
            readiness='requires_lab'),
        BioGPUMaterialSpec(
            prototype='Prototype C — patterned engineered neural network',
            biological_material='Engineered neuronal co-culture with support cells and designed topology.',
            interface_material='Patterned HD-MEA, microfluidics, optional optical stimulation/readout.',
            natural_or_artificial='Living cells with intentionally engineered network geometry.',
            live_appearance='Patterned living network aligned into lanes/islands/modules over electrode zones.',
            why_use_it=['more repeatable topology','designed input/output zones','route to modular scaling'],
            main_risks=['requires advanced biofabrication','may need custom chips','future stage'],
            readiness='future')]

def build_hardware_layers_v19():
    return [
        BioGPUHardwareLayer('Living substrate cartridge','holds the biological computing material','2D neuronal culture on MEA/HD-MEA dish/cartridge','3D organoid or patterned engineered culture',['viability','spontaneous firing','response stability','lifetime']),
        BioGPUHardwareLayer('MEA/HD-MEA interface','bidirectional stimulation/readout','commercial MEA/HD-MEA with vendor SDK','higher-density lower-latency array',['channel count','sampling rate','stim timing precision','noise floor','TTL sync']),
        BioGPUHardwareLayer('Environmental control','keeps tissue alive and stable','stage-top incubator or sealed cartridge','microfluidic perfusion and optical monitoring',['temperature','medium state','pH/CO2 proxy','contamination status']),
        BioGPUHardwareLayer('Real-time controller','runs encoder, scheduler, acquisition and readout','Linux workstation with Python SDK','FPGA/RT controller for low latency',['loop latency','jitter','clock drift','energy']),
        BioGPUHardwareLayer('BioGPU software core','hardware-neutral runtime and benchmark harness','current Python BioGPU-Core','production runtime with vendor backends and dashboard',['reproducibility','data integrity','audit logs'])]

def build_benchmark_registry_v19():
    return [
        BioGPUBenchmarkTask('B0_target_vs_random_electrode','Target response separability','verify stimulated target differs from non-target','target electrode pulse','pulse-aligned spike vector','true_target vs random_non_target','implemented from Zenodo v1.5-v1.7','requires live adapter','ROC AUC above shuffled baseline','biological signal validation, not GPU advantage'),
        BioGPUBenchmarkTask('B1_spot_localization','Stimulus spot localization','decode stimulated electrode/region','one-hot/spatial electrode pattern','electrode response vector','spot_id/top-k region','exploratory; limited by labels','needs balanced live protocol','top-k accuracy above label shuffle','I/O calibration task'),
        BioGPUBenchmarkTask('B2_temporal_pattern_classification','Temporal pattern classification','test reservoir memory and time encoding','interval/burst pulse trains','time-binned spike counts/latencies','pattern class','needs NWB/DANDI or live protocol','core first live benchmark','accuracy/AUC above silicon reservoir baseline','candidate sample-efficiency task'),
        BioGPUBenchmarkTask('B3_orientation_like_encoding','Orientation-like task','map visual/orientation classes to stimulation','orientation class to spatiotemporal pattern','reservoir state','orientation class','prepare with Allen adapter','requires repeated live stimulation','accuracy vs GPU/CPU/synthetic reservoirs','first fair task benchmark if energy measured'),
        BioGPUBenchmarkTask('B4_adaptive_closed_loop','Adaptive closed-loop task','test feedback-driven adaptation','state/reward to stimulation','online neural response','action/policy/next-state','scaffold only','requires live hardware and protocol','learning curve and energy per improvement','long-term BioGPU advantage task')]

def build_prototype_plan_v19():
    return BioGPUPrototypePlan(
        version='v1.9',
        target_object='Real working BioGPU prototype: living neural substrate + MEA/HD-MEA + runtime + benchmarks.',
        main_goal=BioGPUObjective().mission,
        selected_first_material='Prototype A: 2D lab-grown neuronal culture on MEA/HD-MEA.',
        architecture_flow=['digital task input','BioGPU encoder maps input to safe stimulation pattern','MEA/HD-MEA stimulates living neural substrate','living neuronal network acts as nonlinear adaptive reservoir','MEA/HD-MEA records spikes/electrical responses','feature extractor builds BioGPUTrace','readout decodes BioGPUResult','benchmark compares against shuffles, CPU/GPU, neuromorphic and synthetic reservoirs'],
        material_plan=build_material_plan_v19(), hardware_layers=build_hardware_layers_v19(), benchmark_tasks=build_benchmark_registry_v19(),
        current_evidence=['11,547 Zenodo pulse windows','target responses beat random-electrode and random-time controls','culture-aware target-vs-random readout around 0.90 ROC AUC in local runs','v1.8 runtime contracts and real-data replay substrate'],
        not_yet_proven=['live MEA/HD-MEA operation','closed-loop biological adaptation','energy/task advantage over GPU/CPU','general task advantage beyond target-response separability'],
        power_pc_backlog=['1000 label shuffles, 10-20 negative seeds, bootstrap confidence intervals','DANDI/NWB task-aligned datasets','Allen orientation-style replay benchmarks','final paper-grade figures and tables'],
        lab_backlog=['select MEA/HD-MEA vendor and SDK','approved neuronal material source and biosafety/ethics protocol','vendor backend behind LiveMEASubstrateAdapter','measure latency, repeatability, biological stability and true energy','balanced live benchmark protocols with full controls'])

def _safe_json(obj): return json.dumps(obj, indent=2, ensure_ascii=False)

class BioGPUClosedLoopReplayRunner:
    def __init__(self, substrate, seed:int=19):
        self.substrate=substrate; self.rng=np.random.default_rng(int(seed))
    def run_demo(self, steps:int=8):
        targets=self.substrate.available_targets(); rows=[]
        if not targets: return rows
        target=int(self.rng.choice(targets))
        for i in range(int(steps)):
            job=BioGPUJob(job_id=f'v19_closed_loop_replay_{i:03d}', task='closed_loop_replay_probe', input_payload={'target_electrode':target}, encoding='v19_target_probe_encoder', substrate='RealDataReplayBioGPUSubstrate', readout='v19_demo_l2_norm_decision', safety_class='offline_public_data_replay_only', metadata={'closed_loop_demo':True})
            result:BioGPUResult=self.substrate.run_job(job); trace=result.trace
            l2=float(result.metrics.get('feature_l2_norm',0.0)); nz=float(result.metrics.get('feature_nonzero_fraction',0.0))
            decision='keep_or_refine_neighborhood' if (l2>0.0 and nz>0.05) else 'switch_target'
            rows.append(ClosedLoopDemoStep(i,job.job_id,target,trace.target_electrode,trace.culture,trace.recording,l2,nz,decision))
            target=int(self.rng.choice(targets))
        return rows

def render_v19_report(plan, health, rows):
    mats='\n'.join(f'- **{m.prototype}** — {m.readiness}: {m.biological_material}' for m in plan.material_plan)
    tasks='\n'.join(f'- **{t.task_id}** — {t.title}: {t.success_metric}' for t in plan.benchmark_tasks)
    ladder='\n'.join(f'- **{s.stage}** — {s.status}: {s.claim}' for s in build_biogpu_claim_ladder())
    return f'''# BioGPU-Core v1.9 — Engineering Blueprint

## Main goal

{plan.main_goal}

v1.9 locks the project direction: BioGPU-Core is an engineering path toward a real biological computing accelerator, not only a MEA analysis toolkit.

## Real material

Selected first material:

```text
{plan.selected_first_material}
```

Live form: a small cartridge/dish with a living 2D neuronal culture on a MEA/HD-MEA chip. Neurons are real biological cells; chip, chamber, medium control, stimulation schedule and runtime are engineered.

## Architecture

```text
{chr(10).join('-> '+x for x in plan.architecture_flow)}
```

## Material ladder

{mats}

## Hardware layers

{chr(10).join(f'- **{h.name}**: {h.first_prototype_choice}' for h in plan.hardware_layers)}

## Benchmark tasks

{tasks}

## Replay substrate health

```json
{_safe_json(health)}
```

## Closed-loop scaffold

v1.9 ran `{len(rows)}` offline replay loop steps. This does not prove live adaptation; it proves the loop shape exists and can be redirected to a live MEA backend.

## Claim ladder

{ladder}

## Power-PC backlog

{chr(10).join('- '+x for x in plan.power_pc_backlog)}

## Lab backlog

{chr(10).join('- '+x for x in plan.lab_backlog)}
'''

def write_v19_engineering_outputs(v15_out_dir, out_dir, image_path=None, closed_loop_steps:int=8, seed:int=19):
    out=Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    plan=build_prototype_plan_v19(); substrate=RealDataReplayBioGPUSubstrate(v15_out_dir, seed=seed); health=substrate.health_check()
    rows=BioGPUClosedLoopReplayRunner(substrate, seed=seed).run_demo(closed_loop_steps)
    summary={'version':'v1.9','title':'BioGPU engineering blueprint + live-substrate direction','main_goal':plan.main_goal,'selected_first_material':plan.selected_first_material,'replay_substrate_health':health,'closed_loop_demo_steps':len(rows),'power_pc_backlog':plan.power_pc_backlog,'lab_backlog':plan.lab_backlog,'safe_boundary':['No biological stimulation safety limits are defined here.','Live stimulation requires vendor documentation, lab protocol and biosafety/ethics approval.','GPU advantage is not claimed until measured on a live device.']}
    (out/'v19_biogpu_prototype_plan.json').write_text(_safe_json(plan.to_dict()), encoding='utf-8')
    (out/'v19_biogpu_engineering_summary.json').write_text(_safe_json(summary), encoding='utf-8')
    (out/'v19_material_plan.json').write_text(_safe_json([m.to_dict() for m in plan.material_plan]), encoding='utf-8')
    (out/'v19_benchmark_registry.json').write_text(_safe_json([t.to_dict() for t in plan.benchmark_tasks]), encoding='utf-8')
    (out/'v19_closed_loop_replay_demo.json').write_text(_safe_json([r.to_dict() for r in rows]), encoding='utf-8')
    with (out/'v19_closed_loop_replay_demo.csv').open('w', encoding='utf-8', newline='') as f:
        w=csv.DictWriter(f, fieldnames=list(ClosedLoopDemoStep(0,'',None,None,None,None,0,0,'').to_dict().keys())); w.writeheader(); [w.writerow(r.to_dict()) for r in rows]
    (out/'BIOGPU_V19_ENGINEERING_REPORT.md').write_text(render_v19_report(plan, health, rows), encoding='utf-8')
    
    if image_path and Path(image_path).exists():
        src = Path(image_path).resolve()
        dst = (out/'biogpu_material_visualization.png').resolve()
        if src != dst:
            shutil.copy2(src, dst)
    return summary
