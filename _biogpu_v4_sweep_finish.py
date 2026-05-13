"""BioGPU v4.3 — Sweep FINISH: neuron_types + Phase B/C/D.

Resumes from phase_a_progress_v2.json checkpoint.
Completes the 8-MEA enhanced sweep:
  - Phase A: neuron_types (6 configs) — NOT YET RUN
  - Phase B: 42-MEA verification with best config
  - Phase C: STDP ablation (with vs without)
  - Phase D: sklearn baselines on 42-MEA

Numba 0.65.0 JIT is active in BioReservoirV40._step().
"""
import sys, time, gc, json
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
print("BioGPU v4.3 — SWEEP FINISH (resume from checkpoint)")
print(f"Started: {now}")
print("Numba JIT: active in BioReservoirV40._step()")
print("=" * 70)

from biogpu.apis.mock_finalspark_api import SpikeEventCache
from biogpu.substrates.bio_reservoir_v40 import BioReservoirV40
from biogpu.runtime.v3_biogpu_runtime import _window_to_stim_pattern
from sklearn.linear_model import RidgeClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold, cross_val_score

# ── Load checkpoint ──────────────────────────────────────────────────
ckpt_path = OUT_DIR / "phase_a_progress_v2.json"
if ckpt_path.exists():
    with open(ckpt_path) as f:
        ckpt = json.load(f)
    best_so_far = ckpt["best"]
    all_results = ckpt["results"]
    print(f"\nCheckpoint loaded: best BA={best_so_far['ba']:.4f}")
    print(f"  Config: units={best_so_far['config'].get('reservoir_units')}, "
          f"K={best_so_far['config'].get('connectivity_degree')}, "
          f"p={best_so_far['config'].get('rewiring_probability')}, "
          f"A+={best_so_far['config'].get('stdp_a_plus')}, "
          f"tau={best_so_far['config'].get('stdp_tau_plus')}/{best_so_far['config'].get('stdp_tau_minus')}, "
          f"input={best_so_far['config'].get('input_scale')}")
else:
    best_so_far = {"ba": 0, "config": {}}
    all_results = {}
    print("\nNo checkpoint found — starting fresh.")

# ── Load spike cache ─────────────────────────────────────────────────
print("\n[1] Loading spike cache...")
cache = SpikeEventCache()
cache.load_from_cache(max_files=42)
all_mea_ids = sorted(cache._index.keys(), key=lambda x: int(x.split("_")[1]))
print(f"  {len(all_mea_ids)} MEAs, {cache.stats()['total_spikes']} spikes")

# ── Precompute sequences ─────────────────────────────────────────────
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

# Tuning on 8-MEA
TUNE_N = 8
print(f"\n[2] Precomputing {TUNE_N}-MEA sequences (tuning set)...")
t0 = time.time()
seq_tune, y_tune = build_sequences(all_mea_ids[:TUNE_N])
cv_tune = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
chance_tune = 1.0 / TUNE_N
print(f"  {len(seq_tune)} sequences, {len(set(y_tune))} classes, chance={chance_tune:.4f}, {time.time()-t0:.1f}s")

# Build defaults from best config
defaults = best_so_far["config"].copy()
# Ensure all required keys exist
for k, v in {
    "num_electrodes": 8, "stdp_enabled": True,
    "stdp_tau_plus": 20.0, "stdp_tau_minus": 20.0,
    "stdp_a_minus": 0.012,
    "neuron_types": {"RS": 0.3, "IB": 0.1, "CH": 0.1, "FS": 0.5},
}.items():
    if k not in defaults:
        defaults[k] = v
print(f"  Defaults from best: {json.dumps({k:v for k,v in defaults.items() if k != 'neuron_types'})}")

def run_biogpu(seqs, y, cv_splitter, **kwargs):
    """Run BioReservoir with given config, return Ridge CV BA."""
    n_units = kwargs.get("reservoir_units", 128)
    r = BioReservoirV40(seed=42, **kwargs)
    t0 = time.time()
    states = []
    for mea_id, seq_wins in seqs:
        r.reset_state()
        for win in seq_wins:
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
                             X_s, y, cv=cv_splitter, scoring="balanced_accuracy")
    return round(float(scores.mean()), 4), round(float(scores.std()), 4), round(dt, 1)

