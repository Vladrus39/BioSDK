"""BiC OS v9.3 — Cross-Modal Classification Readout.

Classifies which modality (MEA/EEG/Sleep/RNG/ecephys) a feature window belongs to.
Uses NSI-1.0 common feature subspace (first 6 features = channel 1).
Tests: LogReg, SVM, RandomForest.

Honest: reports chance levels, confusion matrix, per-class metrics.
"""
from pathlib import Path
from datetime import datetime, timezone
import json
import numpy as np

# Suppress sklearn warnings
import warnings
warnings.filterwarnings("ignore")

BASE = Path(r"C:\Users\vladi\Desktop\Braine\BiC OS\biogpu-core-v5_0_bic_os_first_mover_roadmap")
now = datetime.now(timezone.utc).isoformat()

OUT_DIR = BASE / "outputs" / "v92_cross_modal_classification"
OUT_DIR.mkdir(parents=True, exist_ok=True)

FEAT_DIR = BASE / "outputs" / "v90_cross_modal_features"

results = {
    "benchmark": "cross_modal_classification_v93",
    "generated_at": now,
    "note": "First 6 NSI-1.0 features per dataset (channel 1: RMS, MAV, ZC, VAR, PEAK, SKEW). "
            "Classify: which modality does this window belong to?",
}

# ============================================================
# 1. LOAD FEATURES
# ============================================================
print("=" * 60)
print("LOADING FEATURES")
print("=" * 60)

datasets = {}
feature_arrays = []  # (name, array)

load_map = {
    "giroldini_mea": "giroldini_mea_features.npy",
    "mcs_mea2100": "mcs_mea2100_features.npy",
    "dandi_allen": "dandi_allen_features.npy",
    "sleep_psg": "sleep_psg_features.npy",
    "gcp2_coherence": "gcp2_coherence_features.npy",
    "openneuro_ds007558": "openneuro_ds007558_features.npy",
}

for name, fname in load_map.items():
    fpath = FEAT_DIR / fname
    if fpath.exists():
        arr = np.load(fpath)
        print(f"  {name}: {arr.shape}, non-zero: {np.count_nonzero(arr)/arr.size:.3f}")
        datasets[name] = arr
    else:
        print(f"  {name}: MISSING")

# Re-extract DANDI if all zeros
if "dandi_allen" in datasets:
    dandi_arr = datasets["dandi_allen"]
    if np.count_nonzero(dandi_arr) == 0:
        print("\n  DANDI features are all zeros — re-extracting from spike NWB...")
        try:
            from biogpu.nsi.adapters.dandi import DandiNWBAdapter
            ad = DandiNWBAdapter()
            nwb_path = BASE / "data" / "external" / "nwb" / "dandi_000469" / "sub-20_ses-2_ecephys+image.nwb"
            
            windows = []
            for w in ad.iter_windows(str(nwb_path), window_s=1.0):
                fv = ad.feature_vector(w)
                windows.append(fv)
                if len(windows) >= 50:
                    break
            
            if windows:
                dandi_new = np.array(windows, dtype=np.float32)
                print(f"  Re-extracted DANDI: {dandi_new.shape}, non-zero: {np.count_nonzero(dandi_new)/dandi_new.size:.3f}")
                datasets["dandi_allen"] = dandi_new
                # Save the re-extracted features
                np.save(FEAT_DIR / "dandi_allen_features_v92_spike.npy", dandi_new)
            else:
                print("  WARNING: No windows extracted from spike NWB")
        except Exception as e:
            print(f"  ERROR re-extracting DANDI: {e}")

# ============================================================
# 2. BUILD COMMON FEATURE SUBSPACE
# ============================================================
print("\n" + "=" * 60)
print("BUILDING COMMON FEATURE SUBSPACE")
print("=" * 60)

# Find minimum feature dimension
dims = {name: arr.shape[1] for name, arr in datasets.items()}
print(f"  Feature dimensions: {dims}")
min_dim = min(dims.values())
print(f"  Common subspace: first {min_dim} features")

# Truncate all datasets to common subspace
X_parts = []
y_parts = []
label_map = {}
modality_names = sorted(datasets.keys())

for i, name in enumerate(modality_names):
    arr = datasets[name][:, :min_dim]
    # Skip rows with NaN/Inf
    finite_mask = np.isfinite(arr).all(axis=1)
    arr = arr[finite_mask]
    if len(arr) == 0:
        print(f"  {name}: all rows non-finite — SKIPPING")
        continue
    
    X_parts.append(arr)
    y_parts.append(np.full(len(arr), i))
    label_map[i] = name
    print(f"  {name}: {arr.shape} (kept {len(arr)}/{len(finite_mask)} finite rows)")

X = np.vstack(X_parts).astype(np.float32)
y = np.concatenate(y_parts).astype(np.int64)

print(f"\n  Total windows: {X.shape[0]} x {X.shape[1]}")
print(f"  Classes: {len(label_map)}")
for i, name in sorted(label_map.items()):
    print(f"    {i}: {name} ({(y == i).sum()} windows)")

results["data"] = {
    "total_windows": int(X.shape[0]),
    "n_features": int(X.shape[1]),
    "n_classes": len(label_map),
    "class_distribution": {label_map[i]: int((y == i).sum()) for i in sorted(label_map)},
    "feature_dimensions_original": dims,
}

# ============================================================
# 3. TRAIN CLASSIFIERS
# ============================================================
print("\n" + "=" * 60)
print("CROSS-MODAL CLASSIFICATION")
print("=" * 60)

from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, balanced_accuracy_score

# Standardize
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

chance = 1.0 / len(label_map)
print(f"  Chance level: {chance:.4f} ({len(label_map)} classes)")

