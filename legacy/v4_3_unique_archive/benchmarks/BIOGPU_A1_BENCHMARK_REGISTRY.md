# BioGPU-A1 Benchmark Registry

Version: `v2.3`

## Goal

Turn BioGPU from a hardware/software blueprint into a set of registered, auditable benchmark tasks with explicit inputs, encoders, substrates, readouts, metrics, controls and success gates.

## Boundary

The registry is hardware-neutral and safety-neutral by default. It defines contracts and benchmark evidence gates. It does not provide live wet-lab stimulation parameters, biological protocols, pinouts or vendor-specific operating instructions.

## Global success policy

- No performance claim is valid without registered negative controls.
- No energy advantage claim is valid without matched task and matched accuracy gates.
- Offline replay success is evidence for the software pipeline only, not proof of a live BioGPU device.
- Live-lab tasks require vendor adapter, platform documentation, facility SOP, safety interlocks and trained personnel.
- Each report must include task id, registry version, encoder version, readout, split policy, seed manifest and output bundle hash.

## Registry table

| Task | Stage | Status | Safety | Primary metric | Core controls |
|---|---:|---:|---:|---|---|
| `B0_target_vs_random_electrode` Target response separability | `offline_replay` | `implemented` | `offline_replay_only` | roc_auc | label_shuffle, random_time_window, random_electrode |
| `B1_spot_localization` Stimulus spot localization | `offline_replay` | `requires_data` | `offline_replay_only` | top1_accuracy | label_shuffle, random_time_window, region_prior_only |
| `B2_temporal_pattern_classification` Temporal pattern classification | `dry_run` | `ready_for_dry_run` | `dry_run_only` | macro_f1 | label_shuffle, random_time_window, event_order_shuffle |
| `B3_orientation_like_encoding` Orientation-like classification | `dry_run` | `ready_for_dry_run` | `dry_run_only` | accuracy | label_shuffle, random_time_window, shuffled_reservoir |
| `B4_adaptive_closed_loop` Adaptive closed-loop control | `future` | `requires_live_lab` | `live_lab_only` | learning_curve_slope | label_shuffle, random_time_window, fixed_policy, random_policy |
| `B5_energy_latency_comparison` Energy and latency comparison | `power_pc` | `ready_for_dry_run` | `dry_run_only` | joules_per_task | matched_accuracy_gate, idle_power_subtraction |
| `B6_substrate_stability` Substrate stability and drift | `licensed_lab` | `requires_live_lab` | `live_lab_only` | response_stability_score | environment_snapshot_required, blank_or_no_input_probe |

## Tasks

### B0_target_vs_random_electrode — Target response separability

**Purpose:** Verify that a stimulated target channel/region produces a separable response from non-target controls.

- Stage: `offline_replay`
- Status: `implemented`
- Safety class: `offline_replay_only`
- GPU comparison note: Biological signal validation task; not a silicon GPU speed claim.

**Input contract**

- Format: `BioGPUJob.target_pulse_replay`
- Required fields: `recording_id`, `target_electrode`, `pulse_window_ms`, `feature_window_ms`
- Example payload: `{"recording_id": "zenodo_14363732_recording_001", "target_electrode": 42, "pulse_window_ms": [0, 50], "feature_window_ms": [0, 250]}`
- Validation notes:
  - Target electrode must be present in recording metadata.
  - Feature window must be bounded and deterministic.

**Encoder**

- Name: `target_electrode_identity_encoder`
- Type: `one_hot_or_region_id`
- Output contract: offline replay key selecting target electrode/region; no live stimulation values are emitted.
- Hardware boundary: May map to MEA/HD-MEA sites only through a future vendor adapter and SOP.
- Dry-run checks:
  - target channel exists
  - window bounds valid
  - no hardware output in replay mode

**Substrate requirement**

- Class: `public_mea_replay_or_live_mea`
- Minimum channels: `32`
- Minimum repeats/class: `20`
- Timing: pulse-aligned response features within fixed post-event window
- Hardware components: `mea_chip`, `headstage_stimulator`, `runtime`, `storage`
- Notes:
  - Already supported by the public Zenodo MEA replay pipeline in earlier project stages.

**Readout**

