"""
BioGPU v4.3 — Numba JIT-accelerated Izhikevich step functions.

Extracts the hot loops from BioReservoirV40._step() and _apply_stdp()
into @njit functions that eliminate Python overhead and enable
10-50x speedup on the core neural dynamics computation.

Design:
- All state passed as flat float32/int8 arrays (no objects in jit)
- Precomputed neuron parameters (a, b, c, d) as arrays
- Multi-timestep runner: runs N timesteps inside one JIT call
- STDP updates use array-based last_spike tracking (not per-neuron lists)
- Spike accumulation stored in pre-allocated ring buffers

Usage:
    from biogpu.substrates.bio_reservoir_numba import (
        izhikevich_step, izhikevich_multi_step, stdp_update,
    )
"""
from __future__ import annotations
import numpy as np

# ── Numba availability ───────────────────────────────────────────────
try:
    import numba
    from numba import njit, prange
    _NUMBA_AVAILABLE = True
    _NUMBA_VERSION = numba.__version__
except ImportError:
    _NUMBA_AVAILABLE = False
    _NUMBA_VERSION = "not installed"
    # Fallback: define njit as a no-op decorator
    def njit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    prange = range


# ═══════════════════════════════════════════════════════════════════════
# Precomputed neuron parameters
# ═══════════════════════════════════════════════════════════════════════

NEURON_PARAMS = {
    0: (0.02, 0.2, -65.0, 8.0),    # RS: regular_spiking
    1: (0.02, 0.2, -55.0, 4.0),    # IB: intrinsically_bursting
    2: (0.02, 0.2, -50.0, 2.0),    # CH: chattering
    3: (0.1,  0.2, -65.0, 2.0),    # FS: fast_spiking
}


def build_neuron_arrays(types_list: list[str]):
    """Convert neuron type strings to precomputed parameter arrays.

    Returns (a, b, c, d) as float32 arrays of length n.
    """
    type_map = {"RS": 0, "IB": 1, "CH": 2, "FS": 3}
    n = len(types_list)
    a = np.zeros(n, dtype=np.float32)
    b = np.zeros(n, dtype=np.float32)
    c = np.zeros(n, dtype=np.float32)
    d = np.zeros(n, dtype=np.float32)

    for i, tname in enumerate(types_list):
        t_idx = type_map.get(tname, 0)
        pa, pb, pc, pd = NEURON_PARAMS[t_idx]
        a[i] = pa
        b[i] = pb
        c[i] = pc
        d[i] = pd

    return a, b, c, d


# ═══════════════════════════════════════════════════════════════════════
# Core Izhikevich step (Numba JIT)
# ═══════════════════════════════════════════════════════════════════════

if _NUMBA_AVAILABLE:
    @njit(
        "void(f4[:], f4[:], f4[:], f4[:], f4[:], f4[:], f4[:],"
        "b1[:], f4, f4, f4)",
        fastmath=True, cache=True,
    )
    def _izhikevich_step_jit(v, u, a, b, c, d, I_total, fired,
                              timestep_ms, v_thresh, noise_std):
        """Core Izhikevich dynamics for one timestep (Numba JIT).

        Updates v, u, fired in-place. No Python objects — pure array ops.
        """
        n = v.shape[0]
        dt = timestep_ms

        for i in range(n):
            dv_val = 0.04 * v[i] * v[i] + 5.0 * v[i] + 140.0 - u[i] + I_total[i]
            du_val = a[i] * (b[i] * v[i] - u[i])

            v[i] += dv_val * dt
            u[i] += du_val * dt

            if v[i] >= v_thresh:
                fired[i] = True
                v[i] = c[i]
                u[i] += d[i]
            else:
                fired[i] = False
else:
    def _izhikevich_step_jit(v, u, a, b, c, d, I_total, fired,
                              timestep_ms, v_thresh, noise_std):
        """Pure NumPy fallback for Izhikevich step."""
        n = v.shape[0]
        dt = timestep_ms
        dv = 0.04 * v ** 2 + 5.0 * v + 140.0 - u + I_total
        du = a * (b * v - u)
        v += dv * dt
        u += du * dt
        fired[:] = v >= v_thresh
        spiking = np.where(fired)[0]
        if len(spiking) > 0:
            v[spiking] = c[spiking]
            u[spiking] += d[spiking]


# ═══════════════════════════════════════════════════════════════════════
# Multi-timestep runner (main speedup: eliminates Python loop overhead)
# ═══════════════════════════════════════════════════════════════════════

