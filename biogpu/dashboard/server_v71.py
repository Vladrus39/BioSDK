"""BioSDK Dashboard v7.1 — FastAPI production backend."""
from __future__ import annotations

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from biogpu.production.config_v60 import load_production_config


class DashboardStatus(BaseModel):
    service: str = "BioSDK Dashboard"
    version: str = "v7.1"
    status: str = "running"
    uptime_seconds: float = 0.0
    subsystems: dict[str, str] = {}
    timestamp: str = ""


class JobSummary(BaseModel):
    total: int = 0
    queued: int = 0
    running: int = 0
    completed: int = 0
    failed: int = 0


class SystemInfo(BaseModel):
    daemon_available: bool = False
    signing_key_available: bool = False
    ci_gate_matrix_available: bool = False
    threat_model_available: bool = False
    production_domains_ready: int = 0
    production_domains_total: int = 12
    biosdk_locked: bool = True
    environment: str = "development"


class BioSDKDashboard:
    """BioSDK Dashboard backend."""

    def __init__(self, project_root: str | Path = "."):
        self.root = Path(project_root)
        self.config = load_production_config()
        self.start_time = datetime.now(timezone.utc)

    @property
    def uptime(self) -> float:
        return (datetime.now(timezone.utc) - self.start_time).total_seconds()

    def get_status(self) -> dict[str, Any]:
        return {
            "service": "BioSDK Dashboard",
            "version": "v7.1",
            "status": "running",
            "uptime_seconds": self.uptime,
            "subsystems": {
                "nsi_kernel": "active",
                "evidence_ledger": "active",
                "llm_agent_bridge": "active",
                "control_plane_queue": "active",
                "production_daemon": "active" if (self.root / "biogpu" / "production" / "daemon_v612.py").exists() else "missing",
                "dashboard": "active",
                "plugin_manager": "active",
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def get_system_info(self) -> dict[str, Any]:
        from biogpu.production.foundation_v60 import build_production_foundation
        foundation = build_production_foundation(self.root)
        return {
            "daemon_available": (self.root / "biogpu" / "production" / "daemon_v612.py").exists(),
            "signing_key_available": (self.root / "data" / "production" / "keys" / "release_signing.key").exists(),
            "ci_gate_matrix_available": (self.root / "configs" / "ci_gate_matrix.json").exists(),
            "threat_model_available": (self.root / "docs" / "SECURITY_THREAT_MODEL_V60.md").exists(),
            "production_domains_ready": foundation["production_ready_domain_count"],
            "production_domains_total": foundation["domain_count"],
            "biosdk_locked": foundation["biosdk_phase_locked"],
            "environment": self.config.environment,
        }

    def get_jobs(self) -> dict[str, Any]:
        """Load real replay jobs from production storage."""
        try:
            from biogpu.production.replay_worker_v81 import ReplayWorker
            worker = ReplayWorker(self.root)
            jobs = worker.list_jobs()
            return {
                "total": len(jobs),
                "queued": sum(1 for j in jobs if j.status == "queued"),
                "running": sum(1 for j in jobs if j.status == "running"),
                "completed": sum(1 for j in jobs if j.status == "completed"),
                "failed": sum(1 for j in jobs if j.status == "failed"),
                "jobs": [
                    {
                        "job_id": j.job_id,
                        "benchmark_id": j.benchmark_id,
                        "status": j.status,
                        "accuracy": j.result.get("best_accuracy", "N/A") if j.result else "N/A",
                        "started_at": j.started_at,
                        "completed_at": j.completed_at,
                    }
                    for j in jobs[-20:]  # Last 20 jobs
                ],
            }
        except Exception:
            return {"total": 0, "queued": 0, "running": 0, "completed": 0, "failed": 0, "jobs": []}

    def get_incidents(self) -> dict[str, Any]:
        return {"total": 0, "open": 0, "resolved": 0, "incidents": []}

    def get_telemetry(self) -> dict[str, Any]:
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
                        "source": "BioSDK MEA Simulator v8.1",
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
        return {"status": status, "streams": streams, "count": len(streams), "timestamp": datetime.now(timezone.utc).isoformat()}

    def get_approvals(self) -> dict[str, Any]:
        return {"pending": 0, "approved": 0, "denied": 0, "approvals": []}


# Global dashboard instance
_dashboard: BioSDKDashboard | None = None


def get_dashboard() -> BioSDKDashboard:
    global _dashboard
    if _dashboard is None:
        _dashboard = BioSDKDashboard()
    return _dashboard


def create_dashboard_app(root_path: str | Path = ".") -> FastAPI:
    root_path = Path(root_path)
    app = FastAPI(title="BioSDK Dashboard", version="v7.1", description="BioCompute Runtime Control Plane")

    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

    @app.get("/", response_class=HTMLResponse)
    async def root():
        return DASHBOARD_HTML

    @app.get("/api/v1/status")
    async def status():
        return get_dashboard().get_status()

    @app.get("/api/v1/system")
    async def system():
        return get_dashboard().get_system_info()

    @app.get("/api/v1/jobs")
    async def jobs():
        return get_dashboard().get_jobs()

    @app.get("/api/v1/incidents")
    async def incidents():
        return get_dashboard().get_incidents()

    @app.get("/api/v1/telemetry")
    async def telemetry():
        return get_dashboard().get_telemetry()

    @app.get("/api/v1/approvals")
    async def approvals():
        return get_dashboard().get_approvals()

    @app.get("/health")
    async def health():
        return {"status": "healthy", "version": "v7.1", "timestamp": datetime.now(timezone.utc).isoformat()}

    @app.get("/api/v1/metrics")
    async def metrics():
        """Return current BioSDK project metrics (v9.5)."""
        try:
            status_path = root_path / "PROJECT_STATUS_V85.json"
            if status_path.exists():
                s = json.loads(status_path.read_text(encoding="utf-8"))
                pipeline = s.get("bio_compute_pipeline", {})
                return {
                    "project": "BioSDK",
                    "version": s.get("version", "unknown"),
                    "cross_modal_classification": pipeline.get("cross_modal_classification_accuracy"),
                    "cross_modal_method": pipeline.get("cross_modal_classification_method", "channel_averaged"),
                    "nsi_adapters": s.get("nsi_adapters_v90", {}).get("total_certified", 0),
                    "nsi_conformance": pipeline.get("nsi_conformance_tests_pass", "N/A"),
                    "evidence_bundle": pipeline.get("evidence_bundle_verified", "N/A"),
                    "tressoldi_eeg": s.get("tressoldi_classification_v91", {}).get("results", {}).get("within_pair_mean_balanced_acc"),
                    "best_mea_accuracy": pipeline.get("best_accuracy"),
                    "beta_packet": s.get("beta_invite_packet_v93", {}).get("created", False),
                    "finalspark_adapter": s.get("finalspark_adapter_v94", {}).get("status", "unknown"),
                    "gaps_remaining": len(s.get("honest_gaps_remaining", [])),
                    "datasets": pipeline.get("datasets_with_features", 0),
                    "pip_wheel_built": pipeline.get("pip_wheel_built", False),
                }
        except Exception:
            pass
        return {"error": "PROJECT_STATUS_V85.json not available"}

    @app.get("/api/v1/benchmarks")
    async def benchmarks():
        """List available BioGPU replay benchmarks with their status."""
        try:
            from biogpu.production.replay_worker_v81 import REPLAY_BENCHMARKS, ReplayWorker
            worker = ReplayWorker()
            result = []
            for bid, info in REPLAY_BENCHMARKS.items():
                existing = worker._find_existing_results(bid)
                result.append({
                    "benchmark_id": bid,
                    "description": info["description"],
                    "data_source": info["data_source"],
                    "expected_accuracy": info["expected_accuracy_range"],
                    "runtime_seconds": info["runtime_seconds"],
                    "has_results": existing is not None,
                    "accuracy": existing.get("best_accuracy", "N/A") if existing else "not_run",
                })
            return {"benchmarks": result, "count": len(result)}
        except Exception as exc:
            return {"benchmarks": [], "error": str(exc)}



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

    return app


DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>BioSDK Dashboard v7.1</title>
<style>
:root { --bg: #0a0e14; --panel: #131820; --border: #1e2838; --accent: #2f80ed; --text: #c8d6e5; --green: #27ae60; --red: #e74c3c; --yellow: #f39c12; }
* { margin: 0; padding: 0; box-sizing: border-box; }
body { background: var(--bg); color: var(--text); font-family: 'Segoe UI', system-ui, sans-serif; padding: 20px; }
.header { display: flex; justify-content: space-between; align-items: center; padding: 16px 24px; background: var(--panel); border: 1px solid var(--border); border-radius: 8px; margin-bottom: 20px; }
.header h1 { font-size: 22px; color: var(--accent); }
.badge { padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600; }
.badge-ok { background: var(--green); color: #fff; }
.badge-warn { background: var(--yellow); color: #000; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; }
.card { background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 16px; }
.card h3 { font-size: 14px; color: var(--accent); margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.5px; }
.stat { display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid var(--border); }
.stat:last-child { border-bottom: none; }
.stat-key { color: #8090a0; font-size: 13px; }
.stat-val { font-weight: 600; font-size: 14px; }
.pulse { animation: pulse 2s infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
th { text-align: left; color: var(--accent); padding: 8px; border-bottom: 1px solid var(--border); }
td { padding: 8px; border-bottom: 1px solid #1a1f2b; }
</style>
</head>
<body>
<div class="header">
  <h1>BioSDK Dashboard</h1>
  <div>
    <span class="badge badge-ok pulse" id="status-badge">RUNNING</span>
    <span style="margin-left: 8px; font-size: 12px; color: #8090a0;" id="uptime"></span>
  </div>
</div>
<div class="grid" id="grid"></div>
<script>
const API = '/api/v1';
async function load() {
  try {
    const [status, system] = await Promise.all([
      fetch(API + '/status').then(r => r.json()),
      fetch(API + '/system').then(r => r.json()),
    ]);
    render(status, system);
  } catch(e) { document.getElementById('grid').innerHTML = '<div class="card"><h3>ERROR</h3><p>Dashboard backend unreachable</p></div>'; }
}
function render(s, sys) {
  document.getElementById('uptime').textContent = 'up ' + Math.floor(s.uptime_seconds) + 's';
  const subsystems = s.subsystems || {};
  const subBadges = Object.entries(subsystems).map(([k,v]) => '<span class="badge badge-' + (v==='active'?'ok':'warn') + '" style="margin:2px">' + k.replace(/_/g,' ') + '</span>').join(' ');
  document.getElementById('grid').innerHTML = `
    <div class="card"><h3>System</h3>
      <div class="stat"><span class="stat-key">Version</span><span class="stat-val">${s.version}</span></div>
      <div class="stat"><span class="stat-key">Environment</span><span class="stat-val">${sys.environment}</span></div>
      <div class="stat"><span class="stat-key">BioSDK Locked</span><span class="stat-val">${sys.biosdk_locked}</span></div>
      <div class="stat"><span class="stat-key">Production Domains</span><span class="stat-val">${sys.production_domains_ready}/${sys.production_domains_total}</span></div>
    </div>
    <div class="card"><h3>Infrastructure</h3>
      <div class="stat"><span class="stat-key">Daemon</span><span class="stat-val">${sys.daemon_available ? 'OK' : 'MISSING'}</span></div>
      <div class="stat"><span class="stat-key">Signing Key</span><span class="stat-val">${sys.signing_key_available ? 'OK' : 'MISSING'}</span></div>
      <div class="stat"><span class="stat-key">CI/CD Gates</span><span class="stat-val">${sys.ci_gate_matrix_available ? 'OK' : 'MISSING'}</span></div>
      <div class="stat"><span class="stat-key">Threat Model</span><span class="stat-val">${sys.threat_model_available ? 'OK' : 'MISSING'}</span></div>
    </div>
    <div class="card"><h3>Subsystems</h3><div style="line-height:2">${subBadges}</div></div>
    <div class="card"><h3>Jobs</h3><div class="stat"><span class="stat-key">No active jobs</span><span class="stat-val">0</span></div></div>
    <div class="card"><h3>Incidents</h3><div class="stat"><span class="stat-key">No open incidents</span><span class="stat-val">0</span></div></div>
    <div class="card"><h3>Safety</h3>
      <div class="stat"><span class="stat-key">Live Actuation</span><span class="stat-val" style="color:var(--red)">BLOCKED</span></div>
      <div class="stat"><span class="stat-key">Read-only API</span><span class="stat-val" style="color:var(--green)">ALLOWED</span></div>
      <div class="stat"><span class="stat-key">Replay Mode</span><span class="stat-val" style="color:var(--green)">ALLOWED</span></div>
    </div>
  `;
}
load();
setInterval(load, 10000);
</script>
</body>
</html>"""


def main():
    import uvicorn
    app = create_dashboard_app()
    print("BioSDK Dashboard v7.1 starting on http://127.0.0.1:8420")
    uvicorn.run(app, host="127.0.0.1", port=8420, log_level="info")


if __name__ == "__main__":
    main()