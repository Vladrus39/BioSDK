#!/usr/bin/env bash
set -euo pipefail
# Full power-PC target. This intentionally does heavier shuffle controls than the chat environment.
python - <<'PY'
from pathlib import Path
from biogpu.integration.realdata_sweep_v33 import RealDataSweepConfigV33, run_realdata_sweep_v33
v15=Path('outputs/realdata_zenodo_14363732_v15_readout')
for seed in (34001, 34002, 34003):
    out=Path(f'outputs/powerpc_full_v34_seed_{seed}')
    cfg=RealDataSweepConfigV33(split_offsets=tuple(range(18)), shuffle_count=1000, seed=seed)
    print(run_realdata_sweep_v33(v15, out, cfg))
PY
