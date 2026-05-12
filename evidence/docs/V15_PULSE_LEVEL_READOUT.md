# BioGPU-Core v1.5 — Pulse-level feature vectors and culture-aware readout

v1.5 turns the Zenodo MEA2100 pulse-window analysis into an actual readout benchmark.

## Input data

Source: uploaded `Pre_processed_MEA_data.zip` extracted locally.

The benchmark uses the real `stimulation_protocols/*_stimulation_protocol.csv` files discovered in v1.3. These files contain explicit `start`, `end`, and `target` fields.

## Feature matrix

One row is built for every real protocol pulse window.

Output file:

```text
outputs/realdata_zenodo_14363732_v15_readout/pulse_feature_matrix.npz
```

Shape on the uploaded dataset:

```text
11547 pulse windows x 354 features
```

Feature construction:

```text
59 electrodes x 6 feature blocks = 354 features
```

Feature blocks:

1. `response_delta_count_eXXX` = post-stimulus count - pre-onset count
2. `response_count_eXXX`
3. `pre_response_count_eXXX`
4. `exact_delta_count_eXXX` = exact protocol-window count - same-duration pre-window count
5. `exact_count_eXXX`
6. `exact_pre_count_eXXX`

The response window is 100 ms after stimulus end.

## Culture-aware train/test split

The readouts use leave-one-culture-out evaluation. This avoids random pulse-level leakage from the same culture/recording.

## Readout 1 — multiclass target ID

Task:

```text
pulse spike-response vector -> stimulated target electrode ID
```

This is intentionally strict. Many target IDs occur in only one culture, so some held-out test labels are unseen during training.

Therefore v1.5 reports:

- all-label accuracy;
- seen-label accuracy, where the held-out target label exists in training;
- top-3 accuracy;
- label-shuffled baseline.

## Readout 2 — target vs random electrode candidate

Task:

```text
candidate electrode response features -> true target electrode or same-pulse random non-target electrode
```

This is the cleaner separability test because it asks whether the true target response is distinguishable from a same-pulse random electrode under leave-one-culture-out evaluation.

## Honest interpretation

v1.5 is a real pulse-level biological separability benchmark. It is not yet a claim that BioGPU outperforms silicon GPUs.

The clean positive result is target-vs-random separability. The multiclass target-ID task remains limited by target/culture coverage and should not be overclaimed.
