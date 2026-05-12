"""Test: Giroldini NSI adapter feature extraction."""
from pathlib import Path
import numpy as np

from biogpu.nsi.adapters.giroldini import GiroldiniAdapter

raw_dir = Path("data/external/raw_hdf5/11-11-2022/41438_13DIV")
test_file = raw_dir / "41438_13DIV_D-00144.h5"
print(f"Test file: {test_file}")

adapter = GiroldiniAdapter()
meta = adapter.metadata(test_file)
print(f"Channels: {meta.channel_count}, SR: {meta.sample_rate_hz} Hz, Duration: {meta.duration_s:.1f}s")

# Try 1-second windows, capture first 100
features = []
count = 0
for window in adapter.iter_windows(test_file, window_s=1.0, overlap=0.0):
    count += 1
    if count <= 5:
        print(f"Window {count}: shape={window.shape}, min={window.min():.2f}, max={window.max():.2f}")
    fv = adapter.feature_vector(window)
    features.append(fv)
    if count >= 100:
        break

features = np.array(features)
print(f"Extracted: {len(features)} windows x {features.shape[1]} features")
print(f"First 3 feature names: {adapter.open(test_file).feature_names[:3]}")
print(f"MCS has 102 features (17ch x 6). Giroldini has {features.shape[1]} features ({meta.channel_count}ch x 6).")
print(f"Common subset = first 102 features (first 17 channels)")
