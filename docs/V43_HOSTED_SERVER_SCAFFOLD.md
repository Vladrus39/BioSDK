# BioGPU-Core v4.3 — Hosted Server Scaffold + Job Model

v4.3 turns the beta release architecture into a concrete hosted-server contract.
It does not yet implement production authentication, billing, persistent database,
object storage, or background workers, but it defines the shape of the beta API.

## Core idea

External testers should receive maximum useful software access:

- SDK execution
- hosted jobs
- dataset imports
- replay benchmarks
- read-only API validation
- BioLLM tool runs
- result bundles
- audit events

The only class of access that remains blocked is unapproved live biological
actuation: stimulation commands, electrode writes, unsafe vendor-driver fields,
wet-lab/environment control, pinout/wiring, and uncontrolled closed-loop control.

## Server components

```text
FastAPI app
→ user context headers / future auth
→ job validation
→ quota policy
→ job store / future Postgres
→ worker queue / future Redis-Celery/RQ
→ object storage result bundles
→ audit logging
```

## v4.3 endpoints

```text
GET  /health
GET  /v1/server/capabilities
GET  /v1/server/quotas
POST /v1/jobs
GET  /v1/jobs
GET  /v1/jobs/{job_id}
POST /v1/jobs/{job_id}/cancel
GET  /v1/jobs/{job_id}/result-bundle
POST /v1/datasets/import
```

## Roles

```text
viewer      — read status only
developer   — local/replay/dev beta jobs
researcher  — dataset/import/read-only API validation
operator    — managed enterprise operations
admin       — workspace administration
```

## Access tiers

```text
developer_evaluation
research_pilot
enterprise_read_only
enterprise_live_shadow
lab_approved_closed_loop
```

In v4.3, even `lab_approved_closed_loop` does not enable actuation.  It is present
as a commercial/roadmap tier only; live command allowlists must be implemented in
a later lab-approved module.

## Production backlog

- Real identity provider / SSO / API keys
- Postgres job database
- Redis/Celery/RQ job queue
- Object storage bundle backend
- Workspace data privacy policy enforcement
- Usage metering and billing hooks
- Admin dashboard
- Worker sandboxing
- Signed result bundles and checksum enforcement
