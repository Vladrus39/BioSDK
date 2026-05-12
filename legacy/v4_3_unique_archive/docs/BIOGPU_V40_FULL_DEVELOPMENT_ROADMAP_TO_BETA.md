# BioGPU-Core v4.0 — Full Development Roadmap to Private Beta

This document keeps the whole plan in one place: the earlier items deliberately postponed until a power-PC/server, the dataset/API expansion work, the hosted/server delivery path, the private beta, the enterprise pilot, and only then future lab-approved live validation.

## A. Deferred items from earlier phases — must be completed before strong external claims
### D0_reproduce_v35_v36_smoke — Reproduce v3.5/v3.6 smoke checks on the target workstation
- Phase: before_power_pc_full
- Execution environment: power_pc_or_server
- Why deferred: The beta machine must prove that the same package, sklearn readouts and lineage split run outside this chat environment.
- Required inputs: v3.6/v4.0 archive, Python environment, local outputs directory
- Deliverables: install_log.txt, v35_smoke_result.json, v36_lineage_smoke_result.json
- Exit criteria: all smoke tests pass, no missing modules, lineage overlap is zero

### D1_full_shuffle_1000 — Full shuffled-label validation
- Phase: power_pc_validation
- Execution environment: power_pc_or_server
- Why deferred: Hundreds of thousands of fit/evaluation operations are too heavy for this environment.
- Required inputs: pulse_feature_matrix.npz, pulse_feature_metadata.csv, v3.6 lineage split logic
- Deliverables: full_shuffle_1000_results.csv, shuffle_pvalue_summary.csv, global_readout_summary.json
- Exit criteria: 1000 shuffles complete for approved splits/decoders, empirical p-values reported, failures logged not hidden

### D2_extended_methods_5000 — Extended methods and ablation sweep
- Phase: power_pc_validation
- Execution environment: power_pc_or_server
- Why deferred: Millions of compact model fits require workstation/server runtime.
- Required inputs: v3.5 sklearn readouts, v3.6 lineage split, feature ablation registry
- Deliverables: extended_methods_5000.csv, best_by_dataset_decoder_ablation.csv, failure_modes.md
- Exit criteria: all planned decoders compared, all feature ablations summarized, claim level updated

### D3_bootstrap_confidence_intervals — Bootstrap confidence intervals and calibration tables
- Phase: power_pc_validation
- Execution environment: power_pc_or_server
- Why deferred: Enough resampling must be done to make paper/beta claims statistically defensible.
- Required inputs: prediction tables, split summaries, shuffle summaries
- Deliverables: bootstrap_ci.csv, calibration_curve.csv, paper_table_statistics.csv
- Exit criteria: 95% CI reported, calibration quality reported, negative controls included

### D4_zenodo_raw_hdf5_ttl — Zenodo raw HDF5 / TTL / stimulus reconstruction
- Phase: dataset_expansion
- Execution environment: power_pc_or_server
- Why deferred: Raw archive is large and needs local storage, HDF5 inspection and possibly long parsing.
- Required inputs: Raw_data_MEA_data.zip, HDF5 reader, preprocessed spike windows for comparison
- Deliverables: hdf5_tree_report.md, ttl_channel_candidates.csv, raw_stimulus_windows.csv, raw_vs_preprocessed_comparison.md
- Exit criteria: raw structure mapped, TTL/stimulus presence or absence stated, raw-derived windows compared to v1.5/v3.6

### D5_dandi_nwb_task_aligned — DANDI/NWB task-aligned dataset discovery and parser
- Phase: dataset_expansion
- Execution environment: dev_pc_or_power_pc
- Why deferred: Needs online dataset search/download and multiple file schema checks.
- Required inputs: DANDI API/client, NWB files with units + intervals/trials/stimulus
- Deliverables: dandi_dataset_registry.csv, nwb_task_windows.csv, task_aligned_readout_report.md
- Exit criteria: at least 3 candidate Dandisets profiled, one task-aligned benchmark runs end-to-end

### D6_allen_visual_coding_adapter — Allen Brain Observatory / AllenSDK orientation benchmark
- Phase: dataset_expansion
- Execution environment: dev_pc_or_power_pc
- Why deferred: Allen downloads and SDK setup are better done on a workstation.
- Required inputs: AllenSDK, visual coding / Neuropixels sample, stimulus presentation tables
- Deliverables: allen_orientation_dataset_profile.json, orientation_readout_report.md, allen_result_bundle.zip
- Exit criteria: orientation task extracted, readout and shuffle baseline run, dataset added to registry

### D7_energy_latency_measurement — Measured energy/latency accounting
- Phase: power_pc_and_future_lab
- Execution environment: power_pc_first_then_lab
- Why deferred: Current v2.9 is a model; real energy requires measured host/electronics/lab boundaries.
- Required inputs: power meter or host telemetry, fixed benchmark manifest, task count and latency logs
- Deliverables: measured_energy_report.csv, latency_breakdown.csv, energy_claim_boundary.md
- Exit criteria: measured not only estimated, system boundary stated, no GPU advantage claim without matched baseline

### D8_external_api_credentials — External API read-only credential tests
- Phase: api_validation
- Execution environment: dev_pc_or_partner_environment
- Why deferred: Requires partner/platform access tokens and terms of use.
- Required inputs: FinalSpark or vendor API credentials, read-only API config, safety boundary
- Deliverables: api_metadata_result.json, read_only_trace_sample.json, write_denial_report.json
- Exit criteria: metadata read works, unsafe write is blocked, BioGPUTrace export works

### D9_hosted_server_beta — Hosted BioGPU Server beta deployment
- Phase: beta_platform
- Execution environment: cloud_server_or_onprem_server
- Why deferred: Only valuable after dataset expansion and validation gates exist.
- Required inputs: FastAPI beta server, job queue, auth/API keys, dataset registry, storage
- Deliverables: hosted_beta_url_or_local_deploy, user_role_tests.json, job_queue_demo_bundle.zip
- Exit criteria: two users can run sandbox jobs, quotas and audit logs work, unsafe modes blocked

### D10_lab_live_validation — First approved live BioGPU experiment
- Phase: future_lab
- Execution environment: approved_lab_or_vendor_platform
- Why deferred: Requires partner lab/vendor platform, operator approval, protocol ID and biosafety/ethics boundaries.
- Required inputs: approved protocol, operator, vendor/lab adapter, run manifest, audit plan
- Deliverables: live_shadow_or_closed_loop_bundle.zip, operator_log.md, live_validation_report.md
- Exit criteria: live read-only/shadow validated first, closed-loop only if approved, all results auditable

## B. v4 roadmap after the deferred work is visible
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

## C. Release rule
External users should first receive mock/replay/read-only access. Full live control is not deleted from the business plan; it is a separate premium lab-approved module after safety, operator, protocol and vendor/lab gates.