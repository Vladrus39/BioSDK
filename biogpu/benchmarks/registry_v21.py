from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Literal

Stage = Literal['software_now', 'power_pc', 'live_lab', 'future']


@dataclass(frozen=True)
class BioGPUBenchmarkSpec:
    benchmark_id: str
    title: str
    substrate_modes: list[str]
    input_contract: str
    output_contract: str
    primary_metrics: list[str]
    baselines: list[str]
    success_criteria: list[str]
    stage: Stage
    heavy_compute: bool = False
    live_required: bool = False
    notes: str = ''

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class BioGPUBenchmarkRegistry:
    version: str
    benchmarks: list[BioGPUBenchmarkSpec]
    claim_boundary: str

    def to_dict(self) -> dict:
        return {
            'version': self.version,
            'benchmarks': [b.to_dict() for b in self.benchmarks],
            'claim_boundary': self.claim_boundary,
        }


def build_v21_benchmark_registry() -> BioGPUBenchmarkRegistry:
    """Benchmark registry for the BioGPU-A1 design path.

    This registry makes the project testable without hiding the distinction
    between replay, power-PC and future live-lab modes.
    """
    benchmarks = [
        BioGPUBenchmarkSpec(
            benchmark_id='B0_target_vs_random_electrode',
            title='Target electrode response vs random non-target electrode',
            substrate_modes=['replay_local', 'power_pc_full', 'live_mea_vendor'],
            input_contract='Pulse-aligned BioGPUTrace with target electrode metadata.',
            output_contract='Candidate-pair table: target/non-target label + readout score.',
            primary_metrics=['ROC_AUC', 'balanced_accuracy', 'shuffle_p_value', 'culture_held_out_score'],
            baselines=['label_shuffle', 'random_electrode', 'pulse_context_only_negative_control'],
            success_criteria=['AUC above shuffled baseline', 'effect persists across cultures', 'negative controls near chance'],
            stage='software_now',
            heavy_compute=False,
            live_required=False,
            notes='Already supported by v1.5-v1.7 replay data; first live BioGPU gate.'
        ),
        BioGPUBenchmarkSpec(
            benchmark_id='B1_spot_localization',
            title='Stimulated spot / channel localization',
            substrate_modes=['power_pc_full', 'live_mea_vendor'],
            input_contract='BioGPUTrace windows with repeated stimulation at known spatial targets.',
            output_contract='Predicted target class, top-k target list, confidence scores.',
            primary_metrics=['top1_accuracy', 'top3_accuracy', 'balanced_accuracy', 'seen_label_accuracy'],
            baselines=['chance_by_class_count', 'label_shuffle', 'nearest_electrode_heuristic'],
            success_criteria=['top-k above chance', 'held-out culture/session performance above shuffle', 'class imbalance reported'],
            stage='power_pc',
            heavy_compute=True,
            live_required=False,
            notes='v1.5 showed this is too hard on sparse public data; needs more repeats/HD-MEA or stronger features.'
        ),
        BioGPUBenchmarkSpec(
            benchmark_id='B2_temporal_pattern_classification',
            title='Temporal stimulation pattern classification',
            substrate_modes=['replay_local', 'power_pc_full', 'live_mea_vendor'],
            input_contract='Encoded temporal pulse pattern or replayed temporal labels.',
            output_contract='Predicted temporal pattern class and response-state vector.',
            primary_metrics=['accuracy', 'balanced_accuracy', 'mutual_information', 'latency'],
            baselines=['random_reservoir', 'time_shuffle', 'label_shuffle'],
            success_criteria=['above shuffled time/control baselines', 'repeatable across sessions', 'latency logged'],
            stage='power_pc',
            heavy_compute=True,
            live_required=False,
            notes='Bridge to reservoir-computing tasks beyond single target-electrode response.'
        ),
        BioGPUBenchmarkSpec(
            benchmark_id='B3_orientation_like_task',
            title='Orientation-like spatial/temporal encoding task',
            substrate_modes=['power_pc_full', 'live_mea_vendor'],
            input_contract='Stimulus code representing angle/frequency classes mapped to electrode patterns.',
            output_contract='Predicted orientation/frequency class and confusion matrix.',
            primary_metrics=['accuracy', 'top2_accuracy', 'confusion_by_angle', 'culture_bootstrap_CI'],
            baselines=['CPU_linear_model_on_same_features', 'random_reservoir', 'label_shuffle'],
            success_criteria=['structured confusion by neighboring classes', 'performance above random and shuffled controls'],
            stage='future',
            heavy_compute=True,
            live_required=False,
            notes='Designed to connect public Allen-style orientation benchmarks with future live substrate encoding.'
        ),
        BioGPUBenchmarkSpec(
            benchmark_id='B4_adaptive_closed_loop',
            title='Closed-loop adaptive BioGPU controller',
            substrate_modes=['replay_local', 'live_mea_vendor'],
            input_contract='Task state + previous BioGPUResult + reward/error signal.',
            output_contract='Next stimulation/encoding decision and updated controller state.',
            primary_metrics=['reward_curve', 'adaptation_steps', 'stability_drift', 'loop_latency'],
            baselines=['open_loop_fixed_policy', 'random_policy', 'software_reservoir_policy'],
            success_criteria=['reward improves vs open-loop baseline', 'loop latency measured', 'drift bounded or compensated'],
            stage='future',
            heavy_compute=False,
            live_required=True,
            notes='This is where replay becomes a true live BioGPU controller; requires real hardware.'
        ),
        BioGPUBenchmarkSpec(
            benchmark_id='B5_energy_per_task',
            title='Energy per BioGPU task/inference',
            substrate_modes=['power_pc_full', 'live_mea_vendor'],
            input_contract='Completed benchmark run + wall/electronics/environment power logs.',
            output_contract='Energy accounting table split by host, acquisition electronics, environment and substrate support.',
            primary_metrics=['E_task_total', 'E_task_electronics_only', 'latency', 'accuracy_per_joule'],
            baselines=['CPU_same_readout', 'GPU_same_readout', 'neuromorphic_baseline_where_available'],
            success_criteria=['metering documented', 'accuracy not lower than baseline at same task definition', 'environment overhead disclosed'],
            stage='live_lab',
            heavy_compute=False,
            live_required=True,
            notes='Mandatory before any claim that BioGPU is stronger/more efficient than GPU.'
        ),
    ]
    return BioGPUBenchmarkRegistry(
        version='v2.1',
        benchmarks=benchmarks,
        claim_boundary='The registry supports real-data and future live benchmarking, but no GPU-advantage claim is valid until live energy/latency/task baselines are measured.'
    )


