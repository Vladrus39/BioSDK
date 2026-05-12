from __future__ import annotations
from biogpu.schemas import EventStream, StimPattern

class StimulationPlanner:
    """Converts an EventStream into a hardware-independent StimPattern."""

    def __init__(self, substrate_id: str = "simulated_mea"):
        self.substrate_id = substrate_id

    def plan(self, event_stream: EventStream) -> StimPattern:
        return StimPattern(
            substrate_id=self.substrate_id,
            channels=[e.channel_id for e in event_stream.events],
            times=[e.time for e in event_stream.events],
            intensities=[e.intensity for e in event_stream.events],
            safety_class="simulation_only",
            metadata={"source": "StimulationPlanner", **event_stream.metadata},
        )
