# BioGPU-Core v3.0 Project Summary

## Main goal

Design and implement a real working biological computing accelerator: encoder -> living/replay substrate -> readout -> benchmark -> energy/task comparison.

## Release type

`whitepaper_and_project_package`

## What v3.0 means

BioGPU-Core v3.0 is the project consolidation layer. It does not claim that a live BioGPU has already outperformed a GPU. It consolidates the real-data evidence layer, replay runtime, hardware design, benchmark registry, session/bundle system, encoder/readout/closed-loop software stack and energy comparison model into one whitepaper-grade package.

## Current strongest supported claims

- C1_real_biological_signal: The public MEA dataset contains a real spatial biological response signal usable by BioGPU-Core as an evidence layer.
- C2_replay_biogpu_runtime: A replay BioGPU substrate can expose public biological response vectors through BioGPUJob/BioGPUTrace/BioGPUResult contracts.
- C3_engineering_feasibility_plan: BioGPU-A1 has a coherent engineering design: material, hardware modules, software layers, connection map and run modes.
- C4_full_software_control_loop: BioGPU-Core has the software skeleton for task encoding, substrate interaction, decoding, reward and adaptation.
- C5_energy_comparison_framework: BioGPU-Core can compare energy/latency/throughput under a shared benchmark and measurement boundary.

## Still not proven

- C6_live_biogpu_prototype: A real living-neuronal BioGPU prototype can run task-aligned closed-loop benchmarks.
- C7_gpu_advantage: BioGPU can outperform or be more energy-efficient than conventional GPU/CPU baselines on selected tasks.

## Safety and scientific boundary

- No wet-lab recipe is provided as an executable protocol.
- No live stimulation amplitudes, pulse widths, charge densities, pinouts or wiring steps are included.
- Live work requires qualified laboratory SOPs, vendor documentation and applicable safety/ethics review.
- GPU advantage is a future claim requiring measured evidence; v3.0 does not assert it as proven.
