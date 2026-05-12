from __future__ import annotations

import argparse
import json

from biogpu.analysis.zenodo_pulse_v16 import write_v16_outputs


def _parse_int_list(value: str) -> list[int]:
    return [int(part.strip()) for part in value.split(",") if part.strip()]


def main() -> int:
    p = argparse.ArgumentParser(description="Run Zenodo MEA2100 pulse-level readout robustness v1.6")
    p.add_argument("root_path", help="Path to extracted Pre_processed_MEA_data directory")
    p.add_argument("--out", default="outputs/realdata_zenodo_14363732_v16_robustness")
    p.add_argument("--response-window-ms", type=float, default=100.0)
    p.add_argument("--negative-counts", default="1,3,5", help="Comma-separated negative electrodes per pulse, e.g. 1,3,5")
    p.add_argument("--ablation-negative-per-pulse", type=int, default=3)
    p.add_argument("--label-shuffles", type=int, default=20)
    p.add_argument("--bootstrap-repeats", type=int, default=1000)
    p.add_argument("--seed", type=int, default=101)
    args = p.parse_args()
    result = write_v16_outputs(
        args.root_path,
        args.out,
        response_window_ms=args.response_window_ms,
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
