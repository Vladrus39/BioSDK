# Run Results v4.7

v4.7 is a final PC runner patch, not a new scientific benchmark. It validates that the package has evidence paths, runnable power-PC scripts, restored beta docs, and handoff documentation.

## Local sandbox verification

Executed in this environment:

```text
pytest tests/current/test_biogpu_v47_final_pc_patch.py: 5 passed
v4.7 final PC patch validator: ready_for_power_pc_handoff = true
quick v3.3 sanity run: OK using evidence v15 matrix
quick v3.6 lineage sanity run: OK using evidence v15 matrix
```

The smoke script itself is intended for the power PC. In this sandbox, the component checks were executed directly to avoid environment/tool timeout behavior.

## Evidence retained

- `evidence/outputs/realdata_zenodo_14363732_v15_readout/pulse_feature_matrix.npz`
- `evidence/outputs/realdata_zenodo_14363732_v33_paper_sweep/`
- `evidence/outputs/realdata_zenodo_14363732_v36_lineage_bootstrap/`
- `EVIDENCE_INDEX_V46.md`

## Scientific heavy runs scheduled for power PC

- full_shuffle_1000
- extended_methods_5000
- raw HDF5 / TTL reconstruction
- DANDI/NWB parser
- AllenSDK benchmark
- latency/energy measurement
