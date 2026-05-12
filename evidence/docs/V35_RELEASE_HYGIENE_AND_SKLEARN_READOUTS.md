# BioGPU-Core v3.5 — Release Hygiene + Real sklearn Readouts + Safety Core

v3.5 closes the main lightweight-environment fixes identified after the v3.4 audit.

## What changed

1. `logistic_l2_v27` and `linear_svm_v27` are now real scikit-learn-backed models, not centroid placeholders.
2. A unified safety boundary was added under `biogpu/safety/`.
3. Release metadata was synchronized to `3.5.0`.
4. The Docker entrypoint now targets the current v3.5 hygiene generator.
5. v3.3 real-data sweep CLI now accepts `--decoders` and `--split-offsets`.
6. v3.5 power-PC wrappers were added for sklearn-enabled sweeps.
7. v3.5 generates a release hygiene report and machine-readable manifest.

## New readout status

| Decoder id | Status |
|---|---|
| `centroid_v27` | dependency-free centroid model |
| `online_centroid_v27` | online centroid model |
| `logistic_l2_v27` | real `sklearn.linear_model.LogisticRegression` backend |
| `linear_svm_v27` | real `sklearn.svm.LinearSVC` backend |

## Commands

Local v3.5 check:

```bash
bash scripts/run_biogpu_v35_local_check.sh
```

Power-PC smoke with sklearn decoders:

```bash
bash scripts/run_biogpu_v35_powerpc_smoke.sh
```

Power-PC full replay sweep with sklearn decoders:

```bash
bash scripts/run_biogpu_v35_powerpc_full.sh
```

## Claim boundary

v3.5 remains software/replay only. It does not prove live BioGPU operation and does not prove GPU advantage.

## Next phase

The correct next phase is the power-PC statistical run with full shuffles, stricter grouping, bootstrap confidence intervals, and final paper-grade aggregation.
