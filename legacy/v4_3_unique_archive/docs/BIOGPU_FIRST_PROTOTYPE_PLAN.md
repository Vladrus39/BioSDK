# BioGPU First Prototype Plan

## Stage 1 — Finish replay evidence

Run paper-grade v1.7/v1.9 on strong PC: 1000 shuffles, negative seeds, bootstrap CIs.

## Stage 2 — Select MEA/HD-MEA hardware

Needs stimulation, recording, Python/SDK access, raw/TTL sync, documented safety limits.

## Stage 3 — Prepare biological material

Start with 2D neuronal culture on MEA/HD-MEA.

## Stage 4 — Implement live adapter

Connect vendor backend behind `LiveMEASubstrateAdapter`.

## Stage 5 — Run first live benchmarks

Spontaneous profile, target response validation, random controls, target-vs-nontarget readout, temporal pattern classification.

## Stage 6 — Compare with GPU/CPU

Only after live device works: measure energy, latency, accuracy, data efficiency and adaptation.
