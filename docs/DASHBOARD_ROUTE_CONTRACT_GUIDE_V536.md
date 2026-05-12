# BioGPU-Core v5.36 Dashboard Route Contract

v5.36 adds a local route-contract proof for the future BioCompute Control Plane dashboard.

It validates:

- dashboard route manifest coverage for overview, incidents, incident actions, ledger and permission views;
- DTO/view payload contracts over the v5.35 tenant incident permissions proof;
- viewer write denial, cross-tenant denial and ledger-validation scope checks reused from v5.35;
- no hosted dashboard, browser session security, production auth or BiC OS readiness claim.

## Run

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_biogpu_v536_dashboard_route_contract.ps1
```

## Outputs

- `outputs/v536_dashboard_route_contract/V536_DASHBOARD_ROUTE_CONTRACT_SUMMARY.json`
- `outputs/v536_dashboard_route_contract/V536_DASHBOARD_ROUTES.json`
- `outputs/v536_dashboard_route_contract/V536_DASHBOARD_VIEW_PAYLOADS.json`
- `outputs/v536_dashboard_route_contract/V536_DASHBOARD_ACCESS_MATRIX.json`
- `outputs/v536_dashboard_route_contract/V536_DASHBOARD_ROUTE_CONTRACT_AUDIT_BUNDLE.json`
- `outputs/v536_dashboard_route_contract/BIOGPU_V536_DASHBOARD_ROUTE_CONTRACT_REPORT.md`

## Real data and API requirements before model plus OS

The project should move toward a full model plus BiC OS only after real proof expands beyond local fixtures. Required inputs include public raw neural datasets, validated NWB/DANDI assets, safe vendor or user exports, a non-mock read-only external API/export, production identity, object storage, immutable ledger storage, monitoring and lab approval workflow.

## Boundary

This is a local contract proof. It is not a hosted dashboard, production identity system, browser session security layer, full BioCompute Runtime or BiC OS readiness.
