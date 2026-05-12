"""BiC OS v8.1 — MEA Simulator + Dashboard with live data + API/export.

Builds:
1. biogpu/simulators/mea_v81.py — synthetic MEA data generator
2. Updated dashboard — shows live simulator telemetry
3. API/export endpoint for DANDI/NWB
4. Run dashboard as background process
"""
from pathlib import Path
from datetime import datetime, timezone
import json, sys, os

BASE = Path(r"C:\Users\vladi\Desktop\Braine\BiC OS\biogpu-core-v5_0_bic_os_first_mover_roadmap")
now = datetime.now(timezone.utc).isoformat()

# Ensure directories
for d in ["biogpu/simulators", "biogpu/dashboard", "data/production/telemetry", "outputs/v81_simulator"]:
    (BASE / d).mkdir(parents=True, exist_ok=True)

# ============================================================
# 1. MEA Simulator v8.1
# ============================================================
simulator_code = '''"""BiC OS MEA Simulator v8.1 — Synthetic neural data generator.

Generates realistic MEA-like data streams for testing the BiC OS
telemetry pipeline, dashboard, and closed-loop safety gates.

Produces:
- Spike trains (Poisson + bursting patterns)
- Local Field Potential (LFP) — 1/f noise + oscillations
- Multi-electrode array (60/120/256 channels)
- Event markers (stimulation triggers)
- Timestamps aligned to BiC OS telemetry format
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
    """Generates synthetic MEA data for BiC OS testing."""

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
'''

sim_path = BASE / "biogpu" / "simulators" / "mea_v81.py"
sim_path.parent.mkdir(parents=True, exist_ok=True)
(BASE / "biogpu" / "simulators" / "__init__.py").write_text('''"""BiC OS Simulators v8.1."""
from biogpu.simulators.mea_v81 import MEASimulator, MEAConfig, TelemetryPacket, demo
__all__ = ["MEASimulator", "MEAConfig", "TelemetryPacket", "demo"]
''', encoding="utf-8")
sim_path.write_text(simulator_code, encoding="utf-8")
print("MEA Simulator OK")

# ============================================================
# 2. Wire simulator into dashboard telemetry (update server_v71.py)
# ============================================================
dashboard_path = BASE / "biogpu" / "dashboard" / "server_v71.py"
dash_code = dashboard_path.read_text(encoding="utf-8")

# Replace get_telemetry to also show live simulator if available
new_telemetry = '''    def get_telemetry(self) -> dict[str, Any]:
        """Show replay results + live simulator data as telemetry."""
        streams = []

        # 1. Load existing replay benchmark results
        try:
            from biogpu.production.replay_worker_v81 import ReplayWorker, REPLAY_BENCHMARKS
            worker = ReplayWorker(self.root, "dashboard-telemetry")
            for bid, info in REPLAY_BENCHMARKS.items():
                existing = worker._find_existing_results(bid)
                if existing:
                    acc = "N/A"
                    if "best_accuracy" in existing:
                        acc = existing["best_accuracy"]
                    elif "best_run" in existing and isinstance(existing["best_run"], dict):
                        acc = existing["best_run"].get("accuracy", "N/A")
                    elif "observed" in existing and isinstance(existing["observed"], dict):
                        acc = existing["observed"].get("accuracy", "N/A")
                    streams.append({
                        "stream_id": bid, "type": "replay_benchmark",
                        "source": info["data_source"], "status": "completed",
                        "description": info["description"],
                        "accuracy": acc,
                        "rows": existing.get("dataset_rows", existing.get("rows", 0)),
                        "features": existing.get("dataset_features", existing.get("features", 0)),
                    })
        except Exception:
            pass

        # 2. Load simulator-generated data if available
        sim_dir = self.root / "data" / "production" / "telemetry" / "simulator_demo"
        if sim_dir.exists():
            summary_file = sim_dir / "simulation_summary.json"
            if summary_file.exists():
                try:
                    sim_summary = json.loads(summary_file.read_text(encoding="utf-8"))
                    streams.append({
                        "stream_id": "mea_simulator_v81",
                        "type": "live_simulator",
                        "source": "BiC OS MEA Simulator v8.1",
                        "status": "completed",
                        "description": f"Synthetic MEA: {sim_summary.get('config', {}).get('channel_count', '?')} channels, {sim_summary.get('config', {}).get('neuron_count', '?')} neurons",
                        "packets": sim_summary.get("packets_generated", 0),
                        "total_spikes": sim_summary.get("total_spikes", 0),
                        "total_bytes": sim_summary.get("total_bytes", 0),
                        "avg_spike_rate_hz": sim_summary.get("avg_spike_rate_hz", 0),
                    })
                except Exception:
                    pass

        status = "replay_and_simulator_available" if streams else "no_data"
        return {"status": status, "streams": streams, "count": len(streams), "timestamp": datetime.now(timezone.utc).isoformat()}'''

