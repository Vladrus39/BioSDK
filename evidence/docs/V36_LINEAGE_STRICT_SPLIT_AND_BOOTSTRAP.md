# BioGPU-Core v3.6 — Lineage-Strict Split + Bootstrap Scaffold

v3.6 addresses the main statistical risk left after v3.5: a normal culture
split can still leak base-culture identity when labels such as `40628_13DIV`,
`40628_18DIV`, and `40628_21DIV` are treated as separate cultures. v3.6
parses the base lineage (`40628`) and ensures that all DIV variants are kept
entirely in train or entirely in test.

## Added modules

```text
biogpu/statistics/lineage_split_v36.py
biogpu/statistics/bootstrap_v36.py
biogpu/benchmarks/biogpu_v36_lineage_bootstrap.py
tests/test_biogpu_v36_lineage_bootstrap.py
```

## Scope boundary

This is a software-only replay/statistics layer. It does not provide live
stimulation settings, wet-lab protocols, vendor pinout, wiring, or any GPU
advantage claim.

## Local run

```bash
bash scripts/run_biogpu_v36_local_check.sh
```

## Power-PC direction

v3.6 is not the full heavy result. It prepares stricter split logic and
bootstrap CI aggregation so the next power-PC stage can run larger shuffles
and stronger statistical validation.

## Local result

The included compact local run uses a small shuffle count and restricted decoder/ablation set to stay within this environment. Full sklearn decoder sweeps and 1000+ shuffle runs are intentionally moved to the power-PC scripts.
