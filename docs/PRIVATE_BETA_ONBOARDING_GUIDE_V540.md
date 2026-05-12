# BioGPU-Core v5.40 Private Beta Onboarding Contract

v5.40 adds a local private beta onboarding and release operations contract over the v5.39 packaged SDK install gate.

It validates:

- private beta handoff boundaries;
- required onboarding artifacts;
- release operations and rollback contract;
- read-only participant/data-mode decisions;
- explicit denial of live actuation, production SLA and public package distribution.

## Run

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_biogpu_v540_private_beta_onboarding.ps1
```

## Outputs

- `outputs/v540_private_beta_onboarding_contract/V540_PRIVATE_BETA_ONBOARDING_SUMMARY.json`
- `outputs/v540_private_beta_onboarding_contract/V540_PRIVATE_BETA_PROGRAM_CONTRACT.json`
- `outputs/v540_private_beta_onboarding_contract/V540_ONBOARDING_ARTIFACTS.json`
- `outputs/v540_private_beta_onboarding_contract/V540_RELEASE_OPERATIONS_CONTRACT.json`
- `outputs/v540_private_beta_onboarding_contract/V540_PARTICIPANT_DECISION_MATRIX.json`
- `outputs/v540_private_beta_onboarding_contract/V540_PARTICIPANT_DECISION_MATRIX.csv`

## Missing real inputs

This proof does not launch an external beta. Real readiness still needs named participants, signed agreements, approved artifact handoff or private registry, signed/provenance release artifacts, clean-room install reports, support roster approval and production incident/rollback authority.

## Boundary

This is a local onboarding contract proof only. It is not external beta readiness, published distribution, production support, full BioSDK, production BioCompute Runtime or BiC OS readiness.
