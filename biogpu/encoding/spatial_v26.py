from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, List

from .base_v26 import AbstractBioPattern, BioGPUEncoder, EncoderInput, normalize_vector


@dataclass
class SpatialEncoderV26(BioGPUEncoder):
    """Map vector/grid payloads to abstract electrode-group weights."""

    encoder_id: str = "spatial_v26"
    kind: str = "spatial"
    group_prefix: str = "region"
    max_groups: int = 32

    def _flatten(self, payload: Any) -> List[float]:
        if isinstance(payload, dict) and "values" in payload:
            payload = payload["values"]
        if isinstance(payload, (int, float)):
            return [float(payload)]
        if isinstance(payload, list):
            out: List[float] = []
            for item in payload:
                if isinstance(item, list):
                    out.extend(float(x) for x in item)
                else:
                    out.append(float(item))
            return out
        raise TypeError("SpatialEncoderV26 expects numeric scalar/list/grid or {'values': ...}")

    def encode(self, item: EncoderInput) -> AbstractBioPattern:
        item.validate()
        values = self._flatten(item.payload)[: self.max_groups]
        weights = normalize_vector(values, center=True)
        groups = [f"{self.group_prefix}_{i:02d}" for i in range(len(weights))]
        pattern = AbstractBioPattern(
            pattern_id=f"{item.task_id}:{self.encoder_id}",
            kind="spatial",
            target_groups=groups,
            time_bins=[0.0],
            weights=weights,
            readout_hint="spatial_response_vector",
            safety_level="replay_safe",
            metadata={
                "encoder_id": self.encoder_id,
                "payload_size": len(weights),
                "note": "Abstract spatial weights only; no live stimulation amplitude is encoded.",
            },
        )
        pattern.validate()
        return pattern
