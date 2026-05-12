from __future__ import annotations
from dataclasses import asdict, dataclass
from typing import Dict, Any

@dataclass(frozen=True)
class LatencyComponentsV29:
    encode_ms: float
    substrate_io_ms: float
    biological_response_ms: float
    acquisition_ms: float
    feature_extraction_ms: float
    readout_ms: float
    controller_update_ms: float = 0.0
    notes: str = ""

    def validate(self) -> None:
        for k, v in asdict(self).items():
            if k != "notes" and float(v) < 0:
                raise ValueError(f"latency component {k} must be non-negative")

    def total_ms(self) -> float:
        self.validate()
        return (
            self.encode_ms + self.substrate_io_ms + self.biological_response_ms +
            self.acquisition_ms + self.feature_extraction_ms + self.readout_ms + self.controller_update_ms
        )

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["total_ms"] = self.total_ms()
        d["throughput_tasks_per_s_if_serial"] = 1000.0 / self.total_ms() if self.total_ms() > 0 else 0.0
        return d

@dataclass(frozen=True)
class LatencyEstimateV29:
    total_ms: float
    throughput_tasks_per_s_if_serial: float
    components: Dict[str, Any]
    notes: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def estimate_latency_v29(components: LatencyComponentsV29) -> LatencyEstimateV29:
    components.validate()
    total = components.total_ms()
    return LatencyEstimateV29(
        total_ms=total,
        throughput_tasks_per_s_if_serial=1000.0 / total if total > 0 else 0.0,
        components=components.to_dict(),
        notes=components.notes,
    )


def default_biogpu_a1_latency_v29() -> LatencyComponentsV29:
    return LatencyComponentsV29(
        encode_ms=1.0,
        substrate_io_ms=2.0,
        biological_response_ms=50.0,
        acquisition_ms=5.0,
        feature_extraction_ms=2.0,
        readout_ms=0.5,
        controller_update_ms=0.5,
        notes="Placeholder closed-loop latency budget; biological_response_ms must be measured on real substrate.",
    )
