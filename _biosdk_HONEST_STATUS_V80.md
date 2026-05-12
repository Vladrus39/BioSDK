# BioSDK v8.0 — Honest Project Status

Generated: 2026-05-11T13:12:41.060758+00:00

## What This Project Actually Is

BioSDK is an **operating layer for biological neural computation** — not a
desktop OS. Think of it as Kubernetes for living neural networks. It sits
between:

- **Above**: LLM agents, researchers, enterprise users, dashboards
- **Below**: MEA/HD-MEA chips, vendor APIs (FinalSpark, 3Brain, Axion, MCS),
  public datasets (DANDI, Allen, Zenodo), private neural data

## Core Architecture

```
Task -> Encoder -> Living/Replay Substrate -> Trace/Features -> Readout -> Result -> Evidence Bundle
                                                      |
                                              BioSDK Control Plane
                                      (NSI + Safety + Ledger + Dashboard)
```

## What Is Proven (v1.2-v5.56 — the BioGPU Core)

These are **56 local proof gates** on real biological data:

| Layer | Proof | Data Source |
|-------|-------|-------------|
| Spot response | v12 — LightStim vs baseline above chance | Giroldini MEA |
| Pulse features | v15 — 11,547 windows x 354 features | Giroldini MEA |
| E2E replay | v32 — real-data replay above shuffled controls | Giroldini MEA |
| Lineage strict | v36 — stricter split, weaker but honest signal | Giroldini MEA |
| Raw HDF5 map | v5.6 — 42 Zenodo files, EventStream located | Zenodo 14363732 |
| Raw-native benchmark | v5.8 — feature matrix from raw ChannelData | Zenodo 14363732 |
| Raw stability | v5.9 — within-recording repeatability confirmed | Zenodo 14363732 |
| DANDI/NWB parser | v5.15 — real NWB sample validated | DANDI 000469 |
| DANDI benchmark | v5.16 — spike features + shuffled-label readout | DANDI 000469 |
| Allen orientation | v5.20 — orientation benchmark, 2nd dataset | DANDI 000021 |
| External API mock | v5.17 — read-only adapters for 4 vendors | Local mocks |
| Claim audit | v5.10 — project alignment verified, global uniqueness NOT claimed | Local code |

## What Is Built (v6.0-v8.0 — Production Infrastructure)

### Production Foundation (v6.0)
- ProductionConfig — 12-domain centralized configuration
- ProductionBootstrap — environment initialization (3 SQLite DBs, storage, keys)
- ProductionFoundation — domain readiness assessment
- 15 tests passing

### Production Domains Closed (11/12)
1. production_identity_provider — JWT/OAuth2 configured
2. persistent_tenant_membership — tenants.db with schema
3. production_object_storage — local storage with manifest
4. hosted_runtime_workers — worker pool configured (size=4)
5. live_private_registry — packages directory + registry index
6. trusted_release_signing — HMAC-SHA256 key + sign/verify module
7. production_ci_cd_gates — 6-gate matrix + pre-commit hooks
8. security_review_and_threat_model — 5 boundaries, 5 actors, 10 controls
9. support_incident_system — incidents.db with ledger
10. notification_provider — SMTP configured
11. os_service_supervision — daemon + NSSM Windows installer
12. external_beta_acceptance — OPEN (requires real participants)

### BioSDK Core (v7.0)
- BioSDK unlocked: biosdk_phase_locked = false
- 8/6 boot phases ready
- Status: biosdk_production_boot_ready

### BioSDK Subsystems (v7.1-v7.5)
- **Dashboard** (v7.1): FastAPI backend on port 8420, React HTML shell, 6 API endpoints
- **Plugin Manager** (v7.2): adapter registry, manifest loader, certification runner
- **Live Telemetry** (v7.3): stream registration, snapshots, audit bundles
- **Lab Approval** (v7.4): multi-stage workflow (draft -> operator -> safety -> approved, 24h expiry)
- **Closed-Loop** (v7.5): 7 safety gates, kill switch, Shannon limits (100uA, 200nC, 500Hz)

