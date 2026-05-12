# BioGPU-Core v5.10 Project Alignment and Claim Audit Guide

## Purpose

v5.10 answers a strategic question with local evidence: are we still building the intended BioCompute Runtime / BiC OS path, and what can we honestly claim?

It does not perform an external prior-art search. Therefore it cannot prove global uniqueness. It can prove local artifact coverage, claim discipline and whether current evidence supports or blocks specific statements.

## What It Checks

- Project meaning alignment: NSI, evidence ledger, LLM/agent bridge, control plane and raw-data audit layers.
- Local code distinctness: whether the repository contains the integrated architecture we intended.
- Global uniqueness: explicitly marked as not locally provable.
- Raw-native repeatability: supported only when v5.9 repeatability artifacts pass thresholds.
- Target-ID, live BioGPU, GPU replacement, energy superiority and first-biological-computer claims: blocked or unsupported unless evidence exists.

## Outputs

The runner writes:

- `outputs/v510_project_alignment_claim_audit/V510_PROJECT_ALIGNMENT_SUMMARY.json`
- `outputs/v510_project_alignment_claim_audit/V510_CLAIM_REGISTER.json`
- `outputs/v510_project_alignment_claim_audit/V510_CLAIM_REGISTER.csv`
- `outputs/v510_project_alignment_claim_audit/BIOGPU_V510_PROJECT_ALIGNMENT_CLAIM_AUDIT_REPORT.md`

## Run

```powershell
& .\scripts\run_biogpu_v510_project_alignment_claim_audit.ps1 -Python 'c:/Users/vladi/Desktop/Braine/BiC OS/.venv-1/Scripts/python.exe'
```

## Interpretation

The expected healthy status is `on_mission_with_claim_boundaries`.

That means the project has not drifted away from the vendor-neutral BioCompute Runtime / BiC OS objective, but it still must not claim global uniqueness, live biological compute, GPU replacement, energy superiority or raw equivalence before external and experimental evidence exists.
