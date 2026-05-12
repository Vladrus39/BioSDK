# BioGPU-Core v4.5 Master Project Plan

## Current truth

BioGPU-Core is now best described as an enterprise-oriented BioSDK for living neural compute: replay/read-only first, live actuation only after lab/vendor approval. The original GPU-for-LLM replacement idea matured into a safer and more realistic BioSDK/runtime for biological neural signals, wetware APIs, benchmarks, result bundles, and future lab validation.

## Product model

- Private GitHub/private package for technical partners.
- Hosted BioGPU Server for beta testing and commercial SaaS-style access.
- Enterprise on-prem Docker for serious customers.
- Lab-approved closed-loop add-on only after protocol approval.

## Access policy

Early serious testers should receive maximum software-level access: SDK, Docker, own data import, replay, benchmark sweeps, BioLLM tool interface, read-only/mock API, result bundles, and audit logs. Only unsafe live biological actuation remains gated.

## Roadmap

- **R0 [completed_local] Real-data replay baseline from Zenodo preprocessed MEA data** — status: `done`; environment: `current_environment`; deliverable: `v1.2-v3.3 reports and result bundles`; gate: `repeatable smoke tests pass`.
- **R1 [completed_local] Runtime/SDK core: adapters, encoder, readout, closed-loop, energy model** — status: `done`; environment: `current_environment`; deliverable: `v2.4-v3.1 SDK modules`; gate: `py_compile and targeted tests pass`.
- **R2 [completed_local] Real sklearn readouts and release hygiene** — status: `done`; environment: `current_environment`; deliverable: `v3.5`; gate: `real LogisticRegression/LinearSVC available`.
- **R3 [completed_local] Lineage-strict split and bootstrap scaffold** — status: `done`; environment: `current_environment`; deliverable: `v3.6`; gate: `base lineage is kept either train-only or test-only`.
- **R4 [completed_local] External API/BioSDK skeleton** — status: `done`; environment: `current_environment`; deliverable: `v3.7`; gate: `read-only/mock clients available`.
- **R5 [completed_local] BioLLM tool interface** — status: `done`; environment: `current_environment`; deliverable: `v3.8`; gate: `LLM tool returns structured result`.
- **R6 [completed_local] Enterprise packaging and licensing** — status: `done`; environment: `current_environment`; deliverable: `v3.9`; gate: `commercial tiers documented`.
- **R7 [completed_local] Beta architecture and maximum safe access policy** — status: `done`; environment: `current_environment`; deliverable: `v4.0-v4.1`; gate: `early testers get broad software access, live actuation gated`.
- **R8 [completed_local] Dataset registry/import skeleton and hosted server/job model** — status: `done`; environment: `current_environment`; deliverable: `v4.2-v4.3`; gate: `dataset registry and job model tests pass`.
- **R9 [completed_local] Private beta docs and sample manifests** — status: `included_in_v45`; environment: `current_environment`; deliverable: `beta/ quickstart/checklists/sample manifests`; gate: `external tester can run smoke workflow`.
- **R10 [completed_local] Single master plan and repository cleanup audit** — status: `done`; environment: `current_environment`; deliverable: `MASTER_PROJECT_PLAN_V45.md and cleanup audit`; gate: `single source of truth exists`.
- **P0 [power_pc] Re-run v3.5/v3.6 smoke checks on workstation** — status: `pending`; environment: `power_pc`; deliverable: `POWERPC_SMOKE_RESULT_BUNDLE`; gate: `all smoke tests pass on target machine`.
- **P1 [power_pc] full_shuffle_1000 lineage-strict validation** — status: `pending`; environment: `power_pc`; deliverable: `paper_table_full_shuffle_1000.csv`; gate: `stable signal above shuffled controls or honest negative result`.
- **P2 [power_pc] extended_methods_5000 supplementary sweep** — status: `pending`; environment: `power_pc_or_server`; deliverable: `extended_methods_result_bundle`; gate: `supplementary methods table complete`.
- **P3 [power_pc] Bootstrap confidence intervals and calibration curves** — status: `pending`; environment: `power_pc`; deliverable: `bootstrap_ci_tables and calibration plots`; gate: `95% CI and calibration reported for each claim`.
- **D1 [dataset_expansion] Zenodo raw HDF5 / TTL reconstruction** — status: `pending`; environment: `power_pc`; deliverable: `raw_hdf5_pulse_windows.csv`; gate: `raw-derived windows match or supersede preprocessed windows`.
- **D2 [dataset_expansion] DANDI/NWB discovery and task-aligned parser** — status: `pending`; environment: `power_pc_or_server`; deliverable: `NWB task-aligned benchmark bundle`; gate: `units+intervals/trials/stimulus parsed`.
- **D3 [dataset_expansion] AllenSDK visual coding/orientation benchmark** — status: `pending`; environment: `power_pc_or_server`; deliverable: `Allen orientation benchmark report`; gate: `stimulus presentations and spikes parsed`.
- **A1 [external_api] FinalSpark read-only credential validation** — status: `pending`; environment: `partner_api`; deliverable: `FinalSpark read-only trace bundle`; gate: `metadata and read-only trace import works`.
- **A2 [external_api] 3Brain/Axion/MCS exported-data validation** — status: `pending`; environment: `partner_or_user_data`; deliverable: `vendor export BioGPUTrace bundles`; gate: `vendor data converted without unsafe commands`.
- **S1 [hosted_beta] Hosted BioGPU server with auth, quotas, job queue** — status: `pending`; environment: `server`; deliverable: `hosted beta deployment`; gate: `safe jobs run and unsafe jobs rejected`.
- **S2 [private_beta] Private beta with selected labs/enterprises** — status: `pending`; environment: `server_and_private_repo`; deliverable: `beta feedback reports`; gate: `3+ external testers complete acceptance checklist`.
- **E1 [enterprise] Enterprise pilot package and legal/security review** — status: `pending`; environment: `commercial`; deliverable: `pilot MSA/SLA/security pack`; gate: `pilot partner accepts data handling and access boundaries`.
- **L1 [lab_validation] First approved live BioGPU experiment** — status: `pending`; environment: `approved_lab`; deliverable: `live BioGPU result bundle`; gate: `approved protocol, audit log, readout result, latency/energy report`.

