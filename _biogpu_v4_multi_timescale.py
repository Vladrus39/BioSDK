"""
BioGPU v4.4 — Multi-Timescale BioReservoir.

Addresses the 42-MEA classification bottleneck: single-timescale (1s window)
only achieves 0.0754 BA (3.17x chance) — practically useless.

Multi-timescale architecture:
    Input: Giroldini MEA spike trains (8ch)
    → Fast reservoir (100ms windows, 64 units): rapid dynamics
    → Medium reservoir (1s windows, 128 units): standard dynamics
    → Slow reservoir (10s windows, 256 units): slow cumulative dynamics
    → Hierarchical readout: concatenate all 3 feature vectors
    → RidgeClassifier on 448-dim feature space

Why this should work:
    1. Different temporal scales capture different neural codes
    2. 100ms: spike-timing-dependent patterns (rate code onset)
    3. 1s: standard firing rate patterns (current BioReservoir)
    4. 10s: slow cumulative effects (fatigue, potentiation, burst statistics)
    5. Hierarchical readout lets classifier learn which timescale matters per class

Design:
    - Three independent BioReservoirV40 instances with different window sizes
    - Shared input: same MEA spikes, different temporal aggregation
    - Parallel execution (independent reservoirs, can be parallelized)
    - Feature concatenation: [fast_64, medium_128, slow_256] = 448 features
"""
from __future__ import annotations
import sys, time, gc, json
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
import warnings
warnings.filterwarnings("ignore")

sys.path.insert(0, '.')
from biogpu.apis.mock_finalspark_api import SpikeEventCache
from biogpu.substrates.bio_reservoir_v40 import BioReservoirV40
from biogpu.runtime.v3_biogpu_runtime import _window_to_stim_pattern
from sklearn.linear_model import RidgeClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold, cross_val_score

BASE = Path(r"C:\Users\vladi\Desktop\Braine\BiC OS\biogpu-core-v5_0_bic_os_first_mover_roadmap")
OUT_DIR = BASE / "outputs" / "v4_bio_sweep"
OUT_DIR.mkdir(parents=True, exist_ok=True)