### BioSDK Release (v8.0)
- 23 subsystems inventoried, 17 production-ready
- Deployment manifest (Windows service + Linux systemd)
- Release notes, audit SHA256

## What Is NOT Yet Done (Honest Gaps)

### 1. BioGPU Core Not Run Under Production Daemon
The replay pipeline (v32-v36) has NOT been executed through the v6.12
production daemon or v7.0 scheduler. The daemon is a heartbeat loop
with no actual job execution wired in.

### 2. Zero Live Data in Dashboard
Dashboard shows jobs=0, incidents=0, telemetry=no_live_streams.
No replay run has been triggered through the dashboard API.

### 3. NSI-1.0 Not Integrated With Plugin Manager
The NSI schemas exist (v5.2) but the plugin manager (v7.2) does not
run NSI conformance tests on registered adapters yet.

### 4. No Real External API Validation
v5.17 tested mock adapters. No real FinalSpark/3Brain/Axion/MCS token
or export has been validated. Live telemetry pipeline exists but has
never received a real partner data stream.

### 5. Closed-Loop Never Tested On Hardware
The closed-loop controller (v7.5) has 7 safety gates and Shannon limits
but has NEVER been connected to actual stimulation hardware. All gates
would pass on a theoretical protocol but zero real actuations have occurred.

### 6. External Beta Acceptance Empty
beta_participants.db exists but has zero rows. No real beta participant
has been onboarded.

### 7. Claim Boundaries Still Apply
The project STILL does not claim:
- First biological computer
- GPU replacement
- Live BioGPU proof
- Energy superiority
- Global uniqueness (external prior-art research not done)

### 8. Target-ID Decoding Not Supported
v5.9 explicitly shows target-ID signal is NOT supported on the current
sparse repeated-target raw data subset.

## What BioSDK CAN Do Right Now

1. Boot a production daemon that writes heartbeats
2. Serve a dashboard showing system status (11/12 domains ready)
3. Register, certify, and load adapter plugins
4. Track telemetry streams (when connected)
5. Process lab approval requests through multi-stage workflow
6. Validate stimulation protocols against 7 safety gates
7. Sign release artifacts with HMAC-SHA256
8. Run 6-gate CI/CD pipeline
9. Maintain tamper-evident incident ledger
10. Enforce claim boundaries (no overclaiming)

## What BioSDK CANNOT Do Right Now

1. Run a biological replay pipeline end-to-end through production
2. Connect to a real MEA/HD-MEA device
3. Execute a live closed-loop stimulation session
4. Show non-zero metrics in dashboard
5. Prove cross-vendor adapter portability with real data
6. Accept external beta participants
7. Claim production BioCompute Runtime without external validation

## Next Steps (Priority Order)

1. **Wire replay pipeline to production scheduler**
   - Run v32/v36 replay through daemon
   - Show results in dashboard (jobs > 0)

2. **Validate one real external API**
   - Get a real FinalSpark/MCS read-only token or export
   - Feed through live telemetry pipeline
   - Show in dashboard (telemetry streams > 0)

3. **NSI Plugin Certification**
   - Write a sample adapter plugin manifest
   - Run NSI conformance test through plugin manager
   - Certify the adapter

4. **End-to-End Evidence Bundle**
   - Replay -> Features -> Readout -> Result -> Signed Bundle
   - Store in object storage
   - Verify through evidence ledger

5. **External Beta Onboarding**
   - Onboard at least 1 real beta participant
   - Close external_beta_acceptance gap
   - Achieve 12/12 production domains

## Project Scale

- **Source files**: 70+ benchmark scripts, 32 SDK modules, 21 runtime modules
- **Tests**: 64 test files in tests/current/ (387+ tests at v5.56; 15 new v6.0 tests)
- **Docs**: 90+ markdown guides
- **Outputs**: 50+ evidence bundles in outputs/
- **Versions**: v1.2 through v8.0 — 80+ sequential gates

## Signature

This document is an honest assessment. It does not claim what cannot be proven.
Every claim boundary from the master plan (v5.0) remains in effect.