## Datasets/API still required before confident beta claims

- **zenodo_14363732_preprocessed** (P0, existing_realdata): current smoke/replay baseline. Required before beta: `True`. Power-PC required: `False`.
- **zenodo_14363732_raw_hdf5** (P0, raw_hdf5): TTL/stimulus reconstruction and raw-vs-preprocessed validation. Required before beta: `True`. Power-PC required: `True`.
- **dandi_nwb_discovery** (P1, NWB/API): task-aligned neural benchmarks. Required before beta: `True`. Power-PC required: `True`.
- **allen_visual_coding_orientation** (P1, AllenSDK): orientation/visual coding benchmark. Required before beta: `True`. Power-PC required: `True`.
- **finalspark_readonly_export** (P2, external_api_or_export): remote wetware read-only validation. Required before beta: `False`. Power-PC required: `False`.
- **vendor_exports_mcs_3brain_axion** (P2, vendor_export): enterprise/lab data compatibility. Required before beta: `False`. Power-PC required: `False`.
- **user_uploaded_neural_data** (P0, private_upload): beta tester data import. Required before beta: `True`. Power-PC required: `False`.

## Repository cleanup truth

The project has accumulated historical artifacts. They are useful for audit trail, but they should not be presented as the current entry point. Current entry point is this document plus README_BIOGPU_CORE_V45.md, docs/DOCUMENT_INDEX_V45.md, and beta/PRIVATE_BETA_QUICKSTART.md.

## Claims allowed now

- Allowed: software/replay BioSDK, real-data preprocessed MEA pipeline, lineage-strict split scaffold, read-only/mock API skeleton, hosted server scaffold, enterprise beta packaging.

- Not allowed yet: proven live BioGPU, GPU replacement, LLM replacement, measured live energy advantage, uncontrolled live stimulation.