class MultiTimescaleReservoir:
    """Three parallel BioReservoirs at different temporal scales.

    Architecture:
        Fast (100ms):  64 units, K=10, captures spike-timing patterns
        Medium (1s):  128 units, K=30, captures firing rate patterns
        Slow (10s):   256 units, K=10, captures slow cumulative effects

    Readout: concatenated firing rates from all three → [64 + 128 + 256] = 448 features
    """

    def __init__(self, seed: int = 42, **config):
        self.seed = seed
        self.config = config

        # ── Fast reservoir: 100ms windows, 64 units ───────────────────
        fast_cfg = {
            "num_electrodes": config.get("num_electrodes", 8),
            "reservoir_units": config.get("fast_units", 64),
            "connectivity_degree": config.get("fast_K", 10),
            "rewiring_probability": 0.1,
            "stdp_enabled": config.get("stdp_enabled", True),
            "stdp_a_plus": config.get("stdp_a_plus", 0.01),
            "stdp_a_minus": config.get("stdp_a_minus", 0.012),
            "stdp_tau_plus": 20.0,
            "stdp_tau_minus": 20.0,
            "input_scale": config.get("fast_input_scale", 3.0),
            "noise_current": config.get("noise_current", 2.0),
            "neuron_types": config.get("neuron_types", {"RS": 0.5, "IB": 0.2, "CH": 0.1, "FS": 0.2}),
        }
        self.fast = BioReservoirV40(seed=seed, **fast_cfg)

        # ── Medium reservoir: 1s windows, 128 units ───────────────────
        med_cfg = {
            "num_electrodes": config.get("num_electrodes", 8),
            "reservoir_units": config.get("medium_units", 128),
            "connectivity_degree": config.get("medium_K", 30),
            "rewiring_probability": 0.1,
            "stdp_enabled": config.get("stdp_enabled", True),
            "stdp_a_plus": config.get("stdp_a_plus", 0.01),
            "stdp_a_minus": config.get("stdp_a_minus", 0.012),
            "stdp_tau_plus": 20.0,
            "stdp_tau_minus": 20.0,
            "input_scale": config.get("medium_input_scale", 10.0),
            "noise_current": config.get("noise_current", 2.0),
            "neuron_types": config.get("neuron_types", {"RS": 0.5, "IB": 0.2, "CH": 0.1, "FS": 0.2}),
        }
        self.medium = BioReservoirV40(seed=seed + 1, **med_cfg)

        # ── Slow reservoir: 10s windows, 256 units ────────────────────
        slow_cfg = {
            "num_electrodes": config.get("num_electrodes", 8),
            "reservoir_units": config.get("slow_units", 256),
            "connectivity_degree": config.get("slow_K", 10),
            "rewiring_probability": 0.1,
            "stdp_enabled": config.get("stdp_enabled", True),
            "stdp_a_plus": config.get("stdp_a_plus", 0.01),
            "stdp_a_minus": config.get("stdp_a_minus", 0.012),
            "stdp_tau_plus": 20.0,
            "stdp_tau_minus": 20.0,
            "input_scale": config.get("slow_input_scale", 5.0),
            "noise_current": config.get("noise_current", 2.0),
            "neuron_types": config.get("neuron_types", {"RS": 0.5, "IB": 0.2, "CH": 0.1, "FS": 0.2}),
        }
        self.slow = BioReservoirV40(seed=seed + 2, **slow_cfg)

        print(f"  MultiTimescale built: fast={fast_cfg['reservoir_units']}u, "
              f"med={med_cfg['reservoir_units']}u, slow={slow_cfg['reservoir_units']}u "
              f"=> {fast_cfg['reservoir_units'] + med_cfg['reservoir_units'] + slow_cfg['reservoir_units']} total features")

    def process_windows(self, windows: list[np.ndarray]) -> np.ndarray:
        """Process windows through all three timescales.

        Args:
            windows: list of (n_electrodes, window_len) arrays

        Returns:
            feature vector: (fast_units + medium_units + slow_units,)
        """
        # Fast: original windows (100ms = 100 bins at 1ms)
        fast_windows = windows  # Already 100ms windows (100 bins at 1ms)

        # Medium: downsample to 1s windows (10x)
        medium_windows = []
        for i in range(0, len(windows), 10):
            chunk = windows[i:min(i+10, len(windows))]
            if chunk:
                medium_windows.append(np.concatenate(chunk, axis=1))

        # Slow: downsample to 10s windows (100x)
        slow_windows = []
        for i in range(0, len(windows), 100):
            chunk = windows[i:min(i+100, len(windows))]
            if chunk:
                slow_windows.append(np.concatenate(chunk, axis=1))

        # Process fast
        self.fast.reset_state()
        for win in fast_windows:
            n_units = self.fast.config.get("reservoir_units", 64)
            stim = _window_to_stim_pattern(win, "w", num_electrodes=n_units)
            self.fast.send_stimulation(stim)
            for _ in range(20):
                self.fast._step()
        fast_rates = self.fast.get_firing_rates(window_ms=20000.0)

        # Process medium
        self.medium.reset_state()
        for win in medium_windows:
            n_units = self.medium.config.get("reservoir_units", 128)
            stim = _window_to_stim_pattern(win, "w", num_electrodes=n_units)
            self.medium.send_stimulation(stim)
            for _ in range(20):
                self.medium._step()
        medium_rates = self.medium.get_firing_rates(window_ms=20000.0)

        # Process slow
        self.slow.reset_state()
        for win in slow_windows:
            n_units = self.slow.config.get("reservoir_units", 256)
            stim = _window_to_stim_pattern(win, "w", num_electrodes=n_units)
            self.slow.send_stimulation(stim)
            for _ in range(20):
                self.slow._step()
        slow_rates = self.slow.get_firing_rates(window_ms=20000.0)

        return np.concatenate([fast_rates, medium_rates, slow_rates])

    def process_sequences(self, seqs: list[tuple], n_seqs: int | None = None) -> tuple[np.ndarray, np.ndarray]:
        """Process multiple sequences and return feature matrix.

        Args:
            seqs: list of (mea_id, windows) tuples
            n_seqs: limit to first N sequences (None = all)

        Returns:
            X: (n_sequences, total_features) feature matrix
            y: (n_sequences,) labels
        """
        t0 = time.time()
        X_list = []
        y_list = []

        seqs_to_process = seqs[:n_seqs] if n_seqs else seqs

        for idx, (mea_id, windows) in enumerate(seqs_to_process):
            features = self.process_windows(windows)
            X_list.append(features)
            y_list.append(idx)

            if (idx + 1) % 10 == 0:
                elapsed = time.time() - t0
                rate = (idx + 1) / max(elapsed, 0.01)
                eta = (len(seqs_to_process) - idx - 1) / max(rate, 0.01)
                print(f"    [{idx+1}/{len(seqs_to_process)}] {rate:.1f} seq/s, ETA {eta:.0f}s")

        X = np.array(X_list, dtype=np.float32)
        y = np.array(y_list, dtype=np.int32)
        dt = time.time() - t0
        print(f"  Processed {len(X_list)} sequences in {dt:.1f}s ({len(X_list)/max(dt,0.01):.1f} seq/s)")
        return X, y

    def close(self):
        self.fast.close()
        self.medium.close()
        self.slow.close()


