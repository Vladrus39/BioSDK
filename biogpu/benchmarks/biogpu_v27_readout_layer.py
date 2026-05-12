from __future__ import annotations
import argparse, csv, json
from pathlib import Path
from typing import Any
from biogpu.readout.base_v27 import ReadoutFeatureBatch
from biogpu.readout.registry_v27 import build_readout_registry_v27, registry_summary_v27


def sample_batch() -> ReadoutFeatureBatch:
    return ReadoutFeatureBatch(
        feature_names=["f0", "f1", "f2"],
        X=[[1,0,0], [0.9,0.1,0], [0,1,0], [0.1,0.9,0], [0,0,1], [0,0.1,0.9]],
        y=["A", "A", "B", "B", "C", "C"],
        metadata={"purpose": "v2.7 dry-run synthetic separability check"},
    )


def render_markdown(summary: dict[str, Any]) -> str:
    lines = ["# BioGPU v2.7 Readout / Decoder Layer", "", "## Purpose", "", "Decode BioGPU feature vectors into task predictions and confidence estimates.", "", "## Decoders"]
    for dec in summary["decoders"]:
        lines.append(f"- `{dec['decoder_id']}` — kind `{dec['kind']}`, class `{dec['class']}`")
    lines += ["", "## Safety boundary", "", "The v2.7 readout layer decodes features only. It does not contain live stimulation settings, wet-lab instructions, pinouts, or physical wiring details."]
    return "\n".join(lines) + "\n"


def write_outputs(out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    batch = sample_batch()
    registry = build_readout_registry_v27()
    predictions = []
    for rid, dec in registry.items():
        dec.fit(batch)
        pred_rows = []
        correct = 0
        for x, y in zip(batch.X, batch.y or []):
            p = dec.predict_one(x, batch.feature_names)
            pred_rows.append({"decoder_id": rid, "expected": y, **p.to_dict()})
            correct += int(p.prediction == y)
        acc = correct / len(batch.X)
        predictions.append({"decoder_id": rid, "accuracy": acc, "predictions": pred_rows})
        (out_dir / f"predictions_{rid}.json").write_text(json.dumps(pred_rows, indent=2, ensure_ascii=False), encoding="utf-8")
    summary = {
        "version": "v2.7",
        "readout_count": len(registry),
        "decoders": registry_summary_v27(),
        "dry_run_accuracy": {p["decoder_id"]: p["accuracy"] for p in predictions},
        "live_output_performed": False,
        "safety_boundary": "feature decoding only; no live stimulation or wet-lab settings",
    }
    (out_dir / "v27_readout_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    (out_dir / "BIOGPU_V27_READOUT_LAYER.md").write_text(render_markdown(summary), encoding="utf-8")
    with (out_dir / "v27_readout_registry.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["decoder_id", "kind", "class"])
        w.writeheader(); w.writerows(summary["decoders"])
    return summary


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="outputs/realdata_zenodo_14363732_v27_readout_layer")
    args = ap.parse_args()
    print(json.dumps(write_outputs(Path(args.out_dir)), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