- Name: `binary_target_readout`
- Feature contract: pulse-aligned spike/rate/latency vector
- Model family: regularized logistic regression or linear discriminant baseline
- Training split: grouped by recording/culture where metadata permits
- Output contract: probability(target_response > random_non_target_response)

**Metrics**

| Metric | Primary | Direction | Threshold | Interpretation |
|---|---:|---:|---|---|
| `roc_auc` | `True` | `higher_is_better` | registered threshold above shuffled baseline | Separability of target vs non-target response. |
| `balanced_accuracy` | `False` | `higher_is_better` | above chance | Robustness under class balance. |
| `effect_size` | `False` | `higher_is_better` | positive and stable across repeats | Magnitude of biological response difference. |

**Controls**

| Control | Type | Purpose | Pass condition |
|---|---:|---|---|
| `label_shuffle` | `negative` | Verify the benchmark is not solved by leakage or class imbalance. | Primary metric must drop toward chance or below the registered success threshold after label shuffle. |
| `random_time_window` | `negative` | Verify features are tied to stimulus/response windows and not arbitrary recording statistics. | Random-window metric must be materially worse than true-window metric. |
| `random_electrode` | `negative` | Compare target electrode to random non-target electrode. | Random electrode control must not match true target performance. |

**Success gates**

- `gate_b0_metric` (required): Primary metric beats label-shuffle and random-electrode controls.
- `gate_b0_reproducibility` (required): Result remains stable under repeated seeds or grouped folds.

**Known failure modes**

- metadata leakage
- class imbalance
- single-recording overfit

**Implementation references inside project**

- `biogpu/analysis/zenodo_pulse_readout.py`
- `outputs/realdata_zenodo_14363732_v17_paper_grade`

### B1_spot_localization — Stimulus spot localization

**Purpose:** Decode which electrode/region was stimulated from the observed living-substrate response.

- Stage: `offline_replay`
- Status: `requires_data`
- Safety class: `offline_replay_only`
- GPU comparison note: I/O calibration and spatial addressing task; candidate prerequisite for later compute benchmarks.

**Input contract**

- Format: `BioGPUJob.spatial_spot_replay`
- Required fields: `recording_id`, `spot_id`, `candidate_regions`, `feature_window_ms`
- Example payload: `{"recording_id": "zenodo_14363732_recording_001", "spot_id": "region_A07", "candidate_regions": ["region_A07", "region_B11", "region_C04"], "feature_window_ms": [0, 300]}`
- Validation notes:
  - Candidate regions must be known before training.
  - Region labels must not be inferred from feature names.

**Encoder**

- Name: `spatial_region_encoder`
- Type: `region_id_to_electrode_set`
- Output contract: logical region or electrode-set identifier
- Hardware boundary: Future live implementation must translate logical regions via selected vendor map.
- Dry-run checks:
  - region exists
  - region has enough channels
  - no overlap leakage between train/test labels

**Substrate requirement**

- Class: `balanced_mea_region_replay_or_live_hd_mea`
- Minimum channels: `64`
- Minimum repeats/class: `25`
- Timing: consistent pre/post region stimulation windows
- Hardware components: `mea_chip`, `headstage_stimulator`, `wet_cartridge`, `runtime`
- Notes:
  - Best suited to HD-MEA where spatial resolution and channel density are high.

**Readout**

- Name: `multiclass_spot_readout`
- Feature contract: region-level response vector with optional neighborhood aggregation
- Model family: linear classifier, ridge classifier, or calibrated multinomial logistic regression
- Training split: stratified by region and grouped by recording where possible
- Output contract: spot_id plus top-k candidate list

**Metrics**

| Metric | Primary | Direction | Threshold | Interpretation |
|---|---:|---:|---|---|
| `top1_accuracy` | `True` | `higher_is_better` | above label-shuffle and region-prior baselines | Direct localization accuracy. |
| `topk_accuracy` | `False` | `higher_is_better` | top-k above chance | Spatial neighborhood recall. |
| `confusion_entropy` | `False` | `lower_is_better` | lower than shuffled labels | Whether confusion is structured or random. |

**Controls**

| Control | Type | Purpose | Pass condition |
|---|---:|---|---|
| `label_shuffle` | `negative` | Verify the benchmark is not solved by leakage or class imbalance. | Primary metric must drop toward chance or below the registered success threshold after label shuffle. |
| `random_time_window` | `negative` | Verify features are tied to stimulus/response windows and not arbitrary recording statistics. | Random-window metric must be materially worse than true-window metric. |
| `region_prior_only` | `negative` | Check if class priors alone solve the benchmark. | Prior-only model must fail the registered threshold. |

