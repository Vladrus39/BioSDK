"""BioGPU v4.4 — CUDA Batch Reservoir on Real 42-MEA Data.
Benchmarks CudaBatchReservoir CPU vs GPU with real Giroldini spike data."""
import sys, time, json
sys.path.insert(0, '.')
from pathlib import Path
from datetime import datetime, timezone
import numpy as np

BASE = Path(r"C:\Users\vladi\Desktop\Braine\BiC OS\biogpu-core-v5_0_bic_os_first_mover_roadmap")
OUT_DIR = BASE / "outputs" / "v4_bio_sweep"

print("=" * 70)
print("BioGPU v4.4 — CUDA Batch Reservoir — Real 42-MEA Benchmark")
print("=" * 70)

# Load spike cache
from biogpu.apis.mock_finalspark_api import SpikeEventCache
cache = SpikeEventCache()
cache.load_from_cache(max_files=42)
all_mea_ids = sorted(cache._index.keys(), key=lambda x: int(x.split("_")[1]))
print(f"Loaded {len(all_mea_ids)} MEAs, {cache.stats()['total_spikes']} spikes")

# Build electrode sequences (simplified: rate windows)
def build_electrode_sequences(mea_ids, n_seqs_per_mea=5):
    """Build sequences of electrode vectors from spike data."""
    all_windows = []
    for mea_id in mea_ids[:len(mea_ids)]:
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
        # Take first n_seqs_per_mea sequences
        for ss in range(0, min(len(windows)-20, n_seqs_per_mea*20), 20):
            all_windows.append(windows[ss:ss+20])
            if len(all_windows) >= n_seqs_per_mea * (all_mea_ids.index(mea_id)+1):
                break
        del rate, windows
    return all_windows

# Build windows for B MEAs
B = 8  # Test with 8 MEAs for speed
print(f"\nBuilding sequences for {B} MEAs...")
t0 = time.time()
windows_list = build_electrode_sequences(all_mea_ids[:B], n_seqs_per_mea=3)
print(f"  {len(windows_list)} sequences in {time.time()-t0:.1f}s")

# Import CUDA batch reservoir
from biogpu.substrates.bio_reservoir_cuda import CudaBatchReservoir, benchmark_cuda_vs_cpu
import torch
print(f"\nPyTorch {torch.__version__}, CUDA: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"Device: {torch.cuda.get_device_name(0)}")

# ── CUDA Batch Reservoir on real data ───────────────────────────────
print(f"\n[1] Building CUDA Batch Reservoir (B={B}, n=128)...")
cbr = CudaBatchReservoir(
    batch_size=B, n_units=128, n_electrodes=8,
    stdp_enabled=True, input_scale=10.0,
    device="cuda",
)
cbr.build()

print(f"\n[2] Processing {len(windows_list)} real sequences...")
# Group windows by MEA — each MEA gets its own reservoir slot
# Each sequence is a list of 20 windows (8x100 arrays). 
# process_windows expects: list of B lists, each a list of (8,100) arrays.
# Average each sequence's windows into a single (8,100) pattern.
batch_windows_avg = [[] for _ in range(B)]
for i, seq_wins in enumerate(windows_list):
    # Average all 20 windows in this sequence into one pattern
    avg_win = np.mean(seq_wins, axis=0).astype(np.float32)  # (8, 100)
    batch_windows_avg[i % B].append(avg_win)

# Use first N sequences per batch where all have windows
min_wins = min(len(bw) for bw in batch_windows_avg)
print(f"  Using {min_wins} windows per MEA")

# Trim to equal length
for b in range(B):
    batch_windows_avg[b] = batch_windows_avg[b][:min_wins]

t0 = time.time()
features = cbr.process_windows(batch_windows_avg, steps_per_window=20)
dt = time.time() - t0
print(f"  Processed in {dt:.1f}s — features shape: {features.shape}")
print(f"  Firing rates: mean={features.mean():.2f} Hz, max={features.max():.2f} Hz")

# ── Raw benchmark (synthetic) ───────────────────────────────────────
print(f"\n[3] Raw CUDA vs CPU benchmark (synthetic, n_steps=1000)...")
raw_results = benchmark_cuda_vs_cpu(
    batch_sizes=[1, 4, 8, 16, 42],
    n_units=128,
    n_steps=1000,
)

# ── Save ─────────────────────────────────────────────────────────────
final = {
    "benchmark": "biogpu_v44_cuda_batch_real",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "batch_size": B,
    "n_sequences": len(windows_list),
    "n_windows_per_mea": min_wins,
    "real_data_processing_time_s": round(dt, 2),
    "features_shape": list(features.shape),
    "firing_rate_mean": round(float(features.mean()), 2),
    "firing_rate_max": round(float(features.max()), 2),
    "raw_benchmark": raw_results,
    "gpu_info": {
        "available": torch.cuda.is_available(),
        "device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu",
    },
}

result_path = OUT_DIR / "V4_CUDA_BATCH.json"
with open(result_path, "w") as f:
    json.dump(final, f, indent=2)

print(f"\nResults saved: {result_path}")
print("Done.")
