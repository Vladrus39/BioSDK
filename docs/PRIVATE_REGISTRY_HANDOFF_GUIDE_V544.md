# BioGPU-Core v5.44 Private Registry Handoff Contract

v5.44 adds a local private registry and artifact handoff contract over the v5.43 release approval proof.

It validates:

- local artifact handoff staging from the approved wheel;
- dry-run private registry index generation;
- role/channel/digest access decisions;
- denial of missing claim boundary, wrong artifact digest, revoked access, public registry, production distribution and live-actuation requests;
- revocation denylist behavior.

## Run

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_biogpu_v544_private_registry_handoff.ps1
```

## Outputs

- `outputs/v544_private_registry_handoff/V544_PRIVATE_REGISTRY_HANDOFF_SUMMARY.json`
- `outputs/v544_private_registry_handoff/V544_PRIVATE_REGISTRY_HANDOFF_CONTRACT.json`
- `outputs/v544_private_registry_handoff/V544_HANDOFF_ARTIFACT_RECORD.json`
- `outputs/v544_private_registry_handoff/V544_LOCAL_HANDOFF_PACKAGE.json`
- `outputs/v544_private_registry_handoff/V544_HANDOFF_ACCESS_MATRIX.json`
- `outputs/v544_private_registry_handoff/V544_HANDOFF_REVOCATION_PROBE.json`
- `outputs/v544_private_registry_handoff/V544_LOCAL_REGISTRY_INDEX.json`
- `outputs/v544_private_registry_handoff/V544_HANDOFF_ACCESS_MATRIX.csv`

## Missing real inputs

This proof does not configure a live private package registry. Real readiness still needs an actual private registry or artifact repository, registry auth integration, named recipient accounts, signed URL or package feed expiration, artifact retention/audit export and production yank/revoke authority.

## Boundary

This is a local private registry/artifact handoff contract proof only. It is not live private registry readiness, public distribution, production release, full BioSDK, production BioCompute Runtime or BiC OS readiness.
