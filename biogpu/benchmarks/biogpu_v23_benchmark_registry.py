from __future__ import annotations

import argparse
import json

from biogpu.benchmarks.registry_v23 import write_v23_outputs


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate BioGPU v2.3 benchmark registry outputs.")
    parser.add_argument("--out-dir", default="outputs/realdata_zenodo_14363732_v23_benchmark_registry")
    args = parser.parse_args()
    summary = write_v23_outputs(args.out_dir)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
