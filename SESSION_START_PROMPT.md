# BioGPU-Core v4.4 — Session Start Prompt (2026-05-13)

**Copy this into a new DeepSeek window:**

---

Continue with `HANDOFF_FOR_DEEPSEEK_2026_05_11.md`. Project BioGPU-Core v4.4.

Path: `C:\Users\vladi\Desktop\Braine\BiC OS\biogpu-core-v5_0_bic_os_first_mover_roadmap`
Python: `D:\GameDev\miniconda3\python.exe` (3.13.11)
Node: `C:\Program Files\nodejs\node.exe` v24.13.0
pip: `biosdk` v0.1.4 on PyPI

## CRITICAL: Read HANDOFF_FOR_DEEPSEEK_2026_05_11.md first — v4.3→v4.4 HONEST AUDIT inside.

## GPU/System Status (VERIFIED)
- **Numba 0.65.0** — JIT активен в BioReservoirV40._step()
- **PyTorch 2.10.0+cu128** — CUDA=YES. GPU tensors ready.
- **GPU: NVIDIA RTX 5070 Ti Laptop** — available for CUDA kernels.
- **CPU: 32 cores** — parallel processing available.

## v4.3 Session Results (Что СДЕЛАНО)

### BioReservoirV40 — Numba JIT (1.3x ускорение)
- `biogpu/substrates/bio_reservoir_numba.py` — @njit функции для Izhikevich step, multi-step, STDP
- `biogpu/substrates/bio_reservoir_v40.py` — интегрирован JIT-путь с NumPy fallback

### CLI — biosdk (8 команд)
- `biosdk/cli.py` — open, features, readout, evidence, os, benchmark, list, version
- `pyproject.toml` — entry point: `biosdk = "biosdk.cli:main"`

### BioCompute OS v4.0 (полноценная)
- `biogpu/production/permissions_v40.py` — RBAC: 4 роли, 9 прав, API key + HMAC session auth
- `biogpu/production/lab_approval_v40.py` — 4-стадийный lab approval workflow с safety gates
- `biogpu/production/evidence_ledger_v40.py` — SHA256-chained tamper-evident ledger
- Все три интегрированы в `BioComputeOS`

### Closed-loop v32
- `biogpu/closed_loop/bioreservoir_closed_loop_v32.py` — BioReservoirV40 вместо SimulatedMEA

### Docker
- `Dockerfile` — Python 3.13, Numba, FastAPI, EXPOSE 8420
- `docker-compose.yml` — полный стек

### Свип — В ПРОЦЕССЕ
- `_biogpu_v4_sweep_finish.py` — скрипт создан и запущен
- Phase A (neuron_types): ✅ 6 конфигов, best=0.4833 (FS-heavy, input_scale=10.0)
- Phase B (42-MEA, 7518 seqs): 🔄 выполняется
- Результаты: `outputs/v4_bio_sweep/V4_SWEEP_FINISH.json`

## P0 Priorities (НОВАЯ СЕССИЯ)

1. **Проверить статус свипа** — `dir outputs\v4_bio_sweep\V4_SWEEP_FINISH.json`
2. **Если свип НЕ завершён** — перезапустить: `python -u _biogpu_v4_sweep_finish.py`
3. **Если 42-MEA < 15% BA** — multi-timescale резервуар (100ms + 1s + 10s)
4. **Если свип завершён** — проанализировать результаты, записать в evidence bundle

## P1
5. PyTorch CUDA batch reservoir (параллельная симуляция на GPU)
6. Очистить outputs/ от 100+ симулированных JSON
7. Запустить `_biogpu_v4_neuron_models.py` (LIF vs Izhikevich vs AdEx)

## P2
8. CI/CD GitHub Actions
9. Документация MkDocs
10. Real-time MEA streaming

## Quick Commands

```powershell
# Статус свипа
dir outputs\v4_bio_sweep\V4_SWEEP_FINISH.json

# Перезапуск свипа (если не завершён)
D:\GameDev\miniconda3\python.exe -u _biogpu_v4_sweep_finish.py

# CLI
D:\GameDev\miniconda3\python.exe -m biosdk.cli version

# Дашборд
D:\GameDev\miniconda3\python.exe -m biogpu.dashboard.server_v40

# Сравнение моделей нейронов
D:\GameDev\miniconda3\python.exe -u _biogpu_v4_neuron_models.py

# Бенчмарк
D:\GameDev\miniconda3\python.exe _biogpu_v4_benchmark.py

# Деплой
D:\GameDev\miniconda3\python.exe _deploy.py --prod
```

## RULES
- NO STUBS — всё на Mock FinalSpark API с реальными Giroldini HDF5
- BioCompute OS = BioCompute OS (не переименовывать)
- **GPU доступен — ИСПОЛЬЗОВАТЬ. Numba JIT на каждом горячем цикле.**
- 100% completion, никаких TODO

---

*BioGPU-Core v4.4. GPU + Numba активны. CLI создан. OS достроена. Свип в процессе. 100% real data.*