# ═══════════════════════════════════════════════════════════════════════
# Phase A Resumed: neuron_types sweep (6 configs)
# ═══════════════════════════════════════════════════════════════════════

print(f"\n[3] Phase A (resumed): neuron_types sweep")
print("=" * 70)

if "neuron_types" in all_results:
    print("  neuron_types already completed, skipping...")
    type_results = all_results["neuron_types"]
else:
    type_configs = [
        ("default", {"RS": 0.5, "IB": 0.2, "CH": 0.1, "FS": 0.2}),
        ("FS-heavy", {"RS": 0.3, "IB": 0.1, "CH": 0.1, "FS": 0.5}),
        ("RS-only", {"RS": 1.0}),
        ("IB-only", {"IB": 1.0}),
        ("balanced", {"RS": 0.25, "IB": 0.25, "CH": 0.25, "FS": 0.25}),
        ("CH-dominant", {"RS": 0.2, "IB": 0.1, "CH": 0.6, "FS": 0.1}),
    ]
    type_results = []
    for tname, tdist in type_configs:
        cfg = {**defaults, "neuron_types": tdist}
        print(f"\n  {tname}:")
        ba, std, dt = run_biogpu(seq_tune, y_tune, cv_tune, **cfg)
        r = {"value": tname, "ba": ba, "std": std, "time_s": dt}
        type_results.append(r)
        marker = ""
        if ba > best_so_far["ba"]:
            best_so_far = {"ba": ba, "config": cfg}
            marker = " <<< BEST"
        print(f"    BA={ba:.4f} +/- {std:.4f} ({dt:.1f}s){marker}")

    all_results["neuron_types"] = type_results

    # Save checkpoint
    with open(ckpt_path, "w") as f:
        json.dump({"best": best_so_far, "results": all_results}, f, indent=2)
    print(f"\n  Checkpoint saved.")

# ── Phase A Summary ──────────────────────────────────────────────────
print("\n" + "=" * 70)
print(f"Phase A Complete — Best Config (tuned on {TUNE_N}-MEA)")
print("=" * 70)
neuron_types_str = json.dumps(best_so_far["config"].get("neuron_types", {}))
print(f"  Best BA: {best_so_far['ba']:.4f} (chance={chance_tune:.4f}, {best_so_far['ba']/chance_tune:.1f}x)")
print(f"  Config: units={best_so_far['config'].get('reservoir_units')}, "
      f"K={best_so_far['config'].get('connectivity_degree')}, "
      f"p={best_so_far['config'].get('rewiring_probability')}, "
      f"A+={best_so_far['config'].get('stdp_a_plus')}, "
      f"tau={best_so_far['config'].get('stdp_tau_plus')}/{best_so_far['config'].get('stdp_tau_minus')}, "
      f"input={best_so_far['config'].get('input_scale')}")
print(f"  Neuron types: {neuron_types_str}")

# ═══════════════════════════════════════════════════════════════════════
# Phase B: Verify on 42-MEA
# ═══════════════════════════════════════════════════════════════════════

print("\n[4] Phase B: Verifying best config on 42-MEA...")
print("=" * 70)
seq42, y42 = build_sequences(all_mea_ids)
cv42 = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
chance42 = 1.0 / len(all_mea_ids)
print(f"  {len(seq42)} sequences, {len(set(y42))} classes, chance={chance42:.4f}")

ba42, std42, dt42 = run_biogpu(seq42, y42, cv42, **best_so_far["config"])
print(f"  42-MEA: BA={ba42:.4f} +/- {std42:.4f} ({dt42:.1f}s)")
print(f"  vs chance: {ba42/chance42:.1f}x")

# ═══════════════════════════════════════════════════════════════════════
# Phase C: STDP ablation on 42-MEA
# ═══════════════════════════════════════════════════════════════════════

