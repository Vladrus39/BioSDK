# BioGPU implementation roadmap

## Phase A — Public-data BioGPU core

Status: active.

Tasks:

- maintain Zenodo pulse-level matrix;
- run v1.7/v1.8 paper-grade readouts on strong PC;
- add DANDI/NWB task-aligned parser;
- add Allen orientation parser;
- keep software runtime hardware-neutral.

Deliverable:

```text
BioGPU-Core public-data runtime with reproducible readout evidence
```

## Phase B — Real-data replay BioGPU prototype

Status: started in v1.8.

Tasks:

- implement `BioGPUJob` → replay substrate → `BioGPUResult`;
- use replay substrate to test encoders/readouts without lab hardware;
- build a small API for job submission;
- prepare dashboard with claim ladder and current evidence.

Deliverable:

```text
BioGPU software stack that runs against real recorded biological responses
```

## Phase C — Lab hardware integration

Status: future, requires equipment.

Needed:

- MEA/HD-MEA system with stimulation and recording;
- vendor SDK/API access;
- biological culture/organoid support;
- lab safety/ethics procedures;
- TTL/raw stream capture;
- repeatability and stability tests.

Deliverable:

```text
Live BioGPU prototype: encode → stimulate → read → decode
```

## Phase D — Advantage benchmark

Status: future.

Metrics:

- accuracy;
- latency;
- energy per task;
- adaptation/sample efficiency;
- robustness/noise tolerance;
- stability over time;
- comparison against CPU/GPU/neuromorphic baselines.

Deliverable:

```text
Evidence-based claim whether BioGPU is better on specific tasks
```

## Compute backlog for strong PC

Run these after transferring the project to a stronger PC:

```bash
bash scripts/run_biogpu_v18_full_on_pc.sh
```

Minimum recommended for Zenodo full run:

```text
8-16 CPU cores
32 GB RAM
100 GB disk
GPU not required
```

For DANDI/Allen:

```text
32-64 GB RAM
200 GB-1 TB disk
```
