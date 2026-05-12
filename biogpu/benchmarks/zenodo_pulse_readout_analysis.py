from __future__ import annotations

import argparse
import json

from biogpu.analysis.zenodo_pulse_readout import write_readout_outputs


def main() -> int:
    p = argparse.ArgumentParser(description="Run Zenodo MEA2100 pulse-level feature/readout benchmark")
    p.add_argument("root_path", help="Path to extracted Pre_processed_MEA_data directory")
    p.add_argument("--out", default="outputs/realdata_zenodo_14363732_v15_readout")
    p.add_argument("--response-window-ms", type=float, default=100.0)
    p.add_argument("--label-shuffles", type=int, default=None, help="Legacy option: set both target and candidate label-shuffle counts")
    p.add_argument("--target-label-shuffles", type=int, default=1, help="Label shuffles for strict multiclass target-ID readout")
    p.add_argument("--candidate-label-shuffles", type=int, default=50, help="Label shuffles for binary target-vs-random candidate readout")
    p.add_argument("--negative-per-pulse", type=int, default=1)
    p.add_argument("--seed", type=int, default=23)
    p.add_argument("--plots", action="store_true", help="Write optional matplotlib plots")
    args = p.parse_args()
    result = write_readout_outputs(
        args.root_path,
        args.out,
        response_window_ms=args.response_window_ms,
        n_label_shuffles=(args.label_shuffles if args.label_shuffles is not None else args.candidate_label_shuffles),
        negative_per_pulse=args.negative_per_pulse,
        target_label_shuffles=(args.label_shuffles if args.label_shuffles is not None else args.target_label_shuffles),
        candidate_label_shuffles=(args.label_shuffles if args.label_shuffles is not None else args.candidate_label_shuffles),
        seed=args.seed,
        make_plots=args.plots,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