print("\n[5] Phase C: STDP ablation on 42-MEA...")
print("=" * 70)
cfg_nostdp = {**best_so_far["config"], "stdp_enabled": False}
ba_nostdp, std_nostdp, dt_nostdp = run_biogpu(seq42, y42, cv42, **cfg_nostdp)
print(f"  With STDP:    BA={ba42:.4f} +/- {std42:.4f} ({dt42:.1f}s)")
print(f"  Without STDP: BA={ba_nostdp:.4f} +/- {std_nostdp:.4f} ({dt_nostdp:.1f}s)")
print(f"  STDP delta BA: {ba42 - ba_nostdp:+.4f}")

# ═══════════════════════════════════════════════════════════════════════
# Phase D: Sklearn baselines on 42-MEA
# ═══════════════════════════════════════════════════════════════════════

print("\n[6] Phase D: Sklearn baselines on 42-MEA...")
print("=" * 70)
from sklearn.ensemble import RandomForestClassifier

X_static = []
for mea_id, seq_wins in seq42:
    flat = np.concatenate([w.ravel() for w in seq_wins])
    X_static.append(flat)
X_st = np.array(X_static, dtype=np.float32)
X_st_s = StandardScaler().fit_transform(X_st)

sklearn_42 = {}
for name, clf in [
    ("Ridge", RidgeClassifier(alpha=1.0, random_state=42)),
    ("RF", RandomForestClassifier(n_estimators=100, random_state=42)),
]:
    s = cross_val_score(clf, X_st_s, y42, cv=cv42, scoring="balanced_accuracy")
    sklearn_42[name] = {"ba": round(float(s.mean()), 4), "std": round(float(s.std()), 4)}
    print(f"  {name}: BA={s.mean():.4f} +/- {s.std():.4f} ({s.mean()/chance42:.1f}x chance)")

# ═══════════════════════════════════════════════════════════════════════
# Save final results
# ═══════════════════════════════════════════════════════════════════════

final = {
    "benchmark": "biogpu_v43_sweep_finish",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "tuning_mea_count": TUNE_N,
    "numba_active": True,
    "phase_a": {
        "n_sequences": len(seq_tune),
        "n_classes": len(set(y_tune)),
        "best_ba": best_so_far["ba"],
        "chance": round(chance_tune, 6),
        "config": best_so_far["config"],
        "results": all_results,
    },
    "phase_b_42mea": {
        "n_sequences": len(seq42),
        "n_classes": len(set(y42)),
        "ba": ba42,
        "std": std42,
        "chance": round(chance42, 6),
        "vs_chance": round(ba42 / chance42, 2),
    },
    "phase_c_stdp_ablation": {
        "ba_with_stdp": ba42,
        "ba_without_stdp": ba_nostdp,
        "stdp_delta": round(ba42 - ba_nostdp, 4),
    },
    "phase_d_sklearn_42mea": sklearn_42,
    "comparison": {
        "prev_4mea_sweep_42mea_ba": 0.0754,
        "simulated_mea_42mea_ba": 0.0758,
        "bio_reservoir_42mea_ba": ba42,
        "best_sklearn_42mea_ba": max(v["ba"] for v in sklearn_42.values()),
    },
}

result_path = OUT_DIR / "V4_SWEEP_FINISH.json"
with open(result_path, "w") as f:
    json.dump(final, f, indent=2)

print("\n" + "=" * 70)
print("SWEEP COMPLETE")
print("=" * 70)
print(f"  8-MEA best BA: {best_so_far['ba']:.4f} ({best_so_far['ba']/chance_tune:.1f}x chance)")
print(f"  42-MEA BA:     {ba42:.4f} ({ba42/chance42:.1f}x chance)")
print(f"  STDP effect:   {ba42 - ba_nostdp:+.4f}")
best_sk = max(v["ba"] for v in sklearn_42.values())
print(f"  Best sklearn:  {best_sk:.4f}")
print(f"  BioReservoir vs sklearn: {ba42 - best_sk:+.4f}")
print(f"\nResults saved: {result_path}")
print("Done.")
