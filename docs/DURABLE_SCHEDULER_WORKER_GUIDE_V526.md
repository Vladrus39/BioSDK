# BioGPU-Core v5.26 Durable Scheduler Worker Guide

v5.26 turns the v5.5 in-memory queue proof into a local durable scheduler proof.

It persists safe admitted jobs into SQLite, reopens the store to prove restart visibility, lets a local worker claim queued jobs, writes local JSON result artifacts and records result-bundle references.

## Command

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_biogpu_v526_durable_scheduler_worker.ps1 -Python "c:/Users/vladi/Desktop/Braine/BiC OS/.venv-1/Scripts/python.exe"
```

## Outputs

- `outputs/v526_durable_scheduler_worker/V526_DURABLE_SCHEDULER_WORKER_SUMMARY.json`
- `outputs/v526_durable_scheduler_worker/V526_DURABLE_SCHEDULER.sqlite3`
- `outputs/v526_durable_scheduler_worker/V526_DURABLE_SCHEDULER_JOBS.json`
- `outputs/v526_durable_scheduler_worker/V526_DURABLE_SCHEDULER_EVENTS.json`
- `outputs/v526_durable_scheduler_worker/V526_DURABLE_WORKER_EXECUTIONS.json`
- `outputs/v526_durable_scheduler_worker/BIOGPU_V526_DURABLE_SCHEDULER_WORKER_REPORT.md`

## Boundary

This is a local proof of persisted scheduling and worker lifecycle. It does not provide a production API server, auth, multi-worker deployment, hosted storage, live external API control, closed-loop wetware operation or BiC OS readiness.
