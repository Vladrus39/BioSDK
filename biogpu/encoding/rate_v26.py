from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .base_v26 import AbstractBioPattern, BioGPUEncoder, EncoderInput, clamp01


@dataclass
class RateEncoderV26(BioGPUEncoder):
    """Map class scores/probabilities to abstract normalized group intensity."""

    encoder_id: str = "rate_v26"
    kind: str = "rate"
    group_prefix: str = "rate_class"
    max_classes: int = 16

    def encode(self, item: EncoderInput) -> AbstractBioPattern:
        item.validate()
        payload = item.payload
        if isinstance(payload, dict) and "scores" in payload:
            scores = payload["scores"]
        elif isinstance(payload, dict):
            scores = payload
        else:
            raise TypeError("RateEncoderV26 expects dict or {'scores': dict}")
        ordered = list(scores.items())[: self.max_classes]
        labels = [str(k) for k, _ in ordered]
        values = [clamp01(float(v)) * 2.0 - 1.0 for _, v in ordered]
        groups = [f"{self.group_prefix}_{label}" for label in labels]
        pattern = AbstractBioPattern(
            pattern_id=f"{item.task_id}:{self.encoder_id}",
            kind="rate",
            target_groups=groups,
            time_bins=[0.0],
            weights=values,
            readout_hint="aggregate_rate_response",
            safety_level="replay_safe",
            metadata={
                "encoder_id": self.encoder_id,
                "labels": labels,
                "note": "Normalized class weights only; no stimulation frequency is encoded.",
            },
        )
        pattern.validate()
        return pattern
