# BioGPU-Core v5.5 Control Plane Queue Bridge Guide

## Purpose

v5.5 connects the safe v5.4 LLM/Agent Bridge to the existing v4.3 hosted beta job model.

The goal is an offline control-plane contract: approved agent requests become queued hosted jobs, while blocked, approval-gated or tier-incompatible requests do not enter the queue.

## Flow

1. Agent submits a `BioComputeAgentRequestV54`.
2. v5.4 returns an `AgentToolResponseV54` with policy review and, only when approved, an NSI `BioComputeTaskManifest`.
3. v5.5 validates the NSI manifest and maps the requested tool to a hosted job type.
4. The v4.3 job store applies role, tier, quota and unsafe-field checks.
5. Accepted jobs are queued with audit metadata and result-bundle expectation.

## Tool-to-job mapping

- Dataset validation/import tools map to `dataset_import`.
- Replay benchmark, lineage sweep and shuffle comparison map to `benchmark_run`.
- Result bundle packaging maps to `result_bundle_export`.
- Live-shadow session requests map to `api_readonly_validation` and require an enterprise live-shadow tier.

## Safety boundary

v5.5 does not execute jobs. It only admits safe manifests into a queue contract.

The bridge rejects:

- blocked or approval-gated agent responses;
- missing or invalid NSI task manifests;
- unsupported agent tools;
- direct `approved_actuation` mode;
- live-shadow requests outside the live-shadow tier;
- any job later rejected by the v4.3 role/quota/safety validator.

## Validation

Run the v5.5 gate on Windows:

```powershell
& .\scripts\run_biogpu_v55_control_plane_queue.ps1 -Python 'c:/Users/vladi/Desktop/Braine/BiC OS/.venv-1/Scripts/python.exe'
```

The runner writes `outputs/v55_control_plane_queue/` with a demo queue report and summary JSON.
