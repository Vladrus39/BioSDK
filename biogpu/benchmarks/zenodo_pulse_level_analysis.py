from __future__ import annotations

import argparse
import json

from biogpu.analysis.zenodo_pulse_level import write_outputs


def main() -> int:
    p = argparse.ArgumentParser(description="Run Zenodo MEA2100 pulse-level stimulation-window analysis")
    p.add_argument("root_path", help="Path to extracted Pre_processed_MEA_data directory")
    p.add_argument("--out", default="outputs/realdata_zenodo_14363732_v13_pulse")
    p.add_argument("--response-window-ms", type=float, default=100.0)
    args = p.parse_args()
    result = write_outputs(args.root_path, args.out, response_window_ms=args.response_window_ms)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
