# BioGPU-Core v5.37 Identity Provider Contract

v5.37 adds a local identity-provider contract proof for the future BioCompute Control Plane.

It validates:

- OIDC discovery shape and required claims;
- JWKS public-key rotation contract with no private key material;
- token claim validation for issuer, audience, key id, algorithm, time window, tenant, role and scopes;
- role/scope mapping into the v5.35 incident permission model;
- dashboard access probes over the v5.36 route contracts.

## Run

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_biogpu_v537_identity_provider_contract.ps1
```

## Outputs

- `outputs/v537_identity_provider_contract/V537_IDENTITY_PROVIDER_CONTRACT_SUMMARY.json`
- `outputs/v537_identity_provider_contract/V537_OIDC_DISCOVERY_CONTRACT.json`
- `outputs/v537_identity_provider_contract/V537_JWKS_CONTRACT.json`
- `outputs/v537_identity_provider_contract/V537_IDENTITY_VALIDATION_DECISIONS.json`
- `outputs/v537_identity_provider_contract/V537_IDENTITY_DASHBOARD_ACCESS_PROBE.json`
- `outputs/v537_identity_provider_contract/V537_IDENTITY_PROVIDER_CONTRACT_AUDIT_BUNDLE.json`

## Missing real inputs

No real OIDC/OAuth provider configuration or token was found in the local project. Production auth still requires a real discovery URL, JWKS endpoint, issuer, audience, hosted app registration, persistent tenant membership and dashboard session policy.

## Boundary

This is a local contract proof. It is not real SSO, live token verification, production auth, hosted dashboard security, full BioCompute Runtime or BiC OS readiness.
