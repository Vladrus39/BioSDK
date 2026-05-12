"""Quick test: DandiNWBAdapter on Allen NWB."""
from biogpu.nsi.adapters.dandi import DandiNWBAdapter

allen = "data/external/allen/dandi_000021/sub-703279277_ses-719161530_probe-729445654_ecephys.nwb"
adapter = DandiNWBAdapter()
meta = adapter.metadata(allen)
print(f"Channels: {meta.channel_count}")
print(f"Sample rate: {meta.sample_rate_hz} Hz")
print(f"Duration: {meta.duration_s:.1f}s ({meta.duration_s/60:.1f} min)")
print(f"Format: {meta.source_format}")
print(f"Extra: {meta.extra}")

# Extract 5 windows
count = 0
for window in adapter.iter_windows(allen, window_s=1.0):
    count += 1
    print(f"  Window {count}: shape={window.shape}")
    if count >= 3:
        break
print(f"OK: {count} windows extracted")
