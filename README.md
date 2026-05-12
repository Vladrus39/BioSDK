# BioSDK — Unified Neural Data Library

**v0.1.4 | 7 format adapters | 83 conformance tests | Evidence bundles**

BioSDK is a **unified library** for biological neural data. One `open()` for any format — MEA, EEG, ecephys, Sleep, RNG — with integrity-verified evidence bundles. Think of it as **pandas.read_\* for neural data**.

## Why BioSDK

- **One `open()`, 7 formats**: HDF5 (MCS, Giroldini), NWB (DANDI/Allen), EDF (PhysioNet, OpenNeuro), XLSX (Tressoldi), CSV (GCP2), FinalSpark API.
- **Same features across vendors**: 6 standard features per channel (RMS, MAV, zero-crossings, variance, peak, skewness) — compare MEA from MCS to MEA from Giroldini in one pipeline.
- **Evidence bundles**: Every result is a SHA256-chained, HMAC-signed bundle — manifest + data + results + signatures in one folder. Reproducible, verifiable, tamper-evident. *This is unique to BioSDK — no other neural data library provides this.*
- **Open Core**: MIT (community) + Commercial (enterprise safety/closed-loop).

## Licensing Model: Open Core

| Tier | License | Includes | Price |
|------|---------|----------|-------|
| **Community** | MIT | Format adapters, features, readout, evidence bundles, dashboard | Free |
| **Enterprise** | Commercial | Closed-loop safety controller, managed cloud, SLA, priority support | Contact |

**Why Open Core**: The library must be maximally adopted — MIT ensures zero friction. Revenue comes from enterprise features that labs and companies need for production.

## Install

```bash
# From real PyPI:
pip install biosdk

# From TestPyPI (pre-release):
pip install -i https://test.pypi.org/simple/ biosdk
```

Optional extras:
```bash
pip install "biosdk[dashboard]"   # Web dashboard
pip install "biosdk[mne]"         # EEG/EDF support via MNE
pip install "biosdk[all]"         # Everything
```

## Quick Start

```python
import biosdk

# Open ANY neural data — auto-detects format (HDF5, NWB, EDF, XLSX, CSV)
ds = biosdk.open("recording.h5")

# 6 standard features per channel: RMS, MAV, ZC, VAR, PEAK, SKEW
X = biosdk.features(ds, window_s=1.0)

# Classification readout (Random Forest, Logistic Regression, SVM)
result = biosdk.readout(X, y, classifier="rf")

# Integrity-verified evidence bundle (SHA256-chained, HMAC-signed)
bundle = biosdk.evidence_bundle(result, "my_results")
```

## Format Adapters (7 total)

| # | Adapter | Format | Vendor | Modality | Ch | Hz | Tests |
|---|---------|--------|--------|----------|----|-----|-------|
| 1 | mcs_mea2100 | HDF5 | MCS | MEA | 17 | 500 | 8/8 |
| 2 | dandi_nwb | NWB | DANDI/Allen | ecephys | 5-96 | 100-30k | 8/8 |
| 3 | physionet_edf | EDF | PhysioNet | Sleep/EEG | 7-21 | 100-200 | 8/8 |
| 4 | gcp2_csv | CSV | GCP2 | RNG | 1 | 1/60 | 9/9 |
| 5 | tressoldi_h3 | XLSX | Tressoldi | EEG | 14 | 128 | 9/9 |
| 6 | finalspark_neuroplatform | API | FinalSpark | MEA wetware | 8 | 30k | 41/41* |
| R | giroldini_mea | HDF5 | Giroldini | MEA | 59 | 20k | ref |

*\* FinalSpark: adapter skeleton built. Conformance tested on mocks (41/41). Awaiting API token for live validation.*

**Conformance total: 42 certified + 41 mock = 83/83 PASS**

## Validated Results

All numbers are current-snapshot values. Chance rates shown for context.

