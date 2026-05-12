# NSI-1.0 Draft — Neural Substrate Interface

NSI-1.0 is a draft interface profile for BioGPU-Core / BioCompute Runtime. It is not intended to replace NWB, HDF5 or vendor formats. It defines the runtime-facing objects that allow datasets, vendor exports, wetware APIs and future live platforms to be integrated consistently.

## Principle

Existing formats remain sources of truth where appropriate:

- NWB for neurophysiology and behavioral data;
- HDF5/raw vendor traces for high-throughput recordings;
- CSV/vendor exports for MEA/HD-MEA workflows;
- API streams for remote wetware platforms.

NSI defines the common runtime contract above them.

## Core objects

1. **BioComputeTrace** — spikes/traces/events/channels/metadata from replay/API/vendor sources.
2. **BioComputeTaskManifest** — task, dataset, split policy, decoder, safety mode and output bundle.
3. **BioComputeFeatureBatch** — feature matrix, labels and biological metadata.
4. **BioComputeReadoutResult** — predictions, metrics, baselines, confidence intervals and claim level.
5. **BioComputeResultBundle** — reproducibility bundle with manifests, metrics, logs, checksums, plots and versions.
6. **BioComputeSafetyProfile** — allowed/blocked operations for replay/read-only/live-shadow/approved-actuation.
7. **BioComputeAdapterContract** — minimum interface and conformance tests for dataset/API/device adapters.

## Safety modes

| Mode | Meaning |
| --- | --- |
| replay | Uses historical/offline data only. |
| metadata_only | Reads source metadata only. |
| read_only | Reads data/events/traces without actuation. |
| live_shadow | Reads live data and produces predictions without controlling the system. |
| approved_actuation | Lab/vendor/protocol-approved write/control mode. |

Blocked by default:

- live stimulation;
- electrode actuation;
- free-form vendor write commands;
- wetware environment/media control;
- uncontrolled closed-loop.

## v5.2 implementation status

- The runtime-facing NSI-1.0 profile is frozen in `biogpu/standards/nsi_v10.py` as lightweight JSON-schema-like dictionaries.
- Reference NSI objects and validators exist for all seven core objects.
- Adapter conformance exists for dataset importers and safe dry-run vendor adapter stubs.
- Result-bundle validation and conservative claim-level annotation are implemented.
- Public validation entrypoints exist through `biogpu-validate-nsi`, `python -m biogpu.standards.nsi_cli_v52`, and `python -m biogpu.cli validate-nsi`.
- Developer adapter guidance is in `docs/NSI_1_0_ADAPTER_GUIDE_V52.md`.

## Remaining next steps

- Produce reference mappings from NWB/HDF5/CSV/vendor exports into BioComputeTrace as each source becomes locally available.