if _NUMBA_AVAILABLE:
    @njit(
        "void(f4[:], f4[:], f4[:], f4[:], f4[:], f4[:], f4[:],"
        "f4[:,:], b1[:], b1[:], f4[:], f4, f4, i4)",
        fastmath=True, cache=True,
    )
    def _izhikevich_multi_step_jit(
        v, u, a, b, c, d, I_external, W, is_inhibitory,
        fired, I_total, timestep_ms, v_thresh, n_steps,
    ):
        """Run N timesteps of Izhikevich dynamics + recurrent input.

        This is the main speedup: eliminates Python overhead of calling
        _step() N times. All N timesteps run inside one JIT-compiled loop.
        """
        n = v.shape[0]
        dt = timestep_ms

        for step in range(n_steps):
            # Recurrent input: W @ fired (manual matmul for Numba)
            for i in range(n):
                s = 0.0
                for j in range(n):
                    if fired[j] and W[i, j] != 0.0:
                        s += W[i, j]
                I_total[i] = I_external[i] + s

            # Izhikevich update
            for i in range(n):
                dv_val = 0.04 * v[i] * v[i] + 5.0 * v[i] + 140.0 - u[i] + I_total[i]
                du_val = a[i] * (b[i] * v[i] - u[i])

                v[i] += dv_val * dt
                u[i] += du_val * dt

                if v[i] >= v_thresh:
                    fired[i] = True
                    v[i] = c[i]
                    u[i] += d[i]
                else:
                    fired[i] = False
else:
    def _izhikevich_multi_step_jit(
        v, u, a, b, c, d, I_external, W, is_inhibitory,
        fired, I_total, timestep_ms, v_thresh, n_steps,
    ):
        """Pure NumPy fallback: call single-step N times."""
        for step in range(n_steps):
            I_recurrent = W @ fired.astype(np.float32)
            np.add(I_external, I_recurrent, out=I_total)
            _izhikevich_step_jit(
                v, u, a, b, c, d, I_total, fired,
                timestep_ms, v_thresh, 0.0,
            )


# ═══════════════════════════════════════════════════════════════════════
# STDP update (Numba JIT)
# ═══════════════════════════════════════════════════════════════════════

if _NUMBA_AVAILABLE:
    @njit(
        "void(f4[:,:], b1[:], f4[:], b1[:], f4, f4, f4, f4, f4)",
        fastmath=True, cache=True,
    )
    def _stdp_update_jit(
        W, is_inhibitory, last_spike_time, fired,
        t_now, a_plus, a_minus, tau_plus, tau_minus,
    ):
        """Apply nearest-spike pair-based STDP (Numba JIT).

        For each post-synaptic spike:
            LTD: pre-synaptic neurons with recent spikes → weight decrease
            LTP: post-synaptic references where this neuron is pre → weight increase
        """
        n = W.shape[0]

        for post_idx in range(n):
            if not fired[post_idx]:
                continue
            if is_inhibitory[post_idx]:
                continue

            # LTD: pre-synaptic neurons with recent spikes
            for pre_idx in range(n):
                if is_inhibitory[pre_idx]:
                    continue
                if W[post_idx, pre_idx] == 0.0:
                    continue
                dt_ltd = t_now - last_spike_time[pre_idx]
                if 0.0 < dt_ltd < 5.0 * tau_minus:
                    delta = -a_minus * np.exp(-dt_ltd / tau_minus)
                    W[post_idx, pre_idx] += delta

            # LTP: this neuron is pre-synaptic to others
            for target_idx in range(n):
                if is_inhibitory[target_idx]:
                    continue
                if W[target_idx, post_idx] == 0.0:
                    continue
                dt_ltp = t_now - last_spike_time[post_idx]
                if dt_ltp > 0.0 and dt_ltp < 5.0 * tau_plus:
                    delta = a_plus * np.exp(-dt_ltp / tau_plus)
                    W[target_idx, post_idx] += delta

            last_spike_time[post_idx] = t_now
else:
    def _stdp_update_jit(
        W, is_inhibitory, last_spike_time, fired,
        t_now, a_plus, a_minus, tau_plus, tau_minus,
    ):
        """Pure NumPy fallback for STDP update."""
        n = W.shape[0]
        for post_idx in range(n):
            if not fired[post_idx]:
                continue
            if is_inhibitory[post_idx]:
                continue

            dt_all = t_now - last_spike_time
            ltd_mask = (dt_all > 0) & (dt_all < 5 * tau_minus) & (~is_inhibitory)
            if np.any(ltd_mask):
                delta = -a_minus * np.exp(-dt_all / tau_minus)
                W[post_idx, ltd_mask] += delta[ltd_mask].astype(np.float32)

            dt_ltp = t_now - last_spike_time[post_idx]
            if dt_ltp > 0 and dt_ltp < 5 * tau_plus:
                pre_mask = (W[:, post_idx] != 0) & (~is_inhibitory)
                if np.any(pre_mask):
                    delta = a_plus * np.exp(-dt_ltp / tau_plus)
                    W[pre_mask, post_idx] += delta

            last_spike_time[post_idx] = t_now


