# BioGPU-Core v5.0 — Unique Value and First-Mover Goals

## Updated mission

BioGPU-Core is the technical kernel of a vendor-neutral BioCompute Runtime and BioSDK for living neural compute. The project path is:

```text
BioGPU-Core
→ BioSDK / Living Compute SDK
→ BioCompute Runtime
→ NSI-1.0 / Neural Substrate Interface
→ BioCompute Control Plane
→ BiC OS
```

The goal is **not** to claim that we are the first biological computer, not to replace GPUs for LLM inference, and not to bypass existing neurodata standards. The goal is to become the **runtime, interface, evidence and AI-agent operating layer** connecting public neural datasets, MEA/HD-MEA exports, wetware APIs, LLM/agent workflows, safety policies and reproducible result bundles.

## What can be unique

### 1. Vendor-neutral Neural Substrate Interface

A single interface for multiple substrates and sources:

- Zenodo preprocessed and raw HDF5 data.
- NWB/DANDI task-aligned datasets.
- AllenSDK visual coding datasets.
- FinalSpark read-only/live-shadow data.
- Cortical-like APIs and HDF5 recordings.
- MCS / 3Brain / Axion vendor exports.
- Private user-uploaded data.

**Target claim:** not first wetware computer, but a first-class vendor-neutral interface/runtime for living neural compute workflows.

### 2. Evidence Ledger / Result Bundle Standard

Every run must produce a reproducible result bundle:

- task manifest;
- dataset checksum/source;
- split policy;
- model/decoder config;
- metrics;
- shuffle/negative controls;
- bootstrap confidence intervals;
- plots/tables;
- audit log;
- claim maturity level.

**Target claim:** biological compute results should be auditable like software builds, not just demos.

### 3. LLM/Agent Bridge

The LLM should not directly control biology. It should:

1. propose a safe BioCompute task;
2. generate/validate a manifest;
3. run replay/read-only/live-shadow jobs;
4. consume structured result bundles;
5. ask for human/lab approval before any actuation.

**Target claim:** a structured, safety-aware bridge between LLM agents and living neural compute.

### 4. Safety-graded maximum access

Early testers should get maximum software access:

- SDK;
- Docker/on-prem;
- replay;
- upload own data;
- benchmarks;
- BioLLM tools;
- result bundles;
- read-only/live-shadow API connectors.

But live biological actuation remains gated:

- no free-form stimulation;
- no unapproved electrode commands;
- no wet-lab/environment controls;
- no vendor write mode without approval;
- no uncontrolled closed loop.

### 5. Cross-dataset biological compute benchmark suite

The project must prove that its runtime works beyond one archive:

- Zenodo MEA preprocessed;
- Zenodo raw HDF5/TTL;
- DANDI/NWB;
- AllenSDK visual coding;
- FinalSpark/exported organoid data;
- vendor exports;
- private beta data.

### 6. Adapter conformance tests

Every adapter should pass a standard conformance suite:

- metadata extraction;
- trace conversion;
- safety declaration;
- feature batch generation;
- result bundle creation;
- claim-level annotation.

### 7. BiC OS path

BiC OS should eventually include:

- NSI kernel;
- LLM/agent bridge;
- experiment orchestrator;
- safety supervisor;
- adapter marketplace/plugin layer;
- evidence ledger;
- dashboard/control plane;
- lab approval workflow;
- live telemetry;
- dataset/result storage.

## What we can prove before lab access

Before live biological experiments we can still prove:

- clean-machine reproducibility;
- stable dataset import;
- lineage-strict split performance;
- shuffle and bootstrap controls;
- cross-dataset adapter compatibility;
- NSI schema validity;
- BioLLM safe tool interface;
- result bundle reproducibility;
- hosted/on-prem job lifecycle.

## What requires external API/lab

- FinalSpark/CL/vendor read-only credential validation.
- Live-shadow mode with real external streams.
- Lab-approved closed loop.
- Biological cartridge stability.
- True live energy/latency comparison.

## Strategic statement

The project should compete as a **vendor-neutral operating/runtime layer for biological neural compute**, not as another vertical wetware device. If we finish power-PC validation and cross-dataset adapters, the strongest claim becomes:

> BioGPU-Core is the kernel of BioCompute Runtime and future BiC OS: a vendor-neutral BioSDK, interface standard, benchmark/evidence system and AI-agent control layer for living neural compute.
