# BioGPU-Core v5.25 BioSDK Release-Candidate Evidence Guide

v5.25 packages the current proof layer into a release-candidate evidence manifest for BioSDK review.

It is not an installable production SDK release. It is the evidence checklist that says the current public, user-upload and read-only external export proof can be reviewed together without jumping to BiC OS.

## Evidence Inputs

- v5.12 BioSDK evidence kernel
- v5.13 BioSDK core API facade
- v5.14 sample acquisition gate
- v5.21 cross-dataset evidence matrix
- v5.22 public examples and handoff runbook
- v5.23 safe user-upload fixture proof
- v5.24 validated read-only external export proof

## Command

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_biogpu_v525_biosdk_release_candidate_evidence.ps1 -Python "c:/Users/vladi/Desktop/Braine/BiC OS/.venv-1/Scripts/python.exe"
```

## Outputs

- `outputs/v525_biosdk_release_candidate_evidence/V525_BIOSDK_RELEASE_CANDIDATE_EVIDENCE_SUMMARY.json`
- `outputs/v525_biosdk_release_candidate_evidence/V525_BIOSDK_RELEASE_CANDIDATE_CHECKLIST.json`
- `outputs/v525_biosdk_release_candidate_evidence/V525_BIOSDK_RELEASE_CANDIDATE_CHECKLIST.csv`
- `outputs/v525_biosdk_release_candidate_evidence/V525_BIOSDK_RELEASE_CANDIDATE_MANIFEST.json`
- `outputs/v525_biosdk_release_candidate_evidence/BIOGPU_V525_BIOSDK_RELEASE_CANDIDATE_EVIDENCE_REPORT.md`

## Boundary

The package can support a BioSDK release-candidate evidence review. It does not prove full production BioSDK, BioCompute Runtime, live external API control, closed-loop wetware operation or BiC OS readiness.
