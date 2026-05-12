from __future__ import annotations

import argparse
import json

from biogpu.analysis.zenodo_pulse_v16 import write_v16_outputs_from_v15_matrix


def _parse_int_list(value: str) -> list[int]:
    return [int(part.strip()) for part in value.split(",") if part.strip()]


def main() -> int:
    p = argparse.ArgumentParser(description="Run v1.6 robustness from saved v1.5 pulse feature matrix")
    p.add_argument("v15_out_dir", help="Path to outputs/realdata_zenodo_14363732_v15_readout")
    p.add_argument("--out", default="outputs/realdata_zenodo_14363732_v16_robustness")
    p.add_argument("--negative-counts", default="1,3,5")
    p.add_argument("--ablation-negative-per-pulse", type=int, default=3)
    p.add_argument("--label-shuffles", type=int, default=20)
    p.add_argument("--bootstrap-repeats", type=int, default=1000)
    p.add_argument("--seed", type=int, default=101)
    args = p.parse_args()
    result = write_v16_outputs_from_v15_matrix(
        args.v15_out_dir,
        args.out,
        negative_counts=_parse_int_list(args.negative_counts),
        ablation_negative_per_pulse=args.ablation_negative_per_pulse,
        label_shuffles=args.label_shuffles,
        bootstrap_repeats=args.bootstrap_repeats,
        seed=args.seed,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
