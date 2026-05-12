# BioGPU Hosted Server Architecture v4.0

The hosted server is planned for v4.3. v4.0 defines the contract.

## Components

- FastAPI backend
- user accounts / API keys
- license tier enforcement
- job queue
- dataset registry
- upload/import endpoint
- manifest validation endpoint
- run status endpoint
- result bundle storage/download
- admin dashboard
- audit logs

## v4.0 status

A minimal `biogpu.api.beta_server_v40` skeleton is included. It exposes architecture/dataset metadata and validates safe beta run requests. Actual job queue execution is planned for v4.3.
