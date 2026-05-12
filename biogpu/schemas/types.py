from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import numpy as np

@dataclass
class InputPattern:
    id: str
    data: np.ndarray
    label: int | str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class Event:
    time: float
    channel_id: int
    intensity: float
    polarity: int | None = None
    tag: str | None = None

@dataclass
class EventStream:
    events: list[Event]
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class StimPattern:
    substrate_id: str
    channels: list[int]
    times: list[float]
    intensities: list[float]
    safety_class: str = "simulation_only"
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class SpikeTrain:
    unit_ids: list[int]
    spike_times: list[float]
    amplitudes: list[float] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class FeatureVector:
    values: np.ndarray
    names: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class ExperimentRecord:
    experiment_id: str
    config_hash: str
    input_id: str
    prediction: int | str | float | None
    target: int | str | float | None
    metrics: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)
