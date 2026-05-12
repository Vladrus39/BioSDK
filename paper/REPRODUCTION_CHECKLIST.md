# Reproduction Checklist v3.0

## Local smoke test

```bash
bash scripts/run_biogpu_v30_local_check.sh
```

## Expected v3.0 outputs

- `outputs/realdata_zenodo_14363732_v30_whitepaper/v30_manifest.json`
- `outputs/realdata_zenodo_14363732_v30_whitepaper/BIOGPU_V30_PROJECT_SUMMARY.md`
- `outputs/realdata_zenodo_14363732_v30_whitepaper/v30_claim_ladder.csv`
- `outputs/realdata_zenodo_14363732_v30_whitepaper/v30_release_components.csv`

## Power-PC rerun

Run the existing v2.4/v2.9 bundle workflow with a fixed manifest. Store all JSON, CSV, figures and logs in a single result bundle.

## Live-lab rerun

Only after vendor SDK/backend selection and qualified lab SOP approval. Live mode must preserve audit logs and result bundles.
