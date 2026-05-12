from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
from biogpu.schemas import StimPattern, SpikeTrain

class ComputeSubstrateAdapter(ABC):
    @abstractmethod
    def connect(self) -> None: ...

    @abstractmethod
    def configure(self, config: dict[str, Any]) -> None: ...

    @abstractmethod
    def send_stimulation(self, pattern: StimPattern) -> None: ...

    @abstractmethod
    def read_spikes(self, window_ms: float) -> SpikeTrain: ...

    def read_raw(self, window_ms: float):
        raise NotImplementedError("Raw reading is substrate-specific")

    @abstractmethod
    def health_check(self) -> dict[str, Any]: ...

    @abstractmethod
    def close(self) -> None: ...
