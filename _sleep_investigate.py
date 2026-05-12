"""Sleep PSG — hypnogram parsing + sleep stage classification. Fixed for annotation format."""
import sys
sys.path.insert(0, '.')
sys.stdout.reconfigure(encoding='utf-8')

from pathlib import Path
import numpy as np

try:
    import mne
    print(f"MNE version: {mne.__version__}")
except ImportError:
    print("MNE not installed.")
    sys.exit(1)

data_dir = Path('data/external/sleep_psg')
psg_files = sorted(data_dir.glob('*E0-PSG.edf'))
hyp_files = sorted(data_dir.glob('*Hypnogram.edf'))

# ── Load PSG and hypnogram using MNE's annotation reader ──
for subj_idx, (psg_path, hyp_path) in enumerate(zip(psg_files, hyp_files)):
    print(f"\n{'='*60}")
    print(f"Subject {subj_idx + 1}: {psg_path.name}")

    # Load PSG
    raw = mne.io.read_raw_edf(str(psg_path), preload=True, verbose='ERROR')
    print(f"PSG: {raw.info['nchan']}ch, {raw.info['sfreq']}Hz, {raw.n_times/raw.info['sfreq']/3600:.1f}h")
    print(f"Channels: {raw.ch_names}")

    # Try to read hypnogram as annotations from the hypnogram EDF
    # First, try using mne.read_annotations
    try:
        annot = mne.read_annotations(str(hyp_path))
        print(f"Annotations loaded: {len(annot)} events")
        print(f"  Samples: {annot.onset[:5]}...")
        print(f"  Descriptions: {set(annot.description)}")
    except Exception as e1:
        print(f"read_annotations failed: {e1}")
        # Fallback: try reading the hyp file as raw with its single channel
        try:
            hyp_raw = mne.io.read_raw_edf(str(hyp_path), preload=True, verbose='ERROR')
            print(f"Hyp raw: {hyp_raw.ch_names}, shape={hyp_raw.get_data().shape}")
            hyp_data = hyp_raw.get_data()[0]
            print(f"Hyp unique values: {sorted(set(hyp_data.astype(int)))}")
            print(f"Stage distribution: {dict(zip(*np.unique(hyp_data.astype(int), return_counts=True)))}")
        except Exception as e2:
            print(f"Fallback also failed: {e2}")
            continue

print("\nDone — investigation complete.")
