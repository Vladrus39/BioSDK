# BioGPU-Core v1.9 Run Results

## Scope

v1.9 is an engineering blueprint release. It preserves the v1.8 BioGPU runtime direction and adds:

- real material plan,
- live physical form description,
- hardware architecture,
- software architecture,
- benchmark task registry,
- live MEA dry-run adapter,
- closed-loop replay scaffold,
- power-PC and lab backlog.

## Local run

Command:

```bash
python -m biogpu.benchmarks.biogpu_v19_engineering_analysis \
  --v15-out outputs/realdata_zenodo_14363732_v15_readout \
  --out outputs/realdata_zenodo_14363732_v19_engineering \
  --closed-loop-steps 8 \
  --seed 19
```

Result:

```text
pulse windows: 11,547
features: 354
electrodes: 59
cultures: 18
target classes: 27
closed-loop replay demo steps: 8
```

## Tests

```text
pytest -q tests/test_biogpu_v19_engineering.py
5 passed
```

## Important boundary

v1.9 does not prove live BioGPU operation or GPU superiority. It prepares the engineering framework and live adapter contract.
