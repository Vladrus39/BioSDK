# BioGPU v4.7 — Final Handoff Checklist

## Files to transfer

- `biogpu-core-v4_7_final_pc_runner_patch.zip`
- `Pre_processed_MEA_data.zip`
- Any raw HDF5 manifest once official URL/checksum is filled.

## Before heavy runs

- [ ] `pip install -e .` completed.
- [ ] `bash scripts/run_biogpu_v47_powerpc_smoke.sh` passed.
- [ ] Full preprocessed ZIP checksum validated.
- [ ] Evidence matrix exists at `evidence/outputs/realdata_zenodo_14363732_v15_readout/pulse_feature_matrix.npz`.
- [ ] Compact v3.3/v3.6 runs completed.

## Heavy statistical runs

- [ ] `full_shuffle_1000` completed.
- [ ] `extended_methods_5000` completed or explicitly postponed.
- [ ] Bootstrap CI tables generated.
- [ ] Results compared against v33/v36 evidence.

## Dataset expansion

- [ ] Raw HDF5 download manifest filled from official source.
- [ ] Raw HDF5 downloaded and checksum verified.
- [ ] TTL/stimulus keys inspected.
- [ ] DANDI/NWB discovery run planned.
- [ ] AllenSDK orientation benchmark planned.

## Release gate

- [ ] Final PC result bundle built.
- [ ] Master plan updated with actual PC results.
- [ ] Beta access decision made from evidence, not claims.
