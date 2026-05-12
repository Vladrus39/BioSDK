# BioGPU-Core v5.27 Scheduler API Facade Guide

v5.27 adds local scheduler API semantics over the v5.26 durable queue.

It proves that safe queued jobs can be listed, inspected, cancelled, timed out, retried and stepped through a local worker facade without enabling production hosting or live control.

## Local Routes

- `GET /health`
- `GET /v1/scheduler/jobs`
- `GET /v1/scheduler/jobs/{job_id}`
- `POST /v1/scheduler/jobs/{job_id}/cancel`
- `POST /v1/scheduler/jobs/{job_id}/retry`
- `POST /v1/scheduler/timeouts/scan`
- `POST /v1/scheduler/workers/{worker_id}/step`

## Command

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_biogpu_v527_scheduler_api_facade.ps1 -Python "c:/Users/vladi/Desktop/Braine/BiC OS/.venv-1/Scripts/python.exe"
```

## Outputs

- `outputs/v527_scheduler_api_facade/V527_SCHEDULER_API_FACADE_SUMMARY.json`
- `outputs/v527_scheduler_api_facade/V527_SCHEDULER_API_ROUTES.json`
- `outputs/v527_scheduler_api_facade/V527_SCHEDULER_API_ACTIONS.json`
- `outputs/v527_scheduler_api_facade/V527_SCHEDULER_API_JOBS.json`
- `outputs/v527_scheduler_api_facade/V527_SCHEDULER_API_EVENTS.json`
- `outputs/v527_scheduler_api_facade/BIOGPU_V527_SCHEDULER_API_FACADE_REPORT.md`

## Boundary

This is a local API facade proof. It does not claim an authenticated production API server, hosted BioCompute Runtime, live external API control, closed-loop wetware operation or BiC OS readiness.
