# BioGPU v2.9 — Energy / Performance Model

v2.9 adds the accounting scaffold required before any credible claim that BioGPU can outperform or out-efficient GPU/CPU/neuromorphic systems.

## What this version does

- defines power components;
- estimates total energy and energy per task;
- estimates closed-loop latency and serial throughput;
- compares placeholder CPU/GPU/neuromorphic/BioGPU replay/live-budget baselines;
- exports JSON/CSV/Markdown reports.

## What it does not claim

v2.9 does **not** claim that BioGPU is already more powerful than GPU.
It creates the measurement contract.

A real advantage claim requires:

- same benchmark task;
- same input/output accuracy criteria;
- same batching rules;
- measured wall power / telemetry;
- measured live substrate latency;
- documented environmental overhead;
- reproducible result bundle.

## Core formulae

```text
P_total = Σ P_component
E_total[J] = P_total[W] * T_run[s]
E_task[J/task] = E_total / N_tasks
mWh_task = E_task / 3600 * 1000
T_loop = T_encode + T_io + T_bio + T_acq + T_features + T_readout + T_controller
Throughput_serial = 1000 / T_loop_ms
```
