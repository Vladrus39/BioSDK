# BioGPU-Core v5.42 Signed Artifact Provenance Contract

v5.42 adds a local signed artifact and provenance contract over the v5.41 clean-room install report proof.

It validates:

- wheel artifact identity and SHA-256 digest;
- local provenance statement generation;
- local HMAC-style integrity signature;
- local signature validation;
- tamper detection for modified provenance;
- explicit denial of trusted external signing, transparency-log inclusion, published distribution, full BioSDK and BiC OS claims.

## Run

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_biogpu_v542_signed_artifact_provenance.ps1
```

## Outputs

- `outputs/v542_signed_artifact_provenance/V542_SIGNED_ARTIFACT_PROVENANCE_SUMMARY.json`
- `outputs/v542_signed_artifact_provenance/V542_PROVENANCE_POLICY.json`
- `outputs/v542_signed_artifact_provenance/V542_ARTIFACT_MANIFEST.json`
- `outputs/v542_signed_artifact_provenance/V542_PROVENANCE_STATEMENT.json`
- `outputs/v542_signed_artifact_provenance/V542_LOCAL_SIGNATURE_ENVELOPE.json`
- `outputs/v542_signed_artifact_provenance/V542_SIGNATURE_VALIDATION.json`
- `outputs/v542_signed_artifact_provenance/V542_PROVENANCE_TAMPER_PROBE.json`
- `outputs/v542_signed_artifact_provenance/V542_PROVENANCE_MATERIALS.csv`

## Missing real inputs

This proof does not provide trusted release signing. Real readiness still needs a trusted signing identity or hardware-backed key, external provenance attestation, transparency log or immutable release ledger inclusion, approved artifact handoff or registry, signed checksum publication and release approval/revocation policy.

## Boundary

This is a local signed artifact provenance contract proof only. It is not trusted external signing, published distribution, full BioSDK, production BioCompute Runtime or BiC OS readiness.
