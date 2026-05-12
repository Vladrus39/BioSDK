from __future__ import annotations
from biogpu.encoding.spatial_encoder import SpatialRateEncoder
from biogpu.reservoir.v1_core import V1Core
from biogpu.schemas import Event, EventStream, InputPattern
import numpy as np

class V1LikeEncoder(SpatialRateEncoder):
    """V1-inspired event encoder.

    v0.2 adds orientation filter maps on top of the v0.1 spatial-rate idea.
    Each orientation map is projected into a separate channel bank. This keeps
    the encoder hardware-independent: later the channel banks can be mapped to
    MEA electrodes, neuromorphic cores, or memristor rows.
    """
    def __init__(self, max_events_per_pixel: int = 3, threshold: float = 0.05, use_orientation_banks: bool = True):
        super().__init__(max_events_per_pixel=max_events_per_pixel, threshold=threshold)
        self.use_orientation_banks = bool(use_orientation_banks)
        self.v1 = V1Core()

    def encode(self, pattern: InputPattern) -> EventStream:
        if not self.use_orientation_banks:
            return super().encode(pattern)
        data = np.asarray(pattern.data, dtype=np.float32)
        maps = self.v1.transform_maps(data)
        events: list[Event] = []
        bank_size = data.size
        for bank_idx, ori in enumerate(self.v1.ORIENTATIONS):
            flat = maps[ori].reshape(-1)
            offset = bank_idx * bank_size
            max_val = float(flat.max()) if flat.size else 0.0
            norm = flat / max(max_val, 1e-6)
            for i, value in enumerate(norm):
                if value <= self.threshold:
                    continue
                n_events = max(1, int(round(float(value) * self.max_events_per_pixel)))
                for k in range(n_events):
                    events.append(Event(time=float(k + bank_idx * 0.1), channel_id=offset + i, intensity=float(value), polarity=1, tag=f"v1_ori_{ori}"))
        return EventStream(events=events, metadata={"input_id": pattern.id, "encoder": "V1LikeEncoder", "orientation_banks": True})
