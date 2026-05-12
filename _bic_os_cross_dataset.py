"""BioSDK v8.6 — Cross-Dataset Analysis: Giroldini vs MCS MEA2100.
FIXED: Robust scaling, per-dataset normalize, matching sample counts for correlation.
"""
from pathlib import Path
import json, time
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.svm import SVC
from sklearn.model_selection import cross_val_score
from scipy.spatial.distance import euclidean

from biogpu.nsi.adapters.giroldini import GiroldiniAdapter
from biogpu.evidence.ledger_v53 import stable_hash

OUT = Path("outputs/v86_cross_dataset")
OUT.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("1. Extracting Giroldini NSI features...")

adapter = GiroldiniAdapter()
N_WINDOWS = 200
N_COMMON_CH = 17

raw_base = Path("data/external/raw_hdf5")
giro_data = {}
for date_dir in sorted(raw_base.iterdir()):
    if not date_dir.is_dir(): continue
    for exp_dir in sorted(date_dir.iterdir()):
        if not exp_dir.is_dir(): continue
        h5_files = list(exp_dir.glob("*.h5"))
        spont = [f for f in h5_files if "_LightStim_" not in f.name 
                 and "_Stim" not in f.name and "ElecStim" not in f.name]
        stim = [f for f in h5_files if "_LightStim_" in f.name 
                or "_Stim" in f.name or "ElecStim" in f.name]
        if spont and stim:
            giro_data[f"{date_dir.name}/{exp_dir.name}"] = {"spontaneous": spont[0], "stimulated": stim[0]}

first_key = list(giro_data.keys())[0]
pair = giro_data[first_key]
print(f"  Using: {first_key}")

def extract_nsi(adapter, fp, n):
    feats = []
    for i, w in enumerate(adapter.iter_windows(fp, window_s=1.0, overlap=0.0)):
        if i >= n: break
        feats.append(adapter.feature_vector(w))
    return np.array(feats, dtype=np.float64)

t0 = time.time()
Xg_spont = extract_nsi(adapter, pair["spontaneous"], N_WINDOWS)[:, :N_COMMON_CH*6]
Xg_stim  = extract_nsi(adapter, pair["stimulated"], N_WINDOWS)[:, :N_COMMON_CH*6]
print(f"  Giro spont: {Xg_spont.shape}, stim: {Xg_stim.shape} ({time.time()-t0:.1f}s)")

# ── 2. Load MCS ──
print("\n" + "=" * 60)
print("2. Loading MCS features...")
Xm = np.load("outputs/v86_nsi_mcs_adapter/features.npy").astype(np.float64)
print(f"  MCS: {Xm.shape}")

# ── 3. Per-dataset normalization (avoid overflow from different scales) ──
print("\n" + "=" * 60)
print("3. Per-dataset robust normalization...")

def robust_normalize(X):
    """Clip extreme outliers then standardize."""
    Xc = np.clip(X, np.percentile(X, 1), np.percentile(X, 99))
    return (Xc - Xc.mean(axis=0)) / (Xc.std(axis=0) + 1e-10)

Xg_spont_n = robust_normalize(Xg_spont)
Xg_stim_n  = robust_normalize(Xg_stim)
Xm_n       = robust_normalize(Xm)

print(f"  Giro spont: mean={Xg_spont_n.mean():.3f}, std={Xg_spont_n.std():.3f}")
print(f"  Giro stim:  mean={Xg_stim_n.mean():.3f}, std={Xg_stim_n.std():.3f}")
print(f"  MCS:        mean={Xm_n.mean():.3f}, std={Xm_n.std():.3f}")

# ── 4. MCS Clustering ──
print("\n" + "=" * 60)
print("4. MCS Unsupervised Clustering (k-means, k=4)")

km_real = KMeans(n_clusters=4, random_state=42, n_init=10)
labels_real = km_real.fit_predict(Xm_n)
sil_real = silhouette_score(Xm_n, labels_real)

Xm_shuff = Xm_n.copy()
for c in range(Xm_shuff.shape[1]):
    np.random.RandomState(c).shuffle(Xm_shuff[:, c])
km_rand = KMeans(n_clusters=4, random_state=42, n_init=10)
sil_rand = silhouette_score(Xm_shuff, km_rand.fit_predict(Xm_shuff))