**Success gates**

- `gate_b1_balanced_labels` (required): Each region has enough repeats after exclusions.
- `gate_b1_topk` (required): Top-k accuracy beats all negative controls.

**Known failure modes**

- unbalanced region labels
- neighbor label leakage
- insufficient channel density

**Implementation references inside project**

- `biogpu/analysis/zenodo_condition_spot.py`

### B2_temporal_pattern_classification — Temporal pattern classification

**Purpose:** Test whether the substrate response preserves time-coded input structure.

- Stage: `dry_run`
- Status: `ready_for_dry_run`
- Safety class: `dry_run_only`
- GPU comparison note: Candidate task for sample-efficiency comparison against CPU/GPU/SNN reservoirs.

**Input contract**

- Format: `BioGPUJob.temporal_pattern`
- Required fields: `pattern_id`, `event_times_ms`, `duration_ms`, `class_label`
- Example payload: `{"pattern_id": "burst_3_interval_50ms", "event_times_ms": [0, 50, 100], "duration_ms": 250, "class_label": "burst_3"}`
- Validation notes:
  - Event times must be monotonic.
  - Duration must contain all events.

**Encoder**

- Name: `temporal_pulse_train_encoder`
- Type: `symbol_to_event_train`
- Output contract: abstract event train for replay/simulation; live amplitude/current is not included.
- Hardware boundary: Live mapping requires selected platform adapter and SOP-approved safe stimulation limits.
- Dry-run checks:
  - events monotonic
  - minimum inter-event interval respected
  - pattern checksum stored

**Substrate requirement**

- Class: `simulated_reservoir_then_live_mea`
- Minimum channels: `64`
- Minimum repeats/class: `30`
- Timing: millisecond-resolution event alignment in replay/simulation; vendor timestamping for live mode
- Hardware components: `runtime`, `headstage_stimulator`, `mea_chip`, `storage`
- Notes:
  - First true reservoir-memory candidate before closed-loop work.

**Readout**

- Name: `temporal_state_readout`
- Feature contract: time-binned spike/rate/latency matrix
- Model family: ridge classifier, temporal pooling readout, or SNN readout baseline
- Training split: blocked temporal folds; no adjacent-window leakage
- Output contract: temporal pattern class and confidence

**Metrics**

| Metric | Primary | Direction | Threshold | Interpretation |
|---|---:|---:|---|---|
| `macro_f1` | `True` | `higher_is_better` | above shuffled sequence labels | Class-balanced temporal classification performance. |
| `latency_to_decision_ms` | `False` | `lower_is_better` | lower is better at equal accuracy | How quickly the response becomes decodable. |
| `memory_decay_curve` | `False` | `within_range` | registered curve shape beats null | Whether history is preserved over delay. |

**Controls**

| Control | Type | Purpose | Pass condition |
|---|---:|---|---|
| `label_shuffle` | `negative` | Verify the benchmark is not solved by leakage or class imbalance. | Primary metric must drop toward chance or below the registered success threshold after label shuffle. |
| `random_time_window` | `negative` | Verify features are tied to stimulus/response windows and not arbitrary recording statistics. | Random-window metric must be materially worse than true-window metric. |
| `event_order_shuffle` | `negative` | Destroy temporal order while preserving event counts. | Performance must degrade when order is destroyed. |

**Success gates**

- `gate_b2_no_order_leakage` (required): Order-shuffle control fails while true temporal patterns pass.
- `gate_b2_latency_logged` (required): Latency and decision-window metadata are exported.

**Known failure modes**

- temporal leakage
- clock drift
- readout overfitting to event counts

**Implementation references inside project**

- `biogpu/datasets/sequences.py`
- `biogpu/reservoir/snn_reservoir.py`

### B3_orientation_like_encoding — Orientation-like classification

**Purpose:** Map simple visual/orientation classes to stimulation/replay encodings and decode the response.

- Stage: `dry_run`
- Status: `ready_for_dry_run`
- Safety class: `dry_run_only`
- GPU comparison note: First fair task benchmark once live energy telemetry exists.

**Input contract**

