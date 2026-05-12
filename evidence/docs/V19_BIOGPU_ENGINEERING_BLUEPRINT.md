# BioGPU-Core v1.9 — Engineering Blueprint

v1.9 fixes the correct direction of the project: **BioGPU is a real biological computing accelerator**, not just an MEA analysis toolkit.

Main flow:

```text
BioGPUJob -> encoder -> living MEA/HD-MEA substrate -> BioGPUTrace -> readout -> BioGPUResult
```

The current public-data replay substrate is used to design and validate the runtime before live hardware exists.

## First real material

Recommended first physical material:

```text
2D lab-grown neuronal culture on MEA/HD-MEA
```

It is natural living biological material, but grown and operated in an engineered chamber/chip/protocol.

## What it looks like

A small transparent dish/cartridge with culture medium and a MEA/HD-MEA electrode grid. Under microscope: live neurons connected by neurites. Outside: amplifier/stimulator, environmental control and controller PC.

## What v1.9 adds

- material plan,
- hardware architecture,
- live MEA dry-run adapter contract,
- benchmark task registry,
- closed-loop replay scaffold,
- claim ladder toward GPU advantage,
- power-PC and lab backlog.

## Boundary

v1.9 does not define biological stimulation safety limits. Live protocols must come from vendor documentation and approved lab procedures.
