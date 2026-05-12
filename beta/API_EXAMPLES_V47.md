# BioGPU API Examples — v4.7

## Hosted server health

```bash
curl http://localhost:8000/health
```

## Capabilities

```bash
curl http://localhost:8000/v1/server/capabilities
```

## Create safe replay job

```bash
curl -X POST http://localhost:8000/v1/jobs \
  -H 'Content-Type: application/json' \
  -d '{"job_type":"benchmark","mode":"replay","dataset_id":"zenodo_14363732_preprocessed","decoder":"diag_gaussian","split":"lineage_strict"}'
```

Unsafe live-control fields should be rejected by policy.
