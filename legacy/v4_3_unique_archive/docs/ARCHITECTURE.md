# BioGPU Architecture

## Core idea

BioGPU is a substrate-independent biological/neuromorphic compute architecture:

```text
InputPattern → EventStream → StimPattern → ComputeSubstrate → SpikeTrain → FeatureVector → Decoder → Output
```

## Substrates

- `SimulatedMEA`: current MVP.
- `RealMEA`: future classic MEA adapter.
- `HD-MEA`: future MaxOne-like high-density platform.
- `OrganoidMEA`: long-term 3D/wetware target.
- `NeuromorphicChip`: Loihi/SpiNNaker-like target.
- `MemristorArray`: compute-in-memory target.

## Current proof point

Run Orientation Detection to validate the pipeline, not biological superiority.
