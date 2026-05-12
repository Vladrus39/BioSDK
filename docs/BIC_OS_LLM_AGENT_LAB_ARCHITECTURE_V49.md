# BiC OS — LLM / Agent / Lab Architecture Vision

## One-line vision

**BiC OS is an OS-like control plane for living neural compute, LLM agents, replay datasets, wetware APIs, experiments, safety policies and auditable result bundles.**

## Core idea

BiC OS must not be a simple dashboard. It should become the layer where:

```text
LLM / research agent
→ BioCompute task manifest
→ dataset/API/wetware adapter
→ feature/readout/benchmark runtime
→ safety supervisor
→ result bundle / evidence ledger
→ LLM/lab/enterprise report
```

## LLM-first design

BiC OS should expose biological compute as structured tools:

```text
biocompute.validate_dataset
biocompute.run_replay_benchmark
biocompute.run_lineage_sweep
biocompute.compare_shuffle_baseline
biocompute.import_nwb
biocompute.import_vendor_export
biocompute.package_result_bundle
biocompute.request_live_shadow_session
```

The LLM may plan, explain, compare and report. By default, it must not perform unsafe live actuation.

## v5.4 implementation status

The first safe bridge is implemented in `biogpu/llm/agent_bridge_v54.py`.

It provides:

- an eight-tool BioCompute catalog matching the architecture list above;
- structured `BioComputeAgentRequestV54` inputs;
- policy review for tool/mode compatibility, approvals and forbidden live-lab payloads;
- conversion of approved requests into NSI `BioComputeTaskManifest` objects;
- claim-aware responses and evidence requirements;
- no NSI executable manifest for blocked or approval-gated requests.

Direct `approved_actuation` remains blocked in v5.4. `live_shadow` is read-only and requires partner/operator approval references.

## v5.5 control-plane queue status

The first offline control-plane bridge is implemented in `biogpu/beta/control_plane_v55.py`.

It connects approved v5.4 agent responses to the existing v4.3 hosted beta job model:

- validates the generated NSI `BioComputeTaskManifest`;
- maps BioCompute tools to hosted queue job types;
- admits safe replay jobs into the queue;
- admits live-shadow only for a live-shadow tier and still as read-only/API validation;
- rejects blocked, approval-gated or unsupported agent responses;
- keeps live actuation disabled.

## Agent workflows

### 1. Benchmark agent

Runs allowed replay/read-only sweeps, compares decoders/ablations/splits and produces evidence reports.

### 2. Dataset agent

Discovers DANDI/NWB/Allen/vendor datasets, validates schemas, checks metadata and proposes import manifests.

### 3. Lab copilot

Reads live-shadow result bundles, flags anomalies, prepares next manifests and generates operator-facing reports.

### 4. Enterprise evidence assistant

Creates auditable pilot packages, evidence summaries, customer reports and acceptance-criteria checklists.

## Safety stance

```text
maximum software access
+ no unsafe live actuation by default
+ lab/vendor approval before controlled stimulation
+ all actions logged into result bundles
```

## Differentiators

```text
vendor-neutral adapters
NSI-1.0 schemas
LLM tool interface
result-bundle evidence standard
maximum safe beta access
cross-dataset benchmark suite
future lab-approved live gateway
```
