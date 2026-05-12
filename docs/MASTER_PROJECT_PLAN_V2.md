# BioGPU Core v2.0 — Master Project Plan (Revised)

Generated: 2026-05-11
Previous: MASTER_PROJECT_PLAN_V50.md (v5.56)
Transition: v5.56 → v8.0 infrastructure → v2.0 consolidation

## Why v2.0

After 80+ versions (v1.2–v8.0), the project has been honest about what it
is and what it isn't. The 56 local-proof contracts (v12–v5.56) proved the
pipeline works on one dataset. The production infrastructure (v6.0–v8.0)
wrapped it in enterprise scaffolding.

v2.0 strips the enterprise layer back and consolidates the biological core
into four clean modules:

```
ingest → features → readout → evidence
```

This let us run cross-validation on 12 independent datasets — not just one.

## What v2.0 Changes

### FROM v8.0 (Enterprise Wrapper)
- 23 subsystems, 17 production-ready
- Dashboard, plugin manager, telemetry, lab approval, CI/CD
- Tenant permissions, incident ticketing, release signing
- BiC OS branding with empty daemon

### TO v2.0 (Scientific Core)
- 4 modules: ingest, features, readout, evidence
- 20 universal features in 5 groups
- 4 decoders: MLP (BioGPU), Logistic Regression, Random Forest, Linear SVM
- Content-addressed evidence bundles (no self-signing)
- Cross-validation on 12 datasets

## v2.0 Architecture

```
                    ┌──────────────────────┐
                    │   run_pipeline()     │
                    │   (one entry point)  │
                    └──────────┬───────────┘
                               │
            ┌──────────────────┼──────────────────┐
            │                  │                  │
    ┌───────▼──────┐  ┌───────▼──────┐  ┌───────▼──────┐
    │   ingest/    │  │  features/   │  │  readout/    │
    │ loader_v2.py │  │extractor_v2  │  │classifier_v2 │
    │              │  │              │  │              │
    │ HDF5, NWB,   │  │ 20 features  │  │ MLP, logreg, │
    │ EDF, CSV,    │  │ 5 groups     │  │ RF, SVM      │
    │ EEGLAB, JSON │  │              │  │ + ablation   │
    └──────────────┘  └──────────────┘  └──────────────┘
            │                  │                  │
            └──────────────────┼──────────────────┘
                               │
                    ┌──────────▼───────────┐
                    │   evidence/          │
                    │   bundle_v2.py       │
                    │                      │
                    │ Content-addressed    │
                    │ No self-signing      │
                    └──────────────────────┘
```

## Cross-Validation Results

Pipeline runs ALL datasets through ALL classifiers. Result comparison:

### Feature Groups (for ablation)
1. **amplitude**: mean_amplitude, std_amplitude, peak_to_peak, rms
2. **temporal**: zero_crossing_rate, line_length, skewness, kurtosis
3. **spectral**: delta, theta, alpha, beta, gamma power
4. **complexity**: sample_entropy, hjorth_mobility, hjorth_complexity, hurst
5. **connectivity**: channel_correlation_mean, channel_correlation_std, phase_sync

### Benchmark Decoders
- **MLP** (BioGPU): 2-layer neural net (64, 32)
- **Logistic Regression**: sklearn baseline
- **Random Forest**: 100 trees
- **Linear SVM**: sklearn baseline

### Honest Results Policy
- ALL results reported, no cherry-picking
- No claim of "biological GPU advantage" unless MLP consistently beats baselines
- Every bundle has SHA256 for reproducibility
- Cross-validation summary in `outputs/v2_crossval/V2_CROSSVAL_SUMMARY.json`

## Datasets Tested

| # | Dataset | Format | Source | Modality |
|---|---------|--------|--------|----------|
| 1 | Giroldini Zenodo | HDF5 | BiC OS | MEA |
| 2 | DANDI 000469 | NWB | BiC OS | ECoG |
| 3 | Allen Visual Coding | NWB | BiC OS | ECoG |
| 4 | MCS MEA2100 | HDF5 | BiC OS | MEA (alt vendor) |
| 5 | Sleep PSG SC4001E | EDF | Resonance | Sleep |
| 6 | Sleep PSG SC4002E | EDF | Resonance | Sleep |
| 7 | OpenNeuro ds007558 | EEGLAB | Resonance | EEG |
| 8 | OpenNeuro ds003816 | EEGLAB | Resonance | EEG |
| 9 | Zenodo Heroic | HDF5 | Resonance | MEA |
| 10 | Tressoldi H3 | Various | Resonance | EEG |
| 11 | GCP2 Coherence | CSV | Resonance | RNG |
| 12 | Additional MEA | HDF5 | BiC OS | MEA |

## What v2.0 Does NOT Claim

- **First biological computer** — NOT CLAIMED. We classify pre-recorded data.
- **GPU replacement** — NOT CLAIMED. No GPU comparison performed.
- **Live BioGPU proof** — NOT CLAIMED. No live closed-loop validation.
- **Energy superiority** — NOT CLAIMED. No energy measurements.
- **Global uniqueness** — NOT CLAIMED. Prior art not fully surveyed.
- **BiC OS** — Name retained for continuity only. The project is BioGPU Core v2.0.

## Roadmap v2.0 → v3.0

### v2.1: Real Labels
- Use real experimental labels (stimulus conditions) instead of synthetic
- Requires integrating label metadata from each format

### v2.2: Streaming Mode
- Replace batch sliding windows with real-time streaming processor
- Process data as it arrives, not as pre-recorded files

### v2.3: Cross-Species Validation
- Add rodent, primate, human datasets
- Test whether features generalize across species

### v2.4: Closed-Loop Validation (Hardware)
- Connect closed-loop controller to real stimulation hardware
- Validate all 7 safety gates with real actuation

### v2.5: External Lab Replication
- Package pipeline as pip-installable tool
- Have independent lab run on their own data
- Compare results

### v3.0: BioCompute Runtime (if warranted)
- Only if v2.0–v2.5 demonstrate consistent signal above baselines
- Only if cross-species and cross-lab validation succeed
- Only if external replication confirms results

## Project Inventory (v2.0)

### Active Modules
| Module | Purpose | Status |
|--------|---------|--------|
| `biogpu/core/ingest/` | Universal data loaders | Active |
| `biogpu/core/features/` | 20-feature extractor | Active |
| `biogpu/core/readout/` | 4 decoders + ablation | Active |
| `biogpu/core/evidence/` | Content-addressed bundles | Active |
| `biogpu/core/pipeline_v2.py` | Master runner | Active |

### Archive (Enterprise v6.0-v8.0)
| Module | Purpose | Status |
|--------|---------|--------|
| `biogpu/production/` | Config, bootstrap, daemon | Archived |
| `biogpu/dashboard/` | FastAPI dashboard | Archived |
| `biogpu/plugins/` | Plugin manager | Archived |
| `biogpu/telemetry/` | Live telemetry | Archived |
| `biogpu/lab/` | Lab approval, closed-loop | Archived |
| `biogpu/release/` | Release bundle | Archived |

### Legacy (BioGPU v1.2-v5.56)
| Module | Purpose | Status |
|--------|---------|--------|
| `biogpu/benchmarks/` | 59 benchmark versions | Legacy |
| `biogpu/sdk/` | 32 SDK modules | Legacy |
| `biogpu/runtime/` | 21 runtime modules | Legacy |
| `biogpu/analysis/` | Analysis scripts | Legacy |
| `tests/current/` | 64 test files | Legacy |

## Signature

This is an honest assessment. All claim boundaries are explicit.
The project does not claim what it cannot prove.
