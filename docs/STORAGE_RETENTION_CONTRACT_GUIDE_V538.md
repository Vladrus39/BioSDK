# BioGPU-Core v5.38 Storage Retention Contract

v5.38 adds a local object-storage and retention backend contract proof for the future BioCompute Control Plane.

It validates:

- bucket contracts for result bundles, audit artifacts, retention manifests and ledger roots;
- local JSON object writes with SHA-256 integrity records;
- retention manifest coverage for all stored contract objects;
- local access contracts that require authenticated principals and expose no public internet URL;
- immutable overwrite denial for retention manifests and ledger root anchors.

## Run

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_biogpu_v538_storage_retention_contract.ps1
```

## Outputs

- `outputs/v538_storage_retention_contract/V538_STORAGE_RETENTION_CONTRACT_SUMMARY.json`
- `outputs/v538_storage_retention_contract/V538_STORAGE_BUCKET_CONTRACTS.json`
- `outputs/v538_storage_retention_contract/V538_STORAGE_OBJECT_MANIFEST.json`
- `outputs/v538_storage_retention_contract/V538_STORAGE_INTEGRITY.json`
- `outputs/v538_storage_retention_contract/V538_LOCAL_ACCESS_CONTRACTS.json`
- `outputs/v538_storage_retention_contract/V538_IMMUTABLE_OVERWRITE_PROBE.json`
- `outputs/v538_storage_retention_contract/V538_STORAGE_RETENTION_AUDIT_BUNDLE.json`

## Missing real inputs

No production object-storage configuration was found locally. Production storage still requires a real bucket/account, IAM policy tied to the production identity provider, server-side encryption, versioning and retention locks, remote immutable ledger storage or notarization, backup/restore evidence and signed URL/session policy.

## Boundary

This is a local storage contract proof. It is not production object storage, hosted retention, remote notarization, full BioCompute Runtime or BiC OS readiness.
