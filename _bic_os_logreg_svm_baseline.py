"""
BioSDK v8.5 — HONEST BASELINE: sklearn LogReg + SVM on REAL v33 data.
Replicates the EXACT same 90-run sweep (6 splits x 5 ablations),
but with sklearn classifiers instead of BioSDK decoders.
"""
import numpy as np
from pathlib import Path
from datetime import datetime, timezone
import json, time, sys

BASE = Path(r"C:\Users\vladi\Desktop\Braine\BiC OS\biogpu-core-v5_0_bic_os_first_mover_roadmap")

# ── Load data ──
print("Loading v33 feature matrix...", flush=True)
feat = np.load(
    BASE / "evidence" / "outputs" / "realdata_zenodo_14363732_v15_readout" / "pulse_feature_matrix.npz",
    allow_pickle=True
)
X_full = feat['X']          # (11547, 354) float32
target_id = feat['target_id']  # (11547,)  int64
feature_names = feat['feature_names']  # (354,)   object

# ── Load split catalog ──
sc = json.loads(
    (BASE / "outputs" / "powerpc_stage1_v33_compact" / "split_catalog_v33.json").read_text()
)

# ── Ablation: map ablation_id → feature column indices ──
ablations = {
    "all_features":       list(range(354)),   # all 354 features
    "response_delta_count": [i for i, fn in enumerate(feature_names) if "response_delta_count" in str(fn)],
    "response_count":      [i for i, fn in enumerate(feature_names) if "response_count_" in str(fn) and "response_delta_count" not in str(fn)],
    "pre_response_count":  [i for i, fn in enumerate(feature_names) if "pre_response_count" in str(fn)],
    "exact_features":      [i for i, fn in enumerate(feature_names) if "count_e0" in str(fn) or "count_e1" in str(fn)],
}
print(f"Ablation feature counts: { {k: len(v) for k, v in ablations.items()} }")

# ── sklearn imports ──
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.dummy import DummyClassifier
from sklearn.preprocessing import StandardScaler

# ── RUN ALL 90 BASELINES ──
results = []
run_id = 0
total = 6 * 5  # splits × ablations
now = datetime.now(timezone.utc).isoformat()

for split_entry in sc:
    split_id = split_entry["split_id"]
    train_idx = np.array(split_entry["train_idx"])
    test_idx = np.array(split_entry["test_idx"])
    
    # Get the actual target labels for this split's indices
    y_train_full = target_id[train_idx]
    y_test_full = target_id[test_idx]
    
    # Map target_ids to contiguous class indices (0, 1, 2, ...)
    all_targets = np.unique(np.concatenate([y_train_full, y_test_full]))
    target_to_class = {t: i for i, t in enumerate(all_targets)}
    y_train = np.array([target_to_class[t] for t in y_train_full])
    y_test = np.array([target_to_class[t] for t in y_test_full])
    n_labels = len(all_targets)
    
    for abl_id, feat_cols in ablations.items():
        run_id += 1
        n_feat = len(feat_cols)
        X_train = X_full[train_idx][:, feat_cols]
        X_test = X_full[test_idx][:, feat_cols]
        
        # Scale features
        scaler = StandardScaler()
        X_train_s = scaler.fit_transform(X_train)
        X_test_s = scaler.transform(X_test)
        
        entry = {
            "split_id": split_id,
            "ablation_id": abl_id,
            "n_train": len(train_idx),
            "n_test": len(test_idx),
            "n_labels": n_labels,
            "n_features": n_feat,
            "chance_approx": round(1.0 / n_labels, 4),
        }
        
        # Dummy
        dummy = DummyClassifier(strategy="stratified", random_state=42)
        dummy.fit(X_train_s, y_train)
        entry["dummy_accuracy"] = round(float(dummy.score(X_test_s, y_test)), 6)
        
        # LogisticRegression
        t0 = time.time()
        lr = LogisticRegression(max_iter=5000, random_state=42, n_jobs=-1)
        lr.fit(X_train_s, y_train)
        entry["logreg_accuracy"] = round(float(lr.score(X_test_s, y_test)), 6)
        entry["logreg_time_s"] = round(time.time() - t0, 2)
        
        # SVM (linear for speed, since n_features can be large)
        t0 = time.time()
        try:
            svm = SVC(kernel="linear", random_state=42, max_iter=5000)
            svm.fit(X_train_s, y_train)
            entry["svm_accuracy"] = round(float(svm.score(X_test_s, y_test)), 6)
            entry["svm_time_s"] = round(time.time() - t0, 2)
        except Exception as e:
            entry["svm_accuracy"] = None
            entry["svm_error"] = str(e)[:200]
            entry["svm_time_s"] = round(time.time() - t0, 2)
        
        results.append(entry)
        
        print(f"  [{run_id}/{total}] {split_id:30s} | {abl_id:25s} | "
              f"labels={n_labels} | feat={n_feat:3d} | "
              f"chance={entry['chance_approx']:.3f} | "
              f"dummy={entry['dummy_accuracy']:.3f} | "
              f"LR={entry['logreg_accuracy']:.4f} | "
              f"SVM={entry['svm_accuracy']}", flush=True)

