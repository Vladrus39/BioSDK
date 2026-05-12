from __future__ import annotations
import argparse, json
from biogpu.analysis.zenodo_condition_spot import write_outputs

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument('root_path')
    p.add_argument('--out', default='outputs/realdata_zenodo_14363732_v12')
    args = p.parse_args()
    result = write_outputs(args.root_path, args.out)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
