# BioGPU Software Architecture

BioGPU-Core uses a hardware-neutral contract:

```text
BioGPUJob -> BioGPUTrace -> BioGPUResult
```

## Current backends

- `RealDataReplayBioGPUSubstrate`: returns real public MEA response vectors.
- `LiveMEASubstrateAdapter`: dry-run contract for future live MEA vendor backend.
- simulated substrates: testing and development.

## Future live backend must implement

```text
connect
configure
encode/stimulate
read response window
synchronize TTL/raw clock
extract features
return BioGPUTrace
```

## Safety

This repository does not provide live stimulation safety parameters.
