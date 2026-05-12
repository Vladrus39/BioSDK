
from __future__ import annotations

import argparse
import json
from pathlib import Path

from biogpu.runtime.session_manager_v24 import write_v24_session_outputs


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate BioGPU v2.4 session manifest and result bundle.")
    parser.add_argument("--out-dir", default="outputs/realdata_zenodo_14363732_v24_session_manager")
    parser.add_argument("--run-mode", default="dry_run", choices=["replay", "dry_run", "power_pc", "live_lab"])
    parser.add_argument("--hardware-profile", default="software_only")
    parser.add_argument("--benchmarks", default="")
    parser.add_argument("--operator-note", default="")
    args = parser.parse_args()

    benchmark_ids = [x.strip() for x in args.benchmarks.split(",") if x.strip()] or None
    summary = write_v24_session_outputs(
        args.out_dir,
        run_mode=args.run_mode,
        benchmark_ids=benchmark_ids,
        hardware_profile=args.hardware_profile,
        operator_note=args.operator_note,
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
