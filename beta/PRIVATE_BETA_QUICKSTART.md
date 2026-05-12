# Private Beta Quickstart v4.5

## Local SDK smoke
```bash
python -m pytest tests/test_biogpu_v45_master_plan.py
python -m biogpu.benchmarks.biogpu_v45_master_plan
```

## What to test
1. Read `docs/MASTER_PROJECT_PLAN_V45.md`.
2. Run sample manifest from `data/templates/v45_master_beta_manifest_template.json`.
3. Import sample or own neural data through safe import mode.
4. Run replay/read-only benchmark.
5. Download/check result bundle.
6. Confirm unsafe live-control fields are rejected.
7. Fill `beta/BETA_FEEDBACK_FORM.md`.
