from __future__ import annotations
from dataclasses import asdict, dataclass
from typing import Dict, Any, List
from biogpu.metrics.energy_model_v29 import EnergyRunInputV29, PowerComponentV29, estimate_energy_v29
from biogpu.metrics.latency_model_v29 import LatencyComponentsV29, estimate_latency_v29

@dataclass(frozen=True)
class ComputeBaselineV29:
    baseline_id: str
    name: str
    substrate_class: str
    energy_input: EnergyRunInputV29
    latency_components: LatencyComponentsV29
    claim_boundary: str

    def evaluate(self) -> Dict[str, Any]:
        e = estimate_energy_v29(self.energy_input).to_dict()
        l = estimate_latency_v29(self.latency_components).to_dict()
        return {
            "baseline_id": self.baseline_id,
            "name": self.name,
            "substrate_class": self.substrate_class,
            "energy": e,
            "latency": l,
            "claim_boundary": self.claim_boundary,
        }


def build_baseline_catalog_v29(task_count: int = 1000, run_duration_s: float = 60.0) -> List[ComputeBaselineV29]:
    return [
        ComputeBaselineV29(
            baseline_id="cpu_workstation_placeholder",
            name="CPU workstation placeholder",
            substrate_class="silicon_cpu",
            energy_input=EnergyRunInputV29(task_count, run_duration_s, (PowerComponentV29("cpu_workstation", 90.0, "CPU inference/control", "placeholder"),), "Replace with measured CPU wall power."),
            latency_components=LatencyComponentsV29(encode_ms=0.5, substrate_io_ms=0.0, biological_response_ms=0.0, acquisition_ms=0.0, feature_extraction_ms=1.0, readout_ms=1.0, notes="CPU placeholder latency."),
            claim_boundary="Only a placeholder until same task and same measurement protocol are used.",
        ),
        ComputeBaselineV29(
            baseline_id="gpu_workstation_placeholder",
            name="GPU workstation placeholder",
            substrate_class="silicon_gpu",
            energy_input=EnergyRunInputV29(task_count, run_duration_s, (PowerComponentV29("gpu_workstation", 250.0, "GPU inference/control", "placeholder"),), "Replace with measured GPU board/system power."),
            latency_components=LatencyComponentsV29(encode_ms=0.5, substrate_io_ms=0.0, biological_response_ms=0.0, acquisition_ms=0.0, feature_extraction_ms=0.5, readout_ms=0.2, notes="GPU placeholder latency."),
            claim_boundary="GPU comparison requires identical task, batching rules and measurement boundary.",
        ),
        ComputeBaselineV29(
            baseline_id="neuromorphic_placeholder",
            name="Neuromorphic reference placeholder",
            substrate_class="neuromorphic_silicon",
            energy_input=EnergyRunInputV29(task_count, run_duration_s, (PowerComponentV29("neuromorphic_board", 30.0, "spiking/low-power reference", "placeholder"),), "Replace with real board telemetry."),
            latency_components=LatencyComponentsV29(encode_ms=1.0, substrate_io_ms=1.0, biological_response_ms=0.0, acquisition_ms=0.0, feature_extraction_ms=1.0, readout_ms=1.0, notes="Neuromorphic placeholder latency."),
            claim_boundary="Reference only; exact architecture and task mapping must be documented.",
        ),
        ComputeBaselineV29(
            baseline_id="biogpu_a1_replay_placeholder",
            name="BioGPU-A1 replay placeholder",
            substrate_class="biological_replay",
            energy_input=EnergyRunInputV29(task_count, run_duration_s, (PowerComponentV29("host_replay_pc", 65.0, "replay runtime", "placeholder"),), "Replay has no live substrate energy; do not use as live efficiency claim."),
            latency_components=LatencyComponentsV29(encode_ms=1.0, substrate_io_ms=0.0, biological_response_ms=0.0, acquisition_ms=0.0, feature_extraction_ms=2.0, readout_ms=0.5, notes="Replay mode only."),
            claim_boundary="Replay proves software/runtime mechanics, not live BioGPU energy advantage.",
        ),
        ComputeBaselineV29(
            baseline_id="biogpu_a1_live_budget_placeholder",
            name="BioGPU-A1 future live budget placeholder",
            substrate_class="future_live_biological_substrate",
            energy_input=EnergyRunInputV29(task_count, run_duration_s, (
                PowerComponentV29("host_controller_pc", 65.0, "runtime", "placeholder"),
                PowerComponentV29("mea_electronics", 25.0, "MEA I/O", "placeholder"),
                PowerComponentV29("environment_share", 15.0, "incubator/stage share", "placeholder"),
            ), "Future live budget; replace with lab telemetry."),
            latency_components=LatencyComponentsV29(encode_ms=1.0, substrate_io_ms=2.0, biological_response_ms=50.0, acquisition_ms=5.0, feature_extraction_ms=2.0, readout_ms=0.5, controller_update_ms=0.5, notes="Future live budget."),
            claim_boundary="Only becomes evidence after live measurements with the same benchmark registry.",
        ),
    ]


def compare_baselines_v29(task_count: int = 1000, run_duration_s: float = 60.0) -> Dict[str, Any]:
    rows = [b.evaluate() for b in build_baseline_catalog_v29(task_count, run_duration_s)]
    # Use GPU placeholder as denominator for illustrative ratios only.
    gpu = next(r for r in rows if r["baseline_id"] == "gpu_workstation_placeholder")
    gpu_e = gpu["energy"]["joules_per_task"]
    gpu_l = gpu["latency"]["total_ms"]
    for r in rows:
        e = r["energy"]["joules_per_task"]
        l = r["latency"]["total_ms"]
        r["ratios_vs_gpu_placeholder"] = {
            "energy_per_task_ratio": e / gpu_e if gpu_e > 0 else None,
            "latency_ratio": l / gpu_l if gpu_l > 0 else None,
            "lower_is_better": True,
        }
    return {
        "version": "v2.9",
        "task_count": task_count,
        "run_duration_s": run_duration_s,
        "comparison_boundary": "All values are placeholders until measured under the same task, timing, batching and power boundary.",
        "baselines": rows,
    }
