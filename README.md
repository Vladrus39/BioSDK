# BioSDK — Vendor-Neutral Standard for Biological Neural Computation

**v0.1.3 | 7 NSI-1.0 adapters | 83 conformance tests | 99.67% cross-modal accuracy**

BioSDK is a **vendor-neutral standard** for biological neural computation.
One API for any neural data: MEA, EEG, ecephys, Sleep, RNG.

**Analogy**: Vulkan for GPUs. ROS for robotics. FHIR for medical data. **BioSDK for neural data.**

## Licensing Model: Open Core

BioSDK follows the **Open Core** model — the standard is free and open,
enterprise features are commercial.

| Tier | License | Includes | Price |
|------|---------|----------|-------|
| **Community** | MIT | NSI-1.0 adapters, features, readout, evidence bundles, dashboard | Free |
| **Enterprise** | Commercial | Closed-loop controller, managed cloud, SLA, priority support | Contact |

**Why Open Core**: the NSI-1.0 standard must be maximally adopted — MIT
ensures zero friction. Revenue comes from enterprise features that labs and
companies need for production: safety-certified closed-loop, managed infrastructure, SLA.

## Install

```bash
pip install -i https://test.pypi.org/simple/ biosdk
```

Optional extras:
```bash
pip install -i https://test.pypi.org/simple/ "biosdk[dashboard]"   # Web dashboard
pip install -i https://test.pypi.org/simple/ "biosdk[mne]"         # EEG/EDF support
pip install -i https://test.pypi.org/simple/ "biosdk[all]"         # Everything
```

*Currently on TestPyPI. Real PyPI coming soon.*

## Quick Start

```python
import biosdk

# Open ANY neural data — auto-detects format
ds = biosdk.open("recording.h5")

# 6 standard features per channel: RMS, MAV, ZC, VAR, PEAK, SKEW
X = biosdk.features(ds, window_s=1.0)

# Classification readout
result = biosdk.readout(X, y, classifier="rf")

# Cryptographically signed evidence bundle
bundle = biosdk.evidence_bundle(result, "my_results")
```

## NSI-1.0 Adapters (7 total)

| # | Adapter | Format | Vendor | Modality | Ch | Hz | Tests |
|---|---------|--------|--------|----------|----|-----|-------|
| 1 | mcs_mea2100 | HDF5 | MCS | MEA | 17 | 500 | 8/8 |
| 2 | dandi_nwb | NWB | DANDI/Allen | ecephys | 5-96 | 100-30k | 8/8 |
| 3 | physionet_edf | EDF | PhysioNet | Sleep/EEG | 7-21 | 100-200 | 8/8 |
| 4 | gcp2_csv | CSV | GCP2 | RNG | 1 | 1/60 | 9/9 |
| 5 | tressoldi_h3 | XLSX | Tressoldi | EEG | 14 | 128 | 9/9 |
| 6 | finalspark_neuroplatform | API | FinalSpark | MEA wetware | 8 | 30k | 41/41* |
| R | giroldini_mea | HDF5 | Giroldini | MEA | 59 | 20k | ref |

*\* FinalSpark: skeleton complete, tested on mocks. Awaiting API token.*

**Conformance total: 42 certified + 41 mock = 83/83 PASS**

## Validated Results

| Benchmark | Result | Chance | Improvement |
|-----------|--------|--------|-------------|
| Cross-modal classification | **99.67%** | 16.7% | 6.0x |
| MEA 4-class (Giroldini) | 52.4% | 25% | 2.1x |
| EEG stimulus-vs-rest (Tressoldi) | 64.2% per-pair | 50% | 1.3x |
| Cross-vendor MEA (Giroldini vs MCS) | 100% separable | 50% | 2.0x |

### Cross-Modal Structure

| Modality cluster | Correlation | Interpretation |
|-----------------|-------------|----------------|
| MEA (Giroldini-MCS-DANDI) | 0.90-0.96 | Same modality, different vendors |
| EEG (OpenNeuro-Sleep) | 1.00 | Same modality, same format (EDF) |
| Cross-modality (MEA vs EEG vs RNG) | ~0.00 | Different physical phenomena — CORRECT |

NSI-1.0 preserves modality identity. Different modalities SHOULD be far apart.

## What Remains for Production Launch

| # | Gap | Status |
|---|-----|--------|
| 1 | FinalSpark API token | Application submitted (2026-05-12), awaiting response |
| 2 | Closed-loop on real hardware | 7/7 safety gates tested on simulator. Needs FinalSpark token |
| 3 | Beta participants | Invite packet ready (`beta/BETA_INVITE_PACKET_V93.md`). Needs outreach |
| 4 | Cross-dataset classification (MCS) | Structure proven (silhouette 0.559). Blocked: no labels |
| 5 | Publish to real PyPI | Ready. Waiting for beta feedback |

## Project Identity

| Attribute | Value |
|-----------|-------|
| **Name** | BioSDK (BioCompute Software Development Kit) |
| **Positioning** | Vendor-neutral standard + Python SDK |
| **Package** | `biosdk` v0.1.3 |
| **License** | Open Core: MIT (community) + Commercial (enterprise) |
| **Author** | Vladislav Dobrovolskii (vladimoryachok@gmail.com) |
| **PyPI** | https://test.pypi.org/project/biosdk/ |
| **GitHub** | https://github.com/vladimoryachok/biosdk |

## Key Documents

| Document | Path |
|----------|------|
| Master Status | `MASTER_STATUS_V85.md` |
| Session Handoff | `HANDOFF_FOR_DEEPSEEK_2026_05_11.md` |
| Machine Status | `PROJECT_STATUS_V85.json` |
| NSI-1.0 Spec | `docs/standards/NSI_1_0_SPECIFICATION.md` |
| BioSDK vs FinalSpark | `docs/BIOSDK_VS_FINALSPARK_V95.md` |
| Beta Invite Packet | `beta/BETA_INVITE_PACKET_V93.md` |

## License

- **Community Edition** (this repository): [MIT License](LICENSE) — adapters, features, readout, dashboard
- **Enterprise Edition**: [Commercial License](COMMERCIAL_LICENSE.md) — closed-loop controller, managed cloud, SLA

---

*BioSDK v0.1.3. Open Core. One API for any neural data. 7 adapters. 83 conformance tests. 99.67% cross-modal.*
