# BioGPU v4.3 Hosted Server Deployment Plan

## Deployment modes

### 1. Local beta server

For developers and internal tests.

```bash
uvicorn biogpu.api.hosted_server_v43:app --host 0.0.0.0 --port 8080
```

### 2. Hosted SaaS beta

Recommended early public/private beta setup:

```text
Nginx/Traefik
→ FastAPI API server
→ Postgres
→ Redis queue
→ worker pool
→ S3-compatible object storage
→ metrics/logging
```

### 3. Enterprise on-prem

Recommended enterprise setup:

```text
Docker Compose / Kubernetes
private container registry
offline license file or license server
customer-owned data storage
customer IAM/SSO
customer audit retention
```

## Job lifecycle

```text
validated → queued → running → succeeded/failed/cancelled → result bundle
```

## Safety invariant

The hosted server may run replay/read-only/live-shadow style jobs, but it must not
accept free-form live actuation fields.  The v4.3 job validator rejects unsafe
fields such as voltage, current, pulse width, electrode commands, pinout, wiring,
media recipe, incubator control and live actuation.

## Beta release readiness gates

- v4.3 scaffold tests pass
- v4.4 private beta docs and sample manifests exist
- v4.5 security/data handling pack exists
- Power-PC validation scripts have been run at least in smoke mode
- Dataset registry includes Zenodo/DANDI/Allen/user-upload paths
