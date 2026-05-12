# BioGPU-Core v5.35 Tenant Incident Permissions

v5.35 adds a local tenant-aware permission proof over the v5.34 incident ledger.

It validates four narrow runtime properties:

- tenant operators can acknowledge and resolve their own incidents;
- viewers can read but cannot perform write actions;
- cross-tenant operators are denied incident writes;
- ledger validation is limited to incident admins and auditors.

## Why local-only is correct here

The project is still proving contracts, guardrails and audit behavior. Production auth requires identity-provider integration, key rotation, persistent tenant membership and hosted enforcement, so v5.35 keeps all roles as local fixtures.

## Run

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_biogpu_v535_tenant_incident_permissions.ps1
```

## Outputs

- `outputs/v535_tenant_incident_permissions/V535_TENANT_INCIDENT_PERMISSIONS_SUMMARY.json`
- `outputs/v535_tenant_incident_permissions/V535_INCIDENT_PERMISSION_PRINCIPALS.json`
- `outputs/v535_tenant_incident_permissions/V535_INCIDENT_PERMISSION_DECISIONS.json`
- `outputs/v535_tenant_incident_permissions/V535_INCIDENT_PERMISSION_DECISIONS.csv`
- `outputs/v535_tenant_incident_permissions/V535_INCIDENT_PERMISSIONS_AUDIT_BUNDLE.json`
- `outputs/v535_tenant_incident_permissions/BIOGPU_V535_TENANT_INCIDENT_PERMISSIONS_REPORT.md`

## Boundary

This is a deterministic local permission proof. It is not production identity, hosted auth, persistent tenant membership, live external API control or BiC OS readiness.
