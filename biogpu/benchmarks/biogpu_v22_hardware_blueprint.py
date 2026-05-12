from __future__ import annotations

import argparse
import json

from biogpu.hardware.blueprint_v22 import write_v22_outputs


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate BioGPU-A1 v2.2 hardware blueprint outputs.")
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()
    summary = write_v22_outputs(args.out_dir)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