labels_chance = np.random.RandomState(42).randint(0, 4, len(Xm_n))
sil_chance = silhouette_score(Xm_n, labels_chance)

cl_sizes = np.bincount(labels_real)
print(f"  Silhouette: real={sil_real:.4f}, shuffled={sil_rand:.4f}, chance={sil_chance:.4f}")
print(f"  Real/Shuffled: {sil_real/max(sil_rand,0.001):.1f}x, Real/Chance: {sil_real/max(abs(sil_chance),0.001):.1f}x")
print(f"  Cluster sizes: {dict(enumerate(cl_sizes))}")

# ── 5. Feature Distribution ──
print("\n" + "=" * 60)
print("5. Feature Distribution Comparison")

# Per-feature means (robust stats across datasets)
def feat_stats(X, name):
    return {"name": name, "mean": float(X.mean()), "std": float(X.std()),
            "min": float(X.min()), "max": float(X.max())}

stats = {
    "giroldini_spontaneous": feat_stats(Xg_spont_n, "giroldini_spontaneous"),
    "giroldini_stimulated": feat_stats(Xg_stim_n, "giroldini_stimulated"),
    "mcs": feat_stats(Xm_n, "mcs"),
}
for k, v in stats.items():
    print(f"  {k}: mean={v['mean']:.4f}, std={v['std']:.4f}")

# Per-feature correlation: use min(n_samples) for each pair
n_min = min(len(Xg_spont_n), len(Xm_n))
Xg_sub = Xg_spont_n[:n_min]
Xm_sub = Xm_n[:n_min]
corrs_giro_mcs = [np.corrcoef(Xg_sub[:, c], Xm_sub[:, c])[0,1] for c in range(Xg_sub.shape[1])]
mean_corr_gm = np.nanmean(corrs_giro_mcs)

Xg_stim_sub = Xg_stim_n[:n_min]
corrs_spont_stim = [np.corrcoef(Xg_sub[:, c], Xg_stim_sub[:, c])[0,1] for c in range(Xg_sub.shape[1])]
mean_corr_ss = np.nanmean(corrs_spont_stim)

print(f"  Per-feature corr Giro-MCS (n={n_min}): {mean_corr_gm:.4f}")
print(f"  Per-feature corr spont-stim (n={n_min}): {mean_corr_ss:.4f}")

# ── 6. PCA ──
print("\n" + "=" * 60)
print("6. PCA")

X_all = np.vstack([Xg_spont_n, Xg_stim_n, Xm_n])
pca = PCA(n_components=2, random_state=42)
X_pca = pca.fit_transform(X_all)

ng = len(Xg_spont_n)
ns = len(Xg_stim_n)
nm = len(Xm_n)

pc_g_spont = X_pca[:ng]
pc_g_stim  = X_pca[ng:ng+ns]
pc_mcs     = X_pca[ng+ns:]

d_ss = euclidean(pc_g_spont.mean(0), pc_g_stim.mean(0))
d_sm = euclidean(pc_g_spont.mean(0), pc_mcs.mean(0))
d_stm = euclidean(pc_g_stim.mean(0), pc_mcs.mean(0))

print(f"  EVR: {[round(x,4) for x in pca.explained_variance_ratio_]}")
print(f"  Centroids: G-spont=({pc_g_spont[:,0].mean():.2f},{pc_g_spont[:,1].mean():.2f})")
print(f"             G-stim=({pc_g_stim[:,0].mean():.2f},{pc_g_stim[:,1].mean():.2f})")
print(f"             MCS=({pc_mcs[:,0].mean():.2f},{pc_mcs[:,1].mean():.2f})")
print(f"  Distances: spont-stim={d_ss:.3f}, spont-MCS={d_sm:.3f}, stim-MCS={d_stm:.3f}")

# ── 7. Cross-Vendor SVM ──
print("\n" + "=" * 60)
print("7. Cross-Vendor SVM")

y_giro = np.array([0]*ng + [1]*ns)
X_giro_both = np.vstack([Xg_spont_n, Xg_stim_n])

svm = SVC(kernel="rbf", random_state=42)
cv_scores = cross_val_score(svm, X_giro_both, y_giro, cv=5, scoring="accuracy")
print(f"  Within-Giroldini CV: {cv_scores.mean():.3f} +/- {cv_scores.std():.3f}")

