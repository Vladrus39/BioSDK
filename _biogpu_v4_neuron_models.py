"""BioGPU v4.0 — Neuron Model Comparison: LIF vs Izhikevich vs AdEx.

Implements three neuron models within the same BioReservoir framework
(same connectivity, input projection, readout) and compares them on
4-MEA and 42-MEA temporal classification.

Models:
  LIF — Leaky Integrate-and-Fire (simplest, 1 ODE)
  Izhikevich — 2 ODEs, 4 types, richer dynamics
  AdEx — Adaptive Exponential (2 ODEs, smooth spike onset)
"""
import sys, time, gc, json, copy
sys.path.insert(0, '.')
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import warnings
warnings.filterwarnings("ignore")

BASE = Path(r"C:\Users\vladi\Desktop\Braine\BiC OS\biogpu-core-v5_0_bic_os_first_mover_roadmap")
OUT_DIR = BASE / "outputs" / "v4_bio_sweep"
OUT_DIR.mkdir(parents=True, exist_ok=True)
now = datetime.now(timezone.utc).isoformat()

print("=" * 70)
print("BioGPU v4.0 — Neuron Model Comparison")
print(f"LIF vs Izhikevich vs AdEx")
print(f"Started: {now}")
print("=" * 70)

from biogpu.apis.mock_finalspark_api import SpikeEventCache
from biogpu.substrates.bio_reservoir_v40 import BioReservoirV40
from biogpu.runtime.v3_biogpu_runtime import _window_to_stim_pattern
from sklearn.linear_model import RidgeClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold, cross_val_score


# ── LIF Reservoir ────────────────────────────────────────────────────

class LIFReservoirV40(BioReservoirV40):
    """Leaky Integrate-and-Fire reservoir — replaces Izhikevich dynamics."""

    def __init__(self, seed=42, **config):
        # Set LIF-specific defaults before parent init
        lif_defaults = {
            "tau_m": 20.0,        # membrane time constant (ms)
            "v_rest": -65.0,      # resting potential (mV)
            "v_threshold": -50.0,  # spike threshold (mV)
            "v_reset": -70.0,     # reset potential (mV)
            "refractory_ms": 2.0,  # absolute refractory period
        }
        merged = {**lif_defaults, **config}
        super().__init__(seed=seed, **merged)

    def _step(self, I_ext=None):
        """LIF dynamics: tau_m * dv/dt = -(v - v_rest) + I."""
        assert self.v is not None and self.u is not None and self.W is not None
        n = self.n_units

        I = self._input_current if I_ext is None else I_ext
        I_recurrent = self.W @ self.fired.astype(np.float32)
        noise = self.rng.normal(0, float(self.config.get("noise_current", 2.0)), size=n).astype(np.float32)
        I_total = I + I_recurrent + noise

        tau_m = float(self.config.get("tau_m", 20.0))
        v_rest = float(self.config.get("v_rest", -65.0))
        dt = float(self.config["timestep_ms"])

        # LIF voltage update
        dv = (-(self.v - v_rest) + I_total) / tau_m
        self.v += dv * dt

        # Spike detection
        v_thr = float(self.config.get("v_threshold", -50.0))
        self.fired = self.v >= v_thr
        spiking_units = np.where(self.fired)[0]

        if len(spiking_units) > 0:
            v_reset = float(self.config.get("v_reset", -70.0))
            self.v[spiking_units] = v_reset

            for uid in spiking_units:
                self.accumulated_spikes[int(uid)].append(self._t_ms)

            if self.config.get("stdp_enabled", True):
                self._apply_stdp(spiking_units)

        self._t_ms += dt
        return spiking_units


# ── AdEx Reservoir ───────────────────────────────────────────────────