- Format: `BioGPUJob.orientation_class`
- Required fields: `sample_id`, `orientation_deg`, `encoded_pattern_id`
- Example payload: `{"sample_id": "orientation_090_0001", "orientation_deg": 90, "encoded_pattern_id": "ori_90_spatial_temporal_v1"}`
- Validation notes:
  - Orientation labels must be fixed to registry classes.
  - Encoder version must be recorded.

**Encoder**

- Name: `orientation_to_spatiotemporal_encoder`
- Type: `class_to_spatial_temporal_pattern`
- Output contract: deterministic pattern id and logical channel group sequence
- Hardware boundary: Live mode uses adapter-specific channel map; no direct voltage/current values in registry.
- Dry-run checks:
  - class list stable
  - pattern hash stable
  - train/test encoder version locked

**Substrate requirement**

- Class: `simulated_then_live_mea_reservoir`
- Minimum channels: `64`
- Minimum repeats/class: `40`
- Timing: fixed presentation window and fixed response aggregation window
- Hardware components: `runtime`, `mea_chip`, `headstage_stimulator`, `host_pc`
- Notes:
  - Good bridge task because existing software already has orientation datasets and baselines.

**Readout**

- Name: `orientation_readout`
- Feature contract: reservoir state vector or time-pooled response vector
- Model family: linear, ridge, MLP baseline, SNN baseline
- Training split: stratified train/validation/test with fixed seed manifest
- Output contract: orientation class plus confidence

**Metrics**

| Metric | Primary | Direction | Threshold | Interpretation |
|---|---:|---:|---|---|
| `accuracy` | `True` | `higher_is_better` | above shuffled reservoir and label controls | Main class accuracy. |
| `confusion_matrix_stability` | `False` | `within_range` | stable across seeds | Whether errors are structured and repeatable. |
| `energy_proxy_per_sample` | `False` | `lower_is_better` | compare at matched accuracy | Early bridge to energy/task comparison. |

**Controls**

| Control | Type | Purpose | Pass condition |
|---|---:|---|---|
| `label_shuffle` | `negative` | Verify the benchmark is not solved by leakage or class imbalance. | Primary metric must drop toward chance or below the registered success threshold after label shuffle. |
| `random_time_window` | `negative` | Verify features are tied to stimulus/response windows and not arbitrary recording statistics. | Random-window metric must be materially worse than true-window metric. |
| `shuffled_reservoir` | `negative` | Break substrate structure while preserving dimensions. | Shuffled reservoir must not outperform true substrate. |

**Success gates**

- `gate_b3_baselines` (required): Registered silicon/software baselines are run in the same report.
- `gate_b3_confusion` (required): Confusion matrix and per-class metrics are exported.

**Known failure modes**

- encoder leakage
- too few classes
- baseline mismatch

**Implementation references inside project**

- `biogpu/benchmarks/orientation.py`
- `biogpu/datasets/orientation.py`

### B4_adaptive_closed_loop — Adaptive closed-loop control

**Purpose:** Test whether feedback-driven input selection improves task performance over fixed stimulation/replay schedules.

- Stage: `future`
- Status: `requires_live_lab`
- Safety class: `live_lab_only`
- GPU comparison note: Long-term BioGPU advantage candidate; requires strict live experimental governance.

**Input contract**

- Format: `BioGPUJob.closed_loop_episode`
- Required fields: `episode_id`, `state`, `allowed_actions`, `reward_definition`
- Example payload: `{"episode_id": "closed_loop_0001", "state": {"previous_response_class": "low_activity"}, "allowed_actions": ["pattern_A", "pattern_B", "pattern_C"], "reward_definition": "increase separability without violating safety envelope"}`
- Validation notes:
  - Reward must be declared before run.
  - Action set must be finite and adapter-validated.

**Encoder**

- Name: `feedback_policy_encoder`
- Type: `state_to_next_pattern`
- Output contract: next logical stimulation/replay pattern selected by controller
- Hardware boundary: Live controller must be locked behind vendor adapter, SOP, and safety interlocks.
- Dry-run checks:
  - action set finite
  - policy seed logged
  - safety class not live unless explicit lab mode

**Substrate requirement**

