"""BioGPU v2.8 closed-loop contracts.

Closed loop means: encode task -> run substrate/replay -> decode response ->
score reward/error -> decide next abstract action.

This layer is deliberately hardware-neutral and safe: it does not contain live
stimulation amplitudes, pulse widths, voltages, pinouts, wiring instructions,
cell-culture recipes, or vendor SOP replacement material.
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Literal
import json, math

from biogpu.safety.boundary_v35 import FORBIDDEN_LIVE_FIELDS_V35, assert_no_forbidden_keys_v35

LoopMode = Literal["replay", "dry_run", "power_pc", "live_lab_requires_vendor_sop"]
LoopStatus = Literal["initialized", "running", "completed", "stopped", "failed"]

FORBIDDEN_CLOSED_LOOP_FIELDS = set(FORBIDDEN_LIVE_FIELDS_V35)


@dataclass(frozen=True)
class ClosedLoopConfigV28:
    loop_id: str
    benchmark_id: str
    encoder_id: str = "hybrid_v26"
    readout_id: str = "online_centroid_v27"
    mode: LoopMode = "dry_run"
    max_steps: int = 8
    target_confidence: float = 0.75
    exploration_floor: float = 0.10
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.loop_id:
            raise ValueError("loop_id is required")
        if self.max_steps <= 0:
            raise ValueError("max_steps must be positive")
        if not (0.0 <= float(self.target_confidence) <= 1.0):
            raise ValueError("target_confidence must be within [0,1]")
        assert_no_forbidden_keys_v35(self.metadata.keys(), context="ClosedLoopConfigV28.metadata")

    def to_dict(self) -> Dict[str, Any]:
        self.validate(); return asdict(self)

@dataclass(frozen=True)
class ClosedLoopObservationV28:
    step_index: int
    pattern_id: str
    features: List[float]
    feature_names: List[str]
    prediction: Any
    confidence: float | None
    expected: Any | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if self.step_index < 0:
            raise ValueError("step_index must be non-negative")
        if not self.features:
            raise ValueError("features must not be empty")
        if any(not math.isfinite(float(v)) for v in self.features):
            raise ValueError("features must be finite")
        if self.confidence is not None and not (0.0 <= float(self.confidence) <= 1.0):
            raise ValueError("confidence must be within [0,1]")

    def to_dict(self) -> Dict[str, Any]:
        self.validate(); return asdict(self)

@dataclass(frozen=True)
class RewardSignalV28:
    reward: float
    error: float
    success: bool
    reason: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if not math.isfinite(float(self.reward)) or not math.isfinite(float(self.error)):
            raise ValueError("reward and error must be finite")

    def to_dict(self) -> Dict[str, Any]:
        self.validate(); return asdict(self)

@dataclass(frozen=True)
class ClosedLoopDecisionV28:
    action: Literal["continue", "increase_exploration", "hold_pattern", "stop_success", "stop_max_steps"]
    next_payload: Dict[str, Any]
    policy_state: Dict[str, Any] = field(default_factory=dict)
    reason: str = ""

    def validate(self) -> None:
        assert_no_forbidden_keys_v35(self.next_payload.keys(), context="ClosedLoopDecisionV28.next_payload")

    def to_dict(self) -> Dict[str, Any]:
        self.validate(); return asdict(self)

@dataclass(frozen=True)
class ClosedLoopStepRecordV28:
    step_index: int
    encoder_id: str
    readout_id: str
    pattern: Dict[str, Any]
    observation: ClosedLoopObservationV28
    reward: RewardSignalV28
    decision: ClosedLoopDecisionV28

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_index": self.step_index,
            "encoder_id": self.encoder_id,
            "readout_id": self.readout_id,
            "pattern": self.pattern,
            "observation": self.observation.to_dict(),
            "reward": self.reward.to_dict(),
            "decision": self.decision.to_dict(),
        }

@dataclass(frozen=True)
class ClosedLoopRunSummaryV28:
    config: ClosedLoopConfigV28
    status: LoopStatus
    steps: List[ClosedLoopStepRecordV28]
    final_reward: float
    final_success: bool
    live_output_performed: bool = False
    safety_boundary: str = "abstract closed-loop control only; no live stimulation settings"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "config": self.config.to_dict(),
            "status": self.status,
            "steps": [s.to_dict() for s in self.steps],
            "final_reward": self.final_reward,
            "final_success": self.final_success,
            "live_output_performed": self.live_output_performed,
            "safety_boundary": self.safety_boundary,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)
