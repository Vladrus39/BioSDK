# BioGPU-Core v4.2 — Dataset Registry + Import Skeleton

v4.2 adds the missing dataset expansion layer before private beta. It formalizes which datasets/API sources will be used to prove that BioGPU-Core is not only working on one compact Zenodo-derived matrix.

## Why this version exists

Earlier versions created the SDK/runtime, readouts, safety, external API skeleton, BioLLM tool interface, enterprise packaging, and beta access policy. The next risk is data coverage: one dataset is not enough for a credible beta or enterprise pilot.

v4.2 therefore adds a machine-readable registry for:

- Zenodo 14363732 preprocessed MEA data.
- Zenodo 14363732 raw HDF5/TTL reconstruction.
- DANDI/NWB task-aligned datasets.
- Allen Brain Observatory / AllenSDK orientation-like benchmarks.
- FinalSpark read-only/export/live-shadow data.
- Vendor exports from MCS, 3Brain, and Axion.
- User-uploaded beta tester data.

## Access philosophy

Early testers should receive maximum software-level access: replay, uploads, dataset registry, import dry-runs, BioLLM tool interface, result bundles, and power-PC scripts.

Live biological actuation remains gated. v4.2 does not expose electrode stimulation, pinout, wiring, media/environment control, or free-form closed-loop commands.

## What v4.2 does not do

It does not download multi-GB archives, call live vendor APIs, or perform wet-lab actions. Those are deferred to power-PC, API credential, or laboratory stages.

## Power-PC handoff

The next heavy validation stage must run:

1. Zenodo raw HDF5/TTL reconstruction.
2. DANDI/NWB sample discovery and schema checks.
3. AllenSDK visual coding benchmark extraction.
4. full_shuffle_1000 and extended_methods_5000.
5. bootstrap confidence intervals and final paper tables.
