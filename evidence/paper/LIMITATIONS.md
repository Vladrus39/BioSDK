# Limitations v3.0

## Replay is not live hardware

The replay substrate can expose public biological response vectors through BioGPU contracts, but it does not measure live biological latency, stability, adaptation or energy.

## No proven GPU advantage yet

The project includes an energy/performance model, but no live BioGPU measurement has yet established superiority over GPU/CPU baselines.

## Dataset limitations

Public preprocessed datasets may lack complete raw TTL/protocol details. Any pulse-window benchmark must document reconstruction assumptions and controls.

## Wetware boundary

This repository is not a wet-lab SOP. It intentionally avoids operational culturing instructions, live stimulation settings, pinouts, wiring procedures and vendor-specific safety limits.

## Vendor boundary

Vendor adapters are stubs/contracts. A real adapter must be implemented against official SDKs and verified with qualified hardware documentation.
