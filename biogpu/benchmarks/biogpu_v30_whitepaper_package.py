from __future__ import annotations
import argparse, json
from pathlib import Path
from biogpu.paper.package_v30 import write_v30_package

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate BioGPU-Core v3.0 whitepaper/release package")
    parser.add_argument("--out-dir", default="outputs/realdata_zenodo_14363732_v30_whitepaper")
    parser.add_argument("--write-root", action="store_true")
    args = parser.parse_args()
    root = Path.cwd() if args.write_root else None
    print(json.dumps(write_v30_package(args.out_dir, root), indent=2, ensure_ascii=False))

if __name__ == "__main__": main()
