from __future__ import annotations
import argparse, csv, json
from pathlib import Path
from typing import Any
from biogpu.closed_loop.base_v28 import ClosedLoopConfigV28
from biogpu.closed_loop.controller_v28 import BioGPUClosedLoopControllerV28
from biogpu.closed_loop.registry_v28 import closed_loop_registry_summary_v28


def render_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# BioGPU v2.8 Closed-loop Controller",
        "",
        "## Purpose",
        "",
        "Run a hardware-neutral closed loop: task → encoder → substrate/replay → features → readout → reward/error → next abstract action.",
        "",
        "## Safety boundary",
        "",
        "This layer emits only abstract payload updates. It does not contain live stimulation settings, wet-lab recipes, pinouts, wiring, or vendor SOP replacement instructions.",
        "",
        "## Dry-run result",
        "",
        f"- steps: {summary['step_count']}",
        f"- final_success: {summary['final_success']}",
        f"- final_reward: {summary['final_reward']}",
    ]
    return "\n".join(lines) + "\n"


def write_outputs(out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    config = ClosedLoopConfigV28(
        loop_id="v28_dry_run_loop",
        benchmark_id="B4_adaptive_closed_loop",
        encoder_id="hybrid_v26",
        readout_id="online_centroid_v27",
        mode="dry_run",
        max_steps=8,
        target_confidence=0.35,
        metadata={"purpose": "v2.8 dry-run; no live output"},
    )
    controller = BioGPUClosedLoopControllerV28(config)
    run = controller.run(initial_payload={"spatial": [0, 1, 2, 1], "temporal": [1, 0, 1, 0], "abstract_gain": 0.5}, expected="target")
    summary = {
        "version": "v2.8",
        "registry": closed_loop_registry_summary_v28(),
        "config": config.to_dict(),
        "step_count": len(run.steps),
        "final_reward": run.final_reward,
        "final_success": run.final_success,
        "status": run.status,
        "live_output_performed": False,
        "safety_boundary": run.safety_boundary,
    }
    (out_dir / "v28_closed_loop_run.json").write_text(run.to_json(), encoding="utf-8")
    (out_dir / "v28_closed_loop_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    (out_dir / "BIOGPU_V28_CLOSED_LOOP_CONTROLLER.md").write_text(render_markdown(summary), encoding="utf-8")
    with (out_dir / "v28_closed_loop_steps.csv").open("w", newline="", encoding="utf-8") as f:
        fields = ["step_index", "pattern_id", "prediction", "confidence", "reward", "error", "success", "decision"]
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for s in run.steps:
            w.writerow({
                "step_index": s.step_index,
                "pattern_id": s.observation.pattern_id,
                "prediction": s.observation.prediction,
                "confidence": s.observation.confidence,
                "reward": s.reward.reward,
                "error": s.reward.error,
                "success": s.reward.success,
                "decision": s.decision.action,
            })
    return summary


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="outputs/realdata_zenodo_14363732_v28_closed_loop")
    args = ap.parse_args()
    print(json.dumps(write_outputs(Path(args.out_dir)), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
