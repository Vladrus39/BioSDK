# BioGPU-Core v4.8 — Product Identity

## Decision

Keep **BioGPU-Core** as the technical kernel / repository name / project codename.

Use the following external naming stack:

| Layer | Name | Purpose |
|---|---|---|
| Project codename / core repository | BioGPU-Core | Historical and technical name of the core engine. |
| Main external product | BioCompute Runtime | Manifest-driven runtime for living neural compute workflows. |
| Developer package | BioSDK / Living Compute SDK | Developer-facing SDK for adapters, replay, read-only imports and result bundles. |
| Interface standard | NSI-1.0 / Neural Substrate Interface | Vendor-neutral schema/contract for traces, manifests, bundles, safety profiles and adapters. |
| Hosted/on-prem service | BioCompute Control Plane | Server layer for jobs, users, storage, quotas, audit and dashboards. |
| Long-term target | BioCompute OS | OS-like layer after daemon, scheduler, device/session management, permissions and live safety supervisor exist. |

## What BioGPU-Core is not

BioGPU-Core is not marketed as a direct GPU, CUDA, RTX or LLM accelerator replacement. The name BioGPU remains useful as an internal project identity, but all external claims must describe the project as **BioCompute Runtime / BioSDK for living neural compute** until live evidence proves a narrow task advantage.

## Recommended one-line description

**BioGPU-Core is the technical kernel of BioCompute Runtime: a BioSDK and vendor-neutral interface layer for replaying, benchmarking and eventually integrating living neural compute substrates through datasets, MEA/HD-MEA exports, wetware APIs, readouts, safety policies and reproducible result bundles.**
