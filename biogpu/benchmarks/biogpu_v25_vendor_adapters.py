from __future__ import annotations

import argparse
import json
from biogpu.substrates.vendor_registry_v25 import run_v25_dry_run


def main() -> None:
    ap = argparse.ArgumentParser(description="BioGPU v2.5 vendor adapter dry-run generator")
    ap.add_argument("--out-dir", default="outputs/realdata_zenodo_14363732_v25_vendor_adapters")
    args = ap.parse_args()
    summary = run_v25_dry_run(args.out_dir)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
