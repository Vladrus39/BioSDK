# BioGPU-Core v3.0 Claim Ladder

| Claim | Status | Supporting versions | Required next evidence |
|---|---:|---|---|
| C1_real_biological_signal | supported | v1.2, v1.3-v1.7 | Paper-grade rerun with fixed manifest and stronger shuffle controls. |
| C2_replay_biogpu_runtime | supported | v1.8, v2.4 | Power-PC execution using the session/result bundle contract. |
| C3_engineering_feasibility_plan | supported | v1.9, v2.0, v2.1, v2.2, v2.5 | Selection of one concrete vendor platform and qualified lab SOP. |
| C4_full_software_control_loop | supported | v2.3, v2.4, v2.6, v2.7, v2.8 | Integration test that runs registry task -> encoder -> replay substrate -> readout -> result bundle end-to-end. |
| C5_energy_comparison_framework | supported | v2.9 | Measured power logs from CPU/GPU baselines and future BioGPU hardware. |
| C6_live_biogpu_prototype | requires_live_lab | v1.9, v2.0, v2.1, v2.2, v2.5, v2.8 | Qualified live MEA/HD-MEA implementation, vendor SDK backend, lab SOP, safety review and live result bundle. |
| C7_gpu_advantage | planned | v2.3, v2.8, v2.9 | Same-task measured baselines, live BioGPU energy/latency, accuracy gates, statistical confidence intervals. |

## Boundaries

- **C1_real_biological_signal:** This does not yet prove live closed-loop BioGPU operation.
- **C2_replay_biogpu_runtime:** Replay substrate is not a substitute for live tissue latency and energy measurements.
- **C3_engineering_feasibility_plan:** High-level design only; not a live lab protocol or vendor driver.
- **C4_full_software_control_loop:** The current closed-loop is dry-run/replay; no live biological actuation has been performed.
- **C5_energy_comparison_framework:** No actual BioGPU energy advantage is claimed yet.
- **C6_live_biogpu_prototype:** Not yet demonstrated in this repository.
- **C7_gpu_advantage:** This is a future claim, not a present result.
