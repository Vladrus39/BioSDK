from __future__ import annotations

from dataclasses import asdict
from typing import Dict

from .base_v26 import BioGPUEncoder, EncoderInput, AbstractBioPattern
from .spatial_v26 import SpatialEncoderV26
from .temporal_v26 import TemporalEncoderV26
from .rate_v26 import RateEncoderV26
from .hybrid_v26 import HybridEncoderV26


def build_encoder_registry_v26() -> Dict[str, BioGPUEncoder]:
    encoders = [SpatialEncoderV26(), TemporalEncoderV26(), RateEncoderV26(), HybridEncoderV26()]
    return {e.encoder_id: e for e in encoders}


def encode_with_registry_v26(encoder_id: str, item: EncoderInput) -> AbstractBioPattern:
    reg = build_encoder_registry_v26()
    if encoder_id not in reg:
        raise KeyError(f"Unknown encoder_id: {encoder_id}")
    return reg[encoder_id].encode(item)


def registry_summary_v26() -> list[dict]:
    out = []
    for encoder_id, enc in build_encoder_registry_v26().items():
        out.append({"encoder_id": encoder_id, "kind": getattr(enc, "kind", "unknown"), "class": enc.__class__.__name__})
    return out