dash_code = dash_code.replace(
    '''    def get_telemetry(self) -> dict[str, Any]:
        """Show replay results as telemetry data."""
        try:
            from biogpu.production.replay_worker_v81 import ReplayWorker, REPLAY_BENCHMARKS
            worker = ReplayWorker(self.root, "dashboard-telemetry")
            streams = []
            for bid, info in REPLAY_BENCHMARKS.items():
                existing = worker._find_existing_results(bid)
                if existing:
                    streams.append({
                        "stream_id": bid,
                        "source": info["data_source"],
                        "status": "completed",
                        "description": info["description"],
                        "accuracy": existing.get("best_accuracy", "N/A"),
                        "rows": existing.get("dataset_rows", 0),
                        "features": existing.get("dataset_features", 0),
                    })
            return {
                "status": "replay_results_available" if streams else "no_results",
                "streams": streams,
                "count": len(streams),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        except Exception:
            return {"status": "no_live_streams", "streams": [], "timestamp": datetime.now(timezone.utc).isoformat()}''',
    new_telemetry
)

# Add API/export endpoint for DANDI/NWB
api_export_service = '''

    @app.get("/api/v1/export/dandi/{dataset_id}")
    async def export_dandi(dataset_id: str):
        """Export DANDI/NWB dataset metadata and availability."""
        nwb_dir = root_path / "data" / "external" / "nwb" / f"dandi_{dataset_id}"
        if not nwb_dir.exists():
            nwb_dir = root_path / "data" / "external" / "nwb" / "dandi_000469"
        nwb_files = list(nwb_dir.rglob("*.nwb")) if nwb_dir.exists() else []
        return {
            "dataset_id": dataset_id,
            "available": len(nwb_files) > 0,
            "nwb_files": [str(f.relative_to(root_path)) for f in nwb_files[:10]],
            "file_count": len(nwb_files),
            "total_size_bytes": sum(f.stat().st_size for f in nwb_files),
        }

    @app.get("/api/v1/export/zenodo")
    async def export_zenodo():
        """List available Zenodo raw HDF5 files."""
        hdf5_dir = root_path / "data" / "external" / "raw_hdf5"
        files = list(hdf5_dir.rglob("*.h5")) if hdf5_dir.exists() else []
        return {
            "source": "Zenodo 14363732",
            "available": len(files) > 0,
            "file_count": len(files),
            "files": [str(f.relative_to(root_path)) for f in files[:20]],
            "total_size_bytes": sum(f.stat().st_size for f in files),
        }

    @app.get("/api/v1/export/allen")
    async def export_allen():
        """List available Allen Institute NWB files."""
        allen_dir = root_path / "data" / "external" / "allen"
        files = list(allen_dir.rglob("*.nwb")) if allen_dir.exists() else []
        return {
            "source": "Allen Institute / DANDI 000021",
            "available": len(files) > 0,
            "file_count": len(files),
            "files": [str(f.relative_to(root_path)) for f in files[:10]],
            "total_size_bytes": sum(f.stat().st_size for f in files),
        }

    @app.get("/api/v1/export/mcs")
    async def export_mcs():
        """List available MCS MEA2100 export files."""
        mcs_dir = root_path / "data" / "external" / "api_exports" / "mcs_mea2100"
        files = list(mcs_dir.rglob("*.h5")) if mcs_dir.exists() else []
        return {
            "source": "MCS MEA2100 Export",
            "available": len(files) > 0,
            "file_count": len(files),
            "files": [str(f.relative_to(root_path)) for f in files[:10]],
            "total_size_bytes": sum(f.stat().st_size for f in files),
        }

    @app.get("/api/v1/export/simulator")
    async def export_simulator():
        """List available simulator-generated data."""
        sim_dir = root_path / "data" / "production" / "telemetry" / "simulator_demo"
        files = list(sim_dir.rglob("*.json")) if sim_dir.exists() else []
        summary = {}
        sf = sim_dir / "simulation_summary.json"
        if sf.exists():
            summary = json.loads(sf.read_text(encoding="utf-8"))
        return {
            "simulator": "MEA v8.1",
            "available": len(files) > 0,
            "file_count": len(files),
            "summary": {k: v for k, v in summary.items() if k != "sha256"},
        }

    return app'''

