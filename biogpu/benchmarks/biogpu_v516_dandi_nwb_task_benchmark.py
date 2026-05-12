"""BioGPU-Core v5.16 DANDI/NWB task benchmark runner."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from biogpu.sdk.nwb_task_benchmark_v516 import DEFAULT_OUT, write_dandi_nwb_benchmark_outputs_v516


def run(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT, label_shuffles: int = 100, seed: int = 516) -> dict[str, Any]:
    paths = write_dandi_nwb_benchmark_outputs_v516(root=root, out_dir=out_dir, label_shuffles=label_shuffles, seed=seed)
    summary = json.loads(Path(paths["summary_json"]).read_text(encoding="utf-8"))
    print(f"v516_dandi_nwb_task_benchmark status={summary['overall_status']}")
    print(f"sample_count={summary.get('sample_count')}")
    print(f"unit_count={summary.get('unit_count')}")
    print(f"feature_count={summary.get('feature_count')}")
    observed = summary.get("observed") or {}
    shuffle = summary.get("label_shuffle_baseline") or {}
    print(f"observed_balanced_accuracy={observed.get('balanced_accuracy')}")
    print(f"shuffle_p_value={shuffle.get('p_value_balanced_accuracy_gt_shuffle')}")
    return {"summary": summary, "outputs": paths}


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="BioGPU-Core v5.16 DANDI/NWB task benchmark")
    parser.add_argument("--root", default=".")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    parser.add_argument("--label-shuffles", type=int, default=100)
    parser.add_argument("--seed", type=int, default=516)
    args = parser.parse_args()
    run(root=args.root, out_dir=args.out_dir, label_shuffles=args.label_shuffles, seed=args.seed)


if __name__ == "__main__":
    main()