class AdExReservoirV40(BioReservoirV40):
    """Adaptive Exponential integrate-and-fire reservoir."""

    def __init__(self, seed=42, **config):
        adex_defaults = {
            "C": 281.0,           # membrane capacitance (pF)
            "g_L": 30.0,          # leak conductance (nS)
            "E_L": -70.6,         # leak reversal (mV)
            "delta_T": 2.0,       # slope factor (mV)
            "V_T": -50.4,         # threshold (mV)
            "tau_w": 144.0,       # adaptation time constant (ms)
            "a": 4.0,             # subthreshold adaptation (nS)
            "b": 0.0805,          # spike-triggered adaptation (nA)
            "V_reset": -70.6,     # reset potential (mV)
            "v_threshold": -30.0, # spike detection threshold
        }
        merged = {**adex_defaults, **config}
        super().__init__(seed=seed, **merged)
        self.w = None  # adaptation current

    def reset_state(self):
        super().reset_state()
        self.w = np.zeros(self.n_units, dtype=np.float32)

    def _step(self, I_ext=None):
        """AdEx dynamics.

        C * dv/dt = -g_L*(v - E_L) + g_L*delta_T*exp((v - V_T)/delta_T) - w + I
        tau_w * dw/dt = a*(v - E_L) - w
        """
        assert self.v is not None and self.W is not None
        n = self.n_units

        I = self._input_current if I_ext is None else I_ext
        I_recurrent = self.W @ self.fired.astype(np.float32)
        noise = self.rng.normal(0, float(self.config.get("noise_current", 2.0)), size=n).astype(np.float32)
        I_total = I + I_recurrent + noise

        C = float(self.config.get("C", 281.0))
        g_L = float(self.config.get("g_L", 30.0))
        E_L = float(self.config.get("E_L", -70.6))
        delta_T = float(self.config.get("delta_T", 2.0))
        V_T = float(self.config.get("V_T", -50.4))
        tau_w = float(self.config.get("tau_w", 144.0))
        a = float(self.config.get("a", 4.0))
        b_spike = float(self.config.get("b", 0.0805))
        dt = float(self.config["timestep_ms"])

        # AdEx voltage update
        exp_term = g_L * delta_T * np.exp((self.v - V_T) / delta_T)
        dv = (-g_L * (self.v - E_L) + exp_term - self.w + I_total) / C
        self.v += dv * dt

        # Adaptation update
        dw = (a * (self.v - E_L) - self.w) / tau_w
        self.w += dw * dt

        # Spike detection
        v_peak = float(self.config.get("v_threshold", -30.0))
        self.fired = self.v >= v_peak
        spiking_units = np.where(self.fired)[0]

        if len(spiking_units) > 0:
            V_reset = float(self.config.get("V_reset", -70.6))
            self.v[spiking_units] = V_reset
            self.w[spiking_units] += b_spike

            for uid in spiking_units:
                self.accumulated_spikes[int(uid)].append(self._t_ms)

            if self.config.get("stdp_enabled", True):
                self._apply_stdp(spiking_units)

        self._t_ms += dt
        return spiking_units


# ── Data Loading ─────────────────────────────────────────────────────

print("\n[1] Loading spike cache...")
cache = SpikeEventCache()
cache.load_from_cache(max_files=42)
all_mea_ids = sorted(cache._index.keys(), key=lambda x: int(x.split("_")[1]))
print(f"  {len(all_mea_ids)} MEAs, {cache.stats()['total_spikes']} spikes")

def build_sequences(mea_ids):
    seqs, labs = [], []
    for mea_idx, mea_id in enumerate(mea_ids):
        spikes = cache.get_spike_events(mea_id, duration_s=3600.0)
        if not spikes:
            continue
        n_bins = int(3600.0 * 1000 / 10)
        rate = np.zeros((8, n_bins), dtype=np.float32)
        for ch, ts_ms in spikes:
            if 0 <= ch < 8:
                bi = int(ts_ms / 10)
                if 0 <= bi < n_bins:
                    rate[ch, bi] += 1
        rate *= 100
        windows = [rate[:, s:s+100].astype(np.float32) for s in range(0, n_bins-100, 100)]
        for ss in range(0, len(windows)-20, 20):
            seqs.append((mea_id, windows[ss:ss+20]))
            labs.append(mea_idx)
        del rate, windows
    return seqs, np.array(labs, dtype=np.int32)


