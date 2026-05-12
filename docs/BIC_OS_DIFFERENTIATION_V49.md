# BiC OS Differentiation Plan v4.9

## What BiC OS should become

BiC OS is not just a UI. It is the future operating/control layer for BioCompute workflows.

## Required OS-level modules

```text
1. NSI Kernel
2. LLM/Agent Bridge
3. Experiment Orchestrator
4. Safety Supervisor
5. Adapter Marketplace / Plugin Layer
6. Evidence Ledger
7. BioCompute Dashboard
8. Live Lab Gateway
```

## How it differs from ordinary SDKs

SDKs provide libraries. BiC OS should provide:

```text
persistent service
job scheduler
permissions
adapter lifecycle
dataset/result storage
auditable run bundles
operator approvals
LLM agent interface
live telemetry
```

## How it differs from vendor platforms

Vendor platforms usually optimize for their own hardware/API. BiC OS should support many sources:

```text
Zenodo raw/preprocessed
NWB/DANDI
Allen Visual Coding
FinalSpark exports/API
MCS / 3Brain / Axion exports
future CL-like APIs
private enterprise neural data
```

## How it differs from classic electrophysiology tools

Classic tools record/control experiments. BiC OS must add:

```text
AI/LLM integration
benchmark/evaluation layer
result-bundle evidence
enterprise workflows
safe staged access model
cross-dataset reproducibility
```