# ── Aggregate ──
print("\n" + "=" * 70)
print("AGGREGATE RESULTS (mean over all 30 runs)")
print("=" * 70)

# Group by ablation
for abl_id in ablations:
    abl_results = [r for r in results if r["ablation_id"] == abl_id]
    lr_accs = [r["logreg_accuracy"] for r in abl_results]
    svm_accs = [r["svm_accuracy"] for r in abl_results if r["svm_accuracy"] is not None]
    
    print(f"\n  {abl_id} ({len(abl_results)} runs):")
    print(f"    LogReg: mean={np.mean(lr_accs):.4f}, std={np.std(lr_accs):.4f}, "
          f"best={max(lr_accs):.4f}, worst={min(lr_accs):.4f}")
    if svm_accs:
        print(f"    SVM:    mean={np.mean(svm_accs):.4f}, std={np.std(svm_accs):.4f}, "
              f"best={max(svm_accs):.4f}, worst={min(svm_accs):.4f}")

# Overall aggregate
all_lr = [r["logreg_accuracy"] for r in results]
all_svm = [r["svm_accuracy"] for r in results if r["svm_accuracy"] is not None]
print(f"\n  OVERALL ({len(results)} runs):")
print(f"    LogReg: mean={np.mean(all_lr):.4f}, std={np.std(all_lr):.4f}, best={max(all_lr):.4f}")
if all_svm:
    print(f"    SVM:    mean={np.mean(all_svm):.4f}, std={np.std(all_svm):.4f}, best={max(all_svm):.4f}")

# ── Compare with v33 BioSDK results ──
v33_sweep = json.loads(
    (BASE / "outputs" / "powerpc_stage1_v33_compact" / "sweep_summary_v33.json").read_text()
)

print("\n" + "=" * 70)
print("COMPARISON: BioSDK v33 vs sklearn baselines")
print("=" * 70)

comparison = {
    "title": "BioSDK v33 Honest Baseline — sklearn LogReg + SVM on REAL v33 data",
    "generated_at": now,
    "dataset": "Giroldini MEA (Zenodo 14363732)",
    "dimensions": {"samples": 11547, "features": 354, "cultures": 18},
    "v33_sweep": {
        "n_runs": 90,
        "splits": 6,
        "ablations": 5,
        "decoders": ["centroid_euclidean", "centroid_cosine", "diag_gaussian"],
        "aggregate_by_decoder": v33_sweep["aggregate_by_decoder"],
        "best_run": v33_sweep["best_run"],
    },
    "sklearn_baselines": {
        "n_runs": len(results),
        "overall_logreg_mean": round(float(np.mean(all_lr)), 4),
        "overall_logreg_std": round(float(np.std(all_lr)), 4),
        "overall_logreg_best": round(float(max(all_lr)), 4),
        "overall_svm_mean": round(float(np.mean(all_svm)), 4) if all_svm else None,
        "overall_svm_std": round(float(np.std(all_svm)), 4) if all_svm else None,
        "overall_svm_best": round(float(max(all_svm)), 4) if all_svm else None,
    },
    "per_ablation_logreg": {
        abl_id: {
            "mean": round(float(np.mean([r["logreg_accuracy"] for r in results if r["ablation_id"] == abl_id])), 4),
            "best": round(float(max([r["logreg_accuracy"] for r in results if r["ablation_id"] == abl_id])), 4),
        }
        for abl_id in ablations
    },
    "per_ablation_svm": {
        abl_id: {
            "mean": round(float(np.mean([r["svm_accuracy"] for r in results if r["ablation_id"] == abl_id and r["svm_accuracy"] is not None])), 4),
            "best": round(float(max([r["svm_accuracy"] for r in results if r["ablation_id"] == abl_id and r["svm_accuracy"] is not None])), 4),
        }
        for abl_id in ablations
    },
    "results": results,
}

