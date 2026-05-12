# BioGPU-Core Whitepaper v3.0

## Abstract

BioGPU-Core is a research and engineering project for designing a real biological computing accelerator. The project starts from public MEA-derived biological response data, builds a replay substrate and software runtime, defines hardware and wetware reference designs, and prepares a benchmark/energy framework for future live MEA/HD-MEA implementation.

## Goal

Design and implement a real working biological computing accelerator: encoder -> living/replay substrate -> readout -> benchmark -> energy/task comparison.

## Architecture

```text
task -> encoder -> replay/live substrate -> trace/features -> readout -> result -> benchmark/energy accounting
```

For live implementation:

```text
BioGPU runtime -> vendor adapter -> acquisition/stimulation electronics -> MEA/HD-MEA chip -> living neuronal network -> recorded response -> readout
```

## Release lineage

- **v1.2 — condition/spot analysis:** culture-matched baseline-vs-LightStim and spot-level response profile (supported).
- **v1.3-v1.7 — pulse windows and controls:** pulse-window reconstruction, feature vectors, readout, robustness plan (partial).
- **v1.8 — BioGPU runtime core:** BioGPUJob -> substrate -> trace -> result contract (supported).
- **v1.9 — engineering blueprint:** real BioGPU architecture, live MEA interface concept, material visualization (supported).
- **v2.0 — prototype stack:** physical form, connection architecture, lab boundaries (supported).
- **v2.1 — ideal wetware stack:** BioGPU-A1 ideal working sample with dimensions and formulas (partial).
- **v2.2 — hardware blueprint:** BOM, modules, connection table, signal chain, power-PC spec (supported).
- **v2.3 — benchmark registry:** task contracts, metrics, controls and success gates (supported).
- **v2.4 — session manager:** run manifest, audit log, result bundle modes (supported).
- **v2.5 — vendor adapter stubs:** safe vendor-neutral MEA/HD-MEA adapter contracts (supported).
- **v2.6 — encoder layer:** digital task -> abstract biological pattern (supported).
- **v2.7 — readout layer:** features/trace -> prediction/result (supported).
- **v2.8 — closed-loop controller:** task -> encoder -> substrate -> readout -> reward -> next action (supported).
- **v2.9 — energy/performance model:** energy, latency, throughput and baseline comparison model (supported).
- **v3.0 — whitepaper package:** single project narrative, methods, results template, limitations and roadmap (supported).

## Evidence position

The project currently supports a real-data replay and engineering-design claim. It does not yet support a live biological hardware advantage claim. v3.0 separates what is demonstrated, what is scaffolded, and what remains for power-PC or qualified laboratory work.

## Current claim boundary

- No wet-lab recipe is provided as an executable protocol.
- No live stimulation amplitudes, pulse widths, charge densities, pinouts or wiring steps are included.
- Live work requires qualified laboratory SOPs, vendor documentation and applicable safety/ethics review.
- GPU advantage is a future claim requiring measured evidence; v3.0 does not assert it as proven.

## Next milestone

The next major milestone after v3.0 is an end-to-end reproducibility pass: fixed manifest, replay run, result bundle, power-PC statistics and preparation for a vendor-specific live-lab backend.
