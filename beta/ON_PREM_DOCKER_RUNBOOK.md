# BioGPU On-Prem Docker Runbook — v4.7

## Build

```bash
docker build -t biogpu-core:v4.7 .
```

## Smoke run

```bash
docker run --rm biogpu-core:v4.7 bash scripts/run_biogpu_v47_powerpc_smoke.sh
```

## Mount data

```bash
docker run --rm -v $PWD/data/external:/app/data/external biogpu-core:v4.7 \
  bash scripts/import_preprocessed_mea_data_v46.sh data/external/Pre_processed_MEA_data.zip
```

Production hosted deployment still requires persistent database, object storage, auth/API keys, and queue backend.
