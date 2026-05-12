# Project Inventory v5.0

Added in v5.0 active-development start:

- `scripts/run_biogpu_v50_pc_validation_smoke.ps1`
- `scripts/run_biogpu_v50_dataset_asset_validation.ps1`
- `scripts/run_biogpu_v50_pc_validation_compact.ps1`
- `scripts/run_biogpu_v50_pc_validation_full_shuffle.ps1`
- `scripts/run_biogpu_v50_pc_validation_extended_methods.ps1`
- `scripts/package_biogpu_v50_pc_validation_bundle.ps1`
- `biogpu/release/pc_validation_bundle_v50.py`
- `tests/current/test_biogpu_v50_pc_validation_bundle.py`
- `RUN_RESULTS_REALDATA_V50.md`
- `PROJECT_INVENTORY_V50.md`
- `docs/V43_TO_V50_CONSOLIDATION.md`
- `legacy/v4_3_unique_archive/README_V43_UNIQUE_ARCHIVE.md`
- `legacy/v4_3_unique_archive/MANIFEST_V43_UNIQUE_FILES.csv`
- `legacy/v4_3_unique_archive/**` — reference-only v4.3 unique archive

Generated/validated outputs:

- `outputs/v50_pc_validation_smoke/windows_pc_validation_smoke_summary.json`
- `outputs/v50_pc_validation_compact/windows_pc_validation_compact_summary.json`
- `outputs/v50_dataset_asset_validation/v46_clean_release_summary.json`
- `outputs/powerpc_stage1_v33_compact/`
- `outputs/powerpc_stage2_v36_lineage_compact/`
- `outputs/v46_clean_release_asset_validation/v46_clean_release_summary.json`
- `outputs/powerpc_full_shuffle_1000/`
- `outputs/powerpc_full_shuffle_1000/RUN_MANIFEST_FULL_SHUFFLE_1000_WINDOWS.json`
- `outputs/powerpc_full_shuffle_1000/WINDOWS_FULL_SHUFFLE_1000_RUN_SUMMARY.json`
- `outputs/powerpc_full_shuffle_1000/v36_summary.json`
- `outputs/powerpc_full_shuffle_1000/v36_lineage_sweep_results.csv`
- `outputs/powerpc_full_shuffle_1000/v36_lineage_shuffle_controls.csv`
- `outputs/powerpc_full_shuffle_1000/v36_bootstrap_ci_by_decoder.csv`
- `outputs/powerpc_full_shuffle_1000/v36_bootstrap_ci_by_ablation.csv`
- `outputs/powerpc_full_shuffle_1000/biogpu_v36_lineage_bootstrap_bundle.zip`
- `outputs/powerpc_extended_methods_5000/`
- `outputs/powerpc_extended_methods_5000/RUN_MANIFEST_EXTENDED_METHODS_5000_WINDOWS.json`
- `outputs/powerpc_extended_methods_5000/WINDOWS_EXTENDED_METHODS_5000_RUN_SUMMARY.json`
- `outputs/powerpc_extended_methods_5000/v36_summary.json`
- `outputs/powerpc_extended_methods_5000/v36_lineage_sweep_results.csv`
- `outputs/powerpc_extended_methods_5000/v36_lineage_shuffle_controls.csv`
- `outputs/powerpc_extended_methods_5000/v36_bootstrap_ci_by_decoder.csv`
- `outputs/powerpc_extended_methods_5000/v36_bootstrap_ci_by_ablation.csv`
- `outputs/powerpc_extended_methods_5000/biogpu_v36_lineage_bootstrap_bundle.zip`
- `outputs/v50_pc_validation_bundle/V50_PC_VALIDATION_BUNDLE_MANIFEST.json`
- `outputs/v50_pc_validation_bundle/V50_PC_VALIDATION_BUNDLE_SUMMARY.json`
- `outputs/v50_pc_validation_bundle/biogpu_v50_pc_validation_bundle.zip`

Purpose:

- Make v5.0 the single active development root.
- Preserve v4.3-only files before removing the standalone v4.3 folder.
- Start PC validation with Windows-compatible PowerShell runners.
- Record the first smoke and fast compact validation pass.
- Validate the official `Pre_processed_MEA_data.zip` asset checksum and manifest profile.
- Record the first full_shuffle_1000 lineage-strict validation pass with 24,000 shuffled-control rows, bootstrap CI summaries, and a reproducible result bundle.
- Record the extended_methods_5000 Core profile with 40 lineage-strict sweep rows, 200,000 shuffled-control rows, 5,000 bootstrap iterations, and a reproducible result bundle.
- Package a v5.0 PC validation bundle that links the validated dataset gate, smoke/compact outputs, full-shuffle outputs, extended-methods outputs, runner scripts, docs, and evidence reports.
