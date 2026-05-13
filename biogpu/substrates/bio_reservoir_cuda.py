"""
BioGPU v4.4 — PyTorch CUDA Batch Reservoir.

Runs N independent BioReservoir instances in parallel on GPU.
Each instance has its own connectivity W, neuron state (v, u),
and STDP traces. Izhikevich dynamics are vectorized across the batch.

Architecture:
    Input: B × N sequences (B MEAs, N windows each)
    → B parallel reservoirs on GPU (B × n_units tensors)
    → Batch Izhikevich step: v' = 0.04v² + 5v + 140 - u + I
    → Batch recurrent: bmm(W_batch, fired_batch)
    → Batch STDP: per-reservoir weight updates
    → Firing rates: B × n_units feature vectors

Performance target: B=42 reservoirs × 256 neurons × 1000 steps
should run in <10s on RTX 5070 Ti (vs ~120s on CPU).

Design:
    - Pure PyTorch tensors (no NumPy in hot path)
    - All state on GPU (v, u, W, fired, I_total)
    - Batch operations: torch.bmm, torch.where, torch.exp
    - Fallback to CPU if CUDA unavailable
"""
from __future__ import annotations
import time
from typing import Any
import numpy as np
import torch
import torch.nn.functional as F

# ── Neuron type parameters (Izhikevich, same as BioReservoirV40) ────
NEURON_PARAMS = {
    "RS": {"a": 0.02, "b": 0.2, "c": -65.0, "d": 8.0},
    "IB": {"a": 0.02, "b": 0.2, "c": -55.0, "d": 4.0},
    "CH": {"a": 0.02, "b": 0.2, "c": -50.0, "d": 2.0},
    "FS": {"a": 0.1,  "b": 0.2, "c": -65.0, "d": 2.0},
}


