#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

# 1) Sanity check the BioGPU runtime layer.
bash scripts/run_biogpu_v18_local_check.sh

# 2) Paper-grade readout rerun from saved v1.5 matrix.
# This is CPU-heavy. Adjust shuffles/seeds upward on a strong workstation.
python -m biogpu.benchmarks.zenodo_pulse_v17_from_v15 \
  outputs/realdata_zenodo_14363732_v15_readout \
  --out outputs/realdata_zenodo_14363732_v18_full_paper_readout \
  --negative-counts 1,3,5,10 \
  --negative-seeds 101,202,303,404,505,606,707,808,909,1001 \
  --readouts logistic_l2,linear_svm,centroid \
  --feature-sets raw_candidate_counts_only,all_without_rank_zscore,all_features,pulse_context_only_negative_control \
  --label-shuffles 100

# 3) Keep a manifest that the full run was attempted.
python - <<'PY'
from pathlib import Path
Path('outputs/realdata_zenodo_14363732_v18_full_paper_readout/FULL_RUN_DONE.txt').write_text(
    'Full v1.8 PC run command completed. Check JSON/CSV outputs and rerun with 1000 shuffles for final publication-grade stats.\n',
    encoding='utf-8'
)
PY

printf '\nBioGPU v1.8 full PC run complete.\n'
