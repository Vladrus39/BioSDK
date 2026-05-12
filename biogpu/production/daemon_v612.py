"""BioSDK Production Daemon v6.12.

Production-grade daemon for BioCompute Runtime / BioSDK.
Runs as a Windows service (via NSSM) or systemd unit on Linux.

Usage:
    python -m biogpu.production.daemon_v612 [--foreground]
"""
from __future__ import annotations

import json
import logging
import signal
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from biogpu.production.config_v60 import ProductionConfig, load_production_config

LOG = logging.getLogger("bicos.daemon")


class BioSDKDaemon:
    """Production daemon for BioSDK / BioCompute Runtime."""

    def __init__(self, config: ProductionConfig | None = None, project_root: str | Path = "."):
        self.config = config or load_production_config()
        self.root = Path(project_root)
        self.running = False
        self.start_time: str = ""
        self._setup_logging()

    def _setup_logging(self) -> None:
        log_path = self.root / self.config.os_service_log_path
        log_path.parent.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            handlers=[
                logging.FileHandler(str(log_path), encoding="utf-8"),
                logging.StreamHandler(sys.stdout),
            ],
        )

    def start(self) -> None:
        self.running = True
        self.start_time = datetime.now(timezone.utc).isoformat()
        LOG.info(f"BioSDK Daemon v6.12 starting (env={self.config.environment}, production={self.config.production_mode})")
        self._write_pid()
        self._write_status("running")

    def stop(self) -> None:
        LOG.info("BioSDK Daemon stopping")
        self.running = False
        self._write_status("stopped")
        self._remove_pid()

    def run_forever(self) -> None:
        self.start()
        signal.signal(signal.SIGINT, lambda *_: self.stop())
        signal.signal(signal.SIGTERM, lambda *_: self.stop())
        try:
            while self.running:
                self._tick()
                time.sleep(self.config.worker_heartbeat_interval_seconds)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()

    def _tick(self) -> None:
        heartbeat_file = self.root / "data" / "production" / "daemon_heartbeat.json"
        heartbeat = {
            "status": "alive",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "uptime_seconds": (datetime.now(timezone.utc) - datetime.fromisoformat(self.start_time)).total_seconds() if self.start_time else 0,
            "environment": self.config.environment,
        }
        heartbeat_file.write_text(json.dumps(heartbeat), encoding="utf-8")
        LOG.debug("Heartbeat")

    def _write_pid(self) -> None:
        pid_file = self.root / "data" / "production" / "daemon.pid"
        pid_file.write_text(str(Path(sys.executable).parent), encoding="utf-8")

    def _remove_pid(self) -> None:
        pid_file = self.root / "data" / "production" / "daemon.pid"
        if pid_file.exists():
            pid_file.unlink()

    def _write_status(self, status: str) -> None:
        status_file = self.root / "data" / "production" / "daemon_status.json"
        status_file.write_text(json.dumps({
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "v6.12",
        }), encoding="utf-8")


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="BioSDK Production Daemon v6.12")
    parser.add_argument("--foreground", action="store_true", help="Run in foreground (not as service)")
    parser.add_argument("--root", default=".", help="Project root directory")
    args = parser.parse_args()

    config = load_production_config()
    config.production_mode = True
    daemon = BioSDKDaemon(config, args.root)

    if args.foreground:
        daemon.run_forever()
    else:
        # Service mode entry point
        # When run via NSSM or systemd, the service manager handles start/stop
        daemon.run_forever()


if __name__ == "__main__":
    main()
