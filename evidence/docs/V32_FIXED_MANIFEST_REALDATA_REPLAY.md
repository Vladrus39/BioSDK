# BioGPU-Core v3.2 — Fixed-manifest Real-data Replay Runner

v3.2 connects the v1.5 public Zenodo pulse-window feature matrix to the v3.x end-to-end integration path.

## What changes from v3.1

v3.1 used a deterministic toy/dry observation to prove that the software chain works.
v3.2 uses the real pulse-window feature matrix:

- 11,547 pulse windows;
- 354 response features;
- 18 cultures;
- 27 target classes in the full matrix.

## Fixed split

The default split is a deterministic culture-heldout split:

- split strategy: `fixed_stride_culture_holdout`;
- culture stride: `3`;
- held-out culture count: `5`;
- labels are filtered to target IDs that exist in both train and test.

This prevents a random accidental train/test split from being silently changed between runs.

## Output bundle

The runner emits:

- `run_manifest_v32.json`;
- `dataset_profile_v32.json`;
- `split_summary_v32.json`;
- `realdata_readout_summary_v32.json`;
- `realdata_readout_predictions_sample_v32.csv`;
- `realdata_readout_confusion_v32.csv`;
- `shuffled_baseline_v32.csv`;
- `energy_latency_report_v32.json`;
- `audit_log_v32.jsonl`;
- `BIOGPU_V32_REALDATA_REPLAY_REPORT.md`;
- `biogpu_v32_realdata_replay_result_bundle.zip`.

## Boundary

v3.2 is still software-only replay. It does not include live stimulation settings, wet-lab recipes, vendor pinout/wiring, or a GPU advantage claim.
