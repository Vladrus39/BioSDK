from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Literal

BenchmarkStage = Literal["offline_replay", "dry_run", "power_pc", "licensed_lab", "future"]
BenchmarkStatus = Literal["implemented", "ready_for_dry_run", "requires_data", "requires_live_lab", "future"]
SafetyClass = Literal["offline_replay_only", "dry_run_only", "live_lab_only"]
MetricDirection = Literal["higher_is_better", "lower_is_better", "within_range"]


@dataclass(frozen=True)
class InputSpec:
    format: str
    required_fields: list[str]
    example_payload: dict
    validation_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class EncoderSpec:
    name: str
    encoding_type: str
    output_contract: str
    hardware_boundary: str
    dry_run_checks: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class SubstrateRequirement:
    substrate_class: str
    minimum_channels: int
    minimum_repeats_per_class: int
    timing_requirement: str
    hardware_components: list[str]
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class ReadoutSpec:
    name: str
    feature_contract: str
    model_family: str
    training_split: str
    output_contract: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class MetricSpec:
    name: str
    direction: MetricDirection
    primary: bool
    threshold: str
    interpretation: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class ControlSpec:
    name: str
    control_type: str
    purpose: str
    pass_condition: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class SuccessGate:
    gate_id: str
    description: str
    required: bool = True

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class BenchmarkTaskSpec:
    task_id: str
    title: str
    purpose: str
    stage: BenchmarkStage
    status: BenchmarkStatus
    safety_class: SafetyClass
    input_spec: InputSpec
    encoder: EncoderSpec
    substrate: SubstrateRequirement
    readout: ReadoutSpec
    metrics: list[MetricSpec]
    controls: list[ControlSpec]
    success_gates: list[SuccessGate]
    failure_modes: list[str] = field(default_factory=list)
    gpu_comparison_note: str = ""
    implementation_files: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        data = asdict(self)
        return data


@dataclass(frozen=True)
class BenchmarkRegistry:
    version: str
    name: str
    goal: str
    boundary_note: str
    tasks: list[BenchmarkTaskSpec]
    global_success_policy: list[str]
    required_artifacts: list[str]

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "name": self.name,
            "goal": self.goal,
            "boundary_note": self.boundary_note,
            "tasks": [t.to_dict() for t in self.tasks],
            "global_success_policy": list(self.global_success_policy),
            "required_artifacts": list(self.required_artifacts),
        }


def _common_controls() -> list[ControlSpec]:
    return [
        ControlSpec(
            name="label_shuffle",
            control_type="negative",
            purpose="Verify the benchmark is not solved by leakage or class imbalance.",
            pass_condition="Primary metric must drop toward chance or below the registered success threshold after label shuffle.",
        ),
        ControlSpec(
            name="random_time_window",
            control_type="negative",
            purpose="Verify features are tied to stimulus/response windows and not arbitrary recording statistics.",
            pass_condition="Random-window metric must be materially worse than true-window metric.",
        ),
    ]


