# v0.6 notes — pivot from simulated performance to real-signal readiness

## Added

- external review response;
- real-signal pivot plan;
- regression diagnostic module;
- repeated-seed evaluation utilities;
- CLI command `biogpu-run`;
- NWB-like HDF5 export skeleton;
- Loihi/NRC proposal draft;
- MEA lab outreach email;
- lab requirements checklist;
- tests for diagnostics, CLI and HDF5 export.

## Main decision

v0.6 accepts that the simulated reservoir has not produced convincing scientific signal. It remains a valuable interface and reproducibility scaffold, but the next meaningful evidence should come from neuromorphic hardware or real MEA/HD-MEA data.

## New rule

No BioGPU performance claim without repeated-seed, shuffled/random, raw baseline and ablation checks.
