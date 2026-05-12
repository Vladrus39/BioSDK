"""Sleep PSG — full sleep stage classification pipeline."""
import sys
sys.path.insert(0, '.')
sys.stdout.reconfigure(encoding='utf-8')

from pathlib import Path
import numpy as np
import mne
from biogpu.nsi import _default_feature_vector

data_dir = Path('data/external/sleep_psg')
psg_files = sorted(data_dir.glob('*E0-PSG.edf'))
hyp_files = sorted(data_dir.glob('*Hypnogram.edf'))

stage_label_map = {
    'Sleep stage W': 0,
    'Sleep stage 1': 1,
    'Sleep stage 2': 2,
    'Sleep stage 3': 3,
    'Sleep stage 4': 3,  # merged with N3
    'Sleep stage R': 4,
    'Sleep stage ?': -1,
    'Movement time': -1,
}
stage_names = {0: 'Wake', 1: 'N1', 2: 'N2', 3: 'N3', 4: 'REM'}

all_features = []
all_labels = []
all_subjects = []
epoch_s = 30.0

for subj_idx, (psg_path, hyp_path) in enumerate(zip(psg_files, hyp_files)):
    print(f"\nSubject {subj_idx + 1}: {psg_path.stem}")

    raw = mne.io.read_raw_edf(str(psg_path), preload=True, verbose='ERROR')
    sfreq = raw.info['sfreq']
    data = raw.get_data()
    eeg_idx = [0, 1]  # EEG Fpz-Cz, EEG Pz-Oz
    epoch_samples = int(epoch_s * sfreq)

    annot = mne.read_annotations(str(hyp_path))

    subj_features = []
    subj_labels = []
    skipped = 0

    for onset_sec, duration_sec, desc in zip(annot.onset, annot.duration, annot.description):
        label = stage_label_map.get(desc, -1)
        if label < 0:
            skipped += 1
            continue

        start_sample = int(onset_sec * sfreq)
        end_sample = start_sample + int(duration_sec * sfreq)
        if end_sample > data.shape[1]:
            skipped += 1
            continue

        window = data[eeg_idx, start_sample:end_sample]
        if window.shape[1] < epoch_samples * 0.5:
            skipped += 1
            continue

        fv = _default_feature_vector(window)
        subj_features.append(fv)
        subj_labels.append(label)

    subj_features = np.array(subj_features, dtype=np.float32)
    subj_labels = np.array(subj_labels, dtype=np.int32)

    print(f"  EEG channels: {eeg_idx[0]}-{eeg_idx[1]}")
    print(f"  Feature dim: {subj_features.shape[1] if len(subj_features) else 0}")
    print(f"  Valid epochs: {len(subj_labels)} (skipped {skipped})")
    for lbl, cnt in sorted(zip(*np.unique(subj_labels, return_counts=True))):
        print(f"    {stage_names[lbl]:6s}: {cnt} epochs ({cnt*30/60:.0f} min)")

    all_features.append(subj_features)
    all_labels.append(subj_labels)
    all_subjects.extend([subj_idx] * len(subj_labels))

# ── Merge both subjects ──
X = np.vstack(all_features)
y = np.concatenate(all_labels)
subjects = np.array(all_subjects)

print(f"\n{'='*60}")
print(f"Total: {X.shape[0]} epochs × {X.shape[1]} features ({X.shape[1]//2} features/ch × 2 EEG channels)")
print(f"Label distribution:")
for lbl, cnt in sorted(zip(*np.unique(y, return_counts=True))):
    print(f"  {stage_names[lbl]:6s}: {cnt} ({100*cnt/len(y):.1f}%)")

# ── Classification ──
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold, cross_val_score, LeaveOneGroupOut
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import balanced_accuracy_score, classification_report

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Approach 1: 5-fold CV (mixed subjects — optimistic!)
print(f"\n--- Approach 1: 5-fold CV (within-subject) ---")
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
for clf_name, clf in [
    ("RandomForest", RandomForestClassifier(n_estimators=100, random_state=42)),
]:
    scores = cross_val_score(clf, X_scaled, y, cv=cv, scoring='balanced_accuracy')
    print(f"  {clf_name}: {scores.mean():.4f} ± {scores.std():.4f}")

# Approach 2: Leave-One-Subject-Out (honest cross-subject)
print(f"\n--- Approach 2: Leave-One-Subject-Out (cross-subject) ---")
logo = LeaveOneGroupOut()
for clf_name, clf in [
    ("RandomForest", RandomForestClassifier(n_estimators=100, random_state=42)),
]:
    scores = cross_val_score(clf, X_scaled, y, groups=subjects, cv=logo, scoring='balanced_accuracy')
    print(f"  {clf_name}: {scores.mean():.4f} ± {scores.std():.4f}")

# Approach 3: Per-subject CV
print(f"\n--- Approach 3: Per-subject CV ---")
for subj_idx in np.unique(subjects):
    mask = subjects == subj_idx
    X_s = X_scaled[mask]
    y_s = y[mask]
    if len(np.unique(y_s)) < 2:
        print(f"  Subject {subj_idx}: only 1 class, skipping")
        continue
    cv_s = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    scores = cross_val_score(rf, X_s, y_s, cv=cv_s, scoring='balanced_accuracy')
    print(f"  Subject {subj_idx} ({len(y_s)} epochs): RF = {scores.mean():.4f} ± {scores.std():.4f}")

# ── Save ──
out_dir = Path('outputs/v93_sleep_psg_staging')
out_dir.mkdir(parents=True, exist_ok=True)
np.save(out_dir / 'X_features.npy', X)
np.save(out_dir / 'y_labels.npy', y)
np.save(out_dir / 'subjects.npy', subjects)

import json
results = {
    "task": "sleep_stage_classification",
    "dataset": "PhysioNet Sleep-EDF",
    "subjects": len(psg_files),
    "total_epochs": int(len(y)),
    "feature_dim": int(X.shape[1]),
    "channels_used": 2,
    "channel_names": ["EEG Fpz-Cz", "EEG Pz-Oz"],
    "stage_distribution": {stage_names[l]: int(c) for l, c in zip(*np.unique(y, return_counts=True))},
    "chance_5class": 0.20,
}
(out_dir / 'V93_SLEEP_STAGING_RESULTS.json').write_text(
    json.dumps(results, indent=2, ensure_ascii=False), encoding='utf-8'
)
print(f"\nSaved to {out_dir}")

print("\nDone — Sleep PSG staging complete.")
