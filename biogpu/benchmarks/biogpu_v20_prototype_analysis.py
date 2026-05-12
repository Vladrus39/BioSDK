from __future__ import annotations
import argparse, json
from pathlib import Path
from biogpu.runtime.prototype_v20 import write_v20_outputs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out-dir', required=True)
    ap.add_argument('--image-path', default=None)
    args = ap.parse_args()
    summary = write_v20_outputs(args.out_dir, args.image_path)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
