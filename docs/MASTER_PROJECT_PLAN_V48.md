# BioGPU-Core v4.8 Master Project Plan

## Final naming decision

Keep **BioGPU-Core** as the repository/core name.

Position the project externally as:

```text
BioGPU-Core = technical kernel
BioCompute Runtime = main product
BioSDK / Living Compute SDK = developer layer
NSI-1.0 / Neural Substrate Interface = interface standard
BioCompute Control Plane = hosted/on-prem server layer
BioCompute OS = long-term OS-like commercial target
```

## Goal

Build a vendor-neutral BioCompute Runtime and BioSDK for living neural compute: a reproducible interface, runtime, benchmark suite, adapter layer, safety boundary and result-bundle standard for connecting biological neural data and future wetware compute substrates to AI/LLM/enterprise workflows.

## Near-term before public/private beta

1. Run v4.7 smoke and compact checks on powerful PC.
2. Validate `Pre_processed_MEA_data.zip` via checksum/import script.
3. Run v33 compact and v36 lineage compact.
4. Run full_shuffle_1000.
5. Run extended_methods_5000.
6. Download raw HDF5 and reconstruct TTL/stimulus windows.
7. Add DANDI/NWB and AllenSDK benchmarks.
8. Measure latency/energy on host hardware.
9. Package final PC result bundle.
10. Decide private beta readiness.

## Product path

- v4.8: product identity + NSI draft + OS roadmap.
- v4.9: schema hardening / JSON Schema or Pydantic models.
- v5.0: power-PC validation results.
- v5.1: dataset/API expansion implementation.
- v5.2: hosted/on-prem beta control plane.
- v5.3: private beta with maximum safe software access.
- v6.x: lab-approved live shadow / controlled closed-loop pathway.

## Claim policy

Do not claim direct GPU replacement. Claim only what is supported:

- software/replay BioSDK: supported;
- real-data MEA evidence: supported by included evidence pack;
- lineage-strict signal: preliminary and weaker;
- live BioGPU: not proven;
- GPU advantage: not proven;
- BioCompute OS: roadmap target, not current product.
