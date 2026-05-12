from __future__ import annotations
import argparse, json
from pathlib import Path
from biogpu.integration.realdata_sweep_v33 import RealDataSweepConfigV33, run_realdata_sweep_v33


def main() -> None:
    ap = argparse.ArgumentParser(description="BioGPU v3.3 paper-grade real-data sweep")
    ap.add_argument("--v15-dir", default="outputs/realdata_zenodo_14363732_v15_readout")
    ap.add_argument("--out-dir", default="outputs/realdata_zenodo_14363732_v33_paper_sweep")
    ap.add_argument("--shuffle-count", type=int, default=12)
    ap.add_argument("--seed", type=int, default=33)
    ap.add_argument("--decoders", default="centroid_euclidean,centroid_cosine,diag_gaussian", help="Comma-separated decoder ids. v3.5 also supports logistic_l2 and linear_svm.")
    ap.add_argument("--split-offsets", default="0,1,2,3,4,5", help="Comma-separated split offsets.")
    args = ap.parse_args()
    decoders = tuple(x.strip() for x in args.decoders.split(",") if x.strip())
    split_offsets = tuple(int(x.strip()) for x in args.split_offsets.split(",") if x.strip())
    config = RealDataSweepConfigV33(shuffle_count=args.shuffle_count, seed=args.seed, decoders=decoders, split_offsets=split_offsets)
    summary = run_realdata_sweep_v33(Path(args.v15_dir), Path(args.out_dir), config)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
