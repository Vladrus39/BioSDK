from __future__ import annotations
import argparse, json
from pathlib import Path

from biogpu.runtime.wetware_v21 import write_v21_outputs
from biogpu.wetware.provisional_stack_v21 import write_wetware_outputs_v21
from biogpu.benchmarks.registry_v21 import write_registry_v21
from biogpu.runtime.session_v21 import default_v21_session, write_session_file


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out-dir', required=True)
    args = ap.parse_args()
    out = Path(args.out_dir)
    ideal = write_v21_outputs(out)
    provisional = write_wetware_outputs_v21(out)
    registry = write_registry_v21(out)
    session = default_v21_session('replay_local')
    session_path = write_session_file(session, out)
    summary = {
        'ideal_design': ideal,
        'provisional_wetware_stack': provisional,
        'benchmark_registry': registry,
        'session_path': str(session_path),
    }
    (out / 'v21_local_check_summary.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps(summary, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
