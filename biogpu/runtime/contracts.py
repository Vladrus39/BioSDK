from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal


@dataclass(frozen=True)
class BioGPUObjective:
    """The project-level objective.

    The wording is intentionally strict. BioGPU-Core must not drift into a plain
    MEA analysis toolkit: the analysis is evidence and software scaffolding for a
    future working biological computing accelerator.
    """

    name: str = "BioGPU"
    mission: str = (
        "Design and implement a real working biological computing accelerator: "
        "encoder -> living/neural substrate -> readout -> benchmark -> energy/task comparison."
    )
    current_stage: str = "software-core + public-real-data replay substrate"
    final_stage: str = "closed-loop MEA/HD-MEA wetware accelerator with validated task and energy benchmarks"
    non_claims: tuple[str, ...] = (
        "Current public-data results do not prove BioGPU is faster than silicon GPUs.",
        "Current public-data results do not replace a real live MEA/HD-MEA device.",
        "Current code does not emit physical stimulation parameters for lab use.",
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BioGPUClaimStage:
    """A claim ladder item: what is proven and what is still required."""

    stage: str
    claim: str
    evidence_now: list[str] = field(default_factory=list)
    required_next: list[str] = field(default_factory=list)
    status: Literal["done", "partial", "blocked", "future"] = "partial"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BioGPUJob:
    """Hardware-neutral execution request.

    A future real BioGPU device should accept a job like this, encode it into a
    safe stimulation plan, run it on a living substrate, and return a trace.
    In v1.8 the job can be replayed from public real MEA responses.
    """

    job_id: str
    task: str
    input_payload: dict[str, Any]
    encoding: str = "spatial_temporal_electrode_encoding"
    substrate: str = "public_data_replay"
    readout: str = "linear_readout"
    safety_class: str = "offline_replay_only"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BioGPUTrace:
    """Observed response trace from a substrate call."""

    job_id: str
    source: str
    culture: str | None
    recording: str | None
    target_electrode: int | None
    response_features: list[float]
    feature_names: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BioGPUResult:
    """Decoded result of a BioGPU job."""

    job_id: str
    prediction: Any
    confidence: float | None
    metrics: dict[str, Any] = field(default_factory=dict)
    trace: BioGPUTrace | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        row = asdict(self)
        if self.trace is not None:
            row["trace"] = self.trace.to_dict()
        return row


def build_biogpu_claim_ladder() -> list[BioGPUClaimStage]:
    """Return the project claim ladder from current evidence to final BioGPU."""

    return [
        BioGPUClaimStage(
            stage="L0_simulation_only",
            claim="Synthetic BioGPU-like pipeline can encode inputs, simulate responses, and decode outputs.",
            evidence_now=["SimulatedMEA and synthetic benchmark modules exist."],
            required_next=["Replace simulated-only evidence with public real-data evidence."],
            status="done",
        ),
        BioGPUClaimStage(
            stage="L1_real_spike_data",
            claim="Public MEA recordings contain usable neural spike responses.",
            evidence_now=["Zenodo preprocessed spike data parsed and profiled."],
            required_next=["Align responses to true stimulus/protocol timing."],
            status="done",
        ),
        BioGPUClaimStage(
            stage="L2_pulse_aligned_bioresponse",
            claim="Real pulse-level stimulation windows produce target-specific biological response signals.",
            evidence_now=[
                "11,547 real pulse windows extracted from stimulation_protocol CSV files.",
                "Target electrode response percentile is high against electrode population.",
                "Random-electrode and random-time controls support non-random alignment.",
            ],
            required_next=["Train readouts that generalize across cultures and compare with shuffled baselines."],
            status="done",
        ),
        BioGPUClaimStage(
            stage="L3_cross_culture_readout",
            claim="Spike-response features support cross-culture target-vs-non-target separability.",
            evidence_now=[
                "v1.5-v1.7 candidate readout: ROC AUC around 0.90 on culture-held-out folds in local runs.",
                "Raw-count-only features remain strong; pulse-context negative control stays at chance.",
            ],
            required_next=[
                "Run publication-grade 100-1000 label shuffles.",
                "Repeat across many negative-sampling seeds.",
                "Bootstrap confidence intervals across cultures.",
            ],
            status="partial",
        ),
        BioGPUClaimStage(
            stage="L4_realdata_replay_biogpu_core",
            claim="A software BioGPU runtime can execute jobs against real public biological response traces.",
            evidence_now=[
                "v1.8 defines BioGPUJob, BioGPUTrace, BioGPUResult contracts.",
                "v1.8 public-data replay substrate can return real recorded response vectors through the same interface future hardware will use.",
            ],
            required_next=[
                "Add more public datasets: DANDI/NWB, Allen, raw HDF5/TTL where available.",
                "Standardize input encoders and task labels beyond target-vs-random electrode separability.",
            ],
            status="partial",
        ),
        BioGPUClaimStage(
            stage="L5_closed_loop_lab_prototype",
            claim="A live MEA/HD-MEA BioGPU can accept encoded jobs, stimulate living tissue, read responses, and decode outputs.",
            evidence_now=[],
            required_next=[
                "Lab-approved MEA/HD-MEA hardware and vendor SDK.",
                "Ethics/safety/biological maintenance procedures.",
                "Closed-loop latency and repeatability validation.",
                "Do not derive stimulation safety parameters from this software repository alone.",
            ],
            status="future",
        ),
        BioGPUClaimStage(
            stage="L6_biogpu_advantage",
            claim="BioGPU has a measurable advantage on selected tasks versus conventional baselines.",
            evidence_now=[],
            required_next=[
                "Define fair task benchmark: accuracy, latency, energy, sample efficiency, adaptation, noise robustness.",
                "Compare against CPU/GPU/neuromorphic/synthetic reservoir baselines.",
                "Use measured device energy, not assumed biological energy.",
            ],
            status="future",
        ),
    ]
