# BioGPU-Core v5.45 Recipient Onboarding Audit Contract

v5.45 adds a local recipient onboarding audit contract over the v5.44 private registry handoff proof.

It validates:

- named local recipient fixtures;
- local approval records and claim-boundary acknowledgements;
- artifact digest matching for the approved wheel;
- local access-log chaining for allowed handoff recipients;
- expiry denial for expired access windows;
- denial of missing account, missing approval, wrong artifact digest, revoked recipient, live registry, public registry and production distribution requests.

## Run

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_biogpu_v545_recipient_onboarding_audit.ps1
```

## Outputs

- `outputs/v545_recipient_onboarding_audit/V545_RECIPIENT_ONBOARDING_AUDIT_SUMMARY.json`
- `outputs/v545_recipient_onboarding_audit/V545_RECIPIENT_ONBOARDING_POLICY.json`
- `outputs/v545_recipient_onboarding_audit/V545_RECIPIENT_ONBOARDING_MATRIX.json`
- `outputs/v545_recipient_onboarding_audit/V545_RECIPIENT_ACCESS_LOG.json`
- `outputs/v545_recipient_onboarding_audit/V545_ACCESS_EXPIRY_PROBE.json`
- `outputs/v545_recipient_onboarding_audit/V545_RECIPIENT_AUDIT_BUNDLE.json`
- `outputs/v545_recipient_onboarding_audit/V545_RECIPIENT_ONBOARDING_MATRIX.csv`
- `outputs/v545_recipient_onboarding_audit/V545_RECIPIENT_ACCESS_LOG.csv`

## Missing real inputs

This proof does not onboard real recipients into a live private registry. Real readiness still needs recipient identities and organization approvals, private registry account provisioning, registry authentication/authorization integration, signed URL or private feed expiration enforcement, registry access-log export/retention, recipient notifications and production revoke/yank authority.

## Boundary

This is a local onboarding audit contract only. It is not real participant onboarding, live private registry readiness, public package distribution, full BioSDK, production BioCompute Runtime or BiC OS readiness.