# ═══════════════════════════════════════════════════════════════════════
# Data loading (same as sweep script)
# ═══════════════════════════════════════════════════════════════════════

def build_sequences(mea_ids: list[str], window_step: int = 20, n_windows: int = 20):
    """Build spike-rate windows from MEA data.

    Args:
        mea_ids: sorted MEA IDs
        window_step: stride between sequence starts (in windows)
        n_windows: number of windows per sequence
    """
    import sys
    sys.path.insert(0, '.')
    from biogpu.apis.mock_finalspark_api import SpikeEventCache

    cache = SpikeEventCache()
    cache.load_from_cache(max_files=len(mea_ids))

    seqs, labs = [], []
    for mea_idx, mea_id in enumerate(mea_ids):
        spikes = cache.get_spike_events(mea_id, duration_s=3600.0)
        if not spikes:
            continue
        n_bins = int(3600.0 * 1000 / 10)  # 10ms bins
        rate = np.zeros((8, n_bins), dtype=np.float32)
        for ch, ts_ms in spikes:
            if 0 <= ch < 8:
                bi = int(ts_ms / 10)
                if 0 <= bi < n_bins:
                    rate[ch, bi] += 1
        rate *= 100  # scale to Hz-like
        windows = [rate[:, s:s+100].astype(np.float32) for s in range(0, n_bins - 100, 100)]
        for ss in range(0, len(windows) - n_windows, window_step):
            seqs.append((mea_id, windows[ss:ss + n_windows]))
            labs.append(mea_idx)
        del rate, windows
    return seqs, np.array(labs, dtype=np.int32)


# ═══════════════════════════════════════════════════════════════════════
# Main benchmark
# ═══════════════════════════════════════════════════════════════════════

