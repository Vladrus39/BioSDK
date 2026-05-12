# BioGPU-Core v5.13 BioSDK Core API Guide

v5.13 corrects the project sequence. The active development target is the BioSDK public core, not BiC OS. BiC OS remains locked until SDK, data, runtime and control-plane proof gates are complete.

The core facade is intentionally small. It exposes stable calls over existing proven layers instead of creating another parallel system.

## Public Facade

- `BioSDKClientV513.phase_gate()` reports the active phase and locked future phases.
- `BioSDKClientV513.evidence_pack()` returns the v5.12 BioSDK evidence matrix.
- `BioSDKClientV513.capabilities()` lists SDK capabilities and gaps.
- `BioSDKClientV513.validate_nsi_payload(...)` validates NSI objects.
- `BioSDKClientV513.build_replay_request(...)` creates a safe replay request.
- `BioSDKClientV513.review_agent_task(...)` applies the v5.4 agent policy and NSI manifest generation.
- `BioSDKClientV513.submit_agent_task(...)` admits approved manifests through the v5.5 queue bridge.

## Run

```powershell
Push-Location 'C:\Users\vladi\Desktop\Braine\BiC OS\biogpu-core-v5_0_bic_os_first_mover_roadmap'
& .\scripts\run_biogpu_v513_biosdk_core_api.ps1 -Python 'c:/Users/vladi/Desktop/Braine/BiC OS/.venv-1/Scripts/python.exe'
```

The expected healthy status is `biosdk_core_api_active_bic_os_locked`.

## Minimal Example

```powershell
Push-Location 'C:\Users\vladi\Desktop\Braine\BiC OS\biogpu-core-v5_0_bic_os_first_mover_roadmap'
& 'c:/Users/vladi/Desktop/Braine/BiC OS/.venv-1/Scripts/python.exe' .\examples\biosdk_v513_minimal_flow.py
```

## Correct Next Work

- Add public SDK examples for each NSI schema and adapter contract.
- Validate at least one real NWB/DANDI asset.
- Validate one external read-only adapter/API path.
- Implement durable scheduler/workers for repeatable SDK jobs.
- Package an installable SDK release candidate.

## Blocked For Now

- Production BiC OS claim.
- Global uniqueness claim.
- Live BioGPU claim.
- GPU replacement or energy superiority claim.
- Lab closed-loop module without external approval and evidence.
