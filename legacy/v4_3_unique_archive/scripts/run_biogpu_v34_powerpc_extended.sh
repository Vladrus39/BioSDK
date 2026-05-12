#!/usr/bin/env bash
set -euo pipefail
python - <<'PY'
from pathlib import Path
from biogpu.integration.realdata_sweep_v33 import RealDataSweepConfigV33, run_realdata_sweep_v33
v15=Path('outputs/realdata_zenodo_14363732_v15_readout')
for seed in (34501, 34502, 34503, 34504, 34505):
    out=Path(f'outputs/powerpc_extended_v34_seed_{seed}')
    cfg=RealDataSweepConfigV33(split_offsets=tuple(range(18)), shuffle_count=5000, seed=seed)
    print(run_realdata_sweep_v33(v15, out, cfg))
PY
