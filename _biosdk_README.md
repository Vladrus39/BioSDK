# BioSDK — Vendor-Neutral Standard for Biological Neural Computation

**Status: v8.5 Production | 11/12 domains closed | Cross-modal validation in progress**

BioSDK is a **standard interface** for biological neural computation — not an OS.
Like Vulkan is to GPUs or ROS is to robotics, BioSDK provides a unified way to:

1. **Ingest** neural data from ANY vendor (MEA, NWB, EDF, CSV)
2. **Extract** features (354 per time window)
3. **Classify** neural states (52.4% accuracy on MEA, chance 25%)
4. **Bundle** results as verifiable evidence (SHA256 + HMAC)

## Quick Start

```powershell
# Dashboard
python -m biogpu.dashboard.server_v71
# Open http://127.0.0.1:8420

# Run cross-modal benchmark
python _bic_os_cross_modal.py

# Run all tests (15/15 pass)
pytest tests/current/test_biogpu_v60_production_foundation.py -q
```

## What BioSDK Is

| Attribute | Value |
|-----------|-------|
| Type | Vendor-neutral standard + SDK |
| Scope | Neural data ingest → features → readout → evidence |
| Modalities | MEA, EEG, Sleep PSG, RNG (4 verified) |
| Vendors | Giroldini, MCS, DANDI, Allen, PhysioNet, Tressoldi, GCP |
| Accuracy | 52.4% (chance 25%) on Giroldini MEA |
| License | Research (pre-publication) |

## What BioSDK Is NOT

- ❌ NOT a desktop OS
- ❌ NOT a "first biological computer"
- ❌ NOT a GPU replacement
- ❌ NOT live-BioGPU validated
- ❌ NOT energy-superior
- ❌ NOT globally unique (prior-art pending)

## Architecture

```
Neural Data → NSI-1.0 Ingest → BioCompute Runtime → Evidence Bundle
  (any format)   (unified)     (features+readout)    (signed, verifiable)
```

## Current State

- **11/12** production domains closed
- **5** datasets ready for cross-modal feature extraction
- **6** telemetry streams active (5 replay + 1 MEA simulator)
- **15/15** tests passing
- **Dashboard** running on port 8420 with live data

## Key Documents

- **Master Status**: `MASTER_STATUS_V85.md` ← START HERE
- Deep Audit: `docs/PROJECT_DEEP_AUDIT_V85.md`
- Unique Positioning: `docs/UNIQUENESS_POSITIONING_V85.md`
- Cross-Modal Report: `outputs/v85_cross_modal/V85_CROSS_MODAL_REPORT.md`
- Master Plan: `docs/MASTER_PROJECT_PLAN_V50.md`

---

*Last updated: 2026-05-11T14:44:21.862923+00:00*
*Previous codename: BiC OS / BioGPU-Core*
