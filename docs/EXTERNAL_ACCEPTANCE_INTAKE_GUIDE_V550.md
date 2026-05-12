# BioGPU-Core v5.50 External Acceptance Intake Contract

v5.50 adds a local external acceptance evidence schema and real-pilot intake gate over the v5.49 production readiness gap contract.

It validates:

- required external acceptance evidence types;
- local evidence packet schema;
- evidence matrix with real submitter identity and external signature blockers;
- real-pilot intake gate denials;
- local intake packet shape;
- blocker register for real pilot, production and BiC OS claims.

## Run

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_biogpu_v550_external_acceptance_intake.ps1
```

## Outputs

- `outputs/v550_external_acceptance_intake/V550_EXTERNAL_ACCEPTANCE_INTAKE_SUMMARY.json`
- `outputs/v550_external_acceptance_intake/V550_EXTERNAL_ACCEPTANCE_INTAKE_POLICY.json`
- `outputs/v550_external_acceptance_intake/V550_EXTERNAL_ACCEPTANCE_EVIDENCE_SCHEMA.json`
- `outputs/v550_external_acceptance_intake/V550_EXTERNAL_ACCEPTANCE_EVIDENCE_MATRIX.json`
- `outputs/v550_external_acceptance_intake/V550_REAL_PILOT_INTAKE_GATE.json`
- `outputs/v550_external_acceptance_intake/V550_EXTERNAL_ACCEPTANCE_PACKET.json`
- `outputs/v550_external_acceptance_intake/V550_REAL_PILOT_INTAKE_BLOCKER_REGISTER.json`
- `outputs/v550_external_acceptance_intake/V550_EXTERNAL_ACCEPTANCE_AUDIT_BUNDLE.json`
- `outputs/v550_external_acceptance_intake/V550_EXTERNAL_ACCEPTANCE_EVIDENCE_MATRIX.csv`
- `outputs/v550_external_acceptance_intake/V550_REAL_PILOT_INTAKE_GATE.csv`

## Missing real inputs

This proof does not make a real external pilot ready. Real readiness still needs real partner identity records, signed data-use approvals, external security signoff, production identity-provider approval, live registry administrative approval, trusted signing authority approval, CI/CD gate acceptance, support/incident acceptance, notification acceptance and rollback/yank acceptance.

## Boundary

This is a local external acceptance schema and intake-gate proof only. It is not real external pilot readiness, production readiness, full BioSDK readiness, production BioCompute Runtime readiness or BiC OS readiness.
