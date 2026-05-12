from __future__ import annotations
import argparse, json
from pathlib import Path
from biogpu.powerpc.runner_plan_v34 import write_powerpc_outputs_v34


def main() -> None:
    ap = argparse.ArgumentParser(description='BioGPU v3.4 power-PC runner package generator')
    ap.add_argument('--out-dir', default='outputs/realdata_zenodo_14363732_v34_powerpc')
    args = ap.parse_args()
    summary = write_powerpc_outputs_v34(Path(args.out_dir))
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
