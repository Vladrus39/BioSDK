"""Sleep PSG — hypnogram parsing + sleep stage classification."""
import sys
sys.path.insert(0, '.')
sys.stdout.reconfigure(encoding='utf-8')

from pathlib import Path
import numpy as np

# Check MNE availability
try:
    import mne
    print(f"MNE version: {mne.__version__}")
except ImportError:
    print("MNE not installed. Install: pip install mne")
    sys.exit(1)

data_dir = Path('data/external/sleep_psg')
psg_files = sorted(data_dir.glob('*E0-PSG.edf'))
hyp_files = sorted(data_dir.glob('*Hypnogram.edf'))

print(f"\nSubjects: {len(psg_files)}")
for pf, hf in zip(psg_files, hyp_files):
    print(f"  {pf.name} + {hf.name}")

# Load first subject
print("\n--- Loading subject 1 ---")
psg_path = str(psg_files[0])
hyp_path = str(hyp_files[0])

raw = mne.io.read_raw_edf(psg_path, preload=False, verbose='ERROR')
print(f"PSG: {raw.info['nchan']} channels, {raw.info['sfreq']} Hz, {raw.n_times} samples, {raw.n_times / raw.info['sfreq'] / 3600:.1f}h")

# Print channel names
print(f"Channels: {raw.ch_names}")

# Load hypnogram
hyp = mne.io.read_raw_edf(hyp_path, preload=False, verbose='ERROR')
print(f"\nHypnogram: {hyp.info['nchan']} channels, {hyp.info['sfreq']} Hz, {hyp.n_times} samples")
print(f"Hypnogram channels: {hyp.ch_names}")

# Read annotation data
hyp_data = hyp.get_data()
print(f"Hypnogram shape: {hyp_data.shape}")
print(f"Hypnogram unique values: {np.unique(hyp_data)}")

# Map to sleep stages (standard Sleep-EDF mapping)
# PhysioNet Sleep-EDF uses: W=0, 1=N1, 2=N2, 3=N3, 4=N3, R=REM, ?=unknown
stage_map = {
    0: 'W',    # Wake
    1: 'N1',   # Stage 1
    2: 'N2',   # Stage 2
    3: 'N3',   # Stage 3 (deep sleep)
    4: 'N3',   # Stage 4 (merged with N3)
    5: 'REM',  # REM
}
print(f"\nStage mapping: W=0, N1=1, N2=2, N3=3/4, REM=5")

# Count stage distribution
stages = hyp_data[0]  # first channel is the annotation
for val, name in sorted(stage_map.items()):
    count = np.sum(stages == val)
    if count > 0:
        print(f"  Stage {name} (label={val}): {count} epochs ({count * 30 / 3600:.1f}h)")

# Sample rate of hypnogram is 1 epoch per 30 seconds (typical)
# So each sample = 30s of PSG data
psg_sfreq = raw.info['sfreq']
epoch_s = 30.0
epoch_samples = int(epoch_s * psg_sfreq)

print(f"\nPSG sample rate: {psg_sfreq} Hz")
print(f"Hypnogram epoch: {epoch_s}s = {epoch_samples} PSG samples")
print(f"Total epochs: {len(stages)}")
print(f"PSG samples per epoch: {epoch_samples}")

# Now load the full PSG data
print("\n--- Loading full PSG data ---")
raw.load_data()
data = raw.get_data()
print(f"PSG data shape: {data.shape}")

# For the EDF adapter, we want windows aligned with the hypnogram
# Let's extract features per epoch
from biogpu.nsi import _default_feature_vector

# Check what channels are EEG (not EMG, EOG, etc.)
# Typically: EEG Fpz-Cz, Pz-Oz; EOG horizontal; EMG submental; Resp oro-nasal; Temp rectal; Event marker
eeg_channels = [ch for ch in raw.ch_names if 'EEG' in ch.upper() or ch in ('Fpz-Cz', 'Pz-Oz')]
if not eeg_channels:
    # Default: use all channels
    eeg_channels = raw.ch_names[:2]  # First 2 are typically EEG
print(f"Using EEG channels: {eeg_channels}")

# Get indices of EEG channels
eeg_idx = [raw.ch_names.index(ch) for ch in eeg_channels]
print(f"EEG channel indices: {eeg_idx}")

# Extract features for each 30s epoch
print("\n--- Extracting NSI-1.0 features per epoch ---")
features = []
labels = []
valid_epochs = 0

for i, stage_val in enumerate(stages):
    start = i * epoch_samples
    end = start + epoch_samples
    if end > data.shape[1]:
        break
    if stage_val not in stage_map:
        continue
    window = data[eeg_idx, start:end]
    fv = _default_feature_vector(window)  # shape: (n_channels * 6,)
    features.append(fv)
    labels.append(stage_val)
    valid_epochs += 1

features = np.array(features, dtype=np.float32)
labels = np.array(labels, dtype=np.int32)

print(f"Valid epochs: {valid_epochs}")
print(f"Features shape: {features.shape}")
print(f"Label distribution: {dict(zip(*np.unique(labels, return_counts=True)))}")

# Save
out_dir = Path('outputs/v93_sleep_psg_staging')
out_dir.mkdir(parents=True, exist_ok=True)
np.save(out_dir / 'features_sc4001.npy', features)
np.save(out_dir / 'labels_sc4001.npy', labels)
print(f"\nSaved to {out_dir}")

print("\nDone — Sleep PSG features extracted.")