def render_registry_markdown(registry: BioGPUBenchmarkRegistry) -> str:
    rows = '\n'.join(
        f"| {b.benchmark_id} | {b.title} | {b.stage} | {', '.join(b.primary_metrics)} | {b.live_required} |"
        for b in registry.benchmarks
    )
    details = '\n\n'.join(
        f"## {b.benchmark_id} — {b.title}\n\n"
        f"**Modes:** {', '.join(b.substrate_modes)}\n\n"
        f"**Input:** {b.input_contract}\n\n"
        f"**Output:** {b.output_contract}\n\n"
        f"**Baselines:** {', '.join(b.baselines)}\n\n"
        f"**Success criteria:**\n" + '\n'.join(f"- {x}" for x in b.success_criteria) +
        f"\n\n**Heavy compute:** {b.heavy_compute}; **Live required:** {b.live_required}\n\n{b.notes}"
        for b in registry.benchmarks
    )
    return f'''# BioGPU v2.1 Benchmark Registry

{registry.claim_boundary}

| ID | Title | Stage | Primary metrics | Live required |
|---|---|---|---|---|
{rows}

{details}
'''


def write_registry_v21(out_dir: str | Path) -> dict:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    reg = build_v21_benchmark_registry()
    (out / 'v21_benchmark_registry.json').write_text(json.dumps(reg.to_dict(), indent=2, ensure_ascii=False), encoding='utf-8')
    (out / 'BIOGPU_V21_BENCHMARK_REGISTRY.md').write_text(render_registry_markdown(reg), encoding='utf-8')
    summary = {
        'version': reg.version,
        'benchmarks': len(reg.benchmarks),
        'live_required_count': sum(1 for b in reg.benchmarks if b.live_required),
        'heavy_compute_count': sum(1 for b in reg.benchmarks if b.heavy_compute),
        'claim_boundary': reg.claim_boundary,
    }
    (out / 'v21_benchmark_registry_summary.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding='utf-8')
    return summary
