# RUN RESULTS — BioGPU-Core v3.5

## Scope

v3.5 performs release hygiene and model hardening:

- real sklearn-backed `logistic_l2_v27` using `sklearn.linear_model.LogisticRegression`;
- real sklearn-backed `linear_svm_v27` using `sklearn.svm.LinearSVC`;
- unified safety boundary under `biogpu/safety/`;
- pyproject and Dockerfile synchronized to the v3.5 release;
- v3.3 real-data sweep CLI extended with optional `--decoders` and `--split-offsets`;
- v3.5 power-PC wrapper scripts added for sklearn decoder sweeps.

## Local checks performed in this environment

```text
py_compile: OK
v2.7 + v3.5 targeted tests: 8 passed
v3.5 release hygiene generator: OK
```

Additional compatibility tests run during the build:

```text
v2.5 / v2.6 / v2.8 / v3.1 / v3.5 targeted set: 31 passed
v3.3 real-data sweep tests: 4 passed
```

## Main output directory

`outputs/realdata_zenodo_14363732_v35_release_hygiene/`

## Claim boundary

No live BioGPU claim. No GPU advantage claim. No wet-lab recipe. No vendor wiring/pinout.
