# RUN RESULTS — BioGPU v2.2 Hardware Blueprint

## Scope

v2.2 adds the BioGPU-A1 hardware blueprint:

- hardware module map;
- component-class BOM;
- connection table;
- signal chain;
- power-PC spec;
- engineering formulas for bandwidth, storage, latency and energy;
- generator script and tests.

## Local check performed in this environment

```text
in-process compile of new Python files: OK
blueprint build/import: OK
required component set check: OK
connection graph check: OK
formula set check: OK
output generator write check: OK
```

Direct subprocess `pytest` / `py_compile` invocation in this notebook environment timed out, so this release is marked as:

```text
manual functional check OK
normal-shell script included for power-PC / lab workstation
```

## Normal shell command for power-PC / lab workstation

```bash
bash scripts/run_biogpu_v22_local_check.sh
```

## Generated outputs

```text
outputs/realdata_zenodo_14363732_v22_hardware/
  biogpu_a1_hardware_blueprint.json
  BIOGPU_A1_HARDWARE_REPORT.md
  BIOGPU_A1_CONNECTION_TABLE.csv
  BIOGPU_A1_BOM.csv
  v22_hardware_summary.json
  v22_manual_check.txt
```
