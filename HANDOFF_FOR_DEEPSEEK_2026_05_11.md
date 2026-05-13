# BioGPU-Core v4.4 — Session Handoff (2026-05-13) 🔴 HONEST

## Project Identity
- **Name**: BioGPU-Core / BioSDK v4.4
- **Core goal**: Biological computing accelerator — CUDA batch reservoir + multi-timescale + sweep completion
- **NOT**: a pip package only, an OS, a GPU replacement

## Project Location
- `C:\Users\vladi\Desktop\Braine\BiC OS\biogpu-core-v5_0_bic_os_first_mover_roadmap`
- Python: `D:\GameDev\miniconda3\python.exe` (3.13.11)
- GPU: **RTX 5070 Ti Laptop** (CUDA available, 16GB VRAM)
- PyTorch: 2.10.0+cu128, Numba: 0.65.0

---

## v4.4 Session Progress (2026-05-13)

### P0: Sweep Restart — 🔄 RUNNING
- **`_biogpu_v4_sweep_finish.py`** — restarted after v4.3 session crash
- **Phase A (neuron_types)**: ✅ Completed. Best = 0.4833 BA (FS-heavy, input=10.0, 3.87x chance on 8-MEA)
- **Phase B (42-MEA)**: 🔄 Running. 7518 sequences, 42 classes. ~385M neuron updates. ETA 30-90 min.
- **Phase C (STDP ablation)**: pending
- **Phase D (sklearn baselines)**: pending
- **Output**: `outputs/v4_bio_sweep/V4_SWEEP_FINISH.json` (not yet created)
- **Process**: PID 32628, ~816 MB RAM

### P1: PyTorch CUDA Batch Reservoir — ✅ DONE
- **`biogpu/substrates/bio_reservoir_cuda.py`** — 569 lines, NEW
- Class `CudaBatchReservoir`: B parallel Izhikevich reservoirs on GPU
- Batch operations: `torch.bmm` for recurrent input, vectorized dynamics
- Batch STDP: per-reservoir weight updates
- Tested: 4x64 neurons, RTX 5070 Ti, ~0.1 MB GPU memory
- Benchmark utility: CPU vs CUDA speedup measurement

### P1: Multi-Timescale BioReservoir — ✅ SCRIPT READY
- **`_biogpu_v4_multi_timescale.py`** — 466 lines, NEW
- Class `MultiTimescaleReservoir`: 3 parallel reservoirs at different scales
  - Fast (100ms): 64 units, K=10, captures spike-timing patterns
  - Medium (1s): 128 units, K=30, captures firing rate patterns
  - Slow (10s): 256 units, K=10, captures slow cumulative effects
- Hierarchical readout: concatenated [64 + 128 + 256] = 448 features
- 6 config sweep for tuning, RidgeClassifier readout
- Ready to run after sweep completes

### P1: Output Cleanup — ✅ DONE
- Removed 10 empty d547-d556 directories (contract proofs, all incomplete_by_design)
- Removed test directories (_biosdk_test_bundle, v4_test_ledger_export)
- Kept all real result directories (v* series, powerpc, evidence_ledger, etc.)

### P2: Docker — ⚠️ SKIPPED
- Docker not installed on this Windows machine
- Dockerfile and docker-compose.yml already exist (from v4.3)

---

## Files Created This Session

| File | Purpose | Lines |
|------|---------|-------|
| `biogpu/substrates/bio_reservoir_cuda.py` | CUDA batch reservoir | 569 |
| `_biogpu_v4_multi_timescale.py` | Multi-timescale benchmark | 466 |
| `_test_cuda_batch.py` | CUDA reservoir test | 23 |
| `_gpu_check.py` | GPU verification | 7 |
| `_check_proc.py` | Process checker | 6 |

---

## Current Sweep Status

### BioReservoirV40 Results (so far)
| Scale | BA | xChance | Config |
|-------|-----|---------|--------|
| 4-MEA | 0.6379 | 2.55x | units=64, K=10, A+=0.02 |
| 8-MEA | **0.4833** | **3.87x** | units=128, K=30, A+=0.01, input=10.0, FS-heavy |
| 42-MEA | 🔄 | ? | same as 8-MEA |

### Previous 42-MEA (v4.2, different config)
- BA: 0.0754 (3.17x chance) — practically useless
- Expected: similar result from current sweep → multi-timescale needed

---

## Priority for Next Actions (after sweep)

### If 42-MEA BA < 15%:
1. **Run multi-timescale benchmark**: `python -u _biogpu_v4_multi_timescale.py`
   - Tune on 8-MEA (6 configs)
   - Evaluate on 42-MEA
   - Compare single vs multi-timescale

### If 42-MEA BA >= 15%:
1. **Run neuron model comparison**: `python -u _biogpu_v4_neuron_models.py`
   - LIF vs Izhikevich vs AdEx on 4-MEA and 42-MEA

### Either way:
1. **CUDA batch benchmark**: `python biogpu/substrates/bio_reservoir_cuda.py`
   - Measure CPU vs GPU speedup for batch reservoir
2. **Integrate CUDA reservoir** into sweep pipeline
3. **Update MASTER_STATUS_V85.md** with v4.4 results
4. **GitHub push** with all v4.4 changes

---

## Quick Start

```powershell
cd "C:\Users\vladi\Desktop\Braine\BiC OS\biogpu-core-v5_0_bic_os_first_mover_roadmap"

# 1. Check sweep
dir outputs\v4_bio_sweep\V4_SWEEP_FINISH.json

# 2. If sweep done — check results
type outputs\v4_bio_sweep\V4_SWEEP_FINISH.json

# 3. If 42-MEA < 0.15 → multi-timescale
D:\GameDev\miniconda3\python.exe -u _biogpu_v4_multi_timescale.py

# 4. CUDA batch benchmark
D:\GameDev\miniconda3\python.exe biogpu\substrates\bio_reservoir_cuda.py

# 5. Neuron model comparison
D:\GameDev\miniconda3\python.exe -u _biogpu_v4_neuron_models.py

# 6. Dashboard
D:\GameDev\miniconda3\python.exe -m biogpu.dashboard.server_v40
```

---

*Handoff v4.4 HONEST. CUDA batch built, multi-timescale ready, sweep in progress. Decision pending on 42-MEA result.*
