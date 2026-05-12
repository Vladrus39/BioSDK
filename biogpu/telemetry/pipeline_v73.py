"""BioSDK Live Telemetry v7.3 — Partner API pipeline, live-shadow streams."""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class TelemetryStream:
    stream_id: str
    source: str  # partner_api, local_file, live_shadow
    status: str  # active, paused, stopped, error
    data_format: str  # nwb, hdf5, csv, json_stream
    sample_rate_hz: float = 0.0
    bytes_received: int = 0
    packets_received: int = 0
    started_at: str = ""
    last_packet_at: str = ""
    error_count: int = 0
    error_last: str = ""


@dataclass
class TelemetryBundle:
    bundle_id: str
    stream_count: int = 0
    total_bytes: int = 0
    snapshot_at: str = ""
    sha256: str = ""
    streams: list[dict[str, Any]] = field(default_factory=list)


class TelemetryPipeline:
    """Live telemetry pipeline for BioSDK."""

    def __init__(self, project_root: str | Path = "."):
        self.root = Path(project_root)
        self.streams: dict[str, TelemetryStream] = {}
        self.telemetry_dir = self.root / "data" / "production" / "telemetry"
        self.telemetry_dir.mkdir(parents=True, exist_ok=True)

    def register_stream(self, stream: TelemetryStream) -> None:
        self.streams[stream.stream_id] = stream
        self._persist_stream(stream)

    def update_stream(self, stream_id: str, **kwargs) -> TelemetryStream | None:
        stream = self.streams.get(stream_id)
        if not stream:
            return None
        for key, value in kwargs.items():
            if hasattr(stream, key):
                setattr(stream, key, value)
        stream.last_packet_at = datetime.now(timezone.utc).isoformat()
        self._persist_stream(stream)
        return stream

    def stop_stream(self, stream_id: str) -> None:
        stream = self.streams.get(stream_id)
        if stream:
            stream.status = "stopped"
            self._persist_stream(stream)

    def snapshot(self) -> TelemetryBundle:
        streams_data = [asdict(s) for s in self.streams.values()]
        bundle = TelemetryBundle(
            bundle_id=f"telemetry-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}",
            stream_count=len(streams_data),
            total_bytes=sum(s.bytes_received for s in self.streams.values()),
            snapshot_at=datetime.now(timezone.utc).isoformat(),
            streams=streams_data,
        )
        bundle_json = json.dumps(asdict(bundle), sort_keys=True, ensure_ascii=False)
        bundle.sha256 = hashlib.sha256(bundle_json.encode()).hexdigest()

        # Save snapshot
        snap_path = self.telemetry_dir / f"{bundle.bundle_id}.json"
        snap_path.write_text(bundle_json, encoding="utf-8")
        return bundle

    def _persist_stream(self, stream: TelemetryStream) -> None:
        stream_path = self.telemetry_dir / f"stream_{stream.stream_id}.json"
        stream_path.write_text(json.dumps(asdict(stream), indent=2, ensure_ascii=False), encoding="utf-8")

    def get_active_streams(self) -> list[TelemetryStream]:
        return [s for s in self.streams.values() if s.status == "active"]

    def get_stream(self, stream_id: str) -> TelemetryStream | None:
        return self.streams.get(stream_id)