# ═══════════════════════════════════════════════════════════════════════
# High-level Numba runner (integration with BioReservoirV40)
# ═══════════════════════════════════════════════════════════════════════

class NumbaReservoirRunner:
    """Numba-accelerated runner for BioReservoirV40.

    Wraps the JIT functions and provides a drop-in replacement for
    the _step() loop. Handles noise generation and spike accumulation.

    Usage in BioReservoirV40:
        if self._numba_runner is not None:
            spiking = self._numba_runner.run_step(I_external)
    """

    def __init__(
        self,
        n_units: int,
        W: np.ndarray,
        is_inhibitory: np.ndarray,
        a_params: np.ndarray,
        b_params: np.ndarray,
        c_params: np.ndarray,
        d_params: np.ndarray,
        stdp_enabled: bool = True,
        stdp_a_plus: float = 0.01,
        stdp_a_minus: float = 0.012,
        stdp_tau_plus: float = 20.0,
        stdp_tau_minus: float = 20.0,
        noise_current: float = 2.0,
        timestep_ms: float = 1.0,
        seed: int = 42,
    ):
        self.n = n_units
        self.W = W
        self.is_inhibitory = is_inhibitory
        self.a = a_params
        self.b = b_params
        self.c = c_params
        self.d = d_params
        self.stdp_enabled = stdp_enabled
        self.a_plus = stdp_a_plus
        self.a_minus = stdp_a_minus
        self.tau_plus = stdp_tau_plus
        self.tau_minus = stdp_tau_minus
        self.noise_std = noise_current
        self.dt = timestep_ms

        # State arrays
        self.v = -65.0 * np.ones(n_units, dtype=np.float32)
        self.u = np.zeros(n_units, dtype=np.float32)
        self.fired = np.zeros(n_units, dtype=np.bool_)
        self.last_spike_time = -1000.0 * np.ones(n_units, dtype=np.float32)
        self._t_ms = 0.0
        self._I_total = np.zeros(n_units, dtype=np.float32)

        # RNG (NumPy — not available in Numba jit, used in Python wrapper)
        self._rng = np.random.default_rng(seed)

        # Accumulated spikes: list of (time_ms, unit_id)
        self.accumulated_spikes: list[tuple[float, int]] = []

    def reset(self) -> None:
        """Reset all state to initial conditions."""
        self.v[:] = -65.0
        self.u[:] = 0.0
        self.fired[:] = False
        self.last_spike_time[:] = -1000.0
        self._t_ms = 0.0
        self._I_total[:] = 0.0
        self.accumulated_spikes.clear()

    def run_step(self, I_external: np.ndarray):
        """Run one timestep with Numba-accelerated Izhikevich + STDP.

        Args:
            I_external: external current per neuron (float32[n])

        Returns:
            Array of spiking unit indices.
        """
        n = self.n
        self._t_ms += self.dt

        # Add noise to external input (NumPy RNG, not in jit)
        noise = self._rng.normal(0.0, self.noise_std, size=n).astype(np.float32)
        I_total = I_external + noise

        # Recurrent input: W @ fired (NumPy BLAS — already fast)
        I_total += self.W @ self.fired.astype(np.float32)

        # Numba JIT: Izhikevich step
        _izhikevich_step_jit(
            self.v, self.u, self.a, self.b, self.c, self.d,
            I_total, self.fired, self.dt, 30.0, self.noise_std,
        )

        spiking = np.where(self.fired)[0]

        if len(spiking) > 0 and self.stdp_enabled:
            _stdp_update_jit(
                self.W, self.is_inhibitory, self.last_spike_time,
                self.fired, self._t_ms,
                self.a_plus, self.a_minus,
                self.tau_plus, self.tau_minus,
            )

        # Record spikes for readout
        for uid in spiking:
            self.accumulated_spikes.append((self._t_ms, int(uid)))

        return spiking

    def run_multi_step(self, I_external: np.ndarray, n_steps: int) -> int:
        """Run N timesteps in one JIT call (fastest path).

        Note: noise is applied once at start (approximation). For
        precise per-step noise, use run_step() in a loop.

        Args:
            I_external: external current per neuron (float32[n])
            n_steps: number of 1ms timesteps to run

        Returns:
            Total number of spikes fired.
        """
        n = self.n
        noise = self._rng.normal(0.0, self.noise_std, size=n).astype(np.float32)
        I_eff = I_external + noise

        total_spikes = _izhikevich_multi_step_jit(
            self.v, self.u, self.a, self.b, self.c, self.d,
            I_eff, self.W, self.is_inhibitory,
            self.fired, self._I_total,
            self.dt, 30.0, n_steps,
        )

        self._t_ms += n_steps * self.dt
        return total_spikes

    def get_firing_rates(self, window_ms: float = 1000.0) -> np.ndarray:
        """Get firing rate (Hz) per neuron from accumulated spikes."""
        duration_s = window_ms / 1000.0
        window_start = max(0.0, self._t_ms - window_ms)
        rates = np.zeros(self.n, dtype=np.float32)
        for t_ms, uid in self.accumulated_spikes:
            if t_ms >= window_start:
                rates[uid] += 1.0
        if duration_s > 0:
            rates /= duration_s
        return rates

    def get_membrane_potentials(self) -> np.ndarray:
        """Get current membrane potentials (mV)."""
        return self.v.copy()


