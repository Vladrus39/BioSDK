# RUN_RESULTS_REALDATA_V50

BioGPU-Core v5.0 starts active development from the consolidated v5.0 workspace after archiving unique v4.3 files.

## Environment

- Date: 2026-05-06
- OS: Windows
- Python: 3.12.10 venv at workspace level
- Safety posture: offline replay/read-only validation only; no live actuation; no GPU replacement claim.

## Added validation runners

- `scripts/run_biogpu_v50_pc_validation_smoke.ps1`
- `scripts/run_biogpu_v50_dataset_asset_validation.ps1`
- `scripts/run_biogpu_v50_pc_validation_compact.ps1`

Purpose: make the PC validation phase runnable from PowerShell on Windows without requiring bash.

## Smoke validation

Output: `outputs/v50_pc_validation_smoke/windows_pc_validation_smoke_summary.json`

Results:

- `pip check`: OK
- `compileall biogpu`: OK
- `pytest tests/current`: 20 passed
- `biogpu_v47_final_pc_patch`: OK, `ready_for_power_pc_handoff: true`
- `biogpu_v50_differentiation_roadmap`: OK

## Asset validation baseline

Output: `outputs/v46_clean_release_asset_validation/v46_clean_release_summary.json`

Updated output: `outputs/v50_dataset_asset_validation/v46_clean_release_summary.json`

Results:

- Sample preprocessed MEA asset exists and profiles correctly.
- Full `Pre_processed_MEA_data.zip` is not present in the workspace yet.
- Full extracted `Pre_processed_MEA_data/` exists and validates against the content-count manifest profile.
- Extracted dataset profile: 3,581 files, 3,481 electrode CSV files, 59 metadata CSV files, 59 recordings, 18 cultures, 10 base lineages.
- Extracted tree content SHA256: `f01f2364a2be13ac68519f0cd98b0563e368196db4bdd0bb4a808a1d963d3bd2`.
- Data gate status: `extracted_content_profile_validated_zip_hash_pending`.
- Official ZIP checksum validation remains pending and must not be claimed as complete until `Pre_processed_MEA_data.zip` is available.

Updated ZIP validation result after placing the official archive at `data/external/Pre_processed_MEA_data.zip`:

- ZIP size: 12,103,495 bytes.
- ZIP SHA256: `502afab79d3a843dc16a65d02432ed1d3bcb77bd38179952e74399b420c122f6`.
- ZIP MD5: `56e4be13c4573252f055b6a1f775f9da`.
- ZIP entries: 3,581.
- ZIP profile: 3,481 electrode CSV files, 59 metadata CSV files, 59 recordings, 18 cultures, 10 base lineages.
- Full dataset validation: `valid: true`.
- Data gate status: `zip_checksum_validated`.

## Compact replay validation — fast Windows pass

Output summary: `outputs/v50_pc_validation_compact/windows_pc_validation_compact_summary.json`

This pass used `-FastCentroidOnly` to avoid the slow interactive `linear_svm` path. It does not replace the later full-decoder PC run.

### v33 compact sweep

Output: `outputs/powerpc_stage1_v33_compact/`

- Status: completed software-only replay sweep
- Dataset rows: 11,547
- Features: 354
- Cultures: 18
- Target classes: 27
- Run count: 90
- Best decoder: `diag_gaussian`
- Best ablation: `response_delta_count`
- Best split: `culture_holdout_offset_2`
- Accuracy: 0.524000
- Balanced accuracy: 0.463750
- Shuffle mean accuracy: 0.234944
- Improvement vs shuffle mean: 0.289056
- Empirical p-value, shuffled >= real: 0.076923

### v36 lineage compact

Output: `outputs/powerpc_stage2_v36_lineage_compact/`

- Status: completed lineage-strict bootstrap scaffold
- Dataset rows: 11,547
- Features: 354
- Cultures: 18
- Lineage count: 10
- Split count: 6
- Sweep run count: 24
- Best decoder: `centroid_euclidean`
- Best ablation: `exact_features`
- Best split: `lineage_holdout_offset_5`
- Test lineages: `41311;41434`
- Accuracy: 0.929922
- Balanced accuracy: 0.929974
- Shuffle mean accuracy: 0.344596
- Improvement vs shuffle mean: 0.585326
- Empirical p-value, shuffled >= real: 0.040000

## Full lineage statistics — full_shuffle_1000

Output: `outputs/powerpc_full_shuffle_1000/`

Run mode: `full_shuffle_centroid_diagonal`.

This run deliberately excludes the slower sklearn readouts by default and focuses on lineage-strict centroid/diagonal decoders. It is the first completed v5.0 full-shuffle evidence run after ZIP checksum validation.

Configuration:

- Dataset rows: 11,547
- Features: 354
- Cultures: 18
- Lineage count: 10
- Split count: 6
- Decoders: `centroid_euclidean`, `diag_gaussian`
- Ablations: `response_delta_count`, `exact_features`
- Sweep rows: 24
- Shuffle controls: 24,000
- Shuffles per run: 1,000
- Bootstrap iterations: 2,000
- Runtime: 84.998 seconds

Best lineage-strict run:

- Split: `lineage_holdout_offset_5`
- Test lineages: `41311;41434`
- Decoder: `centroid_euclidean`
- Ablation: `exact_features`
- Accuracy: 0.929922
- Balanced accuracy: 0.929974
- Chance approx: 0.333333
- Shuffle mean accuracy: 0.335546
- Shuffle std accuracy: 0.105094
- Shuffle max accuracy: 0.704116
- Improvement vs shuffle mean: 0.594376
- Empirical p-value, shuffled >= real: 0.000999

