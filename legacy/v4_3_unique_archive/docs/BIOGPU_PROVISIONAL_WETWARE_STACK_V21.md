# BioGPU v2.1 — Provisional Wetware Stack

This is the current ideal wetware design for the first real BioGPU prototype.

It is a **design hypothesis and bill-of-materials level specification**, not a wet-lab protocol.

## My current ideal path

**2D human iPSC-derived mixed cortical-like neuronal network on MEA/HD-MEA.**

## Why not organoids first?

Organoids are promising, but for the first repeatable BioGPU we need clean stimulation/readout, lower variability, easier microscopy, easier electrode coupling and simpler controls. A 2D MEA/HD-MEA culture is the practical first target.

## Candidate molecular / material stack

1. **Cells:** human iPSC-derived mixed cortical-like neurons, ideally excitatory + inhibitory; optional astrocyte support/co-culture.
2. **Adhesion layer:** MEA-compatible PDL or PEI class coating, selected by vendor/lab SOP.
3. **ECM layer:** laminin-focused layer, optionally fibronectin depending on cells and chip surface.
4. **Medium path A:** BrainPhys-class serum-free neuronal medium for functional electrophysiology.
5. **Medium path B:** Neurobasal Plus + B-27 Plus class system for survival/maturation route.
6. **Supplements:** defined neuronal supplements such as B27/SM1/N2-like systems, glutamine/GlutaMAX-class support, antioxidants and maturation factors according to the cell vendor protocol.
7. **Interface:** MEA/HD-MEA with bidirectional stimulation/readout, timestamped raw acquisition and SDK/API access.

## What can change this design

- exact cell supplier and line;
- 2D versus 3D decision;
- MEA vendor and surface chemistry;
- desired experiment duration;
- regulatory/ethics route;
- budget and local availability;
- whether we prioritize survival, physiological realism, or maximum readout separability.

## Explicit boundary

This repository does **not** define exact concentrations, plating densities, incubation durations, medium-change schedules or live-stimulation limits. Those must come from the selected cell-line vendor, MEA vendor, institutional SOP and lab validation.
