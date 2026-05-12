from __future__ import annotations
from biogpu.schemas import StimPattern

class SimulationSafetyLayer:
    """Safety abstraction. v0.1 validates only simulation patterns.

    Real biological stimulation parameters must be defined by qualified labs and
    equipment-specific safety procedures. This project does not provide wetlab protocols.
    """

    def validate(self, pattern: StimPattern) -> None:
        if pattern.safety_class != "simulation_only":
            raise ValueError("v0.1 accepts only simulation-only stimulation patterns")
        if not (len(pattern.channels) == len(pattern.times) == len(pattern.intensities)):
            raise ValueError("StimPattern fields have inconsistent lengths")
        if any(i < 0 for i in pattern.intensities):
            raise ValueError("Stim intensities must be non-negative")
