# BioGPU Closed-loop Design v2.8

## Controller contract

A closed-loop BioGPU run must record:

- run configuration;
- selected encoder;
- selected substrate mode;
- selected readout;
- every abstract pattern;
- feature observation;
- prediction and confidence;
- reward/error;
- policy decision;
- final status.

## Modes

- `dry_run`: no real substrate, deterministic test path;
- `replay`: public real-data replay substrate;
- `power_pc`: heavy replay/benchmark execution;
- `live_lab_requires_vendor_sop`: future laboratory mode only.

## Acceptance gates

A future live run should not be accepted as evidence unless it includes:

- immutable manifest;
- audit log;
- raw/replay trace reference;
- closed-loop step log;
- negative controls;
- hardware/environment metadata;
- energy/latency metrics when claiming device advantage.
