# BioGPU v4.6 Clean Release Audit

## Cleaned from release root

- Historical `PROJECT_INVENTORY_V*.md`
- Historical `RUN_RESULTS_REALDATA_V*.md`
- Historical generated `outputs/*`
- Old default Docker commands
- Old root README content
- Historical tests from default test path

## Preserved

- Source package under `biogpu/`
- Current docs and beta docs
- Dataset asset manifests
- Sample subset
- Current tests under `tests/current/`
- Power-PC run scripts
- Enterprise/beta runbooks

## Current test command

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q tests/current
```
