from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from biogpu.encoding.base_v26 import EncoderInput
from biogpu.encoding.registry_v26 import build_encoder_registry_v26, registry_summary_v26


def sample_inputs() -> dict[str, EncoderInput]:
    return {
        "spatial_v26": EncoderInput(task_id="B1_spot_localization", payload=[[0, 1, 0], [1, 3, 1], [0, 1, 0]]),
        "temporal_v26": EncoderInput(task_id="B2_temporal_pattern_classification", payload={"sequence": [0, 1, 0.5, -0.5, 1]}),
        "rate_v26": EncoderInput(task_id="B0_target_vs_random_electrode", payload={"target": 0.95, "control": 0.05}),
        "hybrid_v26": EncoderInput(task_id="B4_adaptive_closed_loop", payload={"spatial": [0, 1, 2, 1], "temporal": [1, 0, 1, 0]}),
    }


def render_markdown(summary: dict[str, Any]) -> str:
    lines = ["# BioGPU v2.6 Encoder Layer", "", "## Purpose", "", "Convert digital BioGPU task payloads into safe abstract stimulation/readout pattern intents.", "", "## Encoders"]
    for enc in summary["encoders"]:
        lines.append(f"- `{enc['encoder_id']}` — kind `{enc['kind']}`, class `{enc['class']}`")
    lines += ["", "## Safety boundary", "", "The v2.6 encoder layer does not produce live stimulation amplitudes, pulse widths, frequencies, voltages, pinouts, or wiring instructions.", "", "## Demo patterns"]
    for p in summary["demo_patterns"]:
        lines.append(f"- `{p['pattern_id']}` — kind `{p['kind']}`, groups `{len(p['target_groups'])}`, readout `{p['readout_hint']}`")
    return "\n".join(lines) + "\n"


def write_outputs(out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    registry = build_encoder_registry_v26()
    inputs = sample_inputs()
    patterns = []
    for enc_id, encoder in registry.items():
        pattern = encoder.encode(inputs[enc_id])
        patterns.append(pattern.to_dict())
        (out_dir / f"pattern_{enc_id}.json").write_text(pattern.to_json(), encoding="utf-8")
    summary = {
        "version": "v2.6",
        "encoder_count": len(registry),
        "encoders": registry_summary_v26(),
        "demo_patterns": patterns,
        "live_output_performed": False,
        "safety_boundary": "abstract patterns only; no live stimulation settings",
    }
    (out_dir / "v26_encoder_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    (out_dir / "BIOGPU_V26_ENCODER_LAYER.md").write_text(render_markdown(summary), encoding="utf-8")
    with (out_dir / "v26_encoder_registry.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["encoder_id", "kind", "class"])
        w.writeheader()
        for row in summary["encoders"]:
            w.writerow(row)
    return summary


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="outputs/realdata_zenodo_14363732_v26_encoder_layer")
    args = ap.parse_args()
    summary = write_outputs(Path(args.out_dir))
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