# ── Save ──
out_dir = Path("analysis_output_v0_7")
out_dir.mkdir(parents=True, exist_ok=True)

out_path = out_dir / "v33_honest_baseline_logreg_svm.json"
out_path.write_text(json.dumps(comparison, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
print(f"\nSaved to: {out_path}")

# ── Markdown report ──
md = [
    f"# BioSDK v33 — Honest Baseline: sklearn on Real Data",
    f"",
    f"Generated: {now}",
    f"",
    f"## Summary",
    f"",
    f"- **Dataset**: Giroldini MEA (Zenodo 14363732), 11,547 samples × 354 features",
    f"- **Runs**: {len(results)} (6 culture-holdout splits × 5 feature ablations)",
    f"- **Task**: classify stimulated electrode from multi-electrode response",
    f"",
    f"## Overall Results (mean over {len(results)} run-configs)",
    f"",
    f"| Classifier | Mean Accuracy | Std | Best |",
    f"|------------|--------------|-----|------|",
    f"| Dummy (chance) | — | — | — |",
    f"| LogisticRegression | {np.mean(all_lr):.4f} | {np.std(all_lr):.4f} | {max(all_lr):.4f} |",
]
if all_svm:
    md.append(f"| SVM (linear) | {np.mean(all_svm):.4f} | {np.std(all_svm):.4f} | {max(all_svm):.4f} |")

md.extend([
    f"",
    f"## v33 BioSDK Results (for reference)",
    f"",
    f"| Decoder | Mean Accuracy | Best |",
    f"|---------|--------------|------|",
])
for d in v33_sweep["aggregate_by_decoder"]:
    md.append(f"| {d['decoder_id']} | {d['mean_accuracy']:.4f} | {d['best_accuracy']:.4f} |")

md.extend([
    f"",
    f"## Per-Ablation LogReg",
    f"",
    f"| Ablation | Features | LogReg Mean | LogReg Best |",
    f"|----------|----------|------------|------------|",
])
for abl_id in ablations:
    a = [r for r in results if r["ablation_id"] == abl_id]
    md.append(f"| {abl_id} | {len(ablations[abl_id])} | {np.mean([r['logreg_accuracy'] for r in a]):.4f} | {max([r['logreg_accuracy'] for r in a]):.4f} |")

md.extend([
    f"",
    f"## Honest Assessment",
    f"",
    f"This baseline runs sklearn LogisticRegression and SVM on the EXACT same data,",
    f"splits, and feature ablations that the BioSDK v33 sweep used.",
    f"The comparison is apples-to-apples: same train/test indices, same feature subsets.",
    f"",
    f"BioSDK's diag_gaussian decoder is effectively a 2-layer MLP with diagonal covariance.",
    f"Comparing it against LogisticRegression (linear) and SVM (linear kernel) tests whether",
    f"the problem is linearly separable or benefits from non-linear modeling.",
])

md_path = out_dir / "v33_honest_baseline_logreg_svm.md"
md_path.write_text("\n".join(md), encoding="utf-8")
print(f"Saved to: {md_path}")
print("\nDone.")
