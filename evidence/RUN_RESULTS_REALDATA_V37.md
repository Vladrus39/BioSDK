# BioGPU-Core v3.7 Run Results

Target: External API / BioSDK Integration Skeleton.

## Local checks

```text
py_compile: OK
pytest tests/test_biogpu_v37_external_api.py: 6 passed
v3.7 external API generator: OK
```

## Generated output

```text
outputs/realdata_zenodo_14363732_v37_external_api/
├── BIOGPU_V37_EXTERNAL_API_BIOSDK_REPORT.md
├── biogpu_v37_external_api_biosdk_bundle.zip
├── trace_axion_maestro_v37.json
├── trace_finalspark_remote_wetware_v37.json
├── trace_mcs_mea2100_v37.json
├── trace_threebrain_hdmea_v37.json
├── v37_commercial_tiers.csv
├── v37_external_api_metadata.csv
├── v37_external_api_summary.json
├── v37_external_api_trace_summary.csv
└── v37_write_denial_checks.csv
```

## Scope

- metadata/read-only/mock only
- no live output
- no stimulation/control
- commercial SDK tier ladder included
