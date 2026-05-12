#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json

from biogpu.diagnostics.repeated_seed import run_repeated_seeds


def main() -> int:
    parser = argparse.ArgumentParser(description="Run repeated-seed BioGPU benchmark evaluation")
    parser.add_argument("benchmark", choices=["delayed-match", "streaming"], default="delayed-match")
    parser.add_argument("--config", default=None)
    parser.add_argument("--seeds", default="101,202,303")
    args = parser.parse_args()
    seeds = [int(x.strip()) for x in args.seeds.split(",") if x.strip()]
    if args.benchmark == "delayed-match":
        from biogpu.benchmarks.delayed_match import main as bench_main
        config = args.config or "configs/delayed_match.yaml"
    else:
        from biogpu.benchmarks.streaming import main as bench_main
        config = args.config or "configs/streaming.yaml"
    summary = run_repeated_seeds(bench_main, config, seeds)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
