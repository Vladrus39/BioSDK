"""BioGPU-Core v5.20 Allen orientation benchmark runner."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from biogpu.sdk.allen_orientation_benchmark_v520 import DEFAULT_OUT, write_allen_orientation_benchmark_outputs_v520


def run(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT, top_units: int = 64, max_windows: int = 800, label_shuffles: int = 100, seed: int = 520) -> dict[str, Any]:
    paths = write_allen_orientation_benchmark_outputs_v520(root=root, out_dir=out_dir, top_units=top_units, max_windows=max_windows, label_shuffles=label_shuffles, seed=seed)
    summary = json.loads(Path(paths["summary_json"]).read_text(encoding="utf-8"))
    print(f"v520_allen_orientation status={summary['overall_status']}")
    print(f"samples={summary.get('sample_count', 0)}")
    print(f"selected_units={summary.get('selected_unit_count', 0)}")
    print(f"feature_count={summary.get('feature_count', 0)}")
    print(f"readout_status={summary.get('readout_status')}")
    print(f"bic_os_phase_locked={summary['bic_os_phase_locked']}")
    return {"summary": summary, "outputs": paths}


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="BioGPU-Core v5.20 Allen orientation benchmark")
    parser.add_argument("--root", default=".")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    parser.add_argument("--top-units", type=int, default=64)
    parser.add_argument("--max-windows", type=int, default=800)
    parser.add_argument("--label-shuffles", type=int, default=100)
    parser.add_argument("--seed", type=int, default=520)
    args = parser.parse_args()
    run(root=args.root, out_dir=args.out_dir, top_units=args.top_units, max_windows=args.max_windows, label_shuffles=args.label_shuffles, seed=args.seed)


if __name__ == "__main__":
    main()
