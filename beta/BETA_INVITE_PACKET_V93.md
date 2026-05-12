# BioSDK Private Beta — Participant Invite Packet v9.3

**Date**: 2026-05-12
**Project**: BioSDK (BioCompute Software Development Kit)
**Positioning**: Vendor-neutral standard for biological neural computation
**Contact**: Vladislav Dobrovolskii, vladimoryachok@gmail.com

---

## What is BioSDK?

BioSDK is a **vendor-neutral standard** for biological neural computation — the
software layer that lets you read, process, and analyze neural data from ANY
source through a single unified interface.

Think of it as:

| Standard | Domain | What it does |
|----------|--------|-------------|
| **Vulkan** | GPUs | Write once, run on any GPU vendor |
| **ROS** | Robotics | Common middleware for robot hardware |
| **FHIR** | Medical data | Standard API for health records |
| **BioSDK** | Biological neural data | Write once, read from any neural sensor |

BioSDK **is NOT** a biological computer, a GPU replacement, or an energy-superior
platform. It's the **software standard** — the "Vulkan for wetware."

---

## Why participate in the private beta?

### What you get

1. **Early access to NSI-1.0** — the Neural Signal Interface standard. Read MEA,
   EEG, ECG, RNG, ecephys data through a single `open()` → `metadata()` →
   `iter_windows()` → `feature_vector()` pipeline.

2. **5 certified adapters** included: MCS MEA2100, DANDI/NWB, EDF (Sleep/EEG),
   CSV (RNG), Tressoldi H3 (EEG). All 42/42 conformance tests passing.

3. **Cross-modal validation**: 6 datasets across 4 modalities (MEA, EEG, Sleep,
   RNG), cross-modal classification accuracy 94.3% (5.7x chance) — proof that
   NSI-1.0 preserves modality identity.

4. **pip-installable**: `pip install biosdk` from test.pypi.org.

5. **Closed-loop ready**: 7/7 safety gates tested on MEA simulator (2615 spikes).
   Shannon-based safety limits: 100 uA, 200 nC, 500 Hz.

6. **Dashboard**: FastAPI on port 8420 with live telemetry.

7. **Your own data**: Plug in your neural data format, get an NSI-1.0 adapter
   certified, and compare across modalities.

### What we ask

1. Install BioSDK and run the smoke test
2. Import one of your own datasets through the NSI-1.0 interface
3. Run at least one benchmark (cross-modal, classification, or feature extraction)
4. Fill the feedback form (5 questions)
5. Optional: evaluate the closed-loop safety gates

**Time commitment**: ~2-4 hours for basic evaluation.

---

## Quick Start (v9.3)

### Prerequisites

- Python 3.10+
- pip
- Optional: h5py (for MEA), mne (for EEG/EDF), openpyxl (for Tressoldi)

### Install

```bash
pip install --index-url https://test.pypi.org/simple/ biosdk==0.1.0
```

### Verify

```python
from biosdk import __version__
print(__version__)

# List available NSI-1.0 adapters
from biogpu.nsi.adapters import list_adapters
print(list_adapters())
# Expected: ['mcs_mea2100', 'dandi_nwb', 'physionet_edf', 'gcp2_csv', 'tressoldi_h3']
```

### Open any neural data

```python
from biogpu.nsi.adapters.edf import EdfAdapter

ad = EdfAdapter()
ds = ad.open("your_eeg_file.edf")
print(f"Channels: {ds.metadata.channel_count}")
print(f"Sample rate: {ds.metadata.sample_rate_hz} Hz")

for window in ad.iter_windows("your_eeg_file.edf", window_s=1.0):
    features = ad.feature_vector(window)
    print(f"Window features: {features.shape}")
    break
```

### Run benchmark

```bash
python -c "
import json, numpy as np
# Load pre-extracted features
from pathlib import Path
feat = np.load('outputs/v90_cross_modal_features/giroldini_mea_features.npy')
print(f'Giroldini MEA features: {feat.shape}')
"
```

---

## What's been validated (v9.3)

| Capability | Status | Detail |
|-----------|--------|--------|
| NSI-1.0 adapters | **5/5 certified** | MCS, DANDI, EDF, GCP2, Tressoldi |
| Conformance tests | **42/42 PASS** | 8+8+8+9+9 |
| Cross-modal features | **6/6 extracted** | MEA, EEG, Sleep, RNG, ecephys |
| Cross-modal classification | **94.3%** | 5.7x chance (6 classes, first-6 features) |
| Within-modality classification | **64.2%** | Tressoldi EEG stimulus vs rest (per-pair) |
| MEA baseline | **52.4%** | Giroldini 4-class (chance 25%) |
| Evidence bundle | **19/19 verified** | Signed, tamper-evident |
| pip install | **PASSED** | Clean-room test on test.pypi.org |
| Closed-loop simulator | **7/7 gates** | 2615 spikes, Shannon limits enforced |
| Dashboard | **RUNNING** | FastAPI on :8420 |

---

## Next on the roadmap

1. **FinalSpark Neuroplatform integration** — NSI-1.0 adapter for remote wetware.
   Application submitted (free university tier). If approved: live closed-loop
   on biological neurons.

2. **Beta participant feedback** — your input shapes v1.0.

3. **Cross-dataset labeled classification** — MEA data with behavioral labels.

4. **Production foundation** — auth, multi-tenant, persistent storage.

---

## Feedback Form

Please fill and return to vladimoryachok@gmail.com:

```
Organization:
Role:
Deployment mode: [local / Docker / on-prem]

Dataset tested:
Adapter used:
Benchmark run:
Did the run complete? [yes / no]

Installation issues:
Data import issues:
Missing features:
Would you evaluate a paid license? [yes / no]
```

---

## References

- **Publication**: Jordan et al. (2024). "Open and remotely accessible Neuroplatform
  for research in wetware computing." Frontiers in AI. doi:10.3389/frai.2024.1376042
- **FinalSpark docs**: https://finalspark-np.github.io/np-docs/welcome.html
- **BioSDK on PyPI**: https://test.pypi.org/project/biosdk/0.1.0/
- **Project handoff**: HANDOFF_FOR_DEEPSEEK_2026_05_11.md

---

*BioSDK v9.3. Vendor-neutral. Pip-installable. 5 adapters. 42/42 tests. Ready for beta.*
