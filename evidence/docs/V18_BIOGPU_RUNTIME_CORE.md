# v1.8 BioGPU runtime core

v1.8 is not just another analysis step. It converts the project direction into a BioGPU runtime architecture.

## New code

```text
biogpu/runtime/contracts.py
biogpu/runtime/replay_runtime.py
biogpu/benchmarks/biogpu_v18_runtime_analysis.py
tests/test_biogpu_runtime_v18.py
```

## Runtime contract

```text
BioGPUJob
→ substrate execution
→ BioGPUTrace
→ BioGPUResult
```

This contract is hardware-neutral. It works now with public-data replay and later with a live MEA/HD-MEA adapter.

## Why public data is still useful

The public data are enough to build:

1. the software architecture;
2. the readout stack;
3. reproducible benchmark logic;
4. replay of real biological response vectors;
5. the claim ladder needed before hardware work.

They are not enough to finish the final hardware proof.

## The new substrate

`RealDataReplayBioGPUSubstrate` loads:

```text
outputs/realdata_zenodo_14363732_v15_readout/pulse_feature_matrix.npz
outputs/realdata_zenodo_14363732_v15_readout/pulse_feature_metadata.csv
```

It returns real recorded response vectors through the same interface that future hardware must implement.

## How to run local v1.8 demo

```bash
python -m biogpu.benchmarks.biogpu_v18_runtime_analysis \
  outputs/realdata_zenodo_14363732_v15_readout \
  --out outputs/realdata_zenodo_14363732_v18_biogpu_core \
  --demo-jobs 8
```

## How this moves us toward BioGPU

The project now has a clear separation:

```text
public-data replay BioGPU = software prototype
live MEA/HD-MEA BioGPU = hardware implementation target
paper-grade readout = proof layer
energy/task benchmark = final advantage layer
```
