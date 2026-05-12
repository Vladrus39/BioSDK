# BioGPU-Core v6.0 Production Foundation Guide

v6.0 is the first production infrastructure release. It upgrades the project from 56 local contract proofs toward production-ready BioCompute Runtime and BioSDK.

## What v6.0 Provides

- **ProductionConfig**: centralized configuration for all 12 production domains
- **ProductionBootstrap**: environment initialization (databases, storage, directories)
- **ProductionFoundation**: domain readiness assessment and audit

## 12 Production Domains

| # | Domain | v6.0 Status |
|---|--------|------------|
| 1 | production_identity_provider | Configured |
| 2 | persistent_tenant_membership | Database created |
| 3 | production_object_storage | Storage initialized |
| 4 | hosted_runtime_workers | Pool configured |
| 5 | live_private_registry | Directory ready |
| 6 | trusted_release_signing | Deferred to v6.6 |
| 7 | production_ci_cd_gates | Deferred to v6.7 |
| 8 | security_review_and_threat_model | Deferred to v6.8 |
| 9 | support_incident_system | Database created |
| 10 | notification_provider | SMTP configured |
| 11 | external_beta_acceptance | Database created |
| 12 | os_service_supervision | Deferred to v6.12 |

## Run

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_biogpu_v60_production_foundation.ps1
```

## Outputs

- `outputs/v60_production_foundation/V60_PRODUCTION_FOUNDATION_SUMMARY.json`
- `outputs/v60_production_foundation/V60_PRODUCTION_FOUNDATION_AUDIT.json`
- `outputs/v60_production_foundation/V60_PRODUCTION_DOMAIN_MATRIX.csv`
- `outputs/v60_production_foundation/V60_BOOTSTRAP_RESULT.json`
- `outputs/v60_production_foundation/V60_CONFIG_SNAPSHOT.json`
- `outputs/v60_production_foundation/V60_PRODUCTION_FOUNDATION_REPORT.md`

## Configuration

Environment variables (prefix `BICOS_`):
- `BICOS_ENVIRONMENT` — development | staging | production
- `BICOS_PRODUCTION_MODE` — true | false
- `BICOS_IDENTITY_JWT_SECRET` — JWT signing secret
- `BICOS_WORKER_POOL_SIZE` — number of worker processes
- `BICOS_STORAGE_BACKEND` — local | s3 | minio

Or create `configs/production_config_v60.json`.

## Boundary

v6.0 validates production environment bootstrap and domain readiness. It does not claim production deployment, external signoff, or BioSDK production readiness until all 12 domains are closed.
