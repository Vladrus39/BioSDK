"""BioGPU v3.7 External API / BioSDK integration base layer.

This layer is intentionally metadata/read-only/mock-only. It standardizes how a
future external wetware platform can expose data to BioGPU-Core without granting
live stimulation, physical wiring, or wet-lab operational control.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from enum import Enum
from typing import Any, Iterable
from datetime import datetime, timezone
import math

from biogpu.safety.boundary_v35 import assert_no_forbidden_payload_v35


class APIAccessModeV37(str, Enum):
    METADATA_ONLY = "metadata_only"
    READ_ONLY = "read_only"
    REPLAY_IMPORT = "replay_import"
    LIVE_SHADOW = "live_shadow"


class APIPlatformV37(str, Enum):
    FINALSPARK = "finalspark_remote_wetware"
    THREEBRAIN = "threebrain_hdmea"
    AXION = "axion_maestro"
    MCS = "mcs_mea2100"
    DANDI = "dandi_archive"


class APIErrorV37(RuntimeError):
    pass


class PermissionDeniedV37(APIErrorV37):
    pass


@dataclass(frozen=True)
class ExternalAPIConfigV37:
    platform: str
    endpoint: str = "mock://local"
    token_env: str | None = None
    access_mode: str = APIAccessModeV37.READ_ONLY.value
    dataset_ref: str | None = None
    notes: str = "read-only/mock integration config"

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        assert_no_forbidden_payload_v35(data, context="ExternalAPIConfigV37")
        return data


@dataclass(frozen=True)
class ExternalAPIMetadataV37:
    platform: str
    adapter_name: str
    access_mode: str
    connected: bool
    channel_count: int
    sample_rate_hz: float
    supports_metadata: bool
    supports_read_spikes: bool
    supports_read_trace: bool
    supports_live_stimulation: bool
    safety_scope: str
    vendor_or_lab_required_for_live: bool
    timestamp_utc: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SpikeEventV37:
    timestamp_s: float
    channel: int
    unit_id: str | None = None
    value: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TraceSampleV37:
    timestamp_s: float
    channel: int
    value: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BioGPUTraceV37:
    platform: str
    adapter_name: str
    access_mode: str
    source: str
    channel_count: int
    sample_rate_hz: float
    duration_s: float
    spike_events: tuple[dict[str, Any], ...]
    trace_samples: tuple[dict[str, Any], ...]
    metadata: dict[str, Any]
    safety: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CommercialTierV37:
    tier: str
    intended_user: str
    capabilities: tuple[str, ...]
    restrictions: tuple[str, ...]
    commercial_note: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def utc_now_v37() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class BaseExternalAPIClientV37:
    """Read-only external API adapter contract for BioGPU-Core v3.7."""

    adapter_name = "base_external_api_v37"
    platform = "base"
    default_channel_count = 0
    default_sample_rate_hz = 0.0

    def __init__(self, config: ExternalAPIConfigV37):
        assert_no_forbidden_payload_v35(config.to_dict(), context=f"{self.adapter_name}.config")
        if config.platform != self.platform:
            raise ValueError(f"Config platform {config.platform!r} does not match adapter {self.platform!r}")
        self.config = config
        self.connected = False

    def connect(self) -> ExternalAPIMetadataV37:
        self.connected = True
        return self.get_metadata()

    def close(self) -> None:
        self.connected = False

    def _assert_connected(self) -> None:
        if not self.connected:
            raise APIErrorV37(f"{self.adapter_name} is not connected")

    def _assert_mode_allows_read(self) -> None:
        mode = APIAccessModeV37(self.config.access_mode)
        if mode == APIAccessModeV37.METADATA_ONLY:
            raise PermissionDeniedV37("metadata_only mode does not allow reading spikes or traces")

    def _deny_live_write(self, payload: Any | None = None) -> None:
        if payload is not None:
            assert_no_forbidden_payload_v35(payload, context=f"{self.adapter_name}.write_payload")
        raise PermissionDeniedV37(
            "v3.7 is read-only/mock-only. Live stimulation/control is intentionally disabled; "
            "use lab/vendor-approved modules in later tiers."
        )

    def send_stimulation_pattern(self, payload: dict[str, Any]) -> None:
        self._deny_live_write(payload)

    def update_environment(self, payload: dict[str, Any]) -> None:
        self._deny_live_write(payload)

    def get_metadata(self) -> ExternalAPIMetadataV37:
        return ExternalAPIMetadataV37(
            platform=self.platform,
            adapter_name=self.adapter_name,
            access_mode=self.config.access_mode,
            connected=self.connected,
            channel_count=self.default_channel_count,
            sample_rate_hz=self.default_sample_rate_hz,
            supports_metadata=True,
            supports_read_spikes=self.config.access_mode != APIAccessModeV37.METADATA_ONLY.value,
            supports_read_trace=self.config.access_mode != APIAccessModeV37.METADATA_ONLY.value,
            supports_live_stimulation=False,
            safety_scope="metadata/read-only/replay/live-shadow only; no live actuation",
            vendor_or_lab_required_for_live=True,
            timestamp_utc=utc_now_v37(),
        )

    def read_spike_events(self, duration_s: float = 1.0, max_events: int = 128) -> list[SpikeEventV37]:
        self._assert_connected()
        self._assert_mode_allows_read()
        duration_s = float(duration_s)
        if duration_s <= 0:
            raise ValueError("duration_s must be positive")
        n_channels = max(1, min(self.default_channel_count, 64))
        n_events = min(max_events, max(4, int(duration_s * min(n_channels, 32))))
        events: list[SpikeEventV37] = []
        for i in range(n_events):
            t = (i + 1) * duration_s / (n_events + 1)
            ch = (i * 7 + len(self.adapter_name)) % n_channels
            events.append(SpikeEventV37(timestamp_s=round(t, 6), channel=ch, unit_id=f"u{ch:03d}", value=1.0))
        return events

    def read_trace_window(self, duration_s: float = 0.1, channels: Iterable[int] | None = None) -> list[TraceSampleV37]:
        self._assert_connected()
        self._assert_mode_allows_read()
        duration_s = float(duration_s)
        if duration_s <= 0:
            raise ValueError("duration_s must be positive")
        channel_list = list(channels) if channels is not None else list(range(min(self.default_channel_count, 4)))
        if not channel_list:
            channel_list = [0]
        samples: list[TraceSampleV37] = []
        steps = 8
        for step in range(steps):
            t = step * duration_s / max(1, steps - 1)
            for ch in channel_list[:8]:
                val = math.sin(2 * math.pi * (step + 1) / steps + ch * 0.1)
                samples.append(TraceSampleV37(timestamp_s=round(t, 6), channel=int(ch), value=round(val, 6)))
        return samples

    def export_biogpu_trace(self, duration_s: float = 1.0) -> BioGPUTraceV37:
        metadata = self.get_metadata().to_dict()
        spikes = [e.to_dict() for e in self.read_spike_events(duration_s=duration_s)]
        trace = [s.to_dict() for s in self.read_trace_window(duration_s=min(duration_s, 0.25))]
        safety = {
            "live_output_performed": False,
            "live_stimulation_enabled": False,
            "allowed_scope": ["metadata", "read_spike_events", "read_trace_window", "export_biogpu_trace"],
            "blocked_scope": ["send_stimulation_pattern", "update_environment", "pinout", "wetlab_recipe"],
        }
        return BioGPUTraceV37(
            platform=self.platform,
            adapter_name=self.adapter_name,
            access_mode=self.config.access_mode,
            source=self.config.endpoint,
            channel_count=self.default_channel_count,
            sample_rate_hz=self.default_sample_rate_hz,
            duration_s=duration_s,
            spike_events=tuple(spikes),
            trace_samples=tuple(trace),
            metadata=metadata,
            safety=safety,
        )


def commercial_tiers_v37() -> list[CommercialTierV37]:
    """Commercial packaging ladder for enterprises."""
    return [
        CommercialTierV37(
            tier="Community / Evaluation",
            intended_user="researchers, reviewers, first technical validation",
            capabilities=("metadata", "mock clients", "public replay datasets", "result bundles"),
            restrictions=("no live control", "no enterprise SLA", "no vendor-certified backend"),
            commercial_note="low-friction entry; useful for adoption and demos",
        ),
        CommercialTierV37(
            tier="Enterprise Read-Only SDK",
            intended_user="MEA labs, wetware startups, platform teams",
            capabilities=("API credentials", "read-only data access", "BioGPUTrace export", "audit logs", "custom connectors"),
            restrictions=("no stimulation/control", "vendor/lab data policies apply"),
            commercial_note="paid annual license; safest first enterprise product",
        ),
        CommercialTierV37(
            tier="Enterprise Live Shadow",
            intended_user="labs running live acquisition who want AI/readout beside the experiment",
            capabilities=("live stream read", "online readout", "dashboards", "alerts", "result bundles"),
            restrictions=("no actuation", "no closed-loop writes", "operator approval required"),
            commercial_note="premium license; strong commercial bridge before wetware control",
        ),
        CommercialTierV37(
            tier="Lab-Approved Closed-Loop Module",
            intended_user="approved laboratory/vendor deployments",
            capabilities=("approved protocol integration", "controlled closed-loop", "compliance logs", "support"),
            restrictions=("requires vendor/lab SOP", "requires written approval", "no generic public access"),
            commercial_note="highest-value module; milestone/enterprise contract pricing",
        ),
    ]