def run_reservoir(reservoir_cls, seqs, y, cv, name, **config):
    """Build reservoir, process sequences, return CV scores."""
    print(f"\n  {name}:")
    t0 = time.time()
    r = reservoir_cls(seed=42, **config)
    states = []
    for mea_id, seq_wins in seqs:
        r.reset_state()
        for win in seq_wins:
            n_units = config.get("reservoir_units", 128)
            stim = _window_to_stim_pattern(win, "w", num_electrodes=n_units)
            r.send_stimulation(stim)
            for _ in range(20):
                r._step()
        rates = r.get_firing_rates(window_ms=20000.0)
        states.append(rates.copy())
    r.close()
    dt = time.time() - t0
    X = np.array(states, dtype=np.float32)
    X_s = StandardScaler().fit_transform(X)
    scores = cross_val_score(RidgeClassifier(alpha=1.0, random_state=42),
                             X_s, y, cv=cv, scoring="balanced_accuracy")
    ba, std = round(float(scores.mean()), 4), round(float(scores.std()), 4)
    print(f"    BA={ba:.4f} +/- {std:.4f} ({dt:.1f}s)")
    return {"name": name, "ba": ba, "std": std, "time_s": round(dt, 1),
            "units": config.get("reservoir_units", 128)}


# ── Run Comparison ───────────────────────────────────────────────────

# Test on 4-MEA first (fast)
print("\n[2] 4-MEA comparison...")
seq4, y4 = build_sequences(all_mea_ids[:4])
cv4 = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
chance4 = 1.0 / 4

# Common config for fair comparison
base_config = {
    "reservoir_units": 128,
    "connectivity_degree": 10,
    "rewiring_probability": 0.1,
    "input_scale": 5.0,
    "stdp_enabled": True,
    "stdp_a_plus": 0.01,
    "stdp_a_minus": 0.012,
    "neuron_types": {"RS": 0.5, "IB": 0.2, "CH": 0.1, "FS": 0.2},
}

results_4mea = []
results_4mea.append(run_reservoir(BioReservoirV40, seq4, y4, cv4,
                                   "Izhikevich (4 types)", **base_config))

# LIF doesn't use neuron_types — override
lif_config = {**base_config}
lif_config.pop("neuron_types", None)
results_4mea.append(run_reservoir(LIFReservoirV40, seq4, y4, cv4,
                                   "LIF", **lif_config))

# AdEx doesn't use neuron_types either
adex_config = {**base_config}
adex_config.pop("neuron_types", None)
results_4mea.append(run_reservoir(AdExReservoirV40, seq4, y4, cv4,
                                   "AdEx", **adex_config))

print(f"\n  4-MEA Summary (chance={chance4:.4f}):")
for r in sorted(results_4mea, key=lambda x: x["ba"], reverse=True):
    print(f"    {r['name']:25s}: BA={r['ba']:.4f} +/- {r['std']:.4f} ({r['time_s']:.1f}s)")

# ── 42-MEA ───────────────────────────────────────────────────────────
print("\n[3] 42-MEA comparison...")
seq42, y42 = build_sequences(all_mea_ids)
cv42 = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
chance42 = 1.0 / 42

results_42mea = []
results_42mea.append(run_reservoir(BioReservoirV40, seq42, y42, cv42,
                                    "Izhikevich (4 types)", **base_config))
results_42mea.append(run_reservoir(LIFReservoirV40, seq42, y42, cv42,
                                    "LIF", **lif_config))
results_42mea.append(run_reservoir(AdExReservoirV40, seq42, y42, cv42,
                                    "AdEx", **adex_config))

print(f"\n  42-MEA Summary (chance={chance42:.4f}):")
for r in sorted(results_42mea, key=lambda x: x["ba"], reverse=True):
    vs_chance = r["ba"] / chance42
    print(f"    {r['name']:25s}: BA={r['ba']:.4f} +/- {r['std']:.4f} ({r['time_s']:.1f}s, {vs_chance:.1f}x chance)")

# ── Save ─────────────────────────────────────────────────────────────
final = {
    "benchmark": "biogpu_v40_neuron_model_comparison",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "models_compared": ["Izhikevich", "LIF", "AdEx"],
    "config": base_config,
    "results_4mea": results_4mea,
    "results_42mea": results_42mea,
    "chance_4mea": chance4,
    "chance_42mea": chance42,
}

with open(OUT_DIR / "V4_MODEL_COMPARISON.json", "w") as f:
    json.dump(final, f, indent=2)
print(f"\nResults: {OUT_DIR / 'V4_MODEL_COMPARISON.json'}")
print("Done.")
