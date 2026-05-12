"""BioGPU v2.7 readout contracts.

Readout converts BioGPUTrace/feature vectors into BioGPUResult-like predictions.
It is a software decoding layer only. It never emits live stimulation settings,
wiring instructions, wet-lab instructions, or vendor pinouts.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Iterable, List, Literal, Protocol
import json
import math

ReadoutKind = Literal["centroid", "logistic_l2", "linear_svm", "online_centroid"]

@dataclass(frozen=True)
class ReadoutFeatureBatch:
    feature_names: List[str]
    X: List[List[float]]
    y: List[Any] | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.X:
            raise ValueError("ReadoutFeatureBatch.X must not be empty")
        width = len(self.X[0])
        if width == 0:
            raise ValueError("feature vectors must not be empty")
        if self.feature_names and len(self.feature_names) != width:
            raise ValueError("feature_names length must match feature vector width")
        for row in self.X:
            if len(row) != width:
                raise ValueError("all feature rows must have the same width")
            if any(not math.isfinite(float(v)) for v in row):
                raise ValueError("features must be finite")
        if self.y is not None and len(self.y) != len(self.X):
            raise ValueError("labels length must match X length")

    def to_dict(self) -> Dict[str, Any]:
        self.validate()
        return asdict(self)

@dataclass(frozen=True)
class ReadoutPrediction:
    decoder_id: str
    prediction: Any
    confidence: float | None
    scores: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class BioGPUReadout(Protocol):
    decoder_id: str
    kind: ReadoutKind

    def fit(self, batch: ReadoutFeatureBatch) -> "BioGPUReadout":
        ...

    def predict_one(self, features: Iterable[float], feature_names: List[str] | None = None) -> ReadoutPrediction:
        ...


def l2_distance(a: Iterable[float], b: Iterable[float]) -> float:
    aa = [float(x) for x in a]
    bb = [float(x) for x in b]
    if len(aa) != len(bb):
        raise ValueError("vectors must have same length")
    return math.sqrt(sum((x-y)**2 for x, y in zip(aa, bb)))


def soft_confidence_from_distance(best: float, second: float | None) -> float:
    if second is None:
        return 1.0
    if second <= 0:
        return 1.0
    margin = max(0.0, float(second) - float(best))
    return max(0.0, min(1.0, margin / (abs(second) + 1e-12)))


def batch_to_json(batch: ReadoutFeatureBatch) -> str:
    return json.dumps(batch.to_dict(), indent=2, ensure_ascii=False)
