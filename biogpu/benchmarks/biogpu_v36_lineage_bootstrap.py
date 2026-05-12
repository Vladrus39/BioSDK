from __future__ import annotations

import argparse, csv, json, time, zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np

from biogpu.integration.realdata_replay_v32 import load_v15_realdata_matrix_v32
from biogpu.integration.realdata_sweep_v33 import RealDataSweepConfigV33, build_feature_ablations_v33, evaluate_one_v33
from biogpu.statistics.lineage_split_v36 import build_lineage_strict_splits_v36, lineage_audit_table_v36, summarize_lineage_splits_v36
from biogpu.statistics.bootstrap_v36 import aggregate_rows_with_ci_v36


SAFETY_BOUNDARY_V36 = [
    "offline public-data replay only",
    "lineage-strict statistical validation scaffold",
    "no live stimulation settings emitted",
    "no wet-lab protocol or culturing recipe",
    "no vendor pinout/wiring procedure",
    "no GPU advantage claim",
]


@dataclass(frozen=True)
class LineageBootstrapConfigV36:
    version: str = "v3.6"
    benchmark_id: str = "B1_spot_localization:lineage_strict_bootstrap_scaffold"
    split_offsets: tuple[int, ...] = (0, 1, 2, 3, 4, 5)
    lineage_stride: int = 2
    heldout_lineage_count: int = 2
    decoders: tuple[str, ...] = ("centroid_euclidean", "diag_gaussian", "logistic_l2", "linear_svm")
    ablations: tuple[str, ...] = ("response_delta_count", "exact_features")
    shuffle_count: int = 8
    bootstrap_iterations: int = 500
    seed: int = 36

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    keys=[]
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    with path.open("w", newline="", encoding="utf-8") as f:
        w=csv.DictWriter(f, fieldnames=keys)
        w.writeheader(); w.writerows(rows)


def _report(profile: dict[str, Any], summary: dict[str, Any]) -> str:
    b=summary.get("best_run", {})
    return f"""# BioGPU-Core v3.6 Lineage-Strict Split + Bootstrap Scaffold

## Status

`COMPLETED_SOFTWARE_ONLY_REPLAY_VALIDATION_SCAFFOLD`

## Why v3.6 exists

Earlier culture-heldout splits can still be too optimistic if labels such as
`40628_13DIV`, `40628_18DIV`, and `40628_21DIV` come from the same base culture
lineage recorded at different DIV values. v3.6 therefore adds base-lineage
holdout so all DIV variants of the same lineage stay on only one side of the
train/test split.

## Dataset profile

- Rows / pulse windows: `{profile['rows']}`
- Features: `{profile['features']}`
- Culture labels: `{profile['cultures']}`
- Target classes: `{profile['target_classes']}`
- Conditions: `{', '.join(profile['conditions'])}`

## Compact lineage-strict result

- Sweep rows: `{summary['sweep_run_count']}`
- Best split: `{b.get('split_id')}`
- Best decoder: `{b.get('decoder_id')}`
- Best ablation: `{b.get('ablation_id')}`
- Accuracy: `{float(b.get('accuracy', 0.0)):.6f}`
- Balanced accuracy: `{float(b.get('balanced_accuracy', 0.0)):.6f}`
- Shuffle mean accuracy: `{float(b.get('shuffle_mean_accuracy', 0.0)):.6f}`
- Improvement vs shuffle mean: `{float(b.get('improvement_vs_shuffle_mean', 0.0)):.6f}`

## Boundary

This is still replay-only validation. It does not prove live BioGPU operation,
GPU advantage, or biological safety. It only makes the statistical split more
conservative and prepares bootstrap confidence interval aggregation for the
power-PC runs.
"""


