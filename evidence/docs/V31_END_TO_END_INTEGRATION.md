# BioGPU-Core v3.1 — End-to-End Integration Pass

v3.1 wires the project layers into one deterministic software-only run:

```text
run manifest
→ encoder
→ abstract BioGPU pattern
→ replay/dry observation
→ feature batch
→ readout
→ energy/latency accounting
→ audit log
→ result bundle
```

## Purpose

v3.1 is not a new biological result. It is an integration and reproducibility layer. It confirms that the architecture built through v2.4–v2.9 can be run as a single chain under one manifest and exported as an auditable result bundle.

## Included layers

- v2.4 session/result bundle manager;
- v2.6 encoder layer;
- v2.7 readout layer;
- v2.9 energy/performance model;
- v3.0 paper/release boundary.

## Explicit boundary

v3.1 does **not** prove live BioGPU operation and does **not** prove GPU advantage. It performs no live output and includes no wet-lab recipe, pinout, wiring procedure, or live stimulation setting.

## Local command

```bash
bash scripts/run_biogpu_v31_local_check.sh
```
