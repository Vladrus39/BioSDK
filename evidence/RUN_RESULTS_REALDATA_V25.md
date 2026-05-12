# RUN RESULTS — BioGPU v2.5 Vendor Adapter Stubs

## Scope

v2.5 adds safe dry-run vendor adapter stubs for future MEA/HD-MEA integration.
It does not execute live hardware output.

## Local checks performed in this environment

- `py_compile`: OK
- `python -m pytest -q tests/test_biogpu_v25_vendor_adapters.py`: `7 passed`
- `bash scripts/run_biogpu_v25_local_check.sh`: OK

## Dry-run summary

```json
{
  "version": "v2.5",
  "scope": "vendor adapter stubs and safe dry-run contract",
  "adapter_count": 4,
  "adapters": [
    "mcs_mea2100_class",
    "axion_maestro_class",
    "threebrain_hdmea_class",
    "finalspark_remote_wetware_class"
  ],
  "live_output_performed": false,
  "dry_run_status": "ok"
}
```

## Output directory

`outputs/realdata_zenodo_14363732_v25_vendor_adapters/`

Main files:

- `v25_vendor_capability_matrix.json`
- `v25_vendor_capability_matrix.csv`
- `v25_vendor_dry_run_results.json`
- `v25_safe_probe_command.json`
- `v25_vendor_summary.json`
- `BIOGPU_V25_VENDOR_ADAPTERS_REPORT.md`

## Safety boundary

v2.5 includes no live vendor backend, no vendor pinout, no physical wiring procedure, no live stimulation values, and no wet-lab protocol. Real hardware support must be implemented later under vendor SDK/manuals, approved lab SOPs and validated safety gates.
