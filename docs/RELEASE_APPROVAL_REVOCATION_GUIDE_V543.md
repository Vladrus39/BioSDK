# BioGPU-Core v5.43 Release Approval and Revocation Contract

v5.43 adds a local release approval and revocation contract over the v5.42 signed artifact provenance proof.

It validates:

- required local reviewer roles;
- denial of missing claim-boundary acknowledgement;
- denial of unverified local signature/provenance;
- denial of production distribution, full BioSDK and live-actuation requests;
- local release-candidate handoff approval;
- local revocation triggers and handoff blocking.

## Run

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_biogpu_v543_release_approval_revocation.ps1
```

## Outputs

- `outputs/v543_release_approval_revocation/V543_RELEASE_APPROVAL_REVOCATION_SUMMARY.json`
- `outputs/v543_release_approval_revocation/V543_RELEASE_APPROVAL_POLICY.json`
- `outputs/v543_release_approval_revocation/V543_RELEASE_APPROVAL_MATRIX.json`
- `outputs/v543_release_approval_revocation/V543_RELEASE_REVOCATION_POLICY.json`
- `outputs/v543_release_approval_revocation/V543_RELEASE_REVOCATION_DRILL.json`
- `outputs/v543_release_approval_revocation/V543_RELEASE_DECISION_RECORD.json`
- `outputs/v543_release_approval_revocation/V543_RELEASE_APPROVAL_MATRIX.csv`
- `outputs/v543_release_approval_revocation/V543_RELEASE_REVOCATION_EVENTS.csv`

## Missing real inputs

This proof does not approve a production release. Real readiness still needs named release authority, trusted signing/revocation key management, approved registry or artifact handoff channel, external clean-room attestation, transparency log or immutable release ledger inclusion and production rollback/yank/user notification authority.

## Boundary

This is a local release-candidate approval and revocation contract proof only. It is not production release approval, public registry distribution, full BioSDK, production BioCompute Runtime or BiC OS readiness.