def run_multi_timescale_benchmark(
    tune_n: int = 8,
    full_n: int = 42,
    n_seqs_tune: int | None = None,
    n_seqs_full: int | None = None,
    seed: int = 42,
):
    """Run multi-timescale benchmark.

    Args:
        tune_n: number of MEAs for tuning (default 8)
        full_n: number of MEAs for full evaluation (default 42)
        n_seqs_tune: limit tuning sequences (None = all)
        n_seqs_full: limit full sequences (None = all)
    """
    now = datetime.now(timezone.utc).isoformat()
    print("=" * 70)
    print("BioGPU v4.4 — Multi-Timescale BioReservoir Benchmark")
    print(f"Started: {now}")
    print("=" * 70)

    # Load data
    print("\n[1] Loading spike cache...")
    cache = SpikeEventCache()
    cache.load_from_cache(max_files=full_n)
    all_mea_ids = sorted(cache._index.keys(), key=lambda x: int(x.split("_")[1]))
    print(f"  {len(all_mea_ids)} MEAs, {cache.stats()['total_spikes']} spikes")

    # Build sequences
    print(f"\n[2] Building sequences ({tune_n}-MEA tuning + {full_n}-MEA full)...")
    t0 = time.time()
    seqs_tune, y_tune = build_sequences(all_mea_ids[:tune_n])
    seqs_full, y_full = build_sequences(all_mea_ids[:full_n])
    # Dynamic n_splits: min(5, smallest class count)
    min_class_tune = min(np.bincount(y_tune))
    min_class_full = min(np.bincount(y_full))
    n_splits_tune = min(5, min_class_tune)
    n_splits_full = min(5, min_class_full)
    cv_tune = StratifiedKFold(n_splits=n_splits_tune, shuffle=True, random_state=seed)
    cv_full = StratifiedKFold(n_splits=n_splits_full, shuffle=True, random_state=seed)
    print(f"  CV splits: tune={n_splits_tune}, full={n_splits_full}")
    chance_tune = 1.0 / tune_n
    chance_full = 1.0 / full_n
    print(f"  Tune: {len(seqs_tune)} seqs, {len(set(y_tune))} classes, chance={chance_tune:.4f}")
    print(f"  Full: {len(seqs_full)} seqs, {len(set(y_full))} classes, chance={chance_full:.4f}")
    print(f"  Build time: {time.time() - t0:.1f}s")

    # ═══════════════════════════════════════════════════════════════════
    # Tuning phase: find best config on 8-MEA
    # ═══════════════════════════════════════════════════════════════════
    print("\n[3] Tuning multi-timescale config on 8-MEA...")
    print("=" * 70)

    configs_to_try = [
        # (name, fast_units, fast_input, medium_units, medium_input, slow_units, slow_input)
        ("baseline", 64, 3.0, 128, 10.0, 256, 5.0),
        ("fast_boost", 64, 8.0, 128, 10.0, 256, 5.0),
        ("slow_boost", 64, 3.0, 128, 10.0, 256, 15.0),
        ("all_boost", 64, 8.0, 128, 15.0, 256, 15.0),
        ("big_fast", 128, 5.0, 128, 10.0, 256, 5.0),
        ("big_slow", 64, 3.0, 128, 10.0, 384, 5.0),
    ]

    best_ba, best_config, best_name = 0.0, None, ""

    for name, fu, fi, mu, mi, su, si in configs_to_try:
        print(f"\n  Config '{name}': fast={fu}u@{fi}, med={mu}u@{mi}, slow={su}u@{si}")
        mt = MultiTimescaleReservoir(seed=seed,
            fast_units=fu, fast_input_scale=fi,
            medium_units=mu, medium_input_scale=mi,
            slow_units=su, slow_input_scale=si,
        )
        X, _ = mt.process_sequences(seqs_tune, n_seqs=n_seqs_tune)
        y = y_tune[:len(X)]  # Use actual class labels, not enumerate indices
        X_s = StandardScaler().fit_transform(X)
        scores = cross_val_score(
            RidgeClassifier(alpha=1.0, random_state=seed),
            X_s, y, cv=cv_tune, scoring="balanced_accuracy",
        )
        ba, std = round(float(scores.mean()), 4), round(float(scores.std()), 4)
        vs_chance = ba / chance_tune
        print(f"    BA={ba:.4f} +/- {std:.4f} ({vs_chance:.1f}x chance)")

        if ba > best_ba:
            best_ba, best_config, best_name = ba, {
                "fast_units": fu, "fast_input_scale": fi,
                "medium_units": mu, "medium_input_scale": mi,
                "slow_units": su, "slow_input_scale": si,
            }, name
            print(f"    <<< BEST")

        mt.close()
        del X, y, mt
        gc.collect()

    print(f"\n  Best: '{best_name}' — BA={best_ba:.4f} ({best_ba/chance_tune:.1f}x chance)")
    print(f"  Config: {best_config}")

    # ═══════════════════════════════════════════════════════════════════
    # Full 42-MEA evaluation
    # ═══════════════════════════════════════════════════════════════════
    print(f"\n[4] 42-MEA evaluation with best config...")
    print("=" * 70)

    mt_full = MultiTimescaleReservoir(seed=seed, **best_config)
    X_full, _ = mt_full.process_sequences(seqs_full, n_seqs=n_seqs_full)
    y_full_arr = y_full[:len(X_full)]  # Use actual class labels
    X_full_s = StandardScaler().fit_transform(X_full)
    scores_full = cross_val_score(
        RidgeClassifier(alpha=1.0, random_state=seed),
        X_full_s, y_full_arr, cv=cv_full, scoring="balanced_accuracy",
    )
    ba_full, std_full = round(float(scores_full.mean()), 4), round(float(scores_full.std()), 4)
    vs_chance_full = ba_full / chance_full
    print(f"  42-MEA: BA={ba_full:.4f} +/- {std_full:.4f} ({vs_chance_full:.1f}x chance)")

    mt_full.close()

    # ═══════════════════════════════════════════════════════════════════
    # Comparison: single-timescale baseline
    # ═══════════════════════════════════════════════════════════════════
    print(f"\n[5] Single-timescale baseline on 42-MEA...")
    print("=" * 70)
    single_cfg = {
        "reservoir_units": 128,
        "connectivity_degree": 30,
        "rewiring_probability": 0.1,
        "stdp_enabled": True,
        "stdp_a_plus": 0.01,
        "stdp_a_minus": 0.012,
        "input_scale": 10.0,
        "neuron_types": {"RS": 0.3, "IB": 0.1, "CH": 0.1, "FS": 0.5},
    }
    r_single = BioReservoirV40(seed=seed, **single_cfg)
    states_single = []
    t0 = time.time()
    for mea_id, seq_wins in (seqs_full[:n_seqs_full] if n_seqs_full else seqs_full):
        r_single.reset_state()
        for win in seq_wins:
            stim = _window_to_stim_pattern(win, "w", num_electrodes=single_cfg["reservoir_units"])
            r_single.send_stimulation(stim)
            for _ in range(20):
                r_single._step()
        rates = r_single.get_firing_rates(window_ms=20000.0)
        states_single.append(rates.copy())
    r_single.close()
    dt_single = time.time() - t0

    X_single = np.array(states_single, dtype=np.float32)
    X_single_s = StandardScaler().fit_transform(X_single)
    n_single = len(states_single)
    y_single = y_full[:n_single] if n_seqs_full else y_full
    s_single = cross_val_score(
        RidgeClassifier(alpha=1.0, random_state=seed),
        X_single_s, y_single, cv=cv_full,
        scoring="balanced_accuracy",
    )
    ba_single, std_single = round(float(s_single.mean()), 4), round(float(s_single.std()), 4)
    print(f"  Single: BA={ba_single:.4f} +/- {std_single:.4f} ({ba_single/chance_full:.1f}x chance)")
    print(f"  Multi:  BA={ba_full:.4f} +/- {std_full:.4f} ({vs_chance_full:.1f}x chance)")
    print(f"  Delta:  {ba_full - ba_single:+.4f}")

    # ═══════════════════════════════════════════════════════════════════
    # Save results
    # ═══════════════════════════════════════════════════════════════════
    final = {
        "benchmark": "biogpu_v44_multi_timescale",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "tuning_mea_count": tune_n,
        "full_mea_count": full_n,
        "best_config": best_config,
        "best_name": best_name,
        "tuning_best_ba": best_ba,
        "tuning_chance": round(chance_tune, 6),
        "results_42mea": {
            "multi_timescale_ba": ba_full,
            "multi_timescale_std": std_full,
            "single_timescale_ba": ba_single,
            "single_timescale_std": std_single,
            "delta": round(ba_full - ba_single, 4),
            "n_sequences": len(seqs_full) if n_seqs_full is None else n_seqs_full,
            "n_classes": full_n,
            "chance": round(chance_full, 6),
            "vs_chance_multi": round(vs_chance_full, 1),
            "vs_chance_single": round(ba_single / chance_full, 1),
        },
        "comparison_previous": {
            "v42_42mea_ba": 0.0754,
            "v42_42mea_vs_chance": 3.17,
            "v44_single_42mea_ba": ba_single,
            "v44_multi_42mea_ba": ba_full,
            "improvement": round((ba_full - 0.0754) / 0.0754 * 100, 1) if ba_full > 0.0754 else 0,
        },
    }

    result_path = OUT_DIR / "V4_MULTI_TIMESCALE.json"
    with open(result_path, "w") as f:
        json.dump(final, f, indent=2)

    print(f"\nResults saved: {result_path}")
    print("Done.")

    return final


# ═══════════════════════════════════════════════════════════════════════
# Quick test
# ═══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    run_multi_timescale_benchmark(
        tune_n=8,
        full_n=42,
        n_seqs_tune=500,    # Fast tuning on subset
        n_seqs_full=None,   # Full 42-MEA evaluation (7518 seqs)
    )
