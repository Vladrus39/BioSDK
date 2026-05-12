# BioGPU-Core v4.0 — Beta Release Architecture + Full Roadmap

BioGPU-Core is positioned as an Enterprise BioSDK for living neural compute. v4.0 does not claim live BioGPU control. It defines how to deliver the SDK safely and commercially before external beta access.

## Delivery channels

1. Private GitHub / private Python package for technical partners.
2. Hosted BioGPU Server for demo/beta users.
3. Enterprise on-prem Docker for customers that keep data in-house.
4. Lab-Approved Live Add-on as a later premium module only after protocol/operator/vendor gates.

## What changed in v4.0

- Added beta release architecture.
- Added hosted server model and validation endpoint skeleton.
- Added dataset/API expansion plan.
- Added full deferred backlog from earlier phases: power-PC tests, raw HDF5/TTL, DANDI/NWB, AllenSDK, energy/latency, external API credential tests, hosted beta, lab validation.
- Added validation gates before external test access.
- Added machine-readable tables and JSON outputs.

## Current external access default

Mock / replay / read-only only.

Full live wetware control remains blocked until a paid lab-approved module with a protocol ID, operator oversight, vendor/lab approval, safety boundary and audit bundle.

## Main docs

- docs/V40_BETA_RELEASE_ARCHITECTURE.md
- docs/BIOGPU_V40_FULL_DEVELOPMENT_ROADMAP_TO_BETA.md
- docs/BIOGPU_V40_DATASET_API_EXPANSION_PLAN.md
- docs/BIOGPU_V40_POWERPC_VALIDATION_PLAN.md
- docs/BIOGPU_V40_HOSTED_SERVER_ARCHITECTURE.md
- docs/BIOGPU_V40_ENTERPRISE_TEST_ACCESS.md


## v4.3 hosted server scaffold

Adds FastAPI server contract, job model, roles, quotas, result bundle endpoint, and safety-gated job validation.
