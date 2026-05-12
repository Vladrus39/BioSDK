# v1.7 Paper-grade rerun plan

This file records work that should be run on a stronger CPU machine so it is not lost.

## Recommended machine

Minimum practical:

- 8 CPU cores
- 32 GB RAM
- fast SSD
- Python 3.12/3.13

Better:

- 16+ CPU cores
- 64 GB RAM
- local SSD

GPU is not required for the current linear readouts. CPU parallelization is more useful here.

## Step 1 — verify v1.5 matrix exists

```bash
ls -lh outputs/realdata_zenodo_14363732_v15_readout/pulse_feature_matrix.npz
ls -lh outputs/realdata_zenodo_14363732_v15_readout/pulse_feature_metadata.csv
```

## Step 2 — full negative-seed/readout/ablation run

Use this as the first serious run:

```bash
PYTHONPATH=. python -m biogpu.benchmarks.zenodo_pulse_v17_from_v15 \
  outputs/realdata_zenodo_14363732_v15_readout \
  --out outputs/realdata_zenodo_14363732_v17_paper_full \
  --negative-counts 1,3,5,10 \
  --negative-seeds 101,202,303,404,505,606,707,808,909,1001 \
  --readouts centroid,logistic_l2,linear_svm \
  --feature-sets all_features,raw_candidate_counts_only,all_without_rank_zscore,pulse_context_only_negative_control \
  --label-shuffles 100
```

This gives:

- 4 negative levels
- 10 negative sampling seeds
- 3 readouts
- 4 feature sets
- 100 label shuffles per row

Expected cost: CPU-heavy but feasible on a workstation.

## Step 3 — final publication-grade shuffle run

Only after Step 2 is stable:

```bash
PYTHONPATH=. python -m biogpu.benchmarks.zenodo_pulse_v17_from_v15 \
  outputs/realdata_zenodo_14363732_v15_readout \
  --out outputs/realdata_zenodo_14363732_v17_paper_1000shuffle \
  --negative-counts 1,3,5 \
  --negative-seeds 101,202,303,404,505,606,707,808,909,1001,1102,1203,1304,1405,1506,1607,1708,1809,1901,2002 \
  --readouts logistic_l2,linear_svm \
  --feature-sets raw_candidate_counts_only,all_without_rank_zscore,pulse_context_only_negative_control \
  --label-shuffles 1000
```

## Required reporting rules

Report these separately:

1. raw-count-only features
2. all-without-rank-zscore features
3. all features
4. pulse-context-only negative control

Do not use all-feature results alone, because within-pulse rank/z-score features may inflate target-vs-random separability.

## Acceptance criteria before strong claims

- raw-count-only AUC remains clearly above shuffled baseline
- all-without-rank-zscore remains above shuffled baseline
- pulse-context-only negative control stays near chance
- results stable across negative seeds
- label-shuffle p-values survive 1000-shuffle run
- results reported by held-out culture, not random row split

## Still not solved by v1.7

- task-level behavioral/NWB benchmark
- exact TTL verification from raw HDF5
- BioGPU-vs-silicon energy/performance claim
- external reproduction of arXiv 2602.05737 BRC experiments
