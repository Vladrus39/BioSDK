# RUN RESULTS — BioGPU v2.9 Energy / Performance Model

## Scope

v2.9 adds energy and performance accounting models. It is not a live measurement and does not claim BioGPU advantage yet.

## Local check

Expected command:

```bash
bash scripts/run_biogpu_v29_local_check.sh
```

Expected result:

- py_compile OK;
- targeted pytest OK;
- outputs generated under `outputs/realdata_zenodo_14363732_v29_energy/`.
