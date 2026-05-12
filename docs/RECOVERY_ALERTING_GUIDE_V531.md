# BioGPU-Core v5.31 Recovery Alerting Guide

v5.31 adds local stale-heartbeat alerting and worker failure recovery proof over the v5.30 observability layer.

It proves:

- stale heartbeat classification for a running local runtime;
- worker timeout failure classification;
- retry of a timed-out job through the durable scheduler facade;
- worker-step recovery of the retry job;
- recovery audit bundle export with SHA-256 hash;
- production alerting, production recovery orchestration and BiC OS readiness remain blocked.

Run the gate:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_biogpu_v531_recovery_alerting.ps1
```

Outputs are written under `outputs/v531_recovery_alerting/`.

This is a deterministic local recovery proof, not a production monitor, pager, hosted recovery controller or live wetware control process.
