from pathlib import Path
files = [
    'evidence/outputs/realdata_zenodo_14363732_v15_readout/pulse_feature_matrix.npz',
    'outputs/powerpc_stage1_v33_compact/split_catalog_v33.json',
    'outputs/powerpc_stage1_v33_compact/sweep_summary_v33.json',
    'outputs/v85_baselines/v33_honest_baseline_logreg_svm.json',
]
for f in files:
    print(f"{'OK' if Path(f).exists() else 'MISSING'}: {f}")