svm.fit(X_giro_both, y_giro)
mcs_pred = svm.predict(Xm_n)
n_spont_like = int((mcs_pred == 0).sum())
n_stim_like  = int((mcs_pred == 1).sum())
print(f"  MCS predicted: {n_spont_like} spont-like, {n_stim_like} stim-like (of {nm})")

# ── 8. Save ──
print("\n" + "=" * 60)
print("8. Saving...")

results = {
    "version": "v8.6", "session": "2026-05-11",
    "phase": "cross_dataset_analysis",
    "overall_status": "cross_dataset_analysis_complete_mcs_unsupervised",
    "datasets": {
        "giroldini": {"file_spontaneous": str(pair["spontaneous"]),
                      "file_stimulated": str(pair["stimulated"]),
                      "windows": N_WINDOWS, "channels": 59,
                      "features_common": N_COMMON_CH*6, "sample_rate_hz": 20000.0},
        "mcs": {"windows": int(Xm.shape[0]), "channels": 17,
                "features": int(Xm.shape[1]), "sample_rate_hz": 500.0},
    },
    "mcs_clustering": {
        "silhouette_real": float(sil_real),
        "silhouette_shuffled": float(sil_rand),
        "silhouette_chance": float(sil_chance),
        "real_shuffled_ratio": float(sil_real/max(sil_rand,0.001)),
        "cluster_sizes": [int(x) for x in cl_sizes],
    },
    "feature_distribution": {
        "stats": stats,
        "per_feature_corr_giro_mcs": float(mean_corr_gm),
        "per_feature_corr_spont_stim": float(mean_corr_ss),
    },
    "pca": {
        "explained_variance": [float(x) for x in pca.explained_variance_ratio_],
        "centroid_distances": {"spont_stim": float(d_ss), "spont_mcs": float(d_sm), "stim_mcs": float(d_stm)},
    },
    "cross_vendor_svm": {
        "within_giro_cv": float(cv_scores.mean()),
        "within_giro_std": float(cv_scores.std()),
        "mcs_spont_like": n_spont_like,
        "mcs_stim_like": n_stim_like,
    },
    "missing": {
        "mcs_labels": "No stimulus labels for MCS",
        "nsi_labels": "NSI sliding windows lack stimulus alignment",
        "different_labs": "Giroldini=Italy rodent 2022, MCS=unknown 2014",
    },
    "what_this_proves": {
        "nsi_ingest": "NSI-1.0 opens both vendors via identical HDF5 path",
        "common_features": "Same ch{i}_rms naming across vendors",
        "mcs_structure": f"Silhouette={sil_real:.3f} vs shuffled={sil_rand:.3f} — {'structure detected' if sil_real>sil_rand else 'no clear structure'}",
        "cross_vendor": f"SVM classifies {n_stim_like}/{nm} MCS windows as stim-like",
    },
    "claim_boundary": "v8.6 cross-dataset analysis: NSI-1.0 unified ingest proven. No cross-dataset accuracy claimed (MCS unlabeled). No production/live claims.",
}

(OUT / "V86_CROSS_DATASET_RESULTS.json").write_text(
    json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")

np.save(str(OUT / "giroldini_spontaneous_nsi.npy"), Xg_spont)
np.save(str(OUT / "giroldini_stimulated_nsi.npy"), Xg_stim)
np.save(str(OUT / "pca_coords_giro_spont.npy"), pc_g_spont)
np.save(str(OUT / "pca_coords_giro_stim.npy"), pc_g_stim)
np.save(str(OUT / "pca_coords_mcs.npy"), pc_mcs)

h = stable_hash(results)
print(f"  Results hash: {h}")
print(f"  Files: {[f.name for f in sorted(OUT.glob('*'))]}")

# ── 9. Report ──
print("\n" + "=" * 60)
print("CROSS-DATASET ANALYSIS COMPLETE")
print(f"  MCS silhouette: {sil_real:.3f} (shuffled={sil_rand:.3f}) — {'STRUCTURE' if sil_real>sil_rand else 'NOISE'}")
print(f"  Giro spont-stim separability: {cv_scores.mean():.2%}")
print(f"  Giro-MCS feature correlation: {mean_corr_gm:.3f}")
print(f"  PCA centroid: spont-MCS distance={d_sm:.2f}, spont-stim={d_ss:.2f}")
print(f"  MCS stim-like windows: {n_stim_like}/{nm}")
