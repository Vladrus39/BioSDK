# BioGPU v2.1 Benchmark Registry

This file mirrors `biogpu/benchmarks/registry_v21.py`.

The registry is the bridge between the ideal BioGPU-A1 physical design and the measurable project goal:

```text
BioGPUJob → BioGPUTrace → feature extraction → readout → benchmark metrics → claim ladder
```

Minimum benchmark groups:

1. `B0_target_vs_random_electrode` — current real-data gate already supported by v1.5-v1.7.
2. `B1_spot_localization` — stronger spatial target classification.
3. `B2_temporal_pattern_classification` — temporal/reservoir task.
4. `B3_orientation_like_task` — bridge to orientation-style tasks.
5. `B4_adaptive_closed_loop` — future live controller.
6. `B5_energy_per_task` — mandatory before any GPU-advantage claim.

The benchmark registry explicitly separates:

- replay/local tasks;
- power-PC heavy compute tasks;
- future live-MEA lab tasks.

No claim that BioGPU is more powerful or more efficient than GPU is valid until `B5_energy_per_task` is measured on real hardware with CPU/GPU baselines.
