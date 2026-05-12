from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path
from datetime import datetime, timezone

from biogpu.release.final_pc_patch_v47 import validate_v47_project, get_first_72h_steps_v47


def _write(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding='utf-8')


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description='BioGPU v4.7 final PC runner patch validator')
    parser.add_argument('--project-root', default='.')
    parser.add_argument('--out-dir', default='outputs/v47_final_pc_patch')
    args = parser.parse_args(argv)
    root = Path(args.project_root)
    out = Path(args.out_dir)
    result = validate_v47_project(root)
    result.update({
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'python': platform.python_version(),
        'platform': platform.platform(),
        'first_command_on_pc': 'bash scripts/run_biogpu_v47_powerpc_smoke.sh',
        'next_command_after_dataset_copy': 'bash scripts/import_preprocessed_mea_data_v46.sh data/external/Pre_processed_MEA_data.zip',
    })
    _write(out / 'v47_final_pc_patch_summary.json', result)
    _write(out / 'v47_first_72h_steps.json', [x.to_dict() for x in get_first_72h_steps_v47()])
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result.get('ready_for_power_pc_handoff') else 2


if __name__ == '__main__':
    raise SystemExit(main())
