"""BioSDK MEA Simulator v8.1 — Synthetic neural data generator.

Generates realistic MEA-like data streams for testing the BioSDK
telemetry pipeline, dashboard, and closed-loop safety gates.

Produces:
- Spike trains (Poisson + bursting patterns)
- Local Field Potential (LFP) — 1/f noise + oscillations
- Multi-electrode array (60/120/256 channels)
- Event markers (stimulation triggers)
- Timestamps aligned to BioSDK telemetry format
"""
from __future__ import annotations

import hashlib
import json
import math
import random
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class MEAConfig:
    """Simulated MEA configuration."""
    channel_count: int = 60
    sample_rate_hz: float = 20000.0
    duration_seconds: float = 10.0
    electrode_spacing_um: float = 200.0
    noise_level_uv: float = 5.0
    neuron_count: int = 30
    burst_probability: float = 0.05
    lfp_oscillation_hz: float = 4.0  # theta band
    seed: int = 42


@dataclass
class SpikeEvent:
    channel: int
    time_ms: float
    amplitude_uv: float
    neuron_id: int

@dataclass
class LFPSample:
    channel: int
    time_ms: float
    value_uv: float


@dataclass
class TelemetryPacket:
    packet_id: int
    timestamp: str
    spike_count: int
    lfp_samples: int
    channels_active: int
    total_bytes: int
    spikes: list[dict[str, Any]] = field(default_factory=list)
    lfp: list[dict[str, Any]] = field(default_factory=list)


class MEASimulator:
    """Generates synthetic MEA data for BioSDK testing."""

    def __init__(self, config: MEAConfig | None = None):
        self.config = config or MEAConfig()
        random.seed(self.config.seed)
        self._init_neurons()
        self.packet_counter: int = 0

    def _init_neurons(self) -> None:
        """Initialize virtual neurons with firing rates."""
        self.neurons: list[dict[str, Any]] = []
        for i in range(self.config.neuron_count):
            channel = i % self.config.channel_count
            base_rate = random.uniform(1.0, 15.0)  # Hz
            is_bursty = random.random() < self.config.burst_probability
            self.neurons.append({
                "id": i,
                "channel": channel,
                "base_rate_hz": base_rate,
                "bursty": is_bursty,
                "burst_rate_hz": base_rate * 5 if is_bursty else base_rate,
                "amplitude_mean_uv": random.uniform(30, 150),
                "amplitude_std_uv": random.uniform(5, 25),
            })

    def generate_spikes(self, duration_ms: float) -> list[SpikeEvent]:
        """Generate Poisson spike trains for the given duration."""
        spikes: list[SpikeEvent] = []
        for neuron in self.neurons:
            rate = neuron["burst_rate_hz"] if random.random() < 0.1 else neuron["base_rate_hz"]
            interval_ms = 1000.0 / rate if rate > 0 else float("inf")
            t = 0.0
            while t < duration_ms:
                t += random.expovariate(1.0 / interval_ms) if interval_ms < float("inf") else duration_ms + 1
                if t < duration_ms:
                    amp = max(0, random.gauss(neuron["amplitude_mean_uv"], neuron["amplitude_std_uv"]))
                    spikes.append(SpikeEvent(
                        channel=neuron["channel"],
                        time_ms=round(t, 2),
                        amplitude_uv=round(amp, 1),
                        neuron_id=neuron["id"],
                    ))
        spikes.sort(key=lambda s: s.time_ms)
        return spikes

    def generate_lfp(self, duration_ms: float, dt_ms: float = 1.0) -> list[LFPSample]:
        """Generate synthetic LFP with 1/f noise and theta oscillation."""
        samples: list[LFPSample] = []
        n_steps = int(duration_ms / dt_ms)
        theta_freq = self.config.lfp_oscillation_hz
        for ch in range(min(8, self.config.channel_count)):
            phase = random.uniform(0, 2 * math.pi)
            for step in range(n_steps):
                t = step * dt_ms
                oscillation = 15.0 * math.sin(2 * math.pi * theta_freq * t / 1000.0 + phase)
                noise = self.config.noise_level_uv * random.gauss(0, 1)
                f_noise = 3.0 * random.gauss(0, 1) / math.sqrt(max(1, step))
                samples.append(LFPSample(
                    channel=ch,
                    time_ms=round(t, 2),
                    value_uv=round(oscillation + noise + f_noise, 2),
                ))
        return samples

    def generate_packet(self, window_ms: float = 1000.0) -> TelemetryPacket:
        """Generate one telemetry packet (1 second of data)."""
        self.packet_counter += 1
        spikes = self.generate_spikes(window_ms)
        lfp = self.generate_lfp(window_ms, dt_ms=10.0)

        # Serialize to estimate bytes
        spike_json = json.dumps([asdict(s) for s in spikes])
        lfp_json = json.dumps([asdict(l) for l in lfp])
        total_bytes = len(spike_json.encode()) + len(lfp_json.encode())

        return TelemetryPacket(
            packet_id=self.packet_counter,
            timestamp=datetime.now(timezone.utc).isoformat(),
            spike_count=len(spikes),
            lfp_samples=len(lfp),
            channels_active=len(set(s.channel for s in spikes)),
            total_bytes=total_bytes,
            spikes=[asdict(s) for s in spikes[:100]],  # cap at 100 for storage
            lfp=[asdict(l) for l in lfp[:200]],       # cap at 200 for storage
        )

    def run_stream(self, packet_count: int = 10, packet_interval_ms: float = 1000.0) -> list[TelemetryPacket]:
        """Generate a stream of telemetry packets."""
        packets = []
        for i in range(packet_count):
            packet = self.generate_packet(1000.0)
            packets.append(packet)
            if i < packet_count - 1:
                time.sleep(packet_interval_ms / 1000.0)
        return packets

    def run_and_save(self, output_dir: str | Path, packet_count: int = 10) -> dict[str, Any]:
        """Run simulation, save to files, return summary."""
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)

        packets = self.run_stream(packet_count, packet_interval_ms=100.0)

        # Save packets
        for p in packets:
            path = out / f"packet_{p.packet_id:04d}.json"
            path.write_text(json.dumps(asdict(p), indent=2, ensure_ascii=False), encoding="utf-8")

        # Save summary
        total_spikes = sum(p.spike_count for p in packets)
        total_bytes = sum(p.total_bytes for p in packets)
        summary = {
            "simulator": "MEA v8.1",
            "config": asdict(self.config),
            "packets_generated": len(packets),
            "total_spikes": total_spikes,
            "total_lfp_samples": sum(p.lfp_samples for p in packets),
            "total_bytes": total_bytes,
            "avg_spike_rate_hz": total_spikes / (packet_count * 1.0),
            "channels_active": max(p.channels_active for p in packets),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "sha256": "",
        }
        summary_json = json.dumps(summary, sort_keys=True, ensure_ascii=False)
        summary["sha256"] = hashlib.sha256(summary_json.encode()).hexdigest()

        (out / "simulation_summary.json").write_text(summary_json, encoding="utf-8")
        return summary


def demo() -> dict[str, Any]:
    """Quick demo: generate 5 packets and return summary."""
    sim = MEASimulator(MEAConfig(channel_count=60, neuron_count=30, duration_seconds=5))
    return sim.run_and_save("data/production/telemetry/simulator_demo", packet_count=5)


if __name__ == "__main__":
    result = demo()
    print(f"MEA Simulator demo: {result['packets_generated']} packets, {result['total_spikes']} spikes, {result['total_bytes']} bytes")
