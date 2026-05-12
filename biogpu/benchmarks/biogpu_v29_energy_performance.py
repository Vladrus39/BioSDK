from __future__ import annotations
import argparse, csv, json
from pathlib import Path
from biogpu.metrics.baseline_v29 import compare_baselines_v29


def render_report(result: dict) -> str:
    lines = [
        "# BioGPU v2.9 — Energy / Performance Model",
        "",
        "## Boundary",
        "",
        result["comparison_boundary"],
        "",
        "## Formulae",
        "",
        "```text",
        "P_total = Σ P_component",
        "E_total[J] = P_total[W] * T_run[s]",
        "E_task[J/task] = E_total / N_tasks",
        "T_loop = T_encode + T_io + T_bio + T_acq + T_features + T_readout + T_controller",
        "Throughput_serial = 1000 / T_loop_ms",
        "Energy_ratio_vs_GPU = E_task_candidate / E_task_GPU_placeholder",
        "Latency_ratio_vs_GPU = T_candidate / T_GPU_placeholder",
        "```",
        "",
        "## Baselines",
        "",
        "| ID | Class | J/task | Total latency ms | Energy ratio vs GPU placeholder | Claim boundary |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for b in result["baselines"]:
        lines.append(
            f"| {b['baseline_id']} | {b['substrate_class']} | {b['energy']['joules_per_task']:.6f} | "
            f"{b['latency']['total_ms']:.3f} | {b['ratios_vs_gpu_placeholder']['energy_per_task_ratio']:.3f} | {b['claim_boundary']} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "v2.9 does not claim that BioGPU is already more efficient than GPU. It creates the measurement scaffold. Real advantage can be claimed only after live_lab telemetry, identical benchmark tasks, and documented system boundaries.",
    ])
    return "\n".join(lines)


def write_outputs(out_dir: str | Path, task_count: int, run_duration_s: float) -> dict:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    result = compare_baselines_v29(task_count=task_count, run_duration_s=run_duration_s)
    (out / "v29_energy_performance_comparison.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    (out / "BIOGPU_V29_ENERGY_PERFORMANCE_REPORT.md").write_text(render_report(result), encoding="utf-8")
    csv_path = out / "v29_baseline_comparison.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["baseline_id", "substrate_class", "total_power_w", "joules_per_task", "total_latency_ms", "tasks_per_joule", "energy_ratio_vs_gpu_placeholder", "latency_ratio_vs_gpu_placeholder", "claim_boundary"])
        for b in result["baselines"]:
            w.writerow([
                b["baseline_id"], b["substrate_class"], b["energy"]["total_power_w"], b["energy"]["joules_per_task"],
                b["latency"]["total_ms"], b["energy"]["tasks_per_joule"], b["ratios_vs_gpu_placeholder"]["energy_per_task_ratio"],
                b["ratios_vs_gpu_placeholder"]["latency_ratio"], b["claim_boundary"],
            ])
    return {
        "version": "v2.9",
        "out_dir": str(out),
        "baseline_count": len(result["baselines"]),
        "live_output_performed": False,
        "files": ["v29_energy_performance_comparison.json", "BIOGPU_V29_ENERGY_PERFORMANCE_REPORT.md", "v29_baseline_comparison.csv"],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="outputs/realdata_zenodo_14363732_v29_energy")
    ap.add_argument("--task-count", type=int, default=1000)
    ap.add_argument("--run-duration-s", type=float, default=60.0)
    args = ap.parse_args()
    print(json.dumps(write_outputs(args.out_dir, args.task_count, args.run_duration_s), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
