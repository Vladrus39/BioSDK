# RUN RESULTS — BioGPU v2.4 Session Manager

## Scope

v2.4 adds runtime packaging and auditability:

- run manifest;
- dry-run / replay / power-PC / live-lab mode distinction;
- validation against v2.3 benchmark registry;
- JSONL audit log;
- SHA256 artifact references;
- reproducible result bundle.

## Local check

Expected local command:

```bash
bash scripts/run_biogpu_v24_local_check.sh
```

## Output directory

```text
outputs/realdata_zenodo_14363732_v24_session_manager/
```

Expected files:

```text
run_manifest.json
BIOGPU_V24_RUN_MANIFEST.md
audit_log.jsonl
system_info.json
dry_run_result.json
selected_benchmarks.csv
session_summary.json
biogpu_v24_result_bundle.zip
```

## Boundary

This version still does not contain wet-lab operating recipes, vendor pinouts, or live stimulation limits.


## Actual local verification

```text
py_compile: OK
manual targeted tests: 6 logical checks passed
validation_errors: []
result_bundle: biogpu_v24_result_bundle.zip
```
