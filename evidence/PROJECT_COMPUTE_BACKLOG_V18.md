# BioGPU-Core v1.8 compute and hardware backlog

This file exists so the project does not lose the heavy tasks that should be completed on a stronger PC or in a lab.

## Strong PC tasks

Run:

```bash
bash scripts/run_biogpu_v18_full_on_pc.sh
```

Then, if time allows, increase label shuffles from 100 to 1000 in that script.

Required outputs to return:

```text
outputs/realdata_zenodo_14363732_v18_full_paper_readout/
outputs/realdata_zenodo_14363732_v18_biogpu_core/
```

## Heavy public-data tasks

1. DANDI/NWB task-aligned parser on real NWB files.
2. Allen Brain Observatory orientation/task benchmark.
3. Raw Zenodo HDF5/TTL check if raw files are available.
4. Culture bootstrap confidence intervals with 1000+ repeats.
5. Negative sampling seed sweep with 20+ seeds.
6. Label shuffles with 1000+ permutations.
7. Compare readouts: logistic, linear SVM, ridge, LDA, centroid.
8. Final paper-grade CSV/plots/report generation.

## Lab-only tasks

1. Choose MEA/HD-MEA hardware and vendor SDK.
2. Implement a real adapter behind `BioGPUJob -> BioGPUTrace -> BioGPUResult`.
3. Measure closed-loop latency.
4. Measure device energy and maintenance energy.
5. Validate stability over hours/days/weeks.
6. Compare against CPU/GPU/neuromorphic baselines on fair tasks.

## Current state

v1.8 is a software/runtime milestone, not a final hardware proof.
