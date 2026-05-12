# BioGPU-Core v5.41 Clean-Room Install Report Contract

v5.41 adds a local clean-room install reporting contract over the v5.40 private beta onboarding proof.

It validates:

- isolated target install requirements;
- required clean-room report sections;
- local report fixture completeness;
- optional local wheel build and target-install probe;
- explicit denial of external clean-room readiness, external beta, full BioSDK and BiC OS claims.

## Run

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_biogpu_v541_clean_room_install_report.ps1
```

## Outputs

- `outputs/v541_clean_room_install_report/V541_CLEAN_ROOM_INSTALL_REPORT_SUMMARY.json`
- `outputs/v541_clean_room_install_report/V541_CLEAN_ROOM_ENVIRONMENT_CONTRACT.json`
- `outputs/v541_clean_room_install_report/V541_CLEAN_ROOM_REPORT_SECTIONS.json`
- `outputs/v541_clean_room_install_report/V541_LOCAL_CLEAN_ROOM_INSTALL_PROBE.json`
- `outputs/v541_clean_room_install_report/V541_CLEAN_ROOM_REPORT_FIXTURE.json`
- `outputs/v541_clean_room_install_report/V541_CLEAN_ROOM_REPORT_COMPLETENESS.json`
- `outputs/v541_clean_room_install_report/V541_CLEAN_ROOM_REPORT_SECTIONS.csv`

## Missing real inputs

This proof does not provide an independent external clean-room report. Real readiness still needs an independent machine or CI runner, signed tester identity or automated attestation, approved artifact handoff, a full command transcript from a fresh environment, network isolation/dependency cache evidence and external beta participant approvals.

## Boundary

This is a local clean-room reporting contract proof only. It is not external clean-room readiness, external beta launch, published distribution, full BioSDK, production BioCompute Runtime or BiC OS readiness.