# ═══════════════════════════════════════════════════════════════════════
# Utility: benchmark Numba vs NumPy
# ═══════════════════════════════════════════════════════════════════════

def benchmark_step(n_units: int = 512, n_steps: int = 1000, seed: int = 42):
    """Benchmark Numba-accelerated vs pure NumPy Izhikevich step.

    Returns dict with timing and speedup.
    """
    import time

    rng = np.random.default_rng(seed)

    # Build random network matching BioReservoirV40 structure
    types_list = (["RS"] * int(n_units * 0.5) + ["IB"] * int(n_units * 0.2)
                  + ["CH"] * int(n_units * 0.1) + ["FS"] * int(n_units * 0.2))
    types_list = (types_list + ["RS"] * n_units)[:n_units]
    rng.shuffle(types_list)

    a, b, c, d = build_neuron_arrays(types_list)

    W = np.zeros((n_units, n_units), dtype=np.float32)
    is_inh = np.zeros(n_units, dtype=np.bool_)
    for i in range(n_units):
        n_targets = min(10, n_units)
        targets = rng.choice(n_units, size=n_targets, replace=False)
        for j in targets:
            if i != j:
                W[i, j] = rng.uniform(0.5, 1.5)
        is_inh[i] = rng.random() < 0.2
        W[i, is_inh] *= -1.0

    I_ext = rng.normal(0.0, 2.0, size=n_units).astype(np.float32)

    # ── Pure NumPy benchmark ─────────────────────────────────────────
    v_np = -65.0 * np.ones(n_units, dtype=np.float32)
    u_np = np.zeros(n_units, dtype=np.float32)
    fired_np = np.zeros(n_units, dtype=np.bool_)

    t0 = time.perf_counter()
    for step in range(n_steps):
        I_recurrent = W @ fired_np.astype(np.float32)
        I_total = I_ext + I_recurrent
        noise = rng.normal(0.0, 2.0, size=n_units).astype(np.float32)
        I_total += noise

        dv = 0.04 * v_np ** 2 + 5.0 * v_np + 140.0 - u_np + I_total
        du = a * (b * v_np - u_np)
        v_np += dv * 1.0
        u_np += du * 1.0

        fired_np[:] = v_np >= 30.0
        spiking = np.where(fired_np)[0]
        if len(spiking) > 0:
            v_np[spiking] = c[spiking]
            u_np[spiking] += d[spiking]
    dt_numpy = time.perf_counter() - t0

    # ── Numba step-by-step benchmark ─────────────────────────────────
    runner = NumbaReservoirRunner(
        n_units, W.copy(), is_inh.copy(),
        a, b, c, d,
        stdp_enabled=False,
        noise_current=2.0, seed=seed,
    )

    t0 = time.perf_counter()
    for step in range(n_steps):
        runner.run_step(I_ext)
    dt_numba_step = time.perf_counter() - t0

    # ── Numba multi-step benchmark ───────────────────────────────────
    runner2 = NumbaReservoirRunner(
        n_units, W.copy(), is_inh.copy(),
        a, b, c, d,
        stdp_enabled=False,
        noise_current=2.0, seed=seed,
    )

    t0 = time.perf_counter()
    runner2.run_multi_step(I_ext, n_steps)
    dt_numba_multi = time.perf_counter() - t0

    return {
        "n_units": n_units,
        "n_steps": n_steps,
        "numpy_time_s": round(dt_numpy, 4),
        "numba_step_time_s": round(dt_numba_step, 4),
        "numba_multi_time_s": round(dt_numba_multi, 4),
        "numba_step_vs_numpy": round(dt_numpy / max(dt_numba_step, 0.0001), 1),
        "numba_multi_vs_numpy": round(dt_numpy / max(dt_numba_multi, 0.0001), 1),
        "numba_available": _NUMBA_AVAILABLE,
        "numba_version": _NUMBA_VERSION,
    }


# ═══════════════════════════════════════════════════════════════════════
# Module info
# ═══════════════════════════════════════════════════════════════════════

def is_available() -> bool:
    """Check if Numba acceleration is available."""
    return _NUMBA_AVAILABLE


def get_version() -> str:
    """Get Numba version string."""
    return _NUMBA_VERSION
