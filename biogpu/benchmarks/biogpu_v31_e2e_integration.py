from __future__ import annotations

import argparse
import json
from pathlib import Path

from biogpu.integration.e2e_v31 import E2EConfigV31, run_e2e_v31


def main() -> None:
    parser = argparse.ArgumentParser(description="BioGPU v3.1 end-to-end integration pass")
    parser.add_argument("--out-dir", default="outputs/realdata_zenodo_14363732_v31_e2e")
    parser.add_argument("--mode", choices=["replay", "dry_run", "power_pc"], default="replay")
    parser.add_argument("--encoder-id", default="spatial_v26")
    parser.add_argument("--decoder-id", default="centroid_v27")
    args = parser.parse_args()
    cfg = E2EConfigV31(run_mode=args.mode, encoder_id=args.encoder_id, decoder_id=args.decoder_id)
    summary = run_e2e_v31(Path(args.out_dir), cfg)
    print(json.dumps(summary.to_dict(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
