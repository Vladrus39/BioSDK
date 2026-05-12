from __future__ import annotations
from typing import Any
import numpy as np
from biogpu.schemas import StimPattern, SpikeTrain
from biogpu.substrates.base import ComputeSubstrateAdapter

class SimulatedMEA(ComputeSubstrateAdapter):
    """Simulation of an MEA-connected living-like reservoir.

    v0.3 adds more explicit reservoir dynamics: recurrent strength, input strength,
    slow memory trace, optional plastic gain adaptation, and state reset. This is
    still an engineering emulator, not a biological model.
    """

    def __init__(self, seed: int = 42, **config: Any):
        self.seed = int(seed)
        self.rng = np.random.default_rng(self.seed)
        self.connected = False
        self.config: dict[str, Any] = {}
        self.last_pattern: StimPattern | None = None
        self.state: np.ndarray | None = None
        self.trace: np.ndarray | None = None
        self.last_input: np.ndarray | None = None
        self.W: np.ndarray | None = None
        self.input_projection: np.ndarray | None = None
        self.configure(config)

    def connect(self) -> None:
        self.connected = True

    def reset_state(self) -> None:
        n = int(self.config["reservoir_units"])
        self.state = np.zeros(n, dtype=np.float32)
        self.trace = np.zeros(n, dtype=np.float32)
        self.last_input = np.zeros(n, dtype=np.float32)

    def configure(self, config: dict[str, Any]) -> None:
        defaults = {
            "num_electrodes": 256,
            "reservoir_units": 256,
            "connectivity_density": 0.06,
            "noise_level": 0.035,
            "spontaneous_rate": 0.008,
            "latency_mean": 2.0,
            "latency_std": 0.5,
            "burst_probability": 0.015,
            "state_decay": 0.88,
            "trace_decay": 0.96,
            "gain": 1.35,
            "recurrent_strength": 0.85,
            "input_strength": 1.25,
            "trace_strength": 0.35,
            "plasticity_strength": 0.0,
            "readout_temperature": 3.0,
        }
        defaults.update(config or {})
        self.config = defaults
        n = int(self.config["reservoir_units"])
        density = float(self.config["connectivity_density"])
        mask = self.rng.random((n, n)) < density
        W = self.rng.normal(0.0, 0.45, size=(n, n)) * mask
        # Spectral-ish stabilization: enough recurrence for memory, not explosion.
        row_scale = max(1.0, np.sqrt(np.sum(mask, axis=1).mean() + 1e-6))
        W = W / row_scale
        self.W = W.astype(np.float32)
        # Deterministic random projection from electrode space into reservoir space.
        e = int(self.config["num_electrodes"])
        P = self.rng.normal(0.0, 1.0 / max(1.0, np.sqrt(e)), size=(n, e)).astype(np.float32)
        # Keep a partial topographic imprint. If the encoder uses four V1 orientation
        # banks (common case: electrodes = 4 * spatial pixels), preserve bank identity
        # by mapping each bank into a different reservoir quadrant. This prevents
        # orientation-bank collisions when the reservoir has fewer units than electrodes.
        if e >= 4 and n >= 4 and e % 4 == 0:
            bank_size = e // 4
            group_size = max(1, n // 4)
            for ch in range(e):
                bank = min(3, ch // bank_size)
                pos = ch % bank_size
                unit = min(n - 1, bank * group_size + (pos % group_size))
                P[unit, ch] += 1.0
        else:
            for i in range(min(e, n)):
                P[i, i] += 1.0
        self.input_projection = P
        self.reset_state()

    def _pattern_to_input(self, pattern: StimPattern) -> np.ndarray:
        e = int(self.config["num_electrodes"])
        electrode_vec = np.zeros(e, dtype=np.float32)
        for ch, inten in zip(pattern.channels, pattern.intensities):
            electrode_vec[int(ch) % e] += float(inten)
        electrode_vec = np.tanh(electrode_vec)
        assert self.input_projection is not None
        inp = self.input_projection @ electrode_vec
        if np.max(np.abs(inp)) > 0:
            inp = inp / (np.max(np.abs(inp)) + 1e-6)
        return inp.astype(np.float32)

    def send_stimulation(self, pattern: StimPattern) -> None:
        if not self.connected:
            self.connect()
        self.last_pattern = pattern
        assert self.state is not None and self.trace is not None and self.W is not None
        inp = self._pattern_to_input(pattern)
        self.last_input = inp.copy()
        noise = self.rng.normal(0, float(self.config["noise_level"]), size=inp.shape[0]).astype(np.float32)
        decay = float(self.config["state_decay"])
        trace_decay = float(self.config["trace_decay"])
        gain = float(self.config["gain"])
        recurrent_strength = float(self.config["recurrent_strength"])
        input_strength = float(self.config["input_strength"])
        trace_strength = float(self.config["trace_strength"])
        drive = recurrent_strength * (self.W @ self.state) + input_strength * inp + trace_strength * self.trace + noise
        new_state = np.tanh(gain * drive).astype(np.float32)
        self.state = decay * self.state + (1.0 - decay) * new_state
        self.trace = trace_decay * self.trace + (1.0 - trace_decay) * np.maximum(0.0, self.state)
        # Tiny optional Hebbian-like gain adaptation, disabled by default.
        p = float(self.config.get("plasticity_strength", 0.0))
        if p > 0 and self.rng.random() < 0.25:
            outer = np.outer(np.maximum(0.0, self.state), np.maximum(0.0, self.state))
            self.W = (1.0 - p) * self.W + p * outer.astype(np.float32) / max(1.0, float(np.linalg.norm(outer)))

    def read_spikes(self, window_ms: float = 20.0) -> SpikeTrain:
        if self.last_pattern is None:
            return SpikeTrain(unit_ids=[], spike_times=[], metadata={"empty": True})
        assert self.state is not None and self.trace is not None
        n = self.state.shape[0]
        last_input = self.last_input if self.last_input is not None else np.zeros(n, dtype=np.float32)
        temperature = float(self.config.get("readout_temperature", 3.0))
        state_drive = 1.0 / (1.0 + np.exp(-temperature * self.state))
        trace_drive = np.clip(self.trace, 0.0, 1.0)
        input_drive = np.clip(np.maximum(0.0, last_input), 0.0, 1.0)
        probs = 0.13 * input_drive + 0.075 * state_drive + 0.055 * trace_drive + float(self.config["spontaneous_rate"])
        if self.rng.random() < float(self.config["burst_probability"]):
            probs *= 2.25
        probs = np.clip(probs, 0.0, 0.85)
        spikes_mask = self.rng.random(n) < probs
        unit_ids = np.nonzero(spikes_mask)[0].astype(int).tolist()
        lat_mu = float(self.config["latency_mean"])
        lat_std = float(self.config["latency_std"])
        times = np.clip(self.rng.normal(lat_mu, lat_std, size=len(unit_ids)), 0.0, window_ms).astype(float).tolist()
        amps = np.abs(self.state[unit_ids]).astype(float).tolist() if unit_ids else []
        return SpikeTrain(
            unit_ids=unit_ids,
            spike_times=times,
            amplitudes=amps,
            metadata={"substrate": "SimulatedMEA", "window_ms": window_ms, "num_units": n, "version": "v0.3"},
        )

    def health_check(self) -> dict[str, Any]:
        return {"connected": self.connected, "type": "SimulatedMEA", "config": self.config}

    def close(self) -> None:
        self.connected = False
