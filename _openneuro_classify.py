"""OpenNeuro ds007558 — eyes-open vs eyes-closed classification pipeline."""
import sys
sys.path.insert(0, '.')
sys.stdout.reconfigure(encoding='utf-8')

from pathlib import Path
import numpy as np
import csv
from biogpu.nsi import _default_feature_vector
import mne

data_dir = Path('data/external/eeg_ds007558')
events_files = sorted(data_dir.rglob('*_events.tsv'))

label_map = {
    'Ojos cerrados': 0,
    'Ojos abiertos': 1,
}
label_names = {0: 'Cerrados', 1: 'Abiertos'}

window_s = 2.0  # 2-second windows post-onset
all_features = []
all_labels = []
all_subjects = []
subj_stats = {}

total_processed = 0
total_skipped = 0

for events_path in events_files:
    # Parse path: sub-XXX/ses-YYY/eeg/sub-XXX_ses-YYY_task-rest_events.tsv
    rel = events_path.relative_to(data_dir)
    parts = rel.parts
    subj_id = parts[0]  # sub-XXX
    ses_id = parts[1]   # ses-pre / ses-post
    
    eeg_file = events_path.parent / events_path.name.replace('_events.tsv', '_eeg.edf')
    if not eeg_file.exists():
        total_skipped += 1
        continue

    # Load EEG
    try:
        raw = mne.io.read_raw_edf(str(eeg_file), preload=True, verbose='ERROR')
    except Exception as e:
        total_skipped += 1
        continue

    sfreq = raw.info['sfreq']
    data = raw.get_data()
    window_samples = int(window_s * sfreq)
    n_channels = data.shape[0]

    # Parse events
    events = []
    with open(events_path, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            onset = float(row['onset'])
            trial = row['trial_type']
            if trial in label_map:
                events.append((onset, trial))

    if len(events) < 2:
        total_skipped += 1
        continue

    # Extract features per event
    subj_key = f"{subj_id}_{ses_id}"
    for onset, trial in events:
        start = int(onset * sfreq)
        end = start + window_samples
        if end > data.shape[1]:
            continue

        # Use first 19 channels (most common across sessions; some have 21)
        n_use = min(19, data.shape[0])
        window = data[:n_use, start:end]
        if window.shape[1] < window_samples * 0.5:
            continue

        fv = _default_feature_vector(window)
        label = label_map[trial]
        all_features.append(fv)
        all_labels.append(label)
        all_subjects.append(subj_key)

    total_processed += 1
    if total_processed <= 3:
        print(f"{subj_id}/{ses_id}: {len(events)} events, {n_channels}ch, {sfreq}Hz")

X = np.array(all_features, dtype=np.float32)
y = np.array(all_labels, dtype=np.int32)

print(f"\n{'='*60}")
print(f"Total EDF+events pairs processed: {total_processed}/{len(events_files)}")
print(f"Total labeled windows: {len(y)}")
print(f"Feature dimension: {X.shape[1]} (= {X.shape[1]//6} channels × 6 features)")
print(f"Label distribution: {dict(zip(*np.unique(y, return_counts=True)))}")
for lbl, cnt in sorted(zip(*np.unique(y, return_counts=True))):
    print(f"  {label_names[lbl]:12s}: {cnt} ({100*cnt/len(y):.1f}%)")

# Per-session stats
unique_sessions = sorted(set(all_subjects))
print(f"\nTotal sessions: {len(unique_sessions)}")

# ── Classification ──
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold, cross_val_score, LeaveOneGroupOut
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Map session IDs to group indices
session_to_idx = {s: i for i, s in enumerate(unique_sessions)}
groups = np.array([session_to_idx[s] for s in all_subjects])

print(f"\n--- 5-fold CV (mixed sessions) ---")
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
for name, clf in [
    ("RandomForest", RandomForestClassifier(n_estimators=100, random_state=42)),
    ("LogisticReg", LogisticRegression(max_iter=2000, random_state=42)),
    ("SVM", SVC(kernel='rbf', random_state=42)),
]:
    scores = cross_val_score(clf, X_scaled, y, cv=cv, scoring='balanced_accuracy')
    print(f"  {name:15s}: {scores.mean():.4f} ± {scores.std():.4f}")

print(f"\n--- Leave-One-Session-Out (cross-session) ---")
logo = LeaveOneGroupOut()
for name, clf in [
    ("RandomForest", RandomForestClassifier(n_estimators=100, random_state=42)),
]:
    scores = cross_val_score(clf, X_scaled, y, groups=groups, cv=logo, scoring='balanced_accuracy')
    print(f"  {name:15s}: {scores.mean():.4f} ± {scores.std():.4f}")

# ── Save ──
out_dir = Path('outputs/v93_openneuro_eeg')
out_dir.mkdir(parents=True, exist_ok=True)
np.save(out_dir / 'X_features.npy', X)
np.save(out_dir / 'y_labels.npy', y)
np.save(out_dir / 'groups.npy', np.array(all_subjects))

import json
results = {
    "task": "eyes_open_vs_closed",
    "dataset": "OpenNeuro ds007558 — EEG Pre/Post Intervention",
    "doi": "doi:10.18112/openneuro.ds007558.v1.0.0",
    "total_windows": int(len(y)),
    "feature_dim": int(X.shape[1]),
    "n_channels": n_channels,
    "window_s": window_s,
    "label_distribution": {label_names[l]: int(c) for l, c in zip(*np.unique(y, return_counts=True))},
    "chance": 0.50,
}
(out_dir / 'V93_OPENNEURO_EEG_RESULTS.json').write_text(
    json.dumps(results, indent=2, ensure_ascii=False), encoding='utf-8'
)
print(f"\nSaved to {out_dir}")
print("Done — OpenNeuro EEG classification complete.")
