from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List

from .base_v26 import AbstractBioPattern, BioGPUEncoder, EncoderInput
from .spatial_v26 import SpatialEncoderV26
from .temporal_v26 import TemporalEncoderV26


@dataclass
class HybridEncoderV26(BioGPUEncoder):
    """Combine spatial and temporal intent into one abstract pattern."""

    encoder_id: str = "hybrid_v26"
    kind: str = "hybrid"
    spatial_encoder: SpatialEncoderV26 = field(default_factory=lambda: SpatialEncoderV26(group_prefix="hybrid_region"))
    temporal_encoder: TemporalEncoderV26 = field(default_factory=lambda: TemporalEncoderV26(group_name="hybrid_temporal_channel"))

    def encode(self, item: EncoderInput) -> AbstractBioPattern:
        item.validate()
        if not isinstance(item.payload, dict) or "spatial" not in item.payload or "temporal" not in item.payload:
            raise TypeError("HybridEncoderV26 expects {'spatial': ..., 'temporal': ...}")
        sp = self.spatial_encoder.encode(EncoderInput(task_id=item.task_id, payload=item.payload["spatial"], metadata=item.metadata))
        tp = self.temporal_encoder.encode(EncoderInput(task_id=item.task_id, payload=item.payload["temporal"], metadata=item.metadata))
        groups = sp.target_groups + tp.target_groups
        weights = sp.weights + tp.weights
        # Keep spatial at t=0 and temporal offsets after it.
        time_bins = [0.0 for _ in sp.target_groups] + tp.time_bins
        pattern = AbstractBioPattern(
            pattern_id=f"{item.task_id}:{self.encoder_id}",
            kind="hybrid",
            target_groups=groups,
            time_bins=time_bins,
            weights=weights,
            readout_hint="spatiotemporal_response_vector",
            safety_level="dry_run_safe",
            metadata={
                "encoder_id": self.encoder_id,
                "spatial_groups": len(sp.target_groups),
                "temporal_steps": len(tp.time_bins),
                "note": "Hybrid abstract pattern only; vendor backend must apply approved SOP before live use.",
            },
        )
        pattern.validate()
        return pattern
