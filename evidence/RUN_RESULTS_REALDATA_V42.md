# BioGPU-Core v4.2 Run Results

Status: generated in lightweight environment.

Checks:

- py_compile: OK
- pytest `tests/test_biogpu_v42_dataset_registry.py`: 5 passed
- v4.2 dataset registry generator: OK
- zip integrity: OK

Generator summary:

```json
{
  "version": "v4.2",
  "dataset_count": 7,
  "importer_count": 7,
  "validation_errors": [],
  "live_control_performed": false,
  "p0_datasets": [
    "zenodo_14363732_preprocessed",
    "zenodo_14363732_raw_hdf5"
  ],
  "p1_datasets": [
    "dandi_nwb_discovery",
    "allen_visual_coding_orientation",
    "finalspark_readonly_export",
    "user_uploaded_neural_data"
  ]
}
```

v4.2 is a planning/import-skeleton layer. It does not run large downloads or live API calls.
