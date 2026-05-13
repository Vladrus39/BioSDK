"""Phase D runner — sklearn baselines on 42-MEA.
Uses pre-computed Phase B/C results to avoid recomputation.
Saves final V4_SWEEP_FINISH.json."""
import sys, time, json
sys.path.insert(0, '.')
from pathlib import Path
from datetime import datetime, timezone
import numpy as np

BASE = Path(r"C:\Users\vladi\Desktop\Braine\BiC OS\biogpu-core-v5_0_bic_os_first_mover_roadmap")
OUT_DIR = BASE / "outputs" / "v4_bio_sweep"

# Pre-computed results from Phases A/B/C
TUNE_N = 8
best_so_far = {
    "ba": 0.4833,
    "config": {
        "reservoir_units": 128, "connectivity_degree": 30,
        "rewiring_probability": 0.1, "stdp_a_plus": 0.01,
        "stdp_a_minus": 0.012, "stdp_tau_plus": 20.0,
        "stdp_tau_minus": 20.0, "input_scale": 10.0,
        "num_electrodes": 8, "stdp_enabled": True,
        "neuron_types": {"RS": 0.3, "IB": 0.1, "CH": 0.1, "FS": 0.5},
    },
}
all_results = {
    "neuron_types": [
        {"value": "default", "ba": 0.4242, "std": 0.0231, "time_s": 54.2},
        {"value": "FS-heavy", "ba": 0.4833, "std": 0.0261, "time_s": 55.4},
        {"value": "RS-only", "ba": 0.2727, "std": 0.0319, "time_s": 56.7},
        {"value": "IB-only", "ba": 0.1979, "std": 0.0220, "time_s": 58.1},
        {"value": "balanced", "ba": 0.3357, "std": 0.0255, "time_s": 55.9},
        {"value": "CH-dominant", "ba": 0.1660, "std": 0.0215, "time_s": 56.3},
    ],
}
ba42, std42, dt42 = 0.0854, 0.0021, 1936.7
ba_nostdp, std_nostdp, dt_nostdp = 0.0299, 0.0039, 26.2
chance42 = 1.0 / 42
chance_tune = 1.0 / TUNE_N

print("=" * 70)
print("BioGPU v4.3 — Phase D: Sklearn baselines on 42-MEA")
print("=" * 70)

# Rebuild sequences
from biogpu.apis.mock_finalspark_api import SpikeEventCache
cache = SpikeEventCache()
cache.load_from_cache(max_files=42)
all_mea_ids = sorted(cache._index.keys(), key=lambda x: int(x.split("_")[1]))

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

print("\n[1] Building 42-MEA sequences...")
seq42, y42 = build_sequences(all_mea_ids)
print(f"  {len(seq42)} sequences, {len(set(y42))} classes")

# Phase D: sklearn baselines
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import RidgeClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold, cross_val_score

print("\n[2] Phase D: Sklearn baselines on 42-MEA...")
print("=" * 70)

X_static = []
for mea_id, seq_wins in seq42:
    flat = np.concatenate([w.ravel() for w in seq_wins])
    X_static.append(flat)
X_st = np.array(X_static, dtype=np.float32)
X_st_s = StandardScaler().fit_transform(X_st)

cv42 = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
sklearn_42 = {}
for name, clf in [
    ("Ridge", RidgeClassifier(alpha=1.0, random_state=42)),
    ("RF", RandomForestClassifier(n_estimators=100, random_state=42)),
]:
    s = cross_val_score(clf, X_st_s, y42, cv=cv42, scoring="balanced_accuracy")
    sklearn_42[name] = {"ba": round(float(s.mean()), 4), "std": round(float(s.std()), 4)}
    print(f"  {name}: BA={s.mean():.4f} +/- {s.std():.4f} ({s.mean()/chance42:.1f}x chance)")

# Save final
final = {
    "benchmark": "biogpu_v43_sweep_finish",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "tuning_mea_count": TUNE_N,
    "numba_active": True,
    "phase_a": {
        "n_sequences": 1432,
        "n_classes": 8,
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