- Class: `live_mea_or_replay_with_episode_logs`
- Minimum channels: `64`
- Minimum repeats/class: `50`
- Timing: online response extraction with bounded decision latency
- Hardware components: `runtime`, `feedback_controller`, `headstage_stimulator`, `wet_cartridge`, `environment_control`
- Notes:
  - This is not a first live benchmark; it depends on prior B0-B3 stability.

**Readout**

- Name: `online_policy_readout`
- Feature contract: streaming features plus episode state
- Model family: bandit/controller baseline, fixed-policy baseline, adaptive controller
- Training split: pre-registered episode blocks with holdout days/cultures where possible
- Output contract: selected action, reward, response feature delta, safety status

**Metrics**

| Metric | Primary | Direction | Threshold | Interpretation |
|---|---:|---:|---|---|
| `learning_curve_slope` | `True` | `higher_is_better` | improves over fixed-policy baseline | Whether closed-loop control learns. |
| `safety_interlock_rate` | `False` | `within_range` | zero unsafe outputs; logged blocked actions allowed | Whether controller stays inside safety envelope. |
| `energy_per_improvement` | `False` | `lower_is_better` | lower than fixed schedule at matched endpoint | Energy cost of adaptation. |

**Controls**

| Control | Type | Purpose | Pass condition |
|---|---:|---|---|
| `label_shuffle` | `negative` | Verify the benchmark is not solved by leakage or class imbalance. | Primary metric must drop toward chance or below the registered success threshold after label shuffle. |
| `random_time_window` | `negative` | Verify features are tied to stimulus/response windows and not arbitrary recording statistics. | Random-window metric must be materially worse than true-window metric. |
| `fixed_policy` | `baseline` | Compare adaptive controller to non-adaptive schedule. | Adaptive controller must beat fixed policy on registered endpoint. |
| `random_policy` | `negative` | Verify reward does not improve under random action selection. | Random policy must not match adaptive performance. |

**Success gates**

- `gate_b4_preconditions` (required): B0-B3 pass on the same substrate class before closed-loop live work.
- `gate_b4_safety` (required): All controller decisions pass adapter and SOP safety checks.

**Known failure modes**

- unsafe feedback
- reward hacking
- culture drift
- nonstationary substrate

**Implementation references inside project**

- `biogpu/feedback/controller.py`

### B5_energy_latency_comparison — Energy and latency comparison

**Purpose:** Measure task-level energy, latency, and throughput for BioGPU runtime versus CPU/GPU/SNN baselines.

- Stage: `power_pc`
- Status: `ready_for_dry_run`
- Safety class: `dry_run_only`
- GPU comparison note: Main comparison wrapper; it does not prove BioGPU advantage unless underlying task and measurement gates pass.

**Input contract**

- Format: `BioGPUJob.energy_latency_suite`
- Required fields: `benchmark_task_id`, `batch_size`, `power_source`, `measurement_window_s`
- Example payload: `{"benchmark_task_id": "B3_orientation_like_encoding", "batch_size": 256, "power_source": "host_power_meter_or_nvidia_smi_proxy", "measurement_window_s": 60}`
- Validation notes:
  - Energy source must be declared.
  - Accuracy threshold must be matched before energy claims.

**Encoder**

- Name: `benchmark_suite_runner`
- Type: `registered_task_batch`
- Output contract: batch of registered benchmark jobs with fixed seed manifest
- Hardware boundary: Does not imply live stimulation; can run replay/simulation baselines first.
- Dry-run checks:
  - baseline list present
  - measurement window present
  - accuracy-matching rule present

**Substrate requirement**

- Class: `software_replay_simulation_then_live_hardware`
- Minimum channels: `0`
- Minimum repeats/class: `0`
- Timing: wall-clock and power telemetry aligned to task window
- Hardware components: `host_pc`, `storage`, `runtime`, `power_telemetry`
- Notes:
  - Energy claims are invalid unless matched against the same task and accuracy target.

**Readout**

- Name: `energy_latency_reporter`
- Feature contract: per-run metrics table with accuracy, latency, energy, hardware metadata
- Model family: reporting layer, not predictive model
- Training split: not applicable; consumes already registered benchmark outputs
- Output contract: task-level energy/latency comparison table

**Metrics**

