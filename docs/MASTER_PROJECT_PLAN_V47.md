# BioGPU-Core v4.7 Master Project Plan — Final PC Handoff

## Purpose

v4.7 is the final patch before moving development to a strong PC/server. It keeps the v4.6 clean/evidence structure, restores beta handoff docs, and replaces placeholder heavy-run scripts with explicit commands.

## Current product definition

BioGPU-Core is a BioSDK/runtime for living neural compute and MEA/HD-MEA/wetware replay workflows. It is not yet a live biological GPU and does not claim GPU replacement.

## What is complete in this package

- BioGPU-Core SDK modules.
- Evidence pack with v12/v15/v32/v33/v36 results.
- Pulse feature matrix: `11,547 × 354` in `evidence/outputs/realdata_zenodo_14363732_v15_readout/`.
- External data asset policy for `Pre_processed_MEA_data.zip`.
- Safety boundary: unsafe live actuation blocked by default.
- API/BioLLM/enterprise/beta scaffolding.
- Hosted server scaffold, not production SaaS.
- Power-PC scripts with explicit commands.

## What must be done on the power PC

1. Reproduce smoke and current tests.
2. Validate full `Pre_processed_MEA_data.zip` asset.
3. Reproduce compact v3.3 and v3.6 results.
4. Run `full_shuffle_1000`.
5. Run `extended_methods_5000` if full run is stable.
6. Download and inspect Zenodo raw HDF5/TTL data.
7. Build raw-derived pulse windows.
8. Add DANDI/NWB task parser validation.
9. Add AllenSDK visual benchmark.
10. Measure latency and energy on the fixed host.
11. Package the final PC result bundle.

## Beta access strategy

Early serious testers get maximum safe software access: SDK, Docker/on-prem, replay, data upload, read-only API/mock connectors, BioLLM tool interface, result bundles, and audit logs. Unsafe live control stays gated behind lab/vendor/protocol approval.
