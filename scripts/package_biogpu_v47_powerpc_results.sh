#!/usr/bin/env bash
set -euo pipefail
OUT="outputs/biogpu_v47_powerpc_final_result_bundle.zip"
mkdir -p outputs
python -m biogpu.benchmarks.biogpu_v47_final_pc_patch --project-root . --out-dir outputs/v47_final_pc_patch || true
python - <<'PY_PACKAGE'
from pathlib import Path
import zipfile, time
out=Path('outputs/biogpu_v47_powerpc_final_result_bundle.zip')
include=[]
for base in ['outputs/powerpc_stage1_v33_compact','outputs/powerpc_stage2_v36_lineage_compact','outputs/powerpc_full_shuffle_1000','outputs/powerpc_extended_methods_5000','outputs/powerpc_latency_energy','outputs/v47_final_pc_patch']:
    p=Path(base)
    if p.exists():
        include += [x for x in p.rglob('*') if x.is_file()]
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
    z.writestr('BUNDLE_CREATED_UTC.txt', time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
    for f in include:
        z.write(f, f.as_posix())
print(out, out.stat().st_size)
PY_PACKAGE
