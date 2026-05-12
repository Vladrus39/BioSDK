# BioGPU Core v2.0 — Honest Project Status

Generated: 2026-05-11

## What This Is

BioGPU Core v2.0 is a **biological neural data classification pipeline**.
Four modules: ingest → features → readout → evidence.

It is NOT an operating system, NOT a GPU replacement, NOT a biological
computer. It extracts 20 features from neural time-series data and runs
classification through 4 decoders, comparing results honestly.

## Current State

- **12 datasets** scanned across 4 formats (HDF5, NWB, EDF, EEGLAB)
- **5 modalities**: MEA, ECoG, EEG, Sleep PSG, RNG
- **4 decoders**: MLP (BioGPU), Logistic Regression, Random Forest, SVM
- **5 feature groups**: amplitude, temporal, spectral, complexity, connectivity
- **Content-addressed evidence** — no self-signing

## Honest Gaps

1. **Synthetic labels** — most datasets lack real experimental condition labels.
   Classification uses synthetic labels (k-means-style grouping).
   This means accuracy metrics are structural, not behavioral.

2. **No live data** — all processing is batch on pre-recorded files.

3. **One main result** — the Giroldini MEA 52.4% accuracy is from one dataset.
   Cross-validation on 12 datasets tests structural consistency, not behavioral.

4. **No external replication** — no independent lab has run this pipeline.

5. **No closed-loop hardware validation** — the safety controller is theoretical.

## Next Steps

1. Integrate real experimental labels from dataset metadata
2. Add streaming data processing mode
3. Add cross-species validation datasets
4. External lab replication package
5. Hardware closed-loop validation (if v2.x warrants it)

## Claims Policy

- First biological computer: NOT CLAIMED
- GPU replacement: NOT CLAIMED
- Live BioGPU proof: NOT CLAIMED
- Energy superiority: NOT CLAIMED
- Global uniqueness: NOT CLAIMED