| Dataset | Task | Accuracy | Chance | Improvement |
|---------|------|----------|--------|-------------|
| OpenNeuro ds007558 | Eyes open/closed (2-class) | **83.7%** | 50% | 1.7x |
| Sleep PSG (PhysioNet) | Sleep staging (5-class) | **66.7%** | 20% | 3.3x |
| Tressoldi H3 BBI | Stimulus vs rest (2-class) | 64.2% per-pair | 50% | 1.3x |
| Giroldini MEA | 4-class stimulus | 52.4% | 25% | 2.1x |
| Cross-vendor MEA | Giroldini vs MCS | 100% separable | 50% | 2.0x |

**Honest baseline**: sklearn SVM achieves 50.7% on the same Giroldini MEA task. BioSDK's pipeline adds +1.7 percentage points. The value is in the unified API + evidence bundles, not in algorithmic edge over standard classifiers.

### Cross-Modal Structure

NSI-1.0 features preserve modality identity — same modality clusters together, different modalities separate:

| Modality cluster | Correlation | Interpretation |
|-----------------|-------------|----------------|
| MEA (Giroldini-MCS-DANDI) | 0.90-0.96 | Same modality, different vendors |
| EEG (OpenNeuro-Sleep) | 1.00 | Same modality, same format (EDF) |
| Cross-modality (MEA vs EEG vs RNG) | ~0.00 | Different physical phenomena — correct behavior |

## What BioSDK Is NOT

- ❌ NOT a new file format (NWB, EDF, HDF5 already exist — BioSDK is a unified loader, not a replacement)
- ❌ NOT an operating system ("BiC OS" was an early working name — the project is a Python library)
- ❌ NOT a biological computer, GPU replacement, or energy platform
- ❌ NOT production-hardened for live stimulation (closed-loop safety gates are designed and simulator-tested; hardware validation pending FinalSpark token)

## What's Next

| # | Item | Status |
|---|------|--------|
| 1 | FinalSpark live validation | Application submitted. Awaiting token. |
| 2 | Closed-loop on real hardware | Safety gates designed (7 Shannon limits), simulator-tested. Requires hardware. |
| 3 | Beta participants | Invite packet ready (`beta/BETA_INVITE_PACKET_V93.md`). |
| 4 | Cross-dataset classification | MCS structure proven (silhouette 0.559, 43.5x shuffled). Blocked: no labels. |
| 5 | Additional labeled datasets | CRCNS, 3Brain samples — requires registration/download. |

## Project Identity

| Attribute | Value |
|-----------|-------|
| **Name** | BioSDK (BioCompute Software Development Kit) |
| **Positioning** | Unified neural data library + evidence bundles |
| **Package** | `biosdk` v0.1.4 |
| **License** | Open Core: MIT (community) + Commercial (enterprise) |
| **Author** | Vladislav Dobrovolskii (vladimoryachok@gmail.com) |
| **PyPI** | https://pypi.org/project/biosdk/ |
| **GitHub** | https://github.com/Vladrus39/BioSDK |

## Key Documents

| Document | Path |
|----------|------|
| Master Status | `MASTER_STATUS_V85.md` |
| Session Handoff | `HANDOFF_FOR_DEEPSEEK_2026_05_11.md` |
| Machine Status | `PROJECT_STATUS_V85.json` |
| NSI-1.0 Spec | `docs/standards/NSI_1_0_SPECIFICATION.md` |
| Evidence Bundle Format | `docs/BIOSDK_EVIDENCE_PACK_GUIDE_V512.md` |
| Beta Invite Packet | `beta/BETA_INVITE_PACKET_V93.md` |

## License

- **Community Edition** (this repository): [MIT License](LICENSE) — adapters, features, readout, evidence bundles, dashboard
- **Enterprise Edition**: [Commercial License](COMMERCIAL_LICENSE.md) — closed-loop safety controller, managed cloud, SLA

---

*BioSDK v0.1.4. Unified neural data library. Open Core. Evidence bundles. One `open()` for 7 formats.*
