import numpy as np
from pathlib import Path

BASE = Path(r"C:\Users\vladi\Desktop\Braine\BiC OS\biogpu-core-v5_0_bic_os_first_mover_roadmap")

# Load the pulse feature matrix from v15 (used as source for v33)
feat_path = BASE / "evidence" / "outputs" / "realdata_zenodo_14363732_v15_readout" / "pulse_feature_matrix.npz"
if feat_path.exists():
    data = np.load(feat_path, allow_pickle=True)
    print("=== pulse_feature_matrix.npz ===")
    print(f"Keys: {list(data.keys())}")
    for k in data.keys():
        arr = data[k]
        if isinstance(arr, np.ndarray):
            print(f"  {k}: shape={arr.shape}, dtype={arr.dtype}")
            if arr.ndim == 2 and arr.shape[0] > 0:
                print(f"    first row[:10]: {arr[0, :10]}")
            elif arr.ndim == 1:
                print(f"    first 10: {arr[:10]}")
        else:
            print(f"  {k}: type={type(arr).__name__}, value={str(arr)[:200]}")
    
    # Get the feature matrix X and labels y
    if 'X' in data or 'features' in data:
        X_key = 'X' if 'X' in data else 'features'
        y_key = 'y' if 'y' in data else 'labels'
        print(f"\n  Feature matrix shape: {data[X_key].shape}")
        if y_key in data:
            print(f"  Labels shape: {data[y_key].shape}")
            print(f"  Unique labels: {np.unique(data[y_key])}")
            print(f"  Label counts: {np.bincount(data[y_key].astype(int))}")
else:
    print(f"NOT FOUND: {feat_path}")

# Also check candidate_target_readout_features
cand_path = BASE / "evidence" / "outputs" / "realdata_zenodo_14363732_v15_readout" / "candidate_target_readout_features.npz"
if cand_path.exists():
    data = np.load(cand_path, allow_pickle=True)
    print("\n=== candidate_target_readout_features.npz ===")
    print(f"Keys: {list(data.keys())}")
    for k in data.keys():
        arr = data[k]
        if isinstance(arr, np.ndarray):
            print(f"  {k}: shape={arr.shape}, dtype={arr.dtype}")
        else:
            print(f"  {k}: type={type(arr).__name__}, value={str(arr)[:200]}")

# Also check the v58 feature matrix
v58_path = BASE / "outputs" / "v58_raw_native_benchmark" / "V58_RAW_NATIVE_FEATURE_MATRIX.npz"
if v58_path.exists():
    data = np.load(v58_path, allow_pickle=True)
    print("\n=== V58_RAW_NATIVE_FEATURE_MATRIX.npz ===")
    print(f"Keys: {list(data.keys())}")
    for k in data.keys():
        arr = data[k]
        if isinstance(arr, np.ndarray):
            print(f"  {k}: shape={arr.shape}, dtype={arr.dtype}")
        else:
            print(f"  {k}: type={type(arr).__name__}")
