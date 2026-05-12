from __future__ import annotations

import argparse
import json

from biogpu.analysis.zenodo_pulse_controls import write_control_outputs


def main() -> int:
    p = argparse.ArgumentParser(description="Run Zenodo MEA2100 pulse-level control/null analyses")
    p.add_argument("root_path", help="Path to extracted Pre_processed_MEA_data directory")
    p.add_argument("--out", default="outputs/realdata_zenodo_14363732_v14_controls")
    p.add_argument("--response-window-ms", type=float, default=100.0)
    p.add_argument("--random-electrode-permutations", type=int, default=1000)
    p.add_argument("--random-time-permutations", type=int, default=300)
    p.add_argument("--seed", type=int, default=13)
    p.add_argument("--plots", action="store_true", help="Write optional matplotlib plots")
    args = p.parse_args()
    result = write_control_outputs(
        args.root_path,
        args.out,
        response_window_ms=args.response_window_ms,
        n_random_electrode_permutations=args.random_electrode_permutations,
        n_random_time_permutations=args.random_time_permutations,
        seed=args.seed,
        make_plots=args.plots,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