def build_biogpu_v23_benchmark_registry() -> BenchmarkRegistry:
    tasks: list[BenchmarkTaskSpec] = [
        BenchmarkTaskSpec(
            task_id="B0_target_vs_random_electrode",
            title="Target response separability",
            purpose="Verify that a stimulated target channel/region produces a separable response from non-target controls.",
            stage="offline_replay",
            status="implemented",
            safety_class="offline_replay_only",
            input_spec=InputSpec(
                format="BioGPUJob.target_pulse_replay",
                required_fields=["recording_id", "target_electrode", "pulse_window_ms", "feature_window_ms"],
                example_payload={
                    "recording_id": "zenodo_14363732_recording_001",
                    "target_electrode": 42,
                    "pulse_window_ms": [0, 50],
                    "feature_window_ms": [0, 250],
                },
                validation_notes=[
                    "Target electrode must be present in recording metadata.",
                    "Feature window must be bounded and deterministic.",
                ],
            ),
            encoder=EncoderSpec(
                name="target_electrode_identity_encoder",
                encoding_type="one_hot_or_region_id",
                output_contract="offline replay key selecting target electrode/region; no live stimulation values are emitted.",
                hardware_boundary="May map to MEA/HD-MEA sites only through a future vendor adapter and SOP.",
                dry_run_checks=["target channel exists", "window bounds valid", "no hardware output in replay mode"],
            ),
            substrate=SubstrateRequirement(
                substrate_class="public_mea_replay_or_live_mea",
                minimum_channels=32,
                minimum_repeats_per_class=20,
                timing_requirement="pulse-aligned response features within fixed post-event window",
                hardware_components=["mea_chip", "headstage_stimulator", "runtime", "storage"],
                notes=["Already supported by the public Zenodo MEA replay pipeline in earlier project stages."],
            ),
            readout=ReadoutSpec(
                name="binary_target_readout",
                feature_contract="pulse-aligned spike/rate/latency vector",
                model_family="regularized logistic regression or linear discriminant baseline",
                training_split="grouped by recording/culture where metadata permits",
                output_contract="probability(target_response > random_non_target_response)",
            ),
            metrics=[
                MetricSpec("roc_auc", "higher_is_better", True, "registered threshold above shuffled baseline", "Separability of target vs non-target response."),
                MetricSpec("balanced_accuracy", "higher_is_better", False, "above chance", "Robustness under class balance."),
                MetricSpec("effect_size", "higher_is_better", False, "positive and stable across repeats", "Magnitude of biological response difference."),
            ],
            controls=_common_controls() + [
                ControlSpec(
                    name="random_electrode",
                    control_type="negative",
                    purpose="Compare target electrode to random non-target electrode.",
                    pass_condition="Random electrode control must not match true target performance.",
                )
            ],
            success_gates=[
                SuccessGate("gate_b0_metric", "Primary metric beats label-shuffle and random-electrode controls."),
                SuccessGate("gate_b0_reproducibility", "Result remains stable under repeated seeds or grouped folds."),
            ],
            failure_modes=["metadata leakage", "class imbalance", "single-recording overfit"],
            gpu_comparison_note="Biological signal validation task; not a silicon GPU speed claim.",
            implementation_files=[
                "biogpu/analysis/zenodo_pulse_readout.py",
                "outputs/realdata_zenodo_14363732_v17_paper_grade",
            ],
        ),
        BenchmarkTaskSpec(
            task_id="B1_spot_localization",
            title="Stimulus spot localization",
            purpose="Decode which electrode/region was stimulated from the observed living-substrate response.",
            stage="offline_replay",
            status="requires_data",
            safety_class="offline_replay_only",
            input_spec=InputSpec(
                format="BioGPUJob.spatial_spot_replay",
                required_fields=["recording_id", "spot_id", "candidate_regions", "feature_window_ms"],
                example_payload={
                    "recording_id": "zenodo_14363732_recording_001",
                    "spot_id": "region_A07",
                    "candidate_regions": ["region_A07", "region_B11", "region_C04"],
                    "feature_window_ms": [0, 300],
                },
                validation_notes=["Candidate regions must be known before training.", "Region labels must not be inferred from feature names."],
            ),
            encoder=EncoderSpec(
                name="spatial_region_encoder",
                encoding_type="region_id_to_electrode_set",
                output_contract="logical region or electrode-set identifier",
                hardware_boundary="Future live implementation must translate logical regions via selected vendor map.",
                dry_run_checks=["region exists", "region has enough channels", "no overlap leakage between train/test labels"],
            ),
            substrate=SubstrateRequirement(
                substrate_class="balanced_mea_region_replay_or_live_hd_mea",
                minimum_channels=64,
                minimum_repeats_per_class=25,
                timing_requirement="consistent pre/post region stimulation windows",
                hardware_components=["mea_chip", "headstage_stimulator", "wet_cartridge", "runtime"],
                notes=["Best suited to HD-MEA where spatial resolution and channel density are high."],
            ),
            readout=ReadoutSpec(
                name="multiclass_spot_readout",
                feature_contract="region-level response vector with optional neighborhood aggregation",
                model_family="linear classifier, ridge classifier, or calibrated multinomial logistic regression",
                training_split="stratified by region and grouped by recording where possible",
                output_contract="spot_id plus top-k candidate list",
            ),
            metrics=[
                MetricSpec("top1_accuracy", "higher_is_better", True, "above label-shuffle and region-prior baselines", "Direct localization accuracy."),
                MetricSpec("topk_accuracy", "higher_is_better", False, "top-k above chance", "Spatial neighborhood recall."),
                MetricSpec("confusion_entropy", "lower_is_better", False, "lower than shuffled labels", "Whether confusion is structured or random."),
            ],
            controls=_common_controls() + [
                ControlSpec("region_prior_only", "negative", "Check if class priors alone solve the benchmark.", "Prior-only model must fail the registered threshold.")
            ],
            success_gates=[
                SuccessGate("gate_b1_balanced_labels", "Each region has enough repeats after exclusions."),
                SuccessGate("gate_b1_topk", "Top-k accuracy beats all negative controls."),
            ],
            failure_modes=["unbalanced region labels", "neighbor label leakage", "insufficient channel density"],
            gpu_comparison_note="I/O calibration and spatial addressing task; candidate prerequisite for later compute benchmarks.",
            implementation_files=["biogpu/analysis/zenodo_condition_spot.py"],
        ),
        BenchmarkTaskSpec(
            task_id="B2_temporal_pattern_classification",
            title="Temporal pattern classification",
            purpose="Test whether the substrate response preserves time-coded input structure.",
            stage="dry_run",
            status="ready_for_dry_run",
            safety_class="dry_run_only",
            input_spec=InputSpec(
                format="BioGPUJob.temporal_pattern",
                required_fields=["pattern_id", "event_times_ms", "duration_ms", "class_label"],
                example_payload={
                    "pattern_id": "burst_3_interval_50ms",
                    "event_times_ms": [0, 50, 100],
                    "duration_ms": 250,
                    "class_label": "burst_3",
                },
                validation_notes=["Event times must be monotonic.", "Duration must contain all events."],
            ),
            encoder=EncoderSpec(
                name="temporal_pulse_train_encoder",
                encoding_type="symbol_to_event_train",
                output_contract="abstract event train for replay/simulation; live amplitude/current is not included.",
                hardware_boundary="Live mapping requires selected platform adapter and SOP-approved safe stimulation limits.",
                dry_run_checks=["events monotonic", "minimum inter-event interval respected", "pattern checksum stored"],
            ),
            substrate=SubstrateRequirement(
                substrate_class="simulated_reservoir_then_live_mea",
                minimum_channels=64,
                minimum_repeats_per_class=30,
                timing_requirement="millisecond-resolution event alignment in replay/simulation; vendor timestamping for live mode",
                hardware_components=["runtime", "headstage_stimulator", "mea_chip", "storage"],
                notes=["First true reservoir-memory candidate before closed-loop work."],
            ),
            readout=ReadoutSpec(
                name="temporal_state_readout",
                feature_contract="time-binned spike/rate/latency matrix",
                model_family="ridge classifier, temporal pooling readout, or SNN readout baseline",
                training_split="blocked temporal folds; no adjacent-window leakage",
                output_contract="temporal pattern class and confidence",
            ),
            metrics=[
                MetricSpec("macro_f1", "higher_is_better", True, "above shuffled sequence labels", "Class-balanced temporal classification performance."),
                MetricSpec("latency_to_decision_ms", "lower_is_better", False, "lower is better at equal accuracy", "How quickly the response becomes decodable."),
                MetricSpec("memory_decay_curve", "within_range", False, "registered curve shape beats null", "Whether history is preserved over delay."),
            ],
            controls=_common_controls() + [
                ControlSpec("event_order_shuffle", "negative", "Destroy temporal order while preserving event counts.", "Performance must degrade when order is destroyed.")
            ],
            success_gates=[
                SuccessGate("gate_b2_no_order_leakage", "Order-shuffle control fails while true temporal patterns pass."),
                SuccessGate("gate_b2_latency_logged", "Latency and decision-window metadata are exported."),
            ],
            failure_modes=["temporal leakage", "clock drift", "readout overfitting to event counts"],
            gpu_comparison_note="Candidate task for sample-efficiency comparison against CPU/GPU/SNN reservoirs.",
            implementation_files=["biogpu/datasets/sequences.py", "biogpu/reservoir/snn_reservoir.py"],
        ),
        BenchmarkTaskSpec(
            task_id="B3_orientation_like_encoding",
            title="Orientation-like classification",
            purpose="Map simple visual/orientation classes to stimulation/replay encodings and decode the response.",
            stage="dry_run",
            status="ready_for_dry_run",
            safety_class="dry_run_only",
            input_spec=InputSpec(
                format="BioGPUJob.orientation_class",
                required_fields=["sample_id", "orientation_deg", "encoded_pattern_id"],
                example_payload={
                    "sample_id": "orientation_090_0001",
                    "orientation_deg": 90,
                    "encoded_pattern_id": "ori_90_spatial_temporal_v1",
                },
                validation_notes=["Orientation labels must be fixed to registry classes.", "Encoder version must be recorded."],
            ),
            encoder=EncoderSpec(
                name="orientation_to_spatiotemporal_encoder",
                encoding_type="class_to_spatial_temporal_pattern",
                output_contract="deterministic pattern id and logical channel group sequence",
                hardware_boundary="Live mode uses adapter-specific channel map; no direct voltage/current values in registry.",
                dry_run_checks=["class list stable", "pattern hash stable", "train/test encoder version locked"],
            ),
            substrate=SubstrateRequirement(
                substrate_class="simulated_then_live_mea_reservoir",
                minimum_channels=64,
                minimum_repeats_per_class=40,
                timing_requirement="fixed presentation window and fixed response aggregation window",
                hardware_components=["runtime", "mea_chip", "headstage_stimulator", "host_pc"],
                notes=["Good bridge task because existing software already has orientation datasets and baselines."],
            ),
            readout=ReadoutSpec(
                name="orientation_readout",
                feature_contract="reservoir state vector or time-pooled response vector",
                model_family="linear, ridge, MLP baseline, SNN baseline",
                training_split="stratified train/validation/test with fixed seed manifest",
                output_contract="orientation class plus confidence",
            ),
            metrics=[
                MetricSpec("accuracy", "higher_is_better", True, "above shuffled reservoir and label controls", "Main class accuracy."),
                MetricSpec("confusion_matrix_stability", "within_range", False, "stable across seeds", "Whether errors are structured and repeatable."),
                MetricSpec("energy_proxy_per_sample", "lower_is_better", False, "compare at matched accuracy", "Early bridge to energy/task comparison."),
            ],
            controls=_common_controls() + [
                ControlSpec("shuffled_reservoir", "negative", "Break substrate structure while preserving dimensions.", "Shuffled reservoir must not outperform true substrate.")
            ],
            success_gates=[
                SuccessGate("gate_b3_baselines", "Registered silicon/software baselines are run in the same report."),
                SuccessGate("gate_b3_confusion", "Confusion matrix and per-class metrics are exported."),
            ],
            failure_modes=["encoder leakage", "too few classes", "baseline mismatch"],
            gpu_comparison_note="First fair task benchmark once live energy telemetry exists.",
            implementation_files=["biogpu/benchmarks/orientation.py", "biogpu/datasets/orientation.py"],
        ),
        BenchmarkTaskSpec(
            task_id="B4_adaptive_closed_loop",
            title="Adaptive closed-loop control",
            purpose="Test whether feedback-driven input selection improves task performance over fixed stimulation/replay schedules.",
            stage="future",
            status="requires_live_lab",
            safety_class="live_lab_only",
            input_spec=InputSpec(
                format="BioGPUJob.closed_loop_episode",
                required_fields=["episode_id", "state", "allowed_actions", "reward_definition"],
                example_payload={
                    "episode_id": "closed_loop_0001",
                    "state": {"previous_response_class": "low_activity"},
                    "allowed_actions": ["pattern_A", "pattern_B", "pattern_C"],
                    "reward_definition": "increase separability without violating safety envelope",
                },
                validation_notes=["Reward must be declared before run.", "Action set must be finite and adapter-validated."],
            ),
            encoder=EncoderSpec(
                name="feedback_policy_encoder",
                encoding_type="state_to_next_pattern",
                output_contract="next logical stimulation/replay pattern selected by controller",
                hardware_boundary="Live controller must be locked behind vendor adapter, SOP, and safety interlocks.",
                dry_run_checks=["action set finite", "policy seed logged", "safety class not live unless explicit lab mode"],
            ),
            substrate=SubstrateRequirement(
                substrate_class="live_mea_or_replay_with_episode_logs",
                minimum_channels=64,
                minimum_repeats_per_class=50,
                timing_requirement="online response extraction with bounded decision latency",
                hardware_components=["runtime", "feedback_controller", "headstage_stimulator", "wet_cartridge", "environment_control"],
                notes=["This is not a first live benchmark; it depends on prior B0-B3 stability."],
            ),
            readout=ReadoutSpec(
                name="online_policy_readout",
                feature_contract="streaming features plus episode state",
                model_family="bandit/controller baseline, fixed-policy baseline, adaptive controller",
                training_split="pre-registered episode blocks with holdout days/cultures where possible",
                output_contract="selected action, reward, response feature delta, safety status",
            ),
            metrics=[
                MetricSpec("learning_curve_slope", "higher_is_better", True, "improves over fixed-policy baseline", "Whether closed-loop control learns."),
                MetricSpec("safety_interlock_rate", "within_range", False, "zero unsafe outputs; logged blocked actions allowed", "Whether controller stays inside safety envelope."),
                MetricSpec("energy_per_improvement", "lower_is_better", False, "lower than fixed schedule at matched endpoint", "Energy cost of adaptation."),
            ],
            controls=_common_controls() + [
                ControlSpec("fixed_policy", "baseline", "Compare adaptive controller to non-adaptive schedule.", "Adaptive controller must beat fixed policy on registered endpoint."),
                ControlSpec("random_policy", "negative", "Verify reward does not improve under random action selection.", "Random policy must not match adaptive performance."),
            ],
            success_gates=[
                SuccessGate("gate_b4_preconditions", "B0-B3 pass on the same substrate class before closed-loop live work."),
                SuccessGate("gate_b4_safety", "All controller decisions pass adapter and SOP safety checks."),
            ],
            failure_modes=["unsafe feedback", "reward hacking", "culture drift", "nonstationary substrate"],
            gpu_comparison_note="Long-term BioGPU advantage candidate; requires strict live experimental governance.",
            implementation_files=["biogpu/feedback/controller.py"],
        ),
        BenchmarkTaskSpec(
            task_id="B5_energy_latency_comparison",
            title="Energy and latency comparison",
            purpose="Measure task-level energy, latency, and throughput for BioGPU runtime versus CPU/GPU/SNN baselines.",
            stage="power_pc",
            status="ready_for_dry_run",
            safety_class="dry_run_only",
            input_spec=InputSpec(
                format="BioGPUJob.energy_latency_suite",
                required_fields=["benchmark_task_id", "batch_size", "power_source", "measurement_window_s"],
                example_payload={
                    "benchmark_task_id": "B3_orientation_like_encoding",
                    "batch_size": 256,
                    "power_source": "host_power_meter_or_nvidia_smi_proxy",
                    "measurement_window_s": 60,
                },
                validation_notes=["Energy source must be declared.", "Accuracy threshold must be matched before energy claims."],
            ),
            encoder=EncoderSpec(
                name="benchmark_suite_runner",
                encoding_type="registered_task_batch",
                output_contract="batch of registered benchmark jobs with fixed seed manifest",
                hardware_boundary="Does not imply live stimulation; can run replay/simulation baselines first.",
                dry_run_checks=["baseline list present", "measurement window present", "accuracy-matching rule present"],
            ),
            substrate=SubstrateRequirement(
                substrate_class="software_replay_simulation_then_live_hardware",
                minimum_channels=0,
                minimum_repeats_per_class=0,
                timing_requirement="wall-clock and power telemetry aligned to task window",
                hardware_components=["host_pc", "storage", "runtime", "power_telemetry"],
                notes=["Energy claims are invalid unless matched against the same task and accuracy target."],
            ),
            readout=ReadoutSpec(
                name="energy_latency_reporter",
                feature_contract="per-run metrics table with accuracy, latency, energy, hardware metadata",
                model_family="reporting layer, not predictive model",
                training_split="not applicable; consumes already registered benchmark outputs",
                output_contract="task-level energy/latency comparison table",
            ),
            metrics=[
                MetricSpec("joules_per_task", "lower_is_better", True, "reported only at matched accuracy gate", "Primary energy comparison metric."),
                MetricSpec("end_to_end_latency_ms", "lower_is_better", False, "reported with batch size", "Wall-clock task latency."),
                MetricSpec("throughput_tasks_per_s", "higher_is_better", False, "reported with batch size", "Task throughput."),
            ],
            controls=[
                ControlSpec("matched_accuracy_gate", "fairness", "Prevent energy comparison when models are not solving the same task.", "Energy metric is claimable only when accuracy is matched or explicitly stratified."),
                ControlSpec("idle_power_subtraction", "measurement", "Separate idle host/life-support power from active run power where possible.", "Report both gross and net energy."),
            ],
            success_gates=[
                SuccessGate("gate_b5_power_metadata", "Power source and measurement method are included in output."),
                SuccessGate("gate_b5_matched_accuracy", "Comparison only claims advantage after matched-accuracy rule passes."),
            ],
            failure_modes=["unmatched task accuracy", "missing idle power", "batch-size cherry-picking"],
            gpu_comparison_note="Main comparison wrapper; it does not prove BioGPU advantage unless underlying task and measurement gates pass.",
            implementation_files=["biogpu/diagnostics/regression.py", "outputs/experiments"],
        ),
        BenchmarkTaskSpec(
            task_id="B6_substrate_stability",
            title="Substrate stability and drift",
            purpose="Quantify whether the substrate remains stable enough for repeated computation across time.",
            stage="licensed_lab",
            status="requires_live_lab",
            safety_class="live_lab_only",
            input_spec=InputSpec(
                format="BioGPUJob.stability_probe",
                required_fields=["probe_id", "probe_pattern_id", "timepoint", "environment_snapshot"],
                example_payload={
                    "probe_id": "daily_probe_0001",
                    "probe_pattern_id": "low_intensity_reference_pattern",
                    "timepoint": "day_03_hour_12",
                    "environment_snapshot": {"temperature_ok": True, "co2_ok": True, "humidity_ok": True},
                },
                validation_notes=["Probe pattern must be pre-registered.", "Environment snapshot must be attached to each run."],
            ),
            encoder=EncoderSpec(
                name="reference_probe_encoder",
                encoding_type="fixed_reference_pattern",
                output_contract="logical reference pattern used for drift monitoring",
                hardware_boundary="Live pattern requires lab SOP and vendor adapter.",
                dry_run_checks=["probe id registered", "environment fields present", "probe version fixed"],
            ),
            substrate=SubstrateRequirement(
                substrate_class="live_mea_hd_mea",
                minimum_channels=64,
                minimum_repeats_per_class=20,
                timing_requirement="repeatable probe windows across hours/days",
                hardware_components=["wet_cartridge", "environment_control", "mea_chip", "headstage_stimulator", "storage"],
                notes=["Required before any long-running claim about biological acceleration."],
            ),
            readout=ReadoutSpec(
                name="drift_monitor_readout",
                feature_contract="reference response vector over time",
                model_family="stability statistics, control charts, drift detector",
                training_split="time-blocked; initial calibration vs later probe windows",
                output_contract="stability score, drift alert, environment correlation summary",
            ),
            metrics=[
                MetricSpec("response_stability_score", "higher_is_better", True, "within registered stability band", "Repeatability of reference response."),
                MetricSpec("drift_rate_per_hour", "lower_is_better", False, "below registered drift threshold", "Rate of substrate state change."),
                MetricSpec("environment_correlation", "within_range", False, "reported, not necessarily optimized", "Whether drift correlates with life-support telemetry."),
            ],
            controls=[
                ControlSpec("environment_snapshot_required", "measurement", "Link response drift to environmental telemetry.", "Every probe has environment metadata."),
                ControlSpec("blank_or_no_input_probe", "negative", "Track spontaneous baseline drift.", "Blank/no-input response is reported separately from reference probe response."),
            ],
            success_gates=[
                SuccessGate("gate_b6_environment", "Environment telemetry is captured with every run."),
                SuccessGate("gate_b6_drift_band", "Stability score remains inside pre-registered range for required duration."),
            ],
            failure_modes=["culture drift", "environment fluctuation", "electrode degradation", "media/handling effects"],
            gpu_comparison_note="Precondition for serious hardware benchmarking; not a GPU comparison by itself.",
            implementation_files=["biogpu/hardware/blueprint_v22.py"],
        ),
    ]

    return BenchmarkRegistry(
        version="v2.3",
        name="BioGPU-A1 Benchmark Registry",
        goal=(
            "Turn BioGPU from a hardware/software blueprint into a set of registered, "
            "auditable benchmark tasks with explicit inputs, encoders, substrates, readouts, "
            "metrics, controls and success gates."
        ),
        boundary_note=(
            "The registry is hardware-neutral and safety-neutral by default. It defines contracts "
            "and benchmark evidence gates. It does not provide live wet-lab stimulation parameters, "
            "biological protocols, pinouts or vendor-specific operating instructions."
        ),
        tasks=tasks,
        global_success_policy=[
            "No performance claim is valid without registered negative controls.",
            "No energy advantage claim is valid without matched task and matched accuracy gates.",
            "Offline replay success is evidence for the software pipeline only, not proof of a live BioGPU device.",
            "Live-lab tasks require vendor adapter, platform documentation, facility SOP, safety interlocks and trained personnel.",
            "Each report must include task id, registry version, encoder version, readout, split policy, seed manifest and output bundle hash.",
        ],
        required_artifacts=[
            "registry JSON",
            "registry CSV",
            "benchmark report Markdown",
            "task input manifest",
            "readout metrics table",
            "negative-control metrics table",
            "hardware/readiness mapping",
            "run metadata and output bundle hash",
        ],
    )


