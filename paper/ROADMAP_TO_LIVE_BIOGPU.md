# Roadmap to Live BioGPU v3.0

## Phase 1 — Power-PC reproducibility

- Run fixed-manifest v1.7/v2.4 pulse readout with 100-1000 label shuffles.
- Run multi-seed negative sampling sweeps and feature ablations.
- Export paper-grade confidence intervals and all result bundles.
- Run CPU/GPU baseline timing and energy proxy measurements under v2.9 schema.
- Add DANDI/Allen task-aligned runs if datasets are available locally.

## Phase 2 — Vendor backend selection

- Select one bridge platform for first live tests.
- Bind vendor SDK to the v2.5 adapter contract.
- Preserve dry-run mode as a safety gate.

## Phase 3 — Qualified live-lab transition

- Select one MEA/HD-MEA platform and vendor SDK.
- Map vendor backend to the v2.5 adapter contract.
- Use qualified lab SOPs for wetware preparation and maintenance.
- Run dry-run -> replay -> live_lab mode transition with audit/result bundles.
- Measure live latency, stability, reproducibility and energy boundary.

## Phase 4 — Advantage claim testing

- Freeze benchmark and accuracy gate.
- Measure CPU/GPU/neuromorphic baselines.
- Measure live BioGPU boundary power and latency.
- Compare only after successful same-task result bundles.
