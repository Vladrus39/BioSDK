# Draft proposal: BioGPU-Core on Loihi 2 / Lava

## Working title

BioGPU-Core: V1-inspired event-based reservoir benchmarks for biological and neuromorphic compute comparison

## Summary

BioGPU-Core is an open research scaffold for comparing event-driven reservoirs across simulated MEA, neuromorphic hardware and future wetware MEA systems. The current software package implements V1-inspired encoders, reservoir benchmarks, baseline comparisons, energy proxy accounting, HDF5/NWB-like export and hardware-neutral adapters.

We request access to Loihi 2 / Lava-compatible hardware to test whether the same benchmark suite shows better event-efficiency and temporal-memory behavior on real neuromorphic hardware than in the current CPU-based simulated reservoir.

## Motivation

The long-term project goal is to evaluate whether biological or biologically inspired compute substrates can become useful AI co-processors. The near-term goal is narrower and measurable: compare event-driven SNN/reservoir execution against digital baselines on small streaming and memory tasks.

## Current status

Implemented:

- V1-like encoder and orientation banks;
- SimulatedMEA and RealMEAAdapter contracts;
- MaxOne-like dry-run reference adapter;
- delayed-match, streaming, orientation, noise and ablation benchmarks;
- baseline comparison against raw linear/MLP/shuffled reservoirs;
- energy accounting scaffold;
- reproducibility/versioning tools;
- Docker/CLI/API scaffold.

Current conclusion: SimulatedMEA is not enough. The benchmark scaffold is ready, but real event-driven hardware is needed for meaningful next-step evidence.

## Proposed Loihi 2 work

1. Port delayed-match and streaming benchmarks to Lava-compatible SNN implementation.
2. Compare CPU simulated reservoir vs Loihi event-driven execution.
3. Measure latency, event count, energy/power where accessible, accuracy and robustness.
4. Evaluate whether recurrent/event-state dynamics are useful on real neuromorphic hardware.
5. Publish all configs, runs and analysis in a reproducible format.

## Expected outcomes

- A small reproducible benchmark suite for Loihi 2 / Lava.
- Evidence on whether event-driven hardware improves the BioGPU-Core path.
- A bridge between future wetware MEA experiments and neuromorphic hardware experiments.

## Why this fits neuromorphic research

The project focuses on sparse event-driven input, temporal state, local reservoir dynamics, baseline-controlled evaluation and energy-per-task accounting. This aligns with neuromorphic goals better than dense GPU-style matrix benchmarking.

## Needed access

- Loihi 2 / Lava execution environment;
- documentation/examples for event injection and SNN deployment;
- guidance on power/latency measurement conventions;
- permission to publish benchmark code/results if possible.
