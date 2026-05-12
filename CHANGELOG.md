# Changelog

All notable changes to BioSDK.

## [0.1.4] — 2026-05-12

### Fixed
- `biosdk.__version__` now reads from `importlib.metadata` instead of a hardcoded string — `pyproject.toml` is the single source of truth, no more drift between versions.
- README replaced "Cryptographically signed evidence bundle" with "Integrity-verified evidence bundle (HMAC-SHA256)" — aligns with the honest description in `SECURITY.md`.
- `requirements.txt` synced with `pyproject.toml` — `fastapi`/`uvicorn` moved to dashboard extras only; `pytest` moved to dev extras.
- `SECURITY.md` supported-versions table now includes `0.1.4`.

## [0.1.3] — 2026-05-12

### Added
- GitHub repository published: https://github.com/Vladrus39/BioSDK
- Open Core licensing model (MIT Community + Commercial Enterprise)
- Unified deploy script: `python _deploy.py`
- Project secrets consolidated in `.env`
- Single README serves both GitHub and PyPI
- `CHANGELOG.md`, `.dockerignore`, `SECURITY.md`
- `packages.find` exclude rules to prevent test/data leakage

### Fixed
- [SECURITY] Hardcoded API fixture keys replaced with env vars (BIOSDK_DEV_KEY, etc.)
- [SECURITY] HMAC signing key moved from hardcoded string to `BIOSDK_SIGNING_KEY` env var
- Version sync: `biosdk/__init__.py` __version__ now matches `pyproject.toml`
- Empty `biogpu/__init__.py` now has package docstring
- `Dockerfile` CMD updated from v47 to current path

## [0.1.0] — 2026-05-11

### Added
- Initial pip package release on TestPyPI
- 7 NSI-1.0 adapters (5 certified + 1 skeleton + 1 reference)
- 83 conformance tests (42 certified + 41 mock)
- 99.67% cross-modal classification accuracy
- Full API: `open()` → `features()` → `readout()` → `evidence_bundle()`