def validate_registry(registry: BenchmarkRegistry) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    for task in registry.tasks:
        if task.task_id in seen:
            errors.append(f"duplicate task id: {task.task_id}")
        seen.add(task.task_id)

        if not task.input_spec.required_fields:
            errors.append(f"{task.task_id}: missing required input fields")
        if not task.encoder.dry_run_checks:
            errors.append(f"{task.task_id}: missing dry-run checks")
        if not task.substrate.hardware_components:
            errors.append(f"{task.task_id}: missing hardware component mapping")
        if not task.metrics or not any(m.primary for m in task.metrics):
            errors.append(f"{task.task_id}: missing primary metric")
        if not task.controls:
            errors.append(f"{task.task_id}: missing controls")
        if not task.success_gates:
            errors.append(f"{task.task_id}: missing success gates")
        if task.stage in {"licensed_lab", "future"} and task.safety_class != "live_lab_only":
            errors.append(f"{task.task_id}: live/future tasks must be live_lab_only")
        if task.stage in {"offline_replay", "dry_run", "power_pc"} and task.safety_class == "live_lab_only":
            errors.append(f"{task.task_id}: non-live stage should not be live_lab_only")
    return errors


def registry_to_markdown(registry: BenchmarkRegistry) -> str:
    lines: list[str] = []
    lines.append(f"# {registry.name}")
    lines.append("")
    lines.append(f"Version: `{registry.version}`")
    lines.append("")
    lines.append("## Goal")
    lines.append("")
    lines.append(registry.goal)
    lines.append("")
    lines.append("## Boundary")
    lines.append("")
    lines.append(registry.boundary_note)
    lines.append("")
    lines.append("## Global success policy")
    lines.append("")
    for item in registry.global_success_policy:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Registry table")
    lines.append("")
    lines.append("| Task | Stage | Status | Safety | Primary metric | Core controls |")
    lines.append("|---|---:|---:|---:|---|---|")
    for task in registry.tasks:
        primary = ", ".join(m.name for m in task.metrics if m.primary)
        controls = ", ".join(c.name for c in task.controls[:4])
        lines.append(f"| `{task.task_id}` {task.title} | `{task.stage}` | `{task.status}` | `{task.safety_class}` | {primary} | {controls} |")
    lines.append("")
    lines.append("## Tasks")
    lines.append("")
    for task in registry.tasks:
        lines.append(f"### {task.task_id} — {task.title}")
        lines.append("")
        lines.append(f"**Purpose:** {task.purpose}")
        lines.append("")
        lines.append(f"- Stage: `{task.stage}`")
        lines.append(f"- Status: `{task.status}`")
        lines.append(f"- Safety class: `{task.safety_class}`")
        lines.append(f"- GPU comparison note: {task.gpu_comparison_note}")
        lines.append("")
        lines.append("**Input contract**")
        lines.append("")
        lines.append(f"- Format: `{task.input_spec.format}`")
        lines.append(f"- Required fields: {', '.join(f'`{x}`' for x in task.input_spec.required_fields)}")
        lines.append(f"- Example payload: `{json.dumps(task.input_spec.example_payload, ensure_ascii=False)}`")
        if task.input_spec.validation_notes:
            lines.append("- Validation notes:")
            for note in task.input_spec.validation_notes:
                lines.append(f"  - {note}")
        lines.append("")
        lines.append("**Encoder**")
        lines.append("")
        lines.append(f"- Name: `{task.encoder.name}`")
        lines.append(f"- Type: `{task.encoder.encoding_type}`")
        lines.append(f"- Output contract: {task.encoder.output_contract}")
        lines.append(f"- Hardware boundary: {task.encoder.hardware_boundary}")
        lines.append("- Dry-run checks:")
        for check in task.encoder.dry_run_checks:
            lines.append(f"  - {check}")
        lines.append("")
        lines.append("**Substrate requirement**")
        lines.append("")
        lines.append(f"- Class: `{task.substrate.substrate_class}`")
        lines.append(f"- Minimum channels: `{task.substrate.minimum_channels}`")
        lines.append(f"- Minimum repeats/class: `{task.substrate.minimum_repeats_per_class}`")
        lines.append(f"- Timing: {task.substrate.timing_requirement}")
        lines.append(f"- Hardware components: {', '.join(f'`{x}`' for x in task.substrate.hardware_components)}")
        if task.substrate.notes:
            lines.append("- Notes:")
            for note in task.substrate.notes:
                lines.append(f"  - {note}")
        lines.append("")
        lines.append("**Readout**")
        lines.append("")
        lines.append(f"- Name: `{task.readout.name}`")
        lines.append(f"- Feature contract: {task.readout.feature_contract}")
        lines.append(f"- Model family: {task.readout.model_family}")
        lines.append(f"- Training split: {task.readout.training_split}")
        lines.append(f"- Output contract: {task.readout.output_contract}")
        lines.append("")
        lines.append("**Metrics**")
        lines.append("")
        lines.append("| Metric | Primary | Direction | Threshold | Interpretation |")
        lines.append("|---|---:|---:|---|---|")
        for metric in task.metrics:
            lines.append(f"| `{metric.name}` | `{metric.primary}` | `{metric.direction}` | {metric.threshold} | {metric.interpretation} |")
        lines.append("")
        lines.append("**Controls**")
        lines.append("")
        lines.append("| Control | Type | Purpose | Pass condition |")
        lines.append("|---|---:|---|---|")
        for control in task.controls:
            lines.append(f"| `{control.name}` | `{control.control_type}` | {control.purpose} | {control.pass_condition} |")
        lines.append("")
        lines.append("**Success gates**")
        lines.append("")
        for gate in task.success_gates:
            req = "required" if gate.required else "optional"
            lines.append(f"- `{gate.gate_id}` ({req}): {gate.description}")
        if task.failure_modes:
            lines.append("")
            lines.append("**Known failure modes**")
            lines.append("")
            for fm in task.failure_modes:
                lines.append(f"- {fm}")
        if task.implementation_files:
            lines.append("")
            lines.append("**Implementation references inside project**")
            lines.append("")
            for path in task.implementation_files:
                lines.append(f"- `{path}`")
        lines.append("")
    lines.append("## Required artifacts")
    lines.append("")
    for item in registry.required_artifacts:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def write_v23_outputs(out_dir: str | Path) -> dict:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    registry = build_biogpu_v23_benchmark_registry()
    errors = validate_registry(registry)

    registry_json = out / "biogpu_v23_benchmark_registry.json"
    registry_json.write_text(json.dumps(registry.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")

    registry_md = out / "BIOGPU_V23_BENCHMARK_REGISTRY.md"
    registry_md.write_text(registry_to_markdown(registry), encoding="utf-8")

    registry_csv = out / "biogpu_v23_benchmark_registry.csv"
    with registry_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "task_id",
                "title",
                "stage",
                "status",
                "safety_class",
                "input_format",
                "encoder",
                "substrate_class",
                "minimum_channels",
                "minimum_repeats_per_class",
                "readout",
                "primary_metrics",
                "controls",
                "hardware_components",
                "success_gates",
            ],
        )
        writer.writeheader()
        for task in registry.tasks:
            writer.writerow(
                {
                    "task_id": task.task_id,
                    "title": task.title,
                    "stage": task.stage,
                    "status": task.status,
                    "safety_class": task.safety_class,
                    "input_format": task.input_spec.format,
                    "encoder": task.encoder.name,
                    "substrate_class": task.substrate.substrate_class,
                    "minimum_channels": task.substrate.minimum_channels,
                    "minimum_repeats_per_class": task.substrate.minimum_repeats_per_class,
                    "readout": task.readout.name,
                    "primary_metrics": ";".join(m.name for m in task.metrics if m.primary),
                    "controls": ";".join(c.name for c in task.controls),
                    "hardware_components": ";".join(task.substrate.hardware_components),
                    "success_gates": ";".join(g.gate_id for g in task.success_gates),
                }
            )

    readiness_csv = out / "biogpu_v23_hardware_readiness_matrix.csv"
    component_rows: list[dict] = []
    for task in registry.tasks:
        for component in task.substrate.hardware_components:
            component_rows.append(
                {
                    "task_id": task.task_id,
                    "task_title": task.title,
                    "stage": task.stage,
                    "status": task.status,
                    "hardware_component": component,
                    "safety_class": task.safety_class,
                }
            )
    with readiness_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["task_id", "task_title", "stage", "status", "hardware_component", "safety_class"],
        )
        writer.writeheader()
        writer.writerows(component_rows)

    summary = {
        "version": registry.version,
        "tasks": len(registry.tasks),
        "stages": sorted({t.stage for t in registry.tasks}),
        "implemented_tasks": [t.task_id for t in registry.tasks if t.status == "implemented"],
        "dry_run_ready_tasks": [t.task_id for t in registry.tasks if t.status == "ready_for_dry_run"],
        "live_lab_tasks": [t.task_id for t in registry.tasks if t.safety_class == "live_lab_only"],
        "validation_errors": errors,
        "outputs": {
            "json": str(registry_json),
            "markdown": str(registry_md),
            "csv": str(registry_csv),
            "readiness_csv": str(readiness_csv),
        },
    }
    (out / "v23_benchmark_registry_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return summary


if __name__ == "__main__":
    result = write_v23_outputs("outputs/realdata_zenodo_14363732_v23_benchmark_registry")
    print(json.dumps(result, indent=2, ensure_ascii=False))
