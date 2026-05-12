# BioGPU-A1 Hardware Modules

BioGPU-A1 is divided into modules so replay, dry-run and live operation share the same architecture.

## Module groups

1. **Wetware module** — replaceable living neural cartridge.
2. **Bioelectronic interface** — MEA/HD-MEA chip and dock.
3. **Acquisition/stimulation module** — headstage, amplifier, stimulator, ADC/timestamping.
4. **Life-support module** — environmental control, optional microfluidics, monitoring.
5. **Compute module** — host PC, storage, BioGPU runtime, result bundles.
6. **Governance module** — lab SOP, vendor manuals, safety gates.

## Bridge vs target build

### Bridge build

A bridge build proves software and hardware control using a lower-channel MEA setup.

Expected role:

- validate BioGPUJob/BioGPUTrace/BioGPUResult contract;
- test replay/dry-run/live adapter boundary;
- collect first live traces when qualified lab support exists.

### Target build

A target build moves to HD-MEA scale.

Expected role:

- higher-dimensional reservoir response;
- better spatial encoding;
- real energy/latency measurements;
- comparison against CPU/GPU/neuromorphic baselines.

## Boundary

This is not a pinout/wiring manual and not a live wetware operating protocol.
