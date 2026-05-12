# RUN RESULTS — BioGPU v3.3 Paper-grade Real-data Sweep

## Scope

v3.3 performs a compact software-only real-data replay sweep over the v1.5 Zenodo pulse-window feature matrix.

It adds:

- multiple culture-heldout split offsets;
- multiple offline decoders;
- feature ablations;
- shuffled-label negative controls;
- paper-ready CSV tables;
- a result bundle.

## Dataset

- Pulse windows: `11,547`
- Features: `354`
- Cultures: `18`
- Target classes: `27`

## Compact sweep result in this environment

- Runs: `90`
- Decoders: `centroid_euclidean`, `centroid_cosine`, `diag_gaussian`
- Ablations: `all_features`, `response_delta_count`, `response_count`, `pre_response_count`, `exact_features`
- Shuffles per run: `12`

Best compact run:

- Split: `culture_holdout_offset_2`
- Decoder: `diag_gaussian`
- Ablation: `response_delta_count`
- Train windows: `1,525`
- Test windows: `1,500`
- Labels: `4`
- Features: `59`
- Accuracy: `0.524000`
- Balanced accuracy: `0.463750`
- Chance approx: `0.250000`
- Shuffled mean accuracy: `0.234944`
- Improvement vs shuffle mean: `0.289056`
- Empirical p-value, shuffled >= real: `0.076923`

## Local checks

- `py_compile`: OK
- `tests/test_biogpu_v33_realdata_sweep.py`: `4 passed`
- Main runner: OK

## Boundary

No live MEA stimulation settings, no wet-lab protocol, no vendor pinout/wiring, and no GPU advantage claim are included.

## Run command

```bash
bash scripts/run_biogpu_v33_local_check.sh
```
