"""Разведка: структура feature_matrix.npz и метки Giroldini."""
import numpy as np, json
from pathlib import Path

bundle = Path("outputs/v86_evidence_bundle")
fm = np.load(str(bundle / "feature_matrix.npz"), allow_pickle=True)

print("Keys:", list(fm.keys()))
print(f"X: shape={fm['X'].shape}, dtype={fm['X'].dtype}")
print(f"target_id: shape={fm['target_id'].shape}, dtype={fm['target_id'].dtype}")
print(f"target_id unique values: {np.unique(fm['target_id'])}")
print(f"target_id counts: {dict(zip(*np.unique(fm['target_id'], return_counts=True)))}")

# Other metadata
for k in ['culture', 'condition', 'feature_names', 'electrodes']:
    v = fm[k]
    if isinstance(v, np.ndarray):
        print(f"{k}: shape={v.shape}, dtype={v.dtype}, sample={v[:3]}")
    else:
        print(f"{k}: {v}")

# MCS features
mcs = np.load("outputs/v86_nsi_mcs_adapter/features.npy")
print(f"\nMCS features: shape={mcs.shape}, dtype={mcs.dtype}")
print(f"MCS first 3 rows:\n{mcs[:3, :6]}")
