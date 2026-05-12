# BioGPU v3.3 — Paper-grade Real-data E2E Sweep

v3.3 upgrades the v3.2 fixed-manifest real-data replay runner into a compact paper-oriented sweep.

It evaluates multiple culture-heldout split offsets, multiple safe offline decoders, feature ablations, shuffled-label negative controls, and aggregate tables for paper/whitepaper reporting.

## Boundary

This version is still software-only real-data replay. It does not contain live MEA stimulation settings, wet-lab procedures, vendor wiring, or a GPU advantage claim.

## Main outputs

`outputs/realdata_zenodo_14363732_v33_paper_sweep/`

Key files:

- `BIOGPU_V33_PAPER_GRADE_SWEEP_REPORT.md`
- `paper_table_sweep_results_v33.csv`
- `paper_table_shuffle_controls_v33.csv`
- `paper_table_aggregate_by_decoder_v33.csv`
- `paper_table_aggregate_by_ablation_v33.csv`
- `sweep_summary_v33.json`
- `session_summary_v33.json`
- `biogpu_v33_paper_grade_sweep_result_bundle.zip`

## Next heavy-PC step

The compact sweep should be expanded on a powerful PC to 100-1000 shuffles per run, more decoders, bootstrap confidence intervals, and raw HDF5/TTL pulse windows if available.