Bootstrap CI summaries:

- Decoder `centroid_euclidean`: mean accuracy 0.268414, 95% CI [0.176078, 0.408518]
- Decoder `diag_gaussian`: mean accuracy 0.375557, 95% CI [0.266839, 0.502357]
- Ablation `exact_features`: mean accuracy 0.385958, 95% CI [0.244284, 0.553725]
- Ablation `response_delta_count`: mean accuracy 0.258013, 95% CI [0.212659, 0.311887]

Bundle audit:

- Result bundle: `outputs/powerpc_full_shuffle_1000/biogpu_v36_lineage_bootstrap_bundle.zip`
- Bundle entries: 11
- Bundle size: 146,105 bytes
- Bundle SHA256: `951C084E7A41AB6846D32547E78292257E0E5B79EA3AAA2BD013837AF7616891`

## Extended methods — extended_methods_5000 Core

Output: `outputs/powerpc_extended_methods_5000/`

Run mode: `Core` profile.

This run extends the lineage-strict validation surface from six split offsets to ten split offsets and increases shuffled controls to 5,000 per run. It keeps the default profile to centroid/diagonal decoders to avoid making the Windows validation path depend on slow sklearn linear SVM convergence.

Configuration:

- Dataset rows: 11,547
- Features: 354
- Cultures: 18
- Lineage count: 10
- Split count: 10
- Decoders: `centroid_euclidean`, `diag_gaussian`
- Ablations: `response_delta_count`, `exact_features`
- Sweep rows: 40
- Shuffle controls: 200,000
- Shuffles per run: 5,000
- Bootstrap iterations: 5,000
- Runtime: 638.337 seconds

Best lineage-strict run:

- Split: `lineage_holdout_offset_5`
- Test lineages: `41311;41434`
- Decoder: `centroid_euclidean`
- Ablation: `exact_features`
- Accuracy: 0.929922
- Balanced accuracy: 0.929974
- Chance approx: 0.333333
- Shuffle mean accuracy: 0.329749
- Shuffle std accuracy: 0.108200
- Shuffle max accuracy: 0.803115
- Improvement vs shuffle mean: 0.600173
- Empirical p-value, shuffled >= real: 0.000200

Bootstrap CI summaries:

- Decoder `centroid_euclidean`: mean accuracy 0.328317, 95% CI [0.241705, 0.429301]
- Decoder `diag_gaussian`: mean accuracy 0.368998, 95% CI [0.292304, 0.453087]
- Ablation `exact_features`: mean accuracy 0.395586, 95% CI [0.295438, 0.504706]
- Ablation `response_delta_count`: mean accuracy 0.301729, 95% CI [0.246038, 0.366434]

Bundle audit:

- Result bundle: `outputs/powerpc_extended_methods_5000/biogpu_v36_lineage_bootstrap_bundle.zip`
- Bundle entries: 12
- Bundle size: 1,111,344 bytes
- Bundle SHA256: `D2E7CD2FA137F45EE8AA8B3C9A0F9DA76A59F114EAF5698CD963C6702F948911`

## V50 PC validation bundle

Output: `outputs/v50_pc_validation_bundle/`

This bundle packages the v5.0 PC validation evidence without embedding the full dataset archive. It includes project docs, runner scripts, asset manifests, smoke/compact/data validation summaries, full-shuffle tables, full-shuffle nested bundle, and a manifest with per-artifact SHA256 hashes.

- Bundle: `outputs/v50_pc_validation_bundle/biogpu_v50_pc_validation_bundle.zip`
- Manifest: `outputs/v50_pc_validation_bundle/V50_PC_VALIDATION_BUNDLE_MANIFEST.json`
- Summary: `outputs/v50_pc_validation_bundle/V50_PC_VALIDATION_BUNDLE_SUMMARY.json`
- Artifact count: 41 after extended-methods artifacts were added.
- Current bundle size and bundle SHA256 are recorded in `outputs/v50_pc_validation_bundle/V50_PC_VALIDATION_BUNDLE_SUMMARY.json`. They are intentionally not duplicated here because this file is itself included in the bundle.
- Evidence highlights: data gate `zip_checksum_validated`, official ZIP SHA256 `502afab79d3a843dc16a65d02432ed1d3bcb77bd38179952e74399b420c122f6`, full-shuffle status `ok`, full-shuffle best p-value 0.000999, extended-methods status `ok`, extended-methods best p-value 0.000200.

Claim boundary:

- Offline public-data replay only.
- Lineage-strict statistical validation scaffold.
- No live stimulation settings emitted.
- No wet-lab protocol or culturing recipe.
- No vendor pinout/wiring procedure.
- No GPU advantage claim.

## Important limitation

A full-decoder compact run with `logistic_l2` and `linear_svm` was started interactively, but `linear_svm` produced a convergence warning and was too slow for the interactive session. The process was stopped deliberately. The new PowerShell compact runner supports both modes:

- fast sanity mode: `-FastCentroidOnly`
- full PC mode: default, includes `logistic_l2` and `linear_svm`

## Next required step

Validate the official full `Pre_processed_MEA_data.zip` at `data/external/Pre_processed_MEA_data.zip` against the manifest checksum before claiming PC validation complete.