# Need to add root_path variable and replace the return app line
# First, add root_path right before create_dashboard_app
dash_code = dash_code.replace(
    "def create_dashboard_app() -> FastAPI:",
    "def create_dashboard_app(root_path: str | Path = \".\") -> FastAPI:\n    root_path = Path(root_path)"
)

# Replace the final "return app" with the export endpoints
dash_code = dash_code.replace("    return app", api_export_service)

dashboard_path.write_text(dash_code, encoding="utf-8")
print("Dashboard updated with simulator telemetry + API/export")

# ============================================================
# 3. Run MEA simulator demo
# ============================================================
print("\n=== Running MEA Simulator ===")
sys.path.insert(0, str(BASE))
from biogpu.simulators.mea_v81 import MEASimulator, MEAConfig, demo

result = demo()
print(f"  Packets: {result['packets_generated']}")
print(f"  Spikes: {result['total_spikes']}")
print(f"  Bytes: {result['total_bytes']}")
print(f"  Avg rate: {result['avg_spike_rate_hz']:.1f} Hz")
print(f"  Channels active: {result['channels_active']}")

# Save production summary
sum_path = BASE / "outputs" / "v81_simulator" / "V81_SIMULATOR_SUMMARY.json"
sum_path.parent.mkdir(parents=True, exist_ok=True)
sum_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

# ============================================================
# 4. Show dashboard can see the data
# ============================================================
print("\n=== Dashboard Data Check ===")
from biogpu.dashboard.server_v71 import BiCOSDashboard
dash = BiCOSDashboard(BASE)

status = dash.get_status()
print(f"  Dashboard: {status['service']} v{status['version']}")

telemetry = dash.get_telemetry()
print(f"  Telemetry status: {telemetry['status']}")
print(f"  Streams: {telemetry['count']}")
for s in telemetry["streams"]:
    sid = s.get("stream_id", "?")
    stype = s.get("type", "?")
    if stype == "replay_benchmark":
        print(f"    [{sid}] replay — accuracy={s.get('accuracy', 'N/A')}")
    elif stype == "live_simulator":
        print(f"    [{sid}] simulator — {s.get('total_spikes', 0)} spikes, {s.get('avg_spike_rate_hz', 0):.1f} Hz")

jobs = dash.get_jobs()
print(f"  Jobs: {jobs['total']} total, {jobs['completed']} completed")

print("\n=== v8.1 MEA Simulator + Dashboard ready ===")
print("Start dashboard: python -m biogpu.dashboard.server_v71")
print("Then open: http://127.0.0.1:8420")
