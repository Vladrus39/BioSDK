# BioGPU-Core v5.30 Runtime Observability Guide

v5.30 adds local runtime metrics and audit-retention proof over the v5.29 supervised runtime.

It proves:

- local metrics snapshot generation from runtime state, heartbeat, jobs and audit events;
- status snapshots across start, heartbeat, worker ticks, idle and shutdown actions;
- non-destructive audit retention policy application;
- full audit export before retaining the recent event window;
- SHA-256 hashes for full and retained audit payloads;
- production metrics, production audit retention and BiC OS readiness remain blocked.

Run the gate:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_biogpu_v530_runtime_observability.ps1
```

Outputs are written under `outputs/v530_runtime_observability/`.

This is a local observability proof, not a production metrics backend, hosted dashboard, tenant audit store or OS runtime.