def run_lineage_bootstrap_v36(v15_dir: Path, out_dir: Path, config: LineageBootstrapConfigV36 | None = None) -> dict[str, Any]:
    config = config or LineageBootstrapConfigV36()
    out_dir.mkdir(parents=True, exist_ok=True)
    matrix=load_v15_realdata_matrix_v32(v15_dir)
    profile=matrix.profile()
    audit=lineage_audit_table_v36(matrix)
    splits=build_lineage_strict_splits_v36(matrix, split_offsets=config.split_offsets, lineage_stride=config.lineage_stride, heldout_lineage_count=config.heldout_lineage_count)
    # Reuse v3.3 ablation builder with v3.6 ablation selection.
    v33_config=RealDataSweepConfigV33(
        split_offsets=config.split_offsets,
        decoders=config.decoders,
        ablations=config.ablations,
        shuffle_count=config.shuffle_count,
        seed=config.seed,
    )
    ablations=build_feature_ablations_v33(matrix, v33_config)
    rng=np.random.default_rng(config.seed)
    rows=[]; shuffles=[]
    for split in splits:
        if not split.leakage_check_passed:
            continue
        for dec in config.decoders:
            for abl in ablations:
                try:
                    row, sh = evaluate_one_v33(matrix, split, abl, dec, v33_config, rng)
                    row["split_strategy"] = split.strategy
                    row["test_lineages"] = ";".join(split.test_lineages)
                    rows.append(row); shuffles.extend(sh)
                except Exception as e:
                    rows.append({
                        "split_id": split.split_id,
                        "decoder_id": dec,
                        "ablation_id": abl.ablation_id,
                        "status": "error",
                        "error": str(e)[:300],
                    })
    ok=[r for r in rows if r.get("status") == "ok"]
    if not ok:
        raise RuntimeError("v3.6 produced no successful lineage-strict sweep rows")
    best=max(ok, key=lambda r:(float(r["accuracy"]), float(r["balanced_accuracy"]), float(r["improvement_vs_shuffle_mean"])))
    agg_decoder=aggregate_rows_with_ci_v36(ok, "decoder_id", iterations=config.bootstrap_iterations, seed=config.seed)
    agg_ablation=aggregate_rows_with_ci_v36(ok, "ablation_id", iterations=config.bootstrap_iterations, seed=config.seed+100)
    summary={
        "version": config.version,
        "benchmark_id": config.benchmark_id,
        "dataset_profile": profile,
        "config": config.to_dict(),
        "safety_boundary": SAFETY_BOUNDARY_V36,
        "lineage_count": len(set(r["base_lineage_id"] for r in audit)),
        "culture_count": len(audit),
        "split_count": len(splits),
        "sweep_run_count": len(ok),
        "best_run": best,
        "artifact_dir": str(out_dir),
    }
    _csv(out_dir/"v36_lineage_audit.csv", audit)
    _csv(out_dir/"v36_lineage_splits.csv", summarize_lineage_splits_v36(splits))
    _csv(out_dir/"v36_lineage_sweep_results.csv", rows)
    _csv(out_dir/"v36_lineage_shuffle_controls.csv", shuffles)
    _csv(out_dir/"v36_bootstrap_ci_by_decoder.csv", agg_decoder)
    _csv(out_dir/"v36_bootstrap_ci_by_ablation.csv", agg_ablation)
    _json(out_dir/"v36_summary.json", summary)
    _json(out_dir/"v36_config.json", config.to_dict())
    (out_dir/"BIOGPU_V36_LINEAGE_BOOTSTRAP_REPORT.md").write_text(_report(profile, summary), encoding="utf-8")
    _json(out_dir/"v36_system_info.json", {"timestamp": time.time(), "numpy_version": np.__version__})
    bundle=out_dir/"biogpu_v36_lineage_bootstrap_bundle.zip"
    with zipfile.ZipFile(bundle, "w", zipfile.ZIP_DEFLATED) as z:
        for p in out_dir.iterdir():
            if p.is_file() and p.name != bundle.name:
                z.write(p, arcname=p.name)
    summary["result_bundle"] = str(bundle)
    _json(out_dir/"v36_summary.json", summary)
    return summary


def main() -> None:
    ap=argparse.ArgumentParser(description="BioGPU v3.6 lineage-strict split and bootstrap scaffold")
    ap.add_argument("--v15-dir", default="outputs/realdata_zenodo_14363732_v15_readout")
    ap.add_argument("--out-dir", default="outputs/realdata_zenodo_14363732_v36_lineage_bootstrap")
    ap.add_argument("--shuffle-count", type=int, default=8)
    ap.add_argument("--bootstrap-iterations", type=int, default=500)
    ap.add_argument("--decoders", default="centroid_euclidean,diag_gaussian,logistic_l2,linear_svm")
    ap.add_argument("--ablations", default="response_delta_count,exact_features")
    ap.add_argument("--split-offsets", default="0,1,2,3,4,5")
    ap.add_argument("--seed", type=int, default=36)
    args=ap.parse_args()
    cfg=LineageBootstrapConfigV36(
        decoders=tuple(x.strip() for x in args.decoders.split(",") if x.strip()),
        ablations=tuple(x.strip() for x in args.ablations.split(",") if x.strip()),
        split_offsets=tuple(int(x.strip()) for x in args.split_offsets.split(",") if x.strip()),
        shuffle_count=args.shuffle_count,
        bootstrap_iterations=args.bootstrap_iterations,
        seed=args.seed,
    )
    summary=run_lineage_bootstrap_v36(Path(args.v15_dir), Path(args.out_dir), cfg)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
