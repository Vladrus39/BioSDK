"""BioGPU v2.6 encoder contracts.

This module converts digital task payloads into *abstract* biological pattern
intents. It intentionally does not expose live stimulation amplitudes,
pulse widths, frequencies, pinouts, or vendor-specific hardware commands.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, Iterable, List, Literal, Optional, Protocol
import json
import math

from biogpu.safety.boundary_v35 import FORBIDDEN_LIVE_FIELDS_V35, assert_no_forbidden_keys_v35

PatternKind = Literal["spatial", "temporal", "rate", "hybrid", "identity"]
SafetyLevel = Literal["replay_safe", "dry_run_safe", "live_requires_vendor_sop"]

FORBIDDEN_LIVE_FIELDS = set(FORBIDDEN_LIVE_FIELDS_V35)



@dataclass(frozen=True)
class EncoderInput:
    """Input payload for an encoder.

    payload can be a vector, token, sequence, small grid, or benchmark-specific
    object. metadata stores benchmark/task context but must not contain unsafe
    live parameters.
    """

    task_id: str
    payload: Any
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        assert_no_forbidden_keys_v35(self.metadata.keys(), context="EncoderInput.metadata")


@dataclass(frozen=True)
class AbstractBioPattern:
    """Abstract pattern intent produced by an encoder.

    This is not a hardware command. Vendor adapters must validate this pattern
    and translate it using approved SOP/vendor configuration later.
    """

    pattern_id: str
    kind: PatternKind
    target_groups: List[str]
    time_bins: List[float]
    weights: List[float]
    readout_hint: str
    safety_level: SafetyLevel = "replay_safe"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.pattern_id:
            raise ValueError("pattern_id is required")
        if not self.target_groups:
            raise ValueError("target_groups must not be empty")
        if not self.time_bins:
            raise ValueError("time_bins must not be empty")
        if len(self.weights) != len(self.target_groups):
            raise ValueError("weights length must match target_groups length")
        if any(not math.isfinite(x) for x in self.time_bins):
            raise ValueError("time_bins must be finite")
        if any(not math.isfinite(x) for x in self.weights):
            raise ValueError("weights must be finite")
        if any(x < 0 for x in self.time_bins):
            raise ValueError("time_bins must be non-negative abstract offsets")
        if any(abs(x) > 1.0 for x in self.weights):
            raise ValueError("weights are normalized abstract values and must be within [-1, 1]")
        assert_no_forbidden_keys_v35(self.metadata.keys(), context="AbstractBioPattern.metadata")

    def to_dict(self) -> Dict[str, Any]:
        self.validate()
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)


class BioGPUEncoder(Protocol):
    encoder_id: str
    kind: PatternKind

    def encode(self, item: EncoderInput) -> AbstractBioPattern:
        ...


def normalize_vector(values: Iterable[float], *, center: bool = False) -> List[float]:
    vals = [float(v) for v in values]
    if not vals:
        raise ValueError("cannot normalize empty vector")
    if center:
        mean = sum(vals) / len(vals)
        vals = [v - mean for v in vals]
    max_abs = max(abs(v) for v in vals) or 1.0
    return [max(-1.0, min(1.0, v / max_abs)) for v in vals]


def clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))
