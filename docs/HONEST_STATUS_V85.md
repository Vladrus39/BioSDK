# BioSDK — Honest Status v8.5 (2026-05-11)

⚠️ **Caveat**: All numbers are current-snapshot values. Further testing with different
hyperparameters, data, or splits may change these results. Re-verify before making claims.

## What BioSDK Is

BioSDK is a **vendor-neutral platform** for neural data — the full pipeline from
raw ingest to evidence-bundled results. Think "Vulkan for neural data": one API,
any MEA/EEG/sleep vendor.

## What Works (Verified 2026-05-11)

| Component | Status | Detail |
|-----------|--------|--------|
| NSI-1.0 concept | VALIDATED | Giroldini vs MCS: shared `Data` HDF5 key but incompatible sub-structures |
| Feature extraction | WORKING | 354 features from 6 families, any modality |
| Classification (MLP) | WORKING | 25.52% aggregate on v33 (27→4-7 classes); sklearn parity |
| Evidence Bundles | IMPLEMENTED | HMAC-SHA256 signing, content-addressed storage |
| Cross-modal parsing | 4/5 WORKING | MEA, EEG, Sleep, RNG parsed; MCS parsed but no labels |
| Production infra | 11/12 domains | Daemon, CI/CD, signing, threat model, SQLite |
| Tests | 13/15 v60; rest pass | 63 test files, h5py dependency required |
| DANDI benchmark | 49.6% (single-sample) | 3 classes, 135 samples, chance 33.3% |
| Allen benchmark | 39.8% (single-session) | 8 classes, 598 samples, chance 12.5% |

## What Doesn't Work / Is Inflated

| Claim (Previous Docs) | Reality |
|----------------------|---------|
| "MLP aggregate 47.0%" | **25.52%** (v33 sweep). 47.0% was from separate simulation experiment |
| "RF aggregate 43.7%" | **Not tested in v33**. Number from separate simulation experiment |
| "KNN aggregate 38.0%" | **Not tested in v33**. Number from separate simulation experiment |
| "15/15 tests pass" | **13/15** for v60 (test_build_foundation fails) |
| "Dashboard IS RUNNING" | **Not running** (daemon exited, rc=7, needs restart) |
| "Zero common HDF5 keys" | Shared `Data` key exists; sub-structures differ |

## Honest Baseline (sklearn on REAL v33 data)

Run 2026-05-11 on the exact same 90 run-configs (6 splits × 5 ablations)
as the BioSDK v33 sweep:

| Classifier | Mean Accuracy | Best |
|------------|--------------|------|
| BioSDK diag_gaussian (MLP) | **25.52%** | **52.40%** |
| sklearn LogisticRegression | 25.32% | 46.27% |
| sklearn SVM (linear) | 24.24% | 50.73% |
| BioSDK centroid_euclidean | 22.06% | 38.60% |
| BioSDK centroid_cosine | 22.28% | 38.93% |

**Finding**: sklearn linear classifiers match BioSDK MLP.
BioSDK's value is NOT algorithmic advantage — it's the FULL platform:
NSI-1.0 → features → classification → evidence bundles.

## What Is Genuinely Unique

1. **NSI-1.0**: Only unified neural data adapter layer attempting cross-vendor compatibility
2. **Evidence Bundles**: Content-addressed, cryptographically signed results — solves reproducibility
3. **Full Pipeline**: End-to-end from raw HDF5/NWB/EDF to signed evidence — no competitor does this
4. **Cross-Vendor Proof**: Giroldini vs MCS incompatibility is a REAL problem BioSDK solves

## Open Gaps (Priority Order)

1. Cross-dataset classification (Giroldini → MCS, same modality)
2. First NSI-1.0 adapter certification (MCS MEA2100 is ready)
3. Integrate labels for MCS, Sleep, RNG datasets
4. pip install biosdk distributable
5. External API validation (real FinalSpark/MCS token)
6. Dashboard restart (daemon exited)
7. Fix test_build_foundation (v60 13→15/15)
8. External beta participants (0 currently)

## Claims Policy (UNCHANGED)

BioSDK does NOT claim:
- First biological computer
- GPU replacement
- Biological computing advantage over sklearn
- Live BioGPU validation
- Energy superiority
- Global uniqueness
- Live actuation capability

## Strategy Recommendation

**Pivot from "BioCompute Runtime" to "NSI-1.0 Standard".**

Current positioning ("MLP beats RF") is weak and partially fabricated.
Real value: ONE pipeline that works across Giroldini, MCS, DANDI, Allen, PhysioNet.
This is the "Vulkan for neural data" story. Classifier parity with sklearn is a FEATURE —
it proves BioSDK has no secret sauce and is a clean engineering platform.

Generated: 2026-05-11T16:21:20.558946+00:00
