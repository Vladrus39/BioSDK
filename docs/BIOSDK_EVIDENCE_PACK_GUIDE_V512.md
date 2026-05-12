# BioGPU-Core v5.12 BioSDK Evidence Pack Guide

v5.12 makes the BioSDK path evidence-first. Before claiming BiC OS as a full production operating layer, the project must prove a useful BioSDK: stable contracts, real-data support, reproducible evidence bundles, safe agent tasking, governed runtime admission and explicit claim boundaries.

The v5.12 evidence pack is a local proof layer. It collects v5.0-v5.11 artifacts into a capability matrix and answers what is already locally proven, what is partial, and what still blocks a complete BioSDK.

## What v5.12 Checks

- PC validation evidence bundle from v5.0.
- Dataset/import probes from v5.1 plus raw HDF5 availability from v5.6.
- NSI-1.0 schemas, validators and adapter conformance from v5.2.
- Evidence ledger and result-bundle validation from v5.3.
- LLM/agent bridge from v5.4.
- Control-plane admission from v5.5.
- Raw HDF5 structure, raw-native feature extraction and repeatability from v5.6-v5.9.
- Claim supervisor from v5.10.
- BiC OS offline runtime-kernel bridge from v5.11.

## Outputs

The default output directory is `outputs/v512_biosdk_evidence_pack/`.

- `V512_BIOSDK_EVIDENCE_PACK_SUMMARY.json`
- `V512_BIOSDK_CAPABILITY_MATRIX.json`
- `V512_BIOSDK_CAPABILITY_MATRIX.csv`
- `BIOGPU_V512_BIOSDK_EVIDENCE_PACK_REPORT.md`

## Run

```powershell
Push-Location 'C:\Users\vladi\Desktop\Braine\BiC OS\biogpu-core-v5_0_bic_os_first_mover_roadmap'
& .\scripts\run_biogpu_v512_biosdk_evidence_pack.ps1 -Python 'c:/Users/vladi/Desktop/Braine/BiC OS/.venv-1/Scripts/python.exe'
```

The expected healthy status is `biosdk_evidence_kernel_ready_full_sdk_not_claimed`.

That means the local evidence kernel for BioSDK is ready, but the project still must not claim a complete production BioSDK, production BiC OS, global uniqueness, live BioGPU proof, GPU replacement or energy superiority.

## What Would Make It A Real Working Tool

- stable SDK imports and CLI commands;
- real examples for every NSI schema and adapter contract;
- multi-source data import with raw HDF5, NWB/DANDI and vendor exports;
- evidence bundles by default for every run;
- safe LLM-agent tasking with no direct live actuation;
- governed jobs with durable scheduling and repeatable execution;
- docs, tests and acceptance gates that outside users can run.

## What Could Make It Distinct And Wanted

- vendor-neutral living-compute runtime instead of one closed wetware platform;
- evidence-first results rather than demo-first claims;
- agent-native biological compute workflows with safety gates;
- a path from replay and raw data to read-only/live-shadow integrations;
- adapter conformance and future plugin certification for labs and vendors;
- a clean bridge from BioSDK to BiC OS without overclaiming.
