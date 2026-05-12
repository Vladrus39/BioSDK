from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from biogpu.safety.boundary_v35 import FORBIDDEN_LIVE_FIELDS_V35, find_forbidden_keys_v35

VendorMode = Literal["dry_run", "metadata_only", "vendor_backend_required"]
AdapterStatus = Literal["created", "connected", "closed"]

FORBIDDEN_LIVE_KEYS = set(FORBIDDEN_LIVE_FIELDS_V35) | {"pulsewidth", "waveform", "wire", "stim_limit", "stimulation_limit", "electrical_limit", "culture_recipe"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _flatten_keys(obj: Any, prefix: str = "") -> list[str]:
    keys: list[str] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            name = str(k).lower()
            keys.append(name)
            keys.extend(_flatten_keys(v, f"{prefix}.{name}" if prefix else name))
    elif isinstance(obj, list):
        for item in obj:
            keys.extend(_flatten_keys(item, prefix))
    return keys


@dataclass(frozen=True)
class BioGPUVendorCapability:
    vendor_id: str
    display_name: str
    platform_class: str
    role_in_biogpu_a1: str
    recording_supported: bool
    stimulation_supported: bool
    raw_trace_supported: bool
    spike_stream_supported: bool
    ttl_sync_supported: bool
    environmental_sensors: list[str]
    api_access_class: str
    channel_count_class: str
    live_backend_status: str
    boundary_notice: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BioGPUVendorCommand:
    """Hardware-neutral command envelope.

    This is intentionally abstract. It may reference groups/aliases and task
    patterns, but it must not contain vendor pinouts, live electrical settings,
    wet-lab recipes, or tissue-specific stimulation limits.
    """

    command_id: str
    benchmark_id: str
    pattern_id: str
    electrode_group_aliases: list[str]
    timing_class: str = "abstract_task_window"
    payload: dict[str, Any] = field(default_factory=dict)
    safety_class: str = "abstract_pattern_only"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BioGPUVendorEvent:
    timestamp_utc: str
    adapter_id: str
    event: str
    status: str
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class UnsafeVendorCommandError(ValueError):
    pass


class BioGPUVendorAdapterBase:
    """Base class for vendor-specific MEA/HD-MEA adapters.

    v2.5 intentionally implements dry-run/metadata behavior only. Real vendor
    backends should subclass this and must be reviewed against vendor docs,
    approved SOPs, and live-lab safety rules before enabling hardware output.
    """

    adapter_id = "base"

    def __init__(self, mode: VendorMode = "dry_run", device_label: str | None = None) -> None:
        self.mode = mode
        self.device_label = device_label or "unbound-device"
        self.status: AdapterStatus = "created"
        self.events: list[BioGPUVendorEvent] = []

    @property
    def capability(self) -> BioGPUVendorCapability:  # pragma: no cover - subclasses override
        raise NotImplementedError

    def _log(self, event: str, status: str, **details: Any) -> BioGPUVendorEvent:
        item = BioGPUVendorEvent(utc_now(), self.adapter_id, event, status, details)
        self.events.append(item)
        return item

    def connect(self) -> dict[str, Any]:
        if self.mode == "vendor_backend_required":
            self._log("connect", "blocked", reason="real vendor backend not implemented in v2.5")
            raise NotImplementedError(
                f"{self.adapter_id} real hardware backend is not implemented in v2.5. "
                "Use dry_run until vendor SDK, SOP, live safety gates and lab approval exist."
            )
        self.status = "connected"
        self._log("connect", "ok", mode=self.mode, live_hardware=False)
        return {"adapter_id": self.adapter_id, "connected": True, "live_hardware": False, "mode": self.mode}

    def close(self) -> dict[str, Any]:
        self.status = "closed"
        self._log("close", "ok")
        return {"adapter_id": self.adapter_id, "closed": True}

    def validate_session(self, manifest: dict[str, Any] | None = None) -> list[str]:
        errors: list[str] = []
        cap = self.capability
        if manifest:
            mode = manifest.get("run_mode")
            if mode == "live_lab" and self.mode != "vendor_backend_required":
                errors.append("live_lab manifest requires a real vendor backend; current adapter is dry-run/metadata only")
            if mode in {"replay", "dry_run", "power_pc"} and self.mode == "vendor_backend_required":
                errors.append("vendor_backend_required mode should not be used for non-live runs")
        if cap.stimulation_supported and cap.live_backend_status == "stub_only":
            # Not an error: it is a reminder, stored as a validation warning format.
            pass
        self._log("validate_session", "ok" if not errors else "error", errors=errors)
        return errors

    def validate_command(self, command: BioGPUVendorCommand) -> list[str]:
        errors: list[str] = []
        if command.safety_class != "abstract_pattern_only":
            errors.append("command.safety_class must remain abstract_pattern_only in v2.5")
        keys = set(_flatten_keys(command.to_dict()))
        unsafe = sorted(set(find_forbidden_keys_v35(keys)).union(keys.intersection(FORBIDDEN_LIVE_KEYS)))
        if unsafe:
            errors.append("unsafe live-lab fields are not allowed in vendor command: " + ", ".join(unsafe))
        for alias in command.electrode_group_aliases:
            if str(alias).strip().isdigit():
                errors.append("electrode_group_aliases must use symbolic aliases, not numeric vendor channel/pin identifiers")
        self._log("validate_command", "ok" if not errors else "error", command_id=command.command_id, errors=errors)
        return errors

    def send_stimulation_pattern(self, command: BioGPUVendorCommand) -> dict[str, Any]:
        errors = self.validate_command(command)
        if errors:
            raise UnsafeVendorCommandError("; ".join(errors))
        if self.mode == "vendor_backend_required":
            self._log("send_stimulation_pattern", "blocked", command_id=command.command_id)
            raise NotImplementedError("Real stimulation output is intentionally not implemented in v2.5.")
        self._log("send_stimulation_pattern", "dry_run_ack", command_id=command.command_id, pattern_id=command.pattern_id)
        return {
            "adapter_id": self.adapter_id,
            "command_id": command.command_id,
            "accepted": True,
            "live_output_performed": False,
            "mode": self.mode,
            "note": "Dry-run acknowledgement only; no live stimulation emitted.",
        }

    def read_spike_stream(self, duration_s: float = 0.0) -> dict[str, Any]:
        if self.status != "connected":
            self.connect()
        self._log("read_spike_stream", "dry_run", duration_s=duration_s)
        return {
            "adapter_id": self.adapter_id,
            "live_input_performed": False,
            "duration_s": duration_s,
            "spikes": [],
            "note": "Dry-run empty stream. Real spike stream requires vendor backend.",
        }

    def read_raw_trace(self, duration_s: float = 0.0) -> dict[str, Any]:
        if self.status != "connected":
            self.connect()
        self._log("read_raw_trace", "dry_run", duration_s=duration_s)
        return {
            "adapter_id": self.adapter_id,
            "live_input_performed": False,
            "duration_s": duration_s,
            "raw_trace": [],
            "note": "Dry-run empty trace. Real raw acquisition requires vendor backend.",
        }

    def export_metadata(self) -> dict[str, Any]:
        return {
            "adapter_id": self.adapter_id,
            "mode": self.mode,
            "device_label": self.device_label,
            "status": self.status,
            "capability": self.capability.to_dict(),
            "events": [e.to_dict() for e in self.events],
            "safety_boundary": {
                "no_live_output_in_v25": True,
                "no_vendor_pinout": True,
                "no_live_stimulation_settings": True,
                "requires_for_real_backend": [
                    "vendor SDK/manuals",
                    "approved lab SOP",
                    "validated stimulation safety gates",
                    "biosafety/ethics approval as applicable",
                    "qualified operator",
                    "hardware interlock and audit logging",
                ],
            },
        }


def write_json(path: str | Path, data: Any) -> None:
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
