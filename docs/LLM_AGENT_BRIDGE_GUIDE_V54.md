# BioGPU-Core v5.4 LLM/Agent Bridge Guide

## Purpose

v5.4 turns the earlier BioLLM tool prototype into a safety-reviewed agent bridge over NSI-1.0.

The bridge lets an LLM or research agent propose a structured BioCompute task, receive a policy review, and, when safe, receive a validated `BioComputeTaskManifest`. It does not give the LLM direct authority to approve or execute live biological actuation.

## Tool catalog

The initial v5.4 catalog contains eight structured tools:

- `biocompute.validate_dataset`
- `biocompute.run_replay_benchmark`
- `biocompute.run_lineage_sweep`
- `biocompute.compare_shuffle_baseline`
- `biocompute.import_nwb`
- `biocompute.import_vendor_export`
- `biocompute.package_result_bundle`
- `biocompute.request_live_shadow_session`

Replay, metadata-only and read-only tools are safe by default when their payload passes the safety scanner. `biocompute.request_live_shadow_session` is allowed only with partner/operator approval references and remains read-only. Direct `approved_actuation` is blocked in v5.4.

## Request flow

1. Agent submits `BioComputeAgentRequestV54`.
2. Policy review checks the tool name, NSI safety mode, approval references and forbidden live-lab fields.
3. Approved requests are converted into an NSI `BioComputeTaskManifest`.
4. The response returns the manifest validation report, claim annotation, required evidence and audit events.
5. Blocked or approval-gated requests return a denial reason and no executable NSI manifest.

## Safety boundary

The bridge inherits the repository safety boundary from v3.5 and adds LLM-specific checks:

- blocked live-lab fields such as stimulation voltage/current/amplitude/pulse-width keys;
- blocked-by-default operations from NSI, including live stimulation and electrode actuation;
- unknown tools;
- tool/mode mismatches;
- direct `approved_actuation` requests from agents;
- live-shadow requests without approval references.

## Outputs

The runner writes these artifacts under `outputs/v54_llm_agent_bridge/`:

- `V54_AGENT_TOOL_CATALOG.json`
- `V54_REFERENCE_AGENT_REQUESTS.json`
- `V54_AGENT_RESPONSES.json`
- `V54_LLM_AGENT_BRIDGE_SUMMARY.json`
- `BIOGPU_V54_LLM_AGENT_BRIDGE_REPORT.md`

## Validation

Run the v5.4 gate on Windows:

```powershell
& .\scripts\run_biogpu_v54_llm_agent_bridge.ps1 -Python 'c:/Users/vladi/Desktop/Braine/BiC OS/.venv-1/Scripts/python.exe'
```

The focused gate validates the reference safe replay request, approval-backed live-shadow request, direct actuation denial and NSI manifest emission.