| Metric | Primary | Direction | Threshold | Interpretation |
|---|---:|---:|---|---|
| `joules_per_task` | `True` | `lower_is_better` | reported only at matched accuracy gate | Primary energy comparison metric. |
| `end_to_end_latency_ms` | `False` | `lower_is_better` | reported with batch size | Wall-clock task latency. |
| `throughput_tasks_per_s` | `False` | `higher_is_better` | reported with batch size | Task throughput. |

**Controls**

| Control | Type | Purpose | Pass condition |
|---|---:|---|---|
| `matched_accuracy_gate` | `fairness` | Prevent energy comparison when models are not solving the same task. | Energy metric is claimable only when accuracy is matched or explicitly stratified. |
| `idle_power_subtraction` | `measurement` | Separate idle host/life-support power from active run power where possible. | Report both gross and net energy. |

**Success gates**

- `gate_b5_power_metadata` (required): Power source and measurement method are included in output.
- `gate_b5_matched_accuracy` (required): Comparison only claims advantage after matched-accuracy rule passes.

**Known failure modes**

- unmatched task accuracy
- missing idle power
- batch-size cherry-picking

**Implementation references inside project**

- `biogpu/diagnostics/regression.py`
- `outputs/experiments`

### B6_substrate_stability — Substrate stability and drift

**Purpose:** Quantify whether the substrate remains stable enough for repeated computation across time.

- Stage: `licensed_lab`
- Status: `requires_live_lab`
- Safety class: `live_lab_only`
- GPU comparison note: Precondition for serious hardware benchmarking; not a GPU comparison by itself.

**Input contract**

- Format: `BioGPUJob.stability_probe`
- Required fields: `probe_id`, `probe_pattern_id`, `timepoint`, `environment_snapshot`
- Example payload: `{"probe_id": "daily_probe_0001", "probe_pattern_id": "low_intensity_reference_pattern", "timepoint": "day_03_hour_12", "environment_snapshot": {"temperature_ok": true, "co2_ok": true, "humidity_ok": true}}`
- Validation notes:
  - Probe pattern must be pre-registered.
  - Environment snapshot must be attached to each run.

**Encoder**

- Name: `reference_probe_encoder`
- Type: `fixed_reference_pattern`
- Output contract: logical reference pattern used for drift monitoring
- Hardware boundary: Live pattern requires lab SOP and vendor adapter.
- Dry-run checks:
  - probe id registered
  - environment fields present
  - probe version fixed

**Substrate requirement**

- Class: `live_mea_hd_mea`
- Minimum channels: `64`
- Minimum repeats/class: `20`
- Timing: repeatable probe windows across hours/days
- Hardware components: `wet_cartridge`, `environment_control`, `mea_chip`, `headstage_stimulator`, `storage`
- Notes:
  - Required before any long-running claim about biological acceleration.

**Readout**

- Name: `drift_monitor_readout`
- Feature contract: reference response vector over time
- Model family: stability statistics, control charts, drift detector
- Training split: time-blocked; initial calibration vs later probe windows
- Output contract: stability score, drift alert, environment correlation summary

**Metrics**

| Metric | Primary | Direction | Threshold | Interpretation |
|---|---:|---:|---|---|
| `response_stability_score` | `True` | `higher_is_better` | within registered stability band | Repeatability of reference response. |
| `drift_rate_per_hour` | `False` | `lower_is_better` | below registered drift threshold | Rate of substrate state change. |
| `environment_correlation` | `False` | `within_range` | reported, not necessarily optimized | Whether drift correlates with life-support telemetry. |

**Controls**

| Control | Type | Purpose | Pass condition |
|---|---:|---|---|
| `environment_snapshot_required` | `measurement` | Link response drift to environmental telemetry. | Every probe has environment metadata. |
| `blank_or_no_input_probe` | `negative` | Track spontaneous baseline drift. | Blank/no-input response is reported separately from reference probe response. |

**Success gates**

- `gate_b6_environment` (required): Environment telemetry is captured with every run.
- `gate_b6_drift_band` (required): Stability score remains inside pre-registered range for required duration.

**Known failure modes**

- culture drift
- environment fluctuation
- electrode degradation
- media/handling effects

**Implementation references inside project**

- `biogpu/hardware/blueprint_v22.py`

## Required artifacts

- registry JSON
- registry CSV
- benchmark report Markdown
- task input manifest
- readout metrics table
- negative-control metrics table
- hardware/readiness mapping
- run metadata and output bundle hash
