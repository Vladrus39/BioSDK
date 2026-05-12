# BioGPU-Core v4.6 PC Ready With Evidence Pack

This archive contains:

1. Clean v4.6 source tree for power-PC development.
2. Evidence folder copied from v4.5 historical archive:
   - evidence/outputs/ — generated results, matrices, CSV/JSON reports, plots, result bundles.
   - evidence/RUN_RESULTS*.md — run summaries.
   - evidence/docs/V*.md — historical technical docs.
   - evidence/tests/test_biogpu_v*.py — historical tests for reference only.

Important: current runnable tests are under tests/current/. Historical tests are evidence and may conflict with current version assumptions.

Full external dataset Pre_processed_MEA_data.zip is not embedded; use /mnt/data/Pre_processed_MEA_data.zip or place it at data/external/Pre_processed_MEA_data.zip and validate via scripts/import_preprocessed_mea_data_v46.sh.

Key evidence included:
- v12 condition/spot analysis
- v15 pulse_feature_matrix.npz and pulse metadata
- v32 fixed-manifest real-data replay
- v33 paper-grade real-data sweep
- v36 lineage-strict split + bootstrap scaffold
- v45 master plan/security/enterprise outputs
