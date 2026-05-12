# BioGPU Roadmap to v3.0

This roadmap preserves the plan after v2.3 and anchors the project to the main objective: **design and implement a real working BioGPU**.

## Completed line

- v1.2–v1.7 — public real-data MEA analysis, pulse windows, readout, controls, robustness.
- v1.8 — BioGPU runtime core.
- v1.9 — engineering blueprint and live-MEA interface.
- v2.0 — prototype stack and material/connection boundary.
- v2.1 — ideal BioGPU-A1 wetware stack, dimensions, formulas and safe SOP boundary.
- v2.2 — hardware blueprint, BOM, connection table and signal chain.
- v2.3 — benchmark registry with input, encoder, substrate, readout, metrics, controls and success gates.
- v2.4 — session manager, audit log and result bundle.

## Remaining plan

### v2.5 — Vendor adapter stubs

Create vendor-neutral adapter interfaces and safe stubs for:

- MCS MEA2100-class systems;
- Axion Maestro-class systems;
- 3Brain HD-MEA-class systems;
- remote wetware API backends.

No live pinout or live stimulation settings should be encoded in the repository.

### v2.6 — Encoder layer

Add the layer that converts digital tasks into substrate-facing patterns:

- spatial encoder;
- temporal encoder;
- rate encoder;
- hybrid encoder;
- replay-safe encoder validation.

### v2.7 — Readout/decoder layer

Turn readout into a standalone BioGPU subsystem:

- centroid readout;
- logistic readout;
- linear SVM readout;
- online readout interface;
- standardized feature extraction contracts.

### v2.8 — Closed-loop controller

Add:

- controller loop;
- policy;
- reward/error;
- adaptation;
- replay-first closed-loop experiments.

### v2.9 — Energy/performance model

Prepare:

- CPU/GPU/neuromorphic baselines;
- BioGPU electronics/environment/substrate energy model;
- latency model;
- fair comparison gates.

### v3.0 — Whitepaper / paper package

Assemble:

- BioGPU core whitepaper;
- methods;
- results template;
- limitations;
- roadmap to live BioGPU;
- claim ladder from real-data replay to live-lab proof.

## What must move to strong PC / lab

- 100–1000 shuffles;
- multi-seed negative sampling sweeps;
- bootstrap confidence intervals;
- DANDI/Allen/NWB large dataset runs;
- live MEA/HD-MEA connection;
- measured energy per task;
- any claim that BioGPU is faster or more efficient than GPU.

## v2.8 status

v2.8 adds the closed-loop controller skeleton:

`task → encoder → substrate/replay → feature observation → readout → reward/error → policy decision`.

The current implementation is dry-run/replay safe and does not emit live stimulation or wet-lab parameters.
