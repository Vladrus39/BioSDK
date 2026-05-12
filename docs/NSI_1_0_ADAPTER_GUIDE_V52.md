# NSI-1.0 Adapter Guide v5.2

NSI-1.0 is the runtime-facing profile above NWB, HDF5, CSV/vendor exports, read-only APIs and future approved device backends. Adapters should translate their source into NSI objects without replacing the source format.

## Adapter contract

Every adapter must expose a `BioComputeAdapterContract` with:

- `adapter_id`
- `platform`
- `capabilities`
- `read_methods`
- `safety_profile`
- `conformance_tests`

Dataset importers should provide `inspect()` and `import_readonly()`. Vendor/API adapters should provide safe read methods such as `export_metadata()`, `read_spike_stream()` or `read_raw_trace()` when supported.

## Safety profile

Default NSI adapters are replay/read-only. They must block:

- `live_stimulation`
- `electrode_actuation`
- `wetware_environment_control`
- `free_form_vendor_write`

Write methods are only valid with `approved_actuation`, `approval_required=true`, and an external lab/vendor approval record. v5.2 conformance does not enable live actuation.

## Result bundles

Adapters that produce benchmark output should emit or support a `BioComputeResultBundle` containing:

- manifest
- metrics
- audit log
- checksums
- software versions
- claim level

Claim levels must remain conservative. Replay-only and read-only API outputs cannot claim live BioGPU proof, GPU replacement, energy superiority, or production OS status.

## Local conformance

Run the Windows gate:

```powershell
.\scripts\run_biogpu_v52_nsi_interface.ps1 -Python 'c:/Users/vladi/Desktop/Braine/BiC OS/.venv-1/Scripts/python.exe'
```

The gate writes NSI schemas, reference objects, conformance reports and result-bundle validation under `outputs/v52_nsi_interface/`.

Validate a payload directly:

```powershell
biogpu-validate-nsi --schema BioComputeTrace --input trace.json --output trace.validation.json
```

From a source checkout without installing console scripts:

```powershell
python -m biogpu.standards.nsi_cli_v52 --list-schemas
python -m biogpu.cli validate-nsi --schema BioComputeResultBundle --input bundle.json
```

Generate local reference objects:

```powershell
biogpu-validate-nsi --write-reference outputs/nsi_reference_objects
```
