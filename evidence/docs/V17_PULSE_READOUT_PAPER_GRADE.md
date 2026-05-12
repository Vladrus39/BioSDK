# BioGPU-Core v1.7 — Pulse readout paper-grade scaffold

v1.7 builds on v1.5/v1.6. It does not invent new biological labels; it reuses the real Zenodo pulse-level feature matrix:

- 11,547 real protocol pulse windows
- 18 cultures
- 59 electrodes
- 354 pulse-response features
- conditions: 11,367 LightStim pulses and 180 ElecStim pulses

## What v1.7 adds

1. Stronger readouts for the target-vs-random-electrode separability test:
   - standardized nearest centroid
   - L2 logistic regression
   - linear SVM
2. Repeated negative-electrode sampling seeds.
3. Feature-set comparison:
   - all features
   - raw candidate counts only
   - all features without rank/z-score
   - pulse-context-only negative control
4. A full rerun plan for large CPU machines.

## Local quick result included in this archive

The included local quick run was intentionally small because this environment times out on larger repeated logistic/SVM runs:

```text
negative_per_pulse: 1
negative_seed: 101
readout: logistic_l2
feature_set: raw_candidate_counts_only
label_shuffles: 1
samples: 23,094
features: 4
ROC AUC: 0.923337
balanced accuracy: 0.859747
single label-shuffle ROC AUC: 0.521292
single label-shuffle balanced accuracy: 0.524682
```

This is a useful confirmation: a stronger linear readout on only raw spike-count candidate features remains high above a shuffled baseline. But one shuffle and one seed are not enough for a paper-grade claim.

## Correct claim level

Allowed:

> BioGPU-Core v1.7 adds a paper-grade rerun scaffold and shows a local quick L2-logistic confirmation of pulse-level target-vs-random-electrode separability on raw spike-count features.

Not allowed yet:

> BioGPU has proven a final general computational advantage over GPUs.

## Main outputs

- `outputs/realdata_zenodo_14363732_v17_paper_grade/v17_readout_paper_grade_summary.json`
- `outputs/realdata_zenodo_14363732_v17_paper_grade/v17_repeated_seed_rows.csv`
- `outputs/realdata_zenodo_14363732_v17_paper_grade/v17_grouped_summary.csv`
- `outputs/realdata_zenodo_14363732_v17_paper_grade/PULSE_LEVEL_READOUT_PAPER_GRADE_REPORT.md`

## How to run quick mode

```bash
PYTHONPATH=. python -m biogpu.benchmarks.zenodo_pulse_v17_from_v15 \
  outputs/realdata_zenodo_14363732_v15_readout \
  --out outputs/realdata_zenodo_14363732_v17_paper_grade \
  --negative-counts 1 \
  --negative-seeds 101 \
  --readouts logistic_l2 \
  --feature-sets raw_candidate_counts_only \
  --label-shuffles 1
```

## How to run larger mode

Use `docs/V17_PAPER_GRADE_RERUN_PLAN.md`.
