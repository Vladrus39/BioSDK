from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List

from .base_v26 import AbstractBioPattern, BioGPUEncoder, EncoderInput, normalize_vector


@dataclass
class TemporalEncoderV26(BioGPUEncoder):
    """Map sequences to abstract time-bin events."""

    encoder_id: str = "temporal_v26"
    kind: str = "temporal"
    group_name: str = "temporal_channel"
    abstract_bin_s: float = 0.1
    max_steps: int = 64

    def encode(self, item: EncoderInput) -> AbstractBioPattern:
        item.validate()
        payload = item.payload.get("sequence", item.payload) if isinstance(item.payload, dict) else item.payload
        if not isinstance(payload, list):
            raise TypeError("TemporalEncoderV26 expects list or {'sequence': list}")
        values = normalize_vector([float(x) for x in payload[: self.max_steps]])
        time_bins = [round(i * self.abstract_bin_s, 6) for i in range(len(values))]
        pattern = AbstractBioPattern(
            pattern_id=f"{item.task_id}:{self.encoder_id}",
            kind="temporal",
            target_groups=[self.group_name for _ in values],
            time_bins=time_bins,
            weights=values,
            readout_hint="time_aligned_response_vector",
            safety_level="dry_run_safe",
            metadata={
                "encoder_id": self.encoder_id,
                "abstract_bin_s": self.abstract_bin_s,
                "note": "Time bins are software offsets, not vendor pulse timing instructions.",
            },
        )
        pattern.validate()
        return pattern
