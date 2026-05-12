# BioGPU-Core v1.8 run results

v1.8 goal: keep the project focused on the real BioGPU objective by adding runtime contracts and a public-real-data replay substrate.

## Local result

Expected command:

```bash
bash scripts/run_biogpu_v18_local_check.sh
```

Outputs:

```text
outputs/realdata_zenodo_14363732_v18_biogpu_core/v18_biogpu_architecture_manifest.json
outputs/realdata_zenodo_14363732_v18_biogpu_core/v18_biogpu_runtime_summary.json
outputs/realdata_zenodo_14363732_v18_biogpu_core/v18_replay_demo_results.json
outputs/realdata_zenodo_14363732_v18_biogpu_core/v18_replay_demo_results.csv
outputs/realdata_zenodo_14363732_v18_biogpu_core/BIOGPU_V18_RUNTIME_REPORT.md
```

## Meaning

v1.8 does not claim a final working live BioGPU. It establishes the software/runtime form of BioGPU and uses public real biological response vectors as the first execution substrate.

## Next heavy run

```bash
bash scripts/run_biogpu_v18_full_on_pc.sh
```

Then return:

```text
outputs/realdata_zenodo_14363732_v18_full_paper_readout/
outputs/realdata_zenodo_14363732_v18_biogpu_core/
```
