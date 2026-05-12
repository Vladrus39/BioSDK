# BioGPU v2.0 — Prototype and Lab Boundaries

This version extends v1.9 in two directions:

1. It makes the *real form* of BioGPU more explicit.
2. It documents what can be prepared safely in the repository versus what must wait for a qualified lab and vendor-specific hardware documentation.

## Real material — what BioGPU would be physically

For the first real prototype, BioGPU is planned as a **living neuronal network on a MEA/HD-MEA cartridge**.

High-level physical form:

- a compact transparent cartridge or dish;
- a MEA/HD-MEA chip at the bottom;
- a living neuronal layer spread over the electrode grid;
- acquisition/stimulation electronics outside the chamber;
- environmental control around the cartridge;
- a workstation running BioGPU runtime and benchmarks.

## Important safety/reality note

This repository intentionally **does not contain**:

- step-by-step wet-lab cultivation protocols;
- exact media recipes, concentrations or incubation formulas;
- exact stimulation safety settings for live tissue;
- vendor-specific wiring pinouts.

Those items must come from a qualified lab, approved SOPs, biosafety/ethics review as applicable, and vendor documentation.

## What the repository *does* contain

- BioGPU runtime contracts;
- replay substrate on public data;
- high-level connection architecture;
- benchmark contracts;
- prototype stack specification;
- power-PC backlog and live-lab backlog.
