# BioGPU system architecture

## Layer 1 — Task and input layer

Defines the task BioGPU should solve. Examples:

- target-vs-non-target biological separability
- orientation task
- temporal sequence task
- delayed match task
- future image/signal reservoir tasks

## Layer 2 — Encoder

Maps input into a stimulation or event pattern.

Current modes:

- synthetic spatial encoder
- recorded Zenodo protocol replay
- future task-to-electrode/time encoder

Future lab mode:

- vendor-safe MEA/HD-MEA stimulation plan generated through lab-approved hardware APIs

## Layer 3 — Biological substrate

Current software substrates:

- `SimulatedMEA`
- `RealDataReplayBioGPUSubstrate`
- dry-run `RealMEAVendorNeutralAdapter`

Future substrate:

- live MEA/HD-MEA with biological culture/organoid/neural tissue, maintained under approved lab conditions

## Layer 4 — Reader

Current:

- spike-count features
- pre/post/exact window delta features
- candidate target/non-target feature extraction

Future:

- raw stream features
- bursts/synchrony/phase features
- latency features
- adaptive closed-loop response features

## Layer 5 — Readout

Current:

- nearest centroid
- logistic regression
- linear SVM
- culture-held-out validation
- label-shuffle baseline

Future:

- ridge/LDA/linear probe suite
- online readout calibration
- continual adaptation tests

## Layer 6 — Benchmark and claim ladder

Every claim must climb this ladder:

```text
L0 simulation only
L1 real spike data
L2 pulse-aligned biological response
L3 cross-culture readout
L4 real-data replay BioGPU runtime
L5 live closed-loop lab BioGPU
L6 measurable advantage vs silicon/neuromorphic baselines
```

The current project is moving from L3 to L4.
