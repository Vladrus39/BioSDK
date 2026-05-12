# BioGPU-Core v5.46 Private Registry Auth Feed Contract

v5.46 adds a local private registry authentication and expiring-feed contract over the v5.45 recipient onboarding audit proof.

It validates:

- local token scope and signature checks;
- local private-feed URL/token manifest generation;
- feed expiry denial;
- denial of missing grant, invalid token signature, wrong artifact digest, expired feed, excessive TTL, revoked token, live registry, public registry and production distribution requests;
- registry log export shape with chained local event hashes.

## Run

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_biogpu_v546_private_registry_auth_feed.ps1
```

## Outputs

- `outputs/v546_private_registry_auth_feed/V546_PRIVATE_REGISTRY_AUTH_FEED_SUMMARY.json`
- `outputs/v546_private_registry_auth_feed/V546_AUTH_FEED_POLICY.json`
- `outputs/v546_private_registry_auth_feed/V546_AUTH_FEED_MATRIX.json`
- `outputs/v546_private_registry_auth_feed/V546_EXPIRING_FEED_MANIFEST.json`
- `outputs/v546_private_registry_auth_feed/V546_EXPIRING_FEED_PROBE.json`
- `outputs/v546_private_registry_auth_feed/V546_REGISTRY_LOG_EXPORT_CONTRACT.json`
- `outputs/v546_private_registry_auth_feed/V546_AUTH_FEED_AUDIT_BUNDLE.json`
- `outputs/v546_private_registry_auth_feed/V546_AUTH_FEED_MATRIX.csv`
- `outputs/v546_private_registry_auth_feed/V546_REGISTRY_LOG_EXPORT.csv`

## Missing real inputs

This proof does not configure a live private registry or real package feed. Real readiness still needs a live registry endpoint, registry auth provider integration, account provisioning, registry-enforced signed URL or feed expiry, registry access-log export/retention, recipient notifications and production revoke/yank authority.

## Boundary

This is a local auth/feed contract proof only. It is not real private registry authentication, live registry feed enforcement, public package distribution, full BioSDK, production BioCompute Runtime or BiC OS readiness.
