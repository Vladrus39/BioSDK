from __future__ import annotations
import argparse, json
from pathlib import Path
from biogpu.release.release_hygiene_v35 import write_release_hygiene_outputs_v35


def main() -> None:
    ap = argparse.ArgumentParser(description="BioGPU v3.5 release hygiene generator")
    ap.add_argument("--out-dir", default="outputs/realdata_zenodo_14363732_v35_release_hygiene")
    ap.add_argument("--root", default=".")
    args = ap.parse_args()
    summary = write_release_hygiene_outputs_v35(Path(args.out_dir), Path(args.root))
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
