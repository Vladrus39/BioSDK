# RUN RESULTS — BioGPU-Core v3.2 Real-data Replay E2E

## Scope

v3.2 connects the v1.5 Zenodo pulse-window feature matrix to the v3.x end-to-end integration path.

## Local checks performed

```text
py_compile: OK
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest tests/test_biogpu_v32_realdata_replay.py: 4 passed
v3.2 real-data replay runner: OK
```

## Real-data replay result

```text
dataset_rows: 11,547
dataset_features: 354
train_windows: 2,700
test_windows: 2,185
overlapping target labels: 7
accuracy: 0.5336384439359267
chance approx: 0.14285714285714285
shuffled-label mean accuracy: 0.15807780320366133
improvement vs shuffle mean: 0.3755606407322654
empirical p-value, shuffled >= real: 0.047619047619047616
```

## Output directory

`outputs/realdata_zenodo_14363732_v32_realdata_e2e/`

## Boundary

This is offline public-data replay only. It does not prove live BioGPU operation or GPU advantage.