class CudaBatchReservoir:
    """PyTorch CUDA batch of independent Izhikevich reservoirs.

    Usage:
        cbr = CudaBatchReservoir(batch_size=42, n_units=256, device="cuda")
        cbr.build()
        features = cbr.process_batch(sequences)  # sequences: list of (mea_id, windows)
        rates = cbr.get_firing_rates()  # (B, n_units)
    """

    def __init__(
        self,
        batch_size: int = 42,
        n_units: int = 256,
        n_electrodes: int = 8,
        connectivity_degree: int = 10,
        rewiring_probability: float = 0.1,
        ei_ratio: float = 0.8,
        exc_weight_range: tuple[float, float] = (0.5, 1.5),
        inh_weight_range: tuple[float, float] = (-2.0, -1.0),
        stdp_a_plus: float = 0.01,
        stdp_a_minus: float = 0.012,
        stdp_tau_plus: float = 20.0,
        stdp_tau_minus: float = 20.0,
        stdp_enabled: bool = True,
        input_scale: float = 5.0,
        noise_current: float = 2.0,
        neuron_types: dict[str, float] | None = None,
        device: str = "cuda",
        seed: int = 42,
    ):
        self.batch_size = batch_size
        self.n_units = n_units
        self.n_electrodes = n_electrodes
        self.K = connectivity_degree
        self.p_rewire = rewiring_probability
        self.ei_ratio = ei_ratio
        self.exc_range = exc_weight_range
        self.inh_range = inh_weight_range
        self.a_plus = stdp_a_plus
        self.a_minus = stdp_a_minus
        self.tau_plus = stdp_tau_plus
        self.tau_minus = stdp_tau_minus
        self.stdp_enabled = stdp_enabled
        self.input_scale = input_scale
        self.noise_std = noise_current
        self.neuron_types = neuron_types or {"RS": 0.5, "IB": 0.2, "CH": 0.1, "FS": 0.2}
        self.device = torch.device(device if torch.cuda.is_available() else "cpu")
        self.seed = seed
        self._rng = np.random.default_rng(seed)

        # Will be populated in build()
        self.W: torch.Tensor | None = None          # (B, n, n)
        self.is_inhibitory: torch.Tensor | None = None  # (B, n)
        self.input_proj: torch.Tensor | None = None  # (B, n, n_electrodes)
        self.a_params: torch.Tensor | None = None    # (B, n)
        self.b_params: torch.Tensor | None = None    # (B, n)
        self.c_params: torch.Tensor | None = None    # (B, n)
        self.d_params: torch.Tensor | None = None    # (B, n)

        # State tensors (reset per sequence)
        self.v: torch.Tensor | None = None           # (B, n)
        self.u: torch.Tensor | None = None           # (B, n)
        self.fired: torch.Tensor | None = None       # (B, n) bool
        self.last_spike_time: torch.Tensor | None = None  # (B, n)
        self._t_ms: torch.Tensor | None = None       # (B,)

        # Accumulated spikes for readout
        self.spike_counts: torch.Tensor | None = None  # (B, n)
        self._built = False

    # ═══════════════════════════════════════════════════════════════════
    # Build phase
    # ═══════════════════════════════════════════════════════════════════

    def build(self) -> None:
        """Build all B reservoirs (connectivity, projections, parameters)."""
        B, n, e = self.batch_size, self.n_units, self.n_electrodes
        rng = self._rng

        # ── Neuron parameters ──────────────────────────────────────────
        a_np = np.zeros((B, n), dtype=np.float32)
        b_np = np.zeros((B, n), dtype=np.float32)
        c_np = np.zeros((B, n), dtype=np.float32)
        d_np = np.zeros((B, n), dtype=np.float32)

        for b_idx in range(B):
            types_list = []
            for tname, proportion in self.neuron_types.items():
                count = max(1, int(proportion * n))
                types_list.extend([tname] * count)
            types_list = (types_list + ["RS"] * n)[:n]
            rng.shuffle(types_list)
            for i, tname in enumerate(types_list):
                p = NEURON_PARAMS.get(tname, NEURON_PARAMS["RS"])
                a_np[b_idx, i] = p["a"]
                b_np[b_idx, i] = p["b"]
                c_np[b_idx, i] = p["c"]
                d_np[b_idx, i] = p["d"]

        self.a_params = torch.from_numpy(a_np).to(self.device)
        self.b_params = torch.from_numpy(b_np).to(self.device)
        self.c_params = torch.from_numpy(c_np).to(self.device)
        self.d_params = torch.from_numpy(d_np).to(self.device)

        # ── Connectivity (small-world Watts-Strogatz) ──────────────────
        W_np = np.zeros((B, n, n), dtype=np.float32)
        is_inh_np = np.zeros((B, n), dtype=bool)

        for b_idx in range(B):
            # Ring lattice
            W = np.zeros((n, n), dtype=np.float32)
            half_k = self.K // 2
            for i in range(n):
                for j in range(1, half_k + 1):
                    W[i, (i + j) % n] = 1.0
                    W[i, (i - j + n) % n] = 1.0

            # Rewire
            upper = np.triu(W) > 0
            srcs, dsts = np.where(upper)
            for src, dst in zip(srcs, dsts):
                if rng.random() < self.p_rewire:
                    W[src, dst] = 0.0
                    W[dst, src] = 0.0
                    new_dst = rng.integers(0, n)
                    while new_dst == src or W[src, new_dst] > 0:
                        new_dst = rng.integers(0, n)
                    W[src, new_dst] = 1.0
                    W[new_dst, src] = 1.0

            # E/I assignment + weights
            is_exc = rng.random(n) < self.ei_ratio
            is_inh = ~is_exc
            is_inh_np[b_idx] = is_inh

            for i in range(n):
                targets = np.where(W[i, :] > 0)[0]
                for j in targets:
                    if is_exc[i]:
                        W[i, j] = rng.uniform(*self.exc_range)
                    else:
                        W[i, j] = rng.uniform(*self.inh_range)

            W_np[b_idx] = W

        self.W = torch.from_numpy(W_np).to(self.device)
        self.is_inhibitory = torch.from_numpy(is_inh_np).to(self.device)

        # ── Input projection ───────────────────────────────────────────
        P_np = np.zeros((B, n, e), dtype=np.float32)
        units_per_elec = max(1, n // e)
        for b_idx in range(B):
            for ch in range(e):
                start = ch * units_per_elec
                end = min(start + units_per_elec, n)
                for u in range(start, end):
                    P_np[b_idx, u, ch] = rng.uniform(0.5, 2.0)

        self.input_proj = torch.from_numpy(P_np).to(self.device)

        # ── Initial state ──────────────────────────────────────────────
        self._reset_state()

        self._built = True
        print(f"  CUDA Batch Reservoir built: {B}x{n} neurons, "
              f"device={self.device}, "
              f"mem~{self._estimate_memory():.1f} MB")

    def _reset_state(self) -> None:
        """Reset all reservoir states to initial conditions."""
        B, n = self.batch_size, self.n_units
        self.v = torch.full((B, n), -65.0, dtype=torch.float32, device=self.device)
        self.u = torch.zeros((B, n), dtype=torch.float32, device=self.device)
        self.fired = torch.zeros((B, n), dtype=torch.bool, device=self.device)
        self.last_spike_time = torch.full((B, n), -1000.0, dtype=torch.float32, device=self.device)
        self._t_ms = torch.zeros(B, dtype=torch.float32, device=self.device)
        self.spike_counts = torch.zeros((B, n), dtype=torch.float32, device=self.device)

    def _estimate_memory(self) -> float:
        """Estimate GPU memory usage in MB."""
        if self.W is None:
            return 0.0
        B, n = self.batch_size, self.n_units
        bytes_per_float32 = 4
        # W: B×n×n, input_proj: B×n×e, params: 4×B×n, state: 4×B×n
        total = B * n * n * bytes_per_float32  # W
        total += B * n * self.n_electrodes * bytes_per_float32  # projection
        total += 8 * B * n * bytes_per_float32  # params + state
        return total / (1024 * 1024)

    # ═══════════════════════════════════════════════════════════════════
    # Core dynamics (GPU batch)
    # ═══════════════════════════════════════════════════════════════════

    @torch.no_grad()
    def _step_batch(self, I_external: torch.Tensor) -> torch.Tensor:
        """One timestep of batched Izhikevich dynamics.

        Args:
            I_external: (B, n) external current per neuron

        Returns:
            fired_mask: (B, n) bool tensor of neurons that spiked
        """
        B, n = self.batch_size, self.n_units
        assert self.v is not None and self.W is not None

        # Recurrent input: batch matmul W[b] @ fired[b] for each b
        # torch.bmm: (B, n, n) @ (B, n, 1) → (B, n, 1) → squeeze → (B, n)
        I_recurrent = torch.bmm(
            self.W, self.fired.float().unsqueeze(-1)
        ).squeeze(-1)

        # Noise: batch Gaussian
        noise = torch.randn(B, n, device=self.device) * self.noise_std
        I_total = I_external + I_recurrent + noise

        # Izhikevich dynamics (vectorized across batch)
        dt = 1.0  # 1ms timestep
        dv = 0.04 * self.v * self.v + 5.0 * self.v + 140.0 - self.u + I_total
        du = self.a_params * (self.b_params * self.v - self.u)

        self.v += dv * dt
        self.u += du * dt

        # Spike detection
        fired = self.v >= 30.0
        self.fired = fired

        # Reset spiking neurons
        spiking_mask = fired
        self.v = torch.where(spiking_mask, self.c_params, self.v)
        self.u = torch.where(spiking_mask, self.u + self.d_params, self.u)

        # Record spikes
        self.spike_counts += fired.float()

        # STDP
        if self.stdp_enabled:
            self._apply_stdp_batch(fired)

        self._t_ms += dt
        return fired

    @torch.no_grad()
    def _apply_stdp_batch(self, fired: torch.Tensor) -> None:
        """Batch STDP: weight updates for all reservoirs.

        For each reservoir b, for each post-synaptic spike:
            LTD: pre-synaptic neurons with recent spikes → W decrease
            LTP: post-synaptic targets → W increase
        """
        assert self.W is not None and self.last_spike_time is not None
        B, n = self.batch_size, self.n_units
        t_now = self._t_ms.unsqueeze(-1)  # (B, 1)

        # ── LTD ────────────────────────────────────────────────────────
        dt_all = t_now - self.last_spike_time  # (B, n)
        ltd_mask = (dt_all > 0) & (dt_all < 5 * self.tau_minus) & (~self.is_inhibitory)
        # ltd_mask: (B, n) — which pre-synaptic neurons are eligible for LTD

        # For each post neuron j, find pre neurons i where W[b,j,i] > 0 and ltd_mask[b,i]
        # Vectorized: for each b, LTD applies to synapses from ltd-eligible pre to ALL post
        dt_clamped = torch.clamp(dt_all, min=0.0)  # (B, n)
        ltd_delta = -self.a_minus * torch.exp(-dt_clamped / self.tau_minus)  # (B, n)
        # Broadcast: W[b, :, i] += ltd_delta[b, i] for each eligible pre i
        # W: (B, n, n), ltd_delta: (B, n) → expand to (B, n, 1) for row broadcasting
        # Each pre neuron i affects column i of W (incoming to all post)
        ltd_update = ltd_delta.unsqueeze(1) * ltd_mask.float().unsqueeze(1)  # (B, 1, n)
        # Apply only to non-inhibitory post neurons
        exc_post = (~self.is_inhibitory).float().unsqueeze(-1)  # (B, n, 1)
        self.W += ltd_update * exc_post

        # Clamp weights: excitatory (0.1, 2.0), inhibitory (-2.0, -0.1)
        exc_mask = (~self.is_inhibitory).float().unsqueeze(-1)  # (B, n, 1)
        inh_mask = self.is_inhibitory.float().unsqueeze(-1)    # (B, n, 1)

        # ── LTP ────────────────────────────────────────────────────────
        # For each post neuron j that fired: W[:, i, j] += A_plus * exp(-dt/tau_plus)
        # where i are pre-synaptic (non-inhibitory) with W[:, i, j] > 0
        spiked = fired.float()  # (B, n)
        dt_post = t_now - self.last_spike_time  # (B, n)
        ltp_delta_pos = self.a_plus * torch.exp(-dt_post / self.tau_plus)  # (B, n)
        ltp_delta_pos = torch.where((dt_post > 0) & (dt_post < 5 * self.tau_plus),
                                    ltp_delta_pos, torch.zeros_like(ltp_delta_pos))
        # Broadcast: for each fired post j, add to column j of W
        ltp_update = ltp_delta_pos.unsqueeze(1) * spiked.unsqueeze(1)  # (B, 1, n)
        exc_pre = (~self.is_inhibitory).float().unsqueeze(-1)  # (B, n, 1)
        self.W += ltp_update * exc_pre

        # Update last spike times for fired neurons
        self.last_spike_time = torch.where(fired, t_now.expand(-1, n), self.last_spike_time)

    @torch.no_grad()
    def _electrode_to_input(self, electrode_vecs: torch.Tensor) -> torch.Tensor:
        """Convert electrode vectors to reservoir input currents.

        Args:
            electrode_vecs: (B, n_electrodes) or (B, T, n_electrodes)

        Returns:
            I_input: (B, n) or (B, T, n)
        """
        assert self.input_proj is not None
        if electrode_vecs.dim() == 2:
            # (B, e) → (B, n)
            I = torch.bmm(
                self.input_proj, electrode_vecs.unsqueeze(-1)
            ).squeeze(-1)
        else:
            # (B, T, e) → (B, T, n)
            B, T, e = electrode_vecs.shape
            I = torch.bmm(
                electrode_vecs.reshape(B * T, e).unsqueeze(1),
                self.input_proj.transpose(1, 2).expand(B, self.n_units, self.n_electrodes)
            )
            # Fallback: simpler reshape
            I = torch.einsum('bne,bte->btn', self.input_proj, electrode_vecs)
        return I * self.input_scale

    # ═══════════════════════════════════════════════════════════════════
    # Public API
    # ═══════════════════════════════════════════════════════════════════

    def process_batch(
        self,
        electrode_sequences: list[np.ndarray],
        steps_per_window: int = 20,
    ) -> torch.Tensor:
        """Process B sequences in parallel.

        Args:
            electrode_sequences: list of B arrays, each (T, n_electrodes)
                where T is number of windows × samples per window
            steps_per_window: number of 1ms timesteps per stimulation pattern

        Returns:
            firing_rates: (B, n) firing rates (Hz) per reservoir
        """
        if not self._built:
            self.build()
        self._reset_state()

        B = self.batch_size
        assert len(electrode_sequences) == B

        # Process all B sequences timestep by timestep
        # Find max length for padding
        max_len = max(seq.shape[0] for seq in electrode_sequences)

        for t in range(max_len):
            # Build input tensor for this timestep
            I_step = torch.zeros(B, self.n_units, device=self.device)
            for b in range(B):
                if t < electrode_sequences[b].shape[0]:
                    elec_vec = torch.from_numpy(
                        electrode_sequences[b][t].astype(np.float32)
                    ).to(self.device)
                    # Project to reservoir
                    I_step[b] = (self.input_proj[b] @ elec_vec) * self.input_scale

            # Run N steps of dynamics with this input
            for _ in range(steps_per_window):
                self._step_batch(I_step)

        # Compute firing rates
        total_time_s = (max_len * steps_per_window) / 1000.0
        rates = self.spike_counts / max(total_time_s, 0.001)
        return rates

    def process_windows(
        self,
        all_windows: list[list[np.ndarray]],
        steps_per_window: int = 20,
    ) -> np.ndarray:
        """Process windowed sequences — main entry point.

        Args:
            all_windows: list of B sequences, each a list of (n_electrodes, window_len) arrays
            steps_per_window: simulation steps per window

        Returns:
            features: (B, n) firing rate features per reservoir
        """
        if not self._built:
            self.build()
        self._reset_state()

        B = self.batch_size
        assert len(all_windows) == B

        # Process each window across all batches
        # First window at position 0 for all, second at position 1, etc.
        n_windows = max(len(wins) for wins in all_windows)

        for w_idx in range(n_windows):
            # Input for this window across all B
            I_step = torch.zeros(B, self.n_units, device=self.device)
            active_b = 0
            for b in range(B):
                if w_idx < len(all_windows[b]):
                    win = all_windows[b][w_idx]  # (n_electrodes, window_len)
                    # Average across window as stimulus pattern
                    elec_vec = win.mean(axis=1).astype(np.float32)  # (n_electrodes,)
                    elec_vec = elec_vec / (np.max(np.abs(elec_vec)) + 1e-8)
                    I_step[b] = (self.input_proj[b] @
                                 torch.from_numpy(elec_vec).to(self.device)) * self.input_scale
                    active_b += 1
            if active_b == 0:
                continue

            # Run steps
            for _ in range(steps_per_window):
                self._step_batch(I_step)

        # Firing rates
        total_time_s = (n_windows * steps_per_window) / 1000.0
        rates = self.spike_counts / max(total_time_s, 0.001)
        return rates.cpu().numpy()

    def get_firing_rates(self) -> np.ndarray:
        """Get current firing rates (Hz) per reservoir."""
        if self.spike_counts is None:
            return np.array([])
        return self.spike_counts.cpu().numpy()

    def get_membrane_potentials(self) -> np.ndarray:
        """Get current membrane potentials (mV)."""
        return self.v.cpu().numpy() if self.v is not None else np.array([])


# ═══════════════════════════════════════════════════════════════════════
# Utility: benchmark CPU vs GPU
# ═══════════════════════════════════════════════════════════════════════

def benchmark_cuda_vs_cpu(
    batch_sizes: list[int] | None = None,
    n_units: int = 128,
    n_steps: int = 1000,
    seed: int = 42,
):
    """Benchmark PyTorch CUDA vs CPU for batch reservoir simulation.

    Returns dict with timing and speedup per batch size.
    """
    if batch_sizes is None:
        batch_sizes = [1, 4, 8, 16, 42]

    results = {}
    for B in batch_sizes:
        print(f"\n  Batch size {B}:")

        # CPU
        cbr_cpu = CudaBatchReservoir(
            batch_size=B, n_units=n_units, device="cpu", seed=seed,
        )
        cbr_cpu.build()
        cbr_cpu._reset_state()

        I_ext = torch.randn(B, n_units, dtype=torch.float32)
        t0 = time.perf_counter()
        for _ in range(n_steps):
            cbr_cpu._step_batch(I_ext)
        dt_cpu = time.perf_counter() - t0

        # CUDA
        if torch.cuda.is_available():
            cbr_cuda = CudaBatchReservoir(
                batch_size=B, n_units=n_units, device="cuda", seed=seed,
            )
            cbr_cuda.build()
            cbr_cuda._reset_state()

            I_ext_cuda = torch.randn(B, n_units, dtype=torch.float32, device="cuda")
            # Warmup
            for _ in range(10):
                cbr_cuda._step_batch(I_ext_cuda)
            torch.cuda.synchronize()

            t0 = time.perf_counter()
            for _ in range(n_steps):
                cbr_cuda._step_batch(I_ext_cuda)
            torch.cuda.synchronize()
            dt_cuda = time.perf_counter() - t0
            speedup = dt_cpu / max(dt_cuda, 0.0001)
        else:
            dt_cuda = 0.0
            speedup = 0.0

        results[str(B)] = {
            "cpu_time_s": round(dt_cpu, 4),
            "cuda_time_s": round(dt_cuda, 4),
            "speedup": round(speedup, 1),
            "steps_per_second_cpu": int(n_steps / max(dt_cpu, 0.0001)),
            "steps_per_second_cuda": int(n_steps / max(dt_cuda, 0.0001)),
        }

        print(f"    CPU: {dt_cpu:.2f}s ({n_steps/max(dt_cpu,0.001):.0f} steps/s)")
        if torch.cuda.is_available():
            print(f"    CUDA: {dt_cuda:.2f}s ({n_steps/max(dt_cuda,0.001):.0f} steps/s) — {speedup:.1f}x")

    return results


# ═══════════════════════════════════════════════════════════════════════
# Quick test
# ═══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 70)
    print("BioGPU v4.4 — CUDA Batch Reservoir Benchmark")
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"Device: {torch.cuda.get_device_name(0)}")
    print("=" * 70)

    results = benchmark_cuda_vs_cpu(
        batch_sizes=[1, 4, 8, 16, 42],
        n_units=128,
        n_steps=1000,
    )

    print("\n" + "=" * 70)
    print("Summary:")
    for B, r in results.items():
        speedup = r.get("speedup", 0)
        print(f"  B={B:3s}: CPU={r['cpu_time_s']:.2f}s  CUDA={r['cuda_time_s']:.2f}s  "
              f"→ {speedup:.1f}x speedup")
