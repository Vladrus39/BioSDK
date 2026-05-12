# BioGPU-Core v4.0 — Beta Release Architecture + Dataset/API Expansion Plan

## Positioning
BioGPU-Core Enterprise BioSDK for living neural compute: SDK + hosted server + on-prem deployment, with read-only/replay beta before approved live-lab modules.

## Delivery channels
### Private GitHub / Private Package SDK
- Audience: labs, enterprise engineers, early technical partners
- Delivery: private repository, wheel package, Docker image, examples, docs
- Use: developer evaluation and on-prem reproducible runs
- Monetization: developer evaluation; paid enterprise license after trial
- Allowed modes: mock, replay, read_only_import, local_dataset_validation
- Blocked modes: unapproved_live_stimulation, wet_lab_protocols, vendor_pinout_commands

### Hosted BioGPU Server
- Audience: non-infra beta users, investors, labs needing quick demos
- Delivery: web UI + REST API + job queue + result-bundle downloads
- Use: fast beta access without installing the full stack
- Monetization: subscription, paid job credits, enterprise workspaces
- Allowed modes: mock, replay, read_only_uploaded_data, curated_dataset_runs
- Blocked modes: live_actuation, unapproved_external_api_write, unsafe_lab_fields

### Enterprise On-Prem Docker
- Audience: companies and regulated labs that cannot upload data externally
- Delivery: Docker image, docker-compose, offline license file, admin guide
- Use: private deployment inside customer infrastructure
- Monetization: annual enterprise license + support/SLA package
- Allowed modes: mock, replay, read_only_import, internal_api_read_only, power_pc_sweeps
- Blocked modes: closed_loop_live_control_without_lab_approval

### Lab-Approved Live Add-on
- Audience: approved laboratories or vendor platforms with operator oversight
- Delivery: separate paid module, protocol-bound adapter, operator checklist
- Use: live-data shadow mode first; controlled closed-loop later
- Monetization: high-value add-on, milestone fees, support contract
- Allowed modes: metadata, read_only_live, live_shadow, approved_protocol_closed_loop
- Blocked modes: unreviewed_stimulation, free-form_electrode_commands, home_wetlab_use

## Dataset/API expansion
### P1 — Zenodo 14363732 raw HDF5 MEA dataset
- ID: `zenodo_14363732_raw_hdf5`
- Type: raw_hdf5
- Adapter status: planned_v4_1
- Why: Validate preprocessed spike windows against raw recordings; search TTL/stimulus markers.
- Required work: download raw archive on power PC, inspect HDF5 tree, locate TTL/stimulus channels, derive raw pulse windows, compare raw-derived features with v1.5/v3.6 features
- Power-PC required: True

### P2 — DANDI NWB task-aligned discovery pack
- ID: `dandi_nwb_discovery_pack`
- Type: nwb_api
- Adapter status: existing_seed_plus_planned_expansion
- Why: Find datasets with units + intervals/trials/stimulus to validate task-aligned BioGPUTrace pipeline.
- Required work: DANDI API search, filter by NWB units and stimulus/trials, download small sample files, build stimulus_windows.csv, run task-aligned readout
- Power-PC required: False

### P3 — Allen Brain Observatory / AllenSDK visual coding adapter
- ID: `allen_brain_observatory_visual_coding`
- Type: allen_sdk
- Adapter status: planned_v4_1
- Why: Orientation/drifting-grating tasks are strong analogs for BioGPU encoding/readout benchmarks.
- Required work: install AllenSDK on power/dev PC, download small Neuropixels/visual-coding sample, extract stimulus presentations, extract spike/unit responses, build orientation benchmark
- Power-PC required: True

### P4 — FinalSpark read-only/live HDF5 bridge
- ID: `finalspark_read_only_live_hdf5`
- Type: external_api
- Adapter status: mock_v3_7_then_real_credentials
- Why: First real remote wetware API path without live actuation.
- Required work: obtain platform access/token, metadata-only smoke test, read-only spike/live trace capture, export BioGPUTrace, run live-shadow result bundle
- Power-PC required: False

### P5 — 3Brain / Axion / MCS exported-data adapters
- ID: `vendor_export_adapters`
- Type: vendor_export
- Adapter status: mock_v3_7_then_partner_samples
- Why: Enterprise labs often start with exported files before allowing live SDK access.
- Required work: collect sample exports, write schema mappers, convert to BioGPUTrace, run read-only benchmark, generate compatibility report
- Power-PC required: False

## Validation gates before beta
### G1_release_install — Install and smoke-test gate
- Purpose: Ensure beta user can install SDK or run Docker without hidden manual steps.
- Pass criteria: pip or Docker install succeeds, health check passes, sample manifest runs, result bundle is created
- Artifacts: install_log.txt, health.json, sample_result_bundle.zip