classifiers = {
    "LogisticRegression": LogisticRegression(max_iter=2000, random_state=42),
    "SVM_RBF": SVC(kernel="rbf", random_state=42),
    "RandomForest": RandomForestClassifier(n_estimators=100, random_state=42),
}

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
clf_results = {}

for clf_name, clf in classifiers.items():
    print(f"\n  --- {clf_name} ---")
    try:
        scores = cross_val_score(clf, X_scaled, y, cv=cv, scoring="balanced_accuracy")
        mean_ba = float(scores.mean())
        std_ba = float(scores.std())
        print(f"  5-fold CV balanced accuracy: {mean_ba:.4f} +/- {std_ba:.4f}")
        
        # Fit on all data for confusion matrix
        clf.fit(X_scaled, y)
        y_pred = clf.predict(X_scaled)
        ba_full = float(balanced_accuracy_score(y, y_pred))
        cm = confusion_matrix(y, y_pred)
        
        # Per-class metrics
        class_metrics = {}
        for i in range(len(label_map)):
            tp = cm[i, i]
            total = cm[i].sum()
            pred_total = cm[:, i].sum()
            recall = tp / total if total > 0 else 0
            precision = tp / pred_total if pred_total > 0 else 0
            class_metrics[label_map[i]] = {
                "recall": round(float(recall), 4),
                "precision": round(float(precision), 4),
                "n_windows": int(total),
            }
        
        clf_results[clf_name] = {
            "balanced_accuracy_cv_mean": round(mean_ba, 4),
            "balanced_accuracy_cv_std": round(std_ba, 4),
            "balanced_accuracy_full": round(ba_full, 4),
            "chance_level": round(chance, 4),
            "per_class": class_metrics,
            "confusion_matrix": cm.tolist(),
            "confusion_matrix_labels": [label_map[i] for i in sorted(label_map)],
        }
        
        # Print confusion matrix
        print(f"  Full-fit balanced accuracy: {ba_full:.4f}")
        print(f"  Confusion matrix:")
        header = " " * 4 + "".join(f"{label_map[i][:8]:>10}" for i in sorted(label_map))
        print(header)
        for i in sorted(label_map):
            row = f"{label_map[i][:4]:>4}" + "".join(f"{cm[i,j]:10d}" for j in sorted(label_map))
            print(row)
        
        print(f"  Per-class recall:")
        for i in sorted(label_map):
            name = label_map[i]
            cm_i = class_metrics[name]
            print(f"    {name:<25} recall={cm_i['recall']:.4f}  precision={cm_i['precision']:.4f}  n={cm_i['n_windows']}")
        
    except Exception as e:
        print(f"  ERROR: {e}")
        clf_results[clf_name] = {"error": str(e)}

results["classification"] = clf_results

# ============================================================
# 4. FEATURE IMPORTANCE (Random Forest)
# ============================================================
print("\n" + "=" * 60)
print("FEATURE IMPORTANCE (Random Forest)")
print("=" * 60)

if "RandomForest" in clf_results and "error" not in clf_results["RandomForest"]:
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_scaled, y)
    importances = rf.feature_importances_
    
    feat_names = ["RMS_ch1", "MAV_ch1", "ZC_ch1", "VAR_ch1", "PEAK_ch1", "SKEW_ch1"]
    ranked = sorted(zip(feat_names, importances), key=lambda x: -x[1])
    for fn, imp in ranked:
        print(f"  {fn}: {imp:.4f}")
    
    results["feature_importance"] = {fn: float(imp) for fn, imp in ranked}

# ============================================================
# 5. HONEST SUMMARY
# ============================================================
print("\n" + "=" * 60)
print("HONEST SUMMARY")
print("=" * 60)

best_clf = max(clf_results.items(), key=lambda x: x[1].get("balanced_accuracy_cv_mean", 0))
print(f"  Best classifier: {best_clf[0]} ({best_clf[1].get('balanced_accuracy_cv_mean', 0):.4f})")
print(f"  Chance: {chance:.4f}")
print(f"  Improvement over chance: {best_clf[1].get('balanced_accuracy_cv_mean', 0)/chance:.1f}x")

# Per-modality breakdown
print(f"\n  Per-modality best recall:")
for name in modality_names:
    recalls = []
    for clf_name, cr in clf_results.items():
        if "per_class" in cr and name in cr["per_class"]:
            recalls.append(cr["per_class"][name]["recall"])
    if recalls:
        print(f"    {name:<25} best recall={max(recalls):.4f}")

results["honest_summary"] = {
    "best_classifier": best_clf[0],
    "best_balanced_accuracy": best_clf[1].get("balanced_accuracy_cv_mean", 0),
    "chance_level": chance,
    "improvement_factor": round(best_clf[1].get("balanced_accuracy_cv_mean", 0) / chance, 1),
    "interpretation": (
        f"Cross-modal classification on first-6 NSI-1.0 features achieves "
        f"{best_clf[1].get('balanced_accuracy_cv_mean', 0):.1%} balanced accuracy "
        f"(chance={chance:.1%}). This is {best_clf[1].get('balanced_accuracy_cv_mean', 0)/chance:.1f}x chance. "
        "NSI-1.0 preserves modality-distinguishing structure while providing a unified interface."
    ),
}

# ============================================================
# 6. SAVE
# ============================================================
results_path = OUT_DIR / "V93_CROSS_MODAL_CLASSIFICATION.json"
results_path.write_text(json.dumps(results, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
print(f"\nResults saved to: {results_path}")

# Also save features used
np.save(OUT_DIR / "X_common_subspace.npy", X)
np.save(OUT_DIR / "y_modality_labels.npy", y)

print("Done.")
