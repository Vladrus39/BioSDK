# Project Inventory — v3.5

Added or updated in v3.5:

- `biogpu/safety/__init__.py`
- `biogpu/safety/boundary_v35.py`
- `biogpu/safety/governance_v35.py`
- `biogpu/release/__init__.py`
- `biogpu/release/release_hygiene_v35.py`
- `biogpu/benchmarks/biogpu_v35_release_hygiene.py`
- `biogpu/readout/linear_v27.py` — replaced centroid placeholders with real sklearn-backed models
- `tests/test_biogpu_v35_release_hygiene.py`
- `docs/V35_RELEASE_HYGIENE_AND_SKLEARN_READOUTS.md`
- `scripts/run_biogpu_v35_local_check.sh`
- `RUN_RESULTS_REALDATA_V35.md`
- `PROJECT_INVENTORY_V35.md`
- `pyproject.toml` — synchronized to version `3.5.0`
- `Dockerfile` — current v3.5 entrypoint
- `scripts/run_biogpu_v35_powerpc_smoke.sh`
- `scripts/run_biogpu_v35_powerpc_full.sh`
- `biogpu/integration/realdata_sweep_v33.py` — extended decoder support for `logistic_l2` and `linear_svm`
- `biogpu/benchmarks/biogpu_v33_realdata_sweep.py` — added CLI flags `--decoders` and `--split-offsets`
