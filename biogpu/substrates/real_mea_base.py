from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from biogpu.schemas import StimPattern, SpikeTrain
from biogpu.substrates.base import ComputeSubstrateAdapter


@dataclass
class RealMEACapabilities:
    """Vendor-neutral capability description for future MEA/HD-MEA backends.

    This class intentionally contains no wet-lab parameters. It only describes the
    software contract that a lab-approved driver must satisfy before it can be
    used by BioGPU.
    """

    vendor: str = "vendor-neutral"
    model: str = "unknown"
    electrode_count: int = 0
    supports_stimulation: bool = False
    supports_recording: bool = True
    supports_raw_stream: bool = False
    supports_closed_loop: bool = False
    max_sample_rate_hz: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RealMEAConfig:
    """Configuration for a real MEA adapter.

    `dry_run=True` is the only active mode in this repository. A real vendor
    implementation must be supplied by a qualified laboratory or equipment SDK.
    """

    substrate_id: str = "real_mea_dry_run"
    dry_run: bool = True
    require_lab_approval: bool = True
    vendor: str = "vendor-neutral"
    model: str = "unknown"
    electrode_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


class RealMEAVendorNeutralAdapter(ComputeSubstrateAdapter):
    """Skeleton for future real MEA/HD-MEA integration.

    The adapter is deliberately safe: it does not talk to hardware and does not
    define stimulation parameters. Its purpose is to freeze the software
    contract so the rest of BioGPU can be developed before lab access exists.
    """

    def __init__(self, config: RealMEAConfig | None = None):
        self.config = config or RealMEAConfig()
        self.connected = False
        self.last_pattern: StimPattern | None = None
        self._capabilities = RealMEACapabilities(
            vendor=self.config.vendor,
            model=self.config.model,
            electrode_count=self.config.electrode_count,
            supports_stimulation=False,
            supports_recording=True,
            supports_raw_stream=False,
            supports_closed_loop=False,
            metadata={"mode": "dry_run", **self.config.metadata},
        )

    @property
    def capabilities(self) -> RealMEACapabilities:
        return self._capabilities

    def connect(self) -> None:
        if not self.config.dry_run:
            raise RuntimeError(
                "Real MEA hardware connection is not implemented in biogpu-core. "
                "Use a lab-approved vendor driver that implements this contract."
            )
        self.connected = True

    def configure(self, config: dict[str, Any]) -> None:
        # Dry-run configuration only. Unknown fields are kept as metadata so the
        # experiment log can preserve intent without touching hardware.
        self.config.metadata.update(config or {})
        if "electrode_count" in config:
            self.config.electrode_count = int(config["electrode_count"])
            self._capabilities.electrode_count = self.config.electrode_count

    def send_stimulation(self, pattern: StimPattern) -> None:
        if not self.connected:
            self.connect()
        if not self.config.dry_run:
            raise RuntimeError("Real stimulation requires a vendor/lab implementation.")
        # Only record the pattern for contract tests. Do not transform it into any
        # physical parameters here.
        self.last_pattern = pattern

    def read_spikes(self, window_ms: float) -> SpikeTrain:
        if not self.connected:
            self.connect()
        return SpikeTrain(
            unit_ids=[],
            spike_times=[],
            amplitudes=[],
            metadata={
                "substrate": "RealMEAVendorNeutralAdapter",
                "mode": "dry_run",
                "window_ms": float(window_ms),
                "note": "No hardware attached; empty spike train by design.",
            },
        )

    def read_raw(self, window_ms: float):
        return {
            "mode": "dry_run",
            "window_ms": float(window_ms),
            "raw": [],
            "note": "Raw MEA stream must be implemented by a vendor/lab adapter.",
        }

    def health_check(self) -> dict[str, Any]:
        return {
            "connected": self.connected,
            "type": "RealMEAVendorNeutralAdapter",
            "dry_run": self.config.dry_run,
            "requires_lab_approval": self.config.require_lab_approval,
            "capabilities": self.capabilities.__dict__,
        }

    def close(self) -> None:
        self.connected = False