### G2_dataset_replay — Dataset replay gate
- Purpose: Verify SDK can run at least one curated dataset end-to-end.
- Pass criteria: dataset registry resolves source, features are generated or loaded, readout runs, shuffle baseline is reported
- Artifacts: run_manifest.json, readout_summary.json, shuffle_controls.csv, audit_log.jsonl

### G3_lineage_statistics — Lineage-strict statistics gate
- Purpose: Prevent overclaiming from culture/DIV leakage before external beta.
- Pass criteria: lineage parser runs, train/test lineage overlap is zero, bootstrap CI is generated, claim level remains honest
- Artifacts: lineage_split_summary.json, bootstrap_ci.csv, claim_ladder.md

### G4_api_read_only — External API read-only gate
- Purpose: Allow enterprise/API validation without live actuation.
- Pass criteria: metadata call succeeds, write commands are denied, BioGPUTrace export succeeds, audit shows read-only mode
- Artifacts: api_metadata.json, write_denial_report.json, biogpu_trace.json, api_audit_log.jsonl

### G5_powerpc_full_validation — Power-PC full validation gate
- Purpose: Run heavy sweeps before commercial/private beta claims.
- Pass criteria: full_shuffle_1000 completed, extended_methods_5000 optional, aggregate paper tables built, no unreviewed GPU advantage claim
- Artifacts: global_results.csv, aggregate_by_dataset.csv, bootstrap_summary.csv, validation_report.md

## Deferred backlog from earlier phases
These items were deliberately postponed until a power-PC/server, external API credentials, or a lab environment is available. They must remain in the project plan before external beta claims.

### D0_reproduce_v35_v36_smoke — Reproduce v3.5/v3.6 smoke checks on the target workstation
- Phase: before_power_pc_full
- Why deferred: The beta machine must prove that the same package, sklearn readouts and lineage split run outside this chat environment.
- Environment: power_pc_or_server
- Required inputs: v3.6/v4.0 archive, Python environment, local outputs directory
- Deliverables: install_log.txt, v35_smoke_result.json, v36_lineage_smoke_result.json
- Exit criteria: all smoke tests pass, no missing modules, lineage overlap is zero

### D1_full_shuffle_1000 — Full shuffled-label validation
- Phase: power_pc_validation
- Why deferred: Hundreds of thousands of fit/evaluation operations are too heavy for this environment.
- Environment: power_pc_or_server
- Required inputs: pulse_feature_matrix.npz, pulse_feature_metadata.csv, v3.6 lineage split logic
- Deliverables: full_shuffle_1000_results.csv, shuffle_pvalue_summary.csv, global_readout_summary.json
- Exit criteria: 1000 shuffles complete for approved splits/decoders, empirical p-values reported, failures logged not hidden

### D2_extended_methods_5000 — Extended methods and ablation sweep
- Phase: power_pc_validation
- Why deferred: Millions of compact model fits require workstation/server runtime.
- Environment: power_pc_or_server
- Required inputs: v3.5 sklearn readouts, v3.6 lineage split, feature ablation registry
- Deliverables: extended_methods_5000.csv, best_by_dataset_decoder_ablation.csv, failure_modes.md
- Exit criteria: all planned decoders compared, all feature ablations summarized, claim level updated

### D3_bootstrap_confidence_intervals — Bootstrap confidence intervals and calibration tables
- Phase: power_pc_validation
- Why deferred: Enough resampling must be done to make paper/beta claims statistically defensible.
- Environment: power_pc_or_server
- Required inputs: prediction tables, split summaries, shuffle summaries
- Deliverables: bootstrap_ci.csv, calibration_curve.csv, paper_table_statistics.csv
- Exit criteria: 95% CI reported, calibration quality reported, negative controls included

### D4_zenodo_raw_hdf5_ttl — Zenodo raw HDF5 / TTL / stimulus reconstruction
- Phase: dataset_expansion
- Why deferred: Raw archive is large and needs local storage, HDF5 inspection and possibly long parsing.
- Environment: power_pc_or_server
- Required inputs: Raw_data_MEA_data.zip, HDF5 reader, preprocessed spike windows for comparison
- Deliverables: hdf5_tree_report.md, ttl_channel_candidates.csv, raw_stimulus_windows.csv, raw_vs_preprocessed_comparison.md
- Exit criteria: raw structure mapped, TTL/stimulus presence or absence stated, raw-derived windows compared to v1.5/v3.6

### D5_dandi_nwb_task_aligned — DANDI/NWB task-aligned dataset discovery and parser
- Phase: dataset_expansion
- Why deferred: Needs online dataset search/download and multiple file schema checks.
- Environment: dev_pc_or_power_pc
- Required inputs: DANDI API/client, NWB files with units + intervals/trials/stimulus
- Deliverables: dandi_dataset_registry.csv, nwb_task_windows.csv, task_aligned_readout_report.md
- Exit criteria: at least 3 candidate Dandisets profiled, one task-aligned benchmark runs end-to-end

