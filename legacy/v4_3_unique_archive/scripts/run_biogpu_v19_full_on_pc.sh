#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
python -m biogpu.benchmarks.biogpu_v19_engineering_analysis \
  --v15-out outputs/realdata_zenodo_14363732_v15_readout \
  --out outputs/realdata_zenodo_14363732_v19_engineering \
  --closed-loop-steps 32 \
  --seed 19
# Heavy paper-grade replay run. Raise --label-shuffles to 1000 after quick validation.
python -m biogpu.benchmarks.zenodo_pulse_v17_from_v15 \
  --v15-out outputs/realdata_zenodo_14363732_v15_readout \
  --out outputs/realdata_zenodo_14363732_v17_paper_grade_full_pc \
  --readouts logistic_l2 linear_svm centroid \
  --feature-sets raw_candidate_counts_only all_features pulse_context_only_negative_control \
  --negatives 1 3 5 10 \
  --negative-seeds 101 102 103 104 105 106 107 108 109 110 \
  --label-shuffles 100 \
  --seed 170
mkdir -p outputs/TO_COPY_BACK_AFTER_FULL_PC_RUN
cp -r outputs/realdata_zenodo_14363732_v19_engineering outputs/TO_COPY_BACK_AFTER_FULL_PC_RUN/ || true
cp -r outputs/realdata_zenodo_14363732_v17_paper_grade_full_pc outputs/TO_COPY_BACK_AFTER_FULL_PC_RUN/ || true
find outputs/TO_COPY_BACK_AFTER_FULL_PC_RUN -maxdepth 3 -type f | sort > outputs/TO_COPY_BACK_AFTER_FULL_PC_RUN/file_list.txt
