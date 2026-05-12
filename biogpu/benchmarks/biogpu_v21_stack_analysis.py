from __future__ import annotations
import argparse, json
from pathlib import Path

from biogpu.runtime.session_v21 import default_v21_session, write_session_file, collect_result_bundle
from biogpu.runtime.wetware_v21 import write_v21_outputs
from biogpu.wetware.provisional_stack_v21 import write_wetware_outputs_v21
from biogpu.benchmarks.registry_v21 import write_registry_v21


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out-dir', required=True)
    ap.add_argument('--mode', default='replay_local', choices=['replay_local','power_pc_full','live_mea_dry_run','live_mea_vendor'])
    ap.add_argument('--include-dir', action='append', default=[])
    args = ap.parse_args()
    out = Path(args.out_dir); out.mkdir(parents=True, exist_ok=True)

    ideal_design = write_v21_outputs(out)
    wetware = write_wetware_outputs_v21(out)
    registry = write_registry_v21(out)
    session = default_v21_session(args.mode)
    session_path = write_session_file(session, out)
    bundle = collect_result_bundle(session, [out] + [Path(x) for x in args.include_dir], out)
    summary = {
        'version': 'v2.1',
        'ideal_design': ideal_design,
        'provisional_wetware_stack': wetware,
        'benchmark_registry': registry,
        'session_path': str(session_path),
        'bundle': bundle,
        'boundary': 'Engineering reference design only; exact wet-lab recipe and live stimulation limits require qualified SOP and vendor manuals.'
    }
    (out/'v21_summary.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps(summary, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
