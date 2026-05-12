"""BioSDK Safe Closed-Loop v7.5 — Protocol-bound actuation with safety gates."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class StimulationProtocol:
    protocol_id: str
    name: str
    max_amplitude_ua: float = 0.0  # microamperes
    max_pulse_width_us: float = 0.0  # microseconds
    max_frequency_hz: float = 0.0
    max_charge_per_phase_nc: float = 0.0  # nanocoulombs
    max_duration_seconds: float = 0.0
    electrode_count: int = 0
    electrode_ids: list[int] = field(default_factory=list)
    safety_limits: dict[str, float] = field(default_factory=dict)
    approved_by: str = ""
    approval_request_id: str = ""
    created_at: str = ""


@dataclass
class SafetyGate:
    gate_id: str
    condition: str  # amplitude_limit, charge_limit, frequency_limit, duration_limit, electrode_check, approval_check
    passed: bool = False
    actual_value: float = 0.0
    limit_value: float = 0.0
    message: str = ""


class ClosedLoopController:
    """Safe closed-loop controller with mandatory safety gates."""

    def __init__(self, project_root: str | Path = "."):
        self.root = Path(project_root)
        self.actuation_enabled: bool = False
        self.active_protocol: StimulationProtocol | None = None
        self.safety_gates: list[SafetyGate] = []
        self.audit_log: list[dict[str, Any]] = []
        self.kill_switch_armed: bool = True
        self.session_id: str = ""

    def arm_kill_switch(self) -> None:
        """Arm the kill switch — must be called before any actuation."""
        self.kill_switch_armed = True
        self.actuation_enabled = False
        self._log("kill_switch_armed")

    def trigger_kill_switch(self, reason: str = "manual") -> None:
        """Immediately stop all actuation."""
        self.actuation_enabled = False
        self.active_protocol = None
        self._log("kill_switch_triggered", {"reason": reason})

    def load_protocol(self, protocol: StimulationProtocol, approval_verified: bool = False) -> list[SafetyGate]:
        """Load and validate a stimulation protocol. Returns safety gate results."""
        gates = self._validate_protocol(protocol, approval_verified)
        self.safety_gates = gates
        all_passed = all(g.passed for g in gates)

        if all_passed and approval_verified and self.kill_switch_armed:
            self.active_protocol = protocol
            self.actuation_enabled = True
            self._log("protocol_loaded", {"protocol": protocol.protocol_id, "gates_passed": len(gates)})
        else:
            self.active_protocol = None
            self.actuation_enabled = False
            self._log("protocol_rejected", {"protocol": protocol.protocol_id, "gates_passed": sum(1 for g in gates if g.passed), "gates_failed": sum(1 for g in gates if not g.passed)})

        return gates

    def _validate_protocol(self, protocol: StimulationProtocol, approval_verified: bool) -> list[SafetyGate]:
        """Run all safety gates against the protocol."""
        gates: list[SafetyGate] = []
        limits = protocol.safety_limits

        # Absolute maximum limits (Shannon safety limits for neural stimulation)
        ABS_MAX_AMPLITUDE_UA = 100.0
        ABS_MAX_CHARGE_NC = 200.0
        ABS_MAX_FREQUENCY_HZ = 500.0
        ABS_MAX_DURATION_S = 3600.0

        # Gate 1: Amplitude limit
        amp_ok = protocol.max_amplitude_ua <= min(limits.get("max_amplitude_ua", ABS_MAX_AMPLITUDE_UA), ABS_MAX_AMPLITUDE_UA)
        gates.append(SafetyGate("amp_limit", "amplitude_limit", amp_ok, protocol.max_amplitude_ua, ABS_MAX_AMPLITUDE_UA, "Amplitude within limits" if amp_ok else f"Amplitude {protocol.max_amplitude_ua}uA exceeds limit"))

        # Gate 2: Charge limit
        charge_ok = protocol.max_charge_per_phase_nc <= min(limits.get("max_charge_nc", ABS_MAX_CHARGE_NC), ABS_MAX_CHARGE_NC)
        gates.append(SafetyGate("charge_limit", "charge_limit", charge_ok, protocol.max_charge_per_phase_nc, ABS_MAX_CHARGE_NC, "Charge within Shannon limits" if charge_ok else f"Charge {protocol.max_charge_per_phase_nc}nC exceeds limit"))

        # Gate 3: Frequency limit
        freq_ok = protocol.max_frequency_hz <= min(limits.get("max_frequency_hz", ABS_MAX_FREQUENCY_HZ), ABS_MAX_FREQUENCY_HZ)
        gates.append(SafetyGate("freq_limit", "frequency_limit", freq_ok, protocol.max_frequency_hz, ABS_MAX_FREQUENCY_HZ, "Frequency within limits" if freq_ok else f"Frequency {protocol.max_frequency_hz}Hz exceeds limit"))

        # Gate 4: Duration limit
        dur_ok = protocol.max_duration_seconds <= min(limits.get("max_duration_s", ABS_MAX_DURATION_S), ABS_MAX_DURATION_S)
        gates.append(SafetyGate("duration_limit", "duration_limit", dur_ok, protocol.max_duration_seconds, ABS_MAX_DURATION_S, "Duration within limits" if dur_ok else f"Duration {protocol.max_duration_seconds}s exceeds limit"))

        # Gate 5: Electrode check
        elec_ok = protocol.electrode_count > 0 and len(protocol.electrode_ids) == protocol.electrode_count
        gates.append(SafetyGate("electrode_check", "electrode_check", elec_ok, protocol.electrode_count, 512, "Electrode configuration valid" if elec_ok else "Electrode count mismatch"))

        # Gate 6: Approval check
        gates.append(SafetyGate("approval_check", "approval_check", approval_verified, 1.0, 1.0, "Lab approval verified" if approval_verified else "Lab approval required before actuation"))

        # Gate 7: Kill switch
        gates.append(SafetyGate("kill_switch", "kill_switch_armed", self.kill_switch_armed, 1.0, 1.0, "Kill switch armed" if self.kill_switch_armed else "Kill switch must be armed"))

        return gates

    def actuate(self, amplitude_ua: float, electrode_id: int) -> dict[str, Any]:
        """Attempt actuation. Returns result with safety status."""
        if not self.actuation_enabled or not self.active_protocol:
            return {"actuated": False, "reason": "Actuation not enabled or no active protocol", "safety_ok": False}

        if not self.kill_switch_armed:
            self.trigger_kill_switch("kill_switch_disarmed")
            return {"actuated": False, "reason": "Kill switch disarmed", "safety_ok": False}

        # Real-time safety check
        if amplitude_ua > self.active_protocol.max_amplitude_ua:
            return {"actuated": False, "reason": f"Amplitude {amplitude_ua}uA exceeds protocol limit {self.active_protocol.max_amplitude_ua}uA", "safety_ok": False}

        if electrode_id not in self.active_protocol.electrode_ids:
            return {"actuated": False, "reason": f"Electrode {electrode_id} not in approved list", "safety_ok": False}

        # Log actuation
        self._log("actuation", {"amplitude_ua": amplitude_ua, "electrode_id": electrode_id, "protocol": self.active_protocol.protocol_id})
        return {"actuated": True, "safety_ok": True, "amplitude_ua": amplitude_ua, "electrode_id": electrode_id}

    def stop_session(self) -> None:
        """End the closed-loop session."""
        self.actuation_enabled = False
        self.active_protocol = None
        self.kill_switch_armed = False
        self._log("session_stopped")
        self._save_audit()

    def _log(self, event: str, data: dict[str, Any] | None = None) -> None:
        self.audit_log.append({
            "event": event,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": data or {},
        })

    def _save_audit(self) -> None:
        audit_path = self.root / "data" / "production" / "closed_loop_audit.jsonl"
        with audit_path.open("a", encoding="utf-8") as f:
            for entry in self.audit_log:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        self.audit_log.clear()
