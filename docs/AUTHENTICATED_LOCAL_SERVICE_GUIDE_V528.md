# BioGPU-Core v5.28 Authenticated Local Service Guide

v5.28 adds a local authenticated service contract over the v5.27 scheduler facade.

It proves:

- v1 scheduler/result-bundle operations require an API key.
- Missing and invalid API keys are rejected.
- Local fixture principals have explicit scopes.
- Worker stepping is denied to non-worker principals.
- Viewer principals cannot cancel jobs.
- A succeeded local worker job exposes a result-bundle download contract with SHA-256 validation.

It does not prove production secret management, hosted API readiness, production object storage, live external API control, closed-loop wetware operation, full BioCompute Runtime or BiC OS readiness.

Run the gate:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_biogpu_v528_authenticated_local_service.ps1
```

Outputs are written under `outputs/v528_authenticated_local_service/`.

The API keys in this layer are non-secret local fixtures used only for deterministic proof tests. Production key management remains a blocker.
