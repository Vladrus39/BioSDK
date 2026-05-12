from __future__ import annotations
import argparse, json
from biogpu.runtime import write_v18_biogpu_core_outputs


def main() -> int:
    p = argparse.ArgumentParser(description="Run BioGPU-Core v1.8 runtime/replay architecture demo")
    p.add_argument("v15_out_dir", help="Path to outputs/realdata_zenodo_14363732_v15_readout")
    p.add_argument("--out", default="outputs/realdata_zenodo_14363732_v18_biogpu_core")
    p.add_argument("--demo-jobs", type=int, default=8)
    p.add_argument("--seed", type=int, default=18)
    a = p.parse_args()
    result = write_v18_biogpu_core_outputs(a.v15_out_dir, a.out, demo_jobs=a.demo_jobs, seed=a.seed)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