### D6_allen_visual_coding_adapter — Allen Brain Observatory / AllenSDK orientation benchmark
- Phase: dataset_expansion
- Why deferred: Allen downloads and SDK setup are better done on a workstation.
- Environment: dev_pc_or_power_pc
- Required inputs: AllenSDK, visual coding / Neuropixels sample, stimulus presentation tables
- Deliverables: allen_orientation_dataset_profile.json, orientation_readout_report.md, allen_result_bundle.zip
- Exit criteria: orientation task extracted, readout and shuffle baseline run, dataset added to registry

### D7_energy_latency_measurement — Measured energy/latency accounting
- Phase: power_pc_and_future_lab
- Why deferred: Current v2.9 is a model; real energy requires measured host/electronics/lab boundaries.
- Environment: power_pc_first_then_lab
- Required inputs: power meter or host telemetry, fixed benchmark manifest, task count and latency logs
- Deliverables: measured_energy_report.csv, latency_breakdown.csv, energy_claim_boundary.md
- Exit criteria: measured not only estimated, system boundary stated, no GPU advantage claim without matched baseline

### D8_external_api_credentials — External API read-only credential tests
- Phase: api_validation
- Why deferred: Requires partner/platform access tokens and terms of use.
- Environment: dev_pc_or_partner_environment
- Required inputs: FinalSpark or vendor API credentials, read-only API config, safety boundary
- Deliverables: api_metadata_result.json, read_only_trace_sample.json, write_denial_report.json
- Exit criteria: metadata read works, unsafe write is blocked, BioGPUTrace export works

### D9_hosted_server_beta — Hosted BioGPU Server beta deployment
- Phase: beta_platform
- Why deferred: Only valuable after dataset expansion and validation gates exist.
- Environment: cloud_server_or_onprem_server
- Required inputs: FastAPI beta server, job queue, auth/API keys, dataset registry, storage
- Deliverables: hosted_beta_url_or_local_deploy, user_role_tests.json, job_queue_demo_bundle.zip
- Exit criteria: two users can run sandbox jobs, quotas and audit logs work, unsafe modes blocked

### D10_lab_live_validation — First approved live BioGPU experiment
- Phase: future_lab
- Why deferred: Requires partner lab/vendor platform, operator approval, protocol ID and biosafety/ethics boundaries.
- Environment: approved_lab_or_vendor_platform
- Required inputs: approved protocol, operator, vendor/lab adapter, run manifest, audit plan
- Deliverables: live_shadow_or_closed_loop_bundle.zip, operator_log.md, live_validation_report.md
- Exit criteria: live read-only/shadow validated first, closed-loop only if approved, all results auditable

## Roadmap to external test access
### v4.0 — Beta Release Architecture
- Purpose: Define how SDK is delivered, governed, tested and monetized.
- Deliverables: release channels, hosted/on-prem/GitHub model, roles, license gates, dataset/API expansion plan
- Exit criteria: architecture manifest generated, docs complete, tests pass

### v4.1 — Dataset Expansion Pack
- Purpose: Expand beyond one preprocessed Zenodo dataset.
- Deliverables: Zenodo raw HDF5 adapter plan, DANDI discovery adapter, AllenSDK adapter, dataset registry, download manifests
- Exit criteria: at least 3 dataset families registered, sample import tests pass

### v4.2 — Power-PC Validation Suite
- Purpose: Run serious statistics and large shuffles on workstation/server.
- Deliverables: full_shuffle_1000, extended_methods_5000, bootstrap CI, lineage-strict reporting, global paper tables
- Exit criteria: large result bundle produced, claim ladder updated

### v4.3 — Hosted BioGPU Server
- Purpose: Make beta usable without local install.
- Deliverables: FastAPI server, job queue, users/API keys, dataset upload, run manifest endpoint, bundle download
- Exit criteria: two demo users can run sandbox jobs, admin can inspect audit logs

### v4.4 — Private Beta SDK
- Purpose: Give controlled external access to technical partners.
- Deliverables: private repo/wheel, Docker image, quickstart, examples, license file, support docs
- Exit criteria: partner onboarding checklist completed, beta feedback form ready

### v4.5 — Enterprise Pilot Package
- Purpose: Convert beta into paid pilots.
- Deliverables: enterprise onboarding, security checklist, DPA/data handling notes, SLA boundaries, commercial offer template, pilot success criteria
- Exit criteria: pilot package complete, pricing assumptions approved

## Beta rules
- **first_external_access**: mock/replay/read-only only
- **full_access_policy**: separate paid lab-approved module after safety, operator and protocol gates
- **commercial_default**: Enterprise Read-Only BioSDK is the first paid product
- **no_go_claims**: ["GPU replacement proven", "live BioGPU proven", "unrestricted wetware control"]
