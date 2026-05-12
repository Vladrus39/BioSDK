from __future__ import annotations
import numpy as np
from biogpu.schemas import Event, EventStream, InputPattern

class SpatialRateEncoder:
    """Maps input pixels/features to electrode channels using spatial + rate coding."""

    def __init__(self, max_events_per_pixel: int = 3, threshold: float = 0.05):
        self.max_events_per_pixel = int(max_events_per_pixel)
        self.threshold = float(threshold)

    def encode(self, pattern: InputPattern) -> EventStream:
        data = np.asarray(pattern.data, dtype=np.float32)
        flat = data.reshape(-1)
        events: list[Event] = []
        for channel_id, value in enumerate(flat):
            if value <= self.threshold:
                continue
            n_events = max(1, int(round(value * self.max_events_per_pixel)))
            for k in range(n_events):
                events.append(Event(
                    time=float(k),
                    channel_id=int(channel_id),
                    intensity=float(value),
                    polarity=1,
                    tag="spatial_rate",
                ))
        return EventStream(events=events, metadata={"input_id": pattern.id, "encoder": "SpatialRateEncoder"})
