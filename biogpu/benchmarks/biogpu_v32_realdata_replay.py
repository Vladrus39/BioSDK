from __future__ import annotations
import argparse, json
from pathlib import Path
from biogpu.integration.realdata_replay_v32 import RealDataReplayConfigV32, run_realdata_replay_v32


def main() -> None:
    ap = argparse.ArgumentParser(description="BioGPU v3.2 fixed-manifest real-data replay runner")
    ap.add_argument("--v15-dir", default="outputs/realdata_zenodo_14363732_v15_readout")
    ap.add_argument("--out-dir", default="outputs/realdata_zenodo_14363732_v32_realdata_e2e")
    ap.add_argument("--shuffle-count", type=int, default=20)
    ap.add_argument("--seed", type=int, default=32)
    args = ap.parse_args()
    config = RealDataReplayConfigV32(shuffle_count=args.shuffle_count, seed=args.seed)
    summary = run_realdata_replay_v32(Path(args.v15_dir), Path(args.out_dir), config)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
