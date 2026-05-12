import numpy as np, h5py
p = r"data\external\nwb\dandi_000469\sub-20_ses-2_ecephys+image.nwb"
with h5py.File(p) as f:
    st = f["units"]["spike_times"]
    sti = f["units"]["spike_times_index"]
    print(f"Spike times: shape={st.shape}, n_spikes={st.shape[0]}")
    print(f"Spike times: min={st[0]:.4f}, max={st[-1]:.4f}")
    print(f"Spike index: shape={sti.shape}, n_units={sti.shape[0]}")
    # Unit spike counts
    counts = np.diff(sti, prepend=0)
    print(f"Unit spike counts: min={counts.min()}, max={counts.max()}, mean={counts.mean():.1f}")
    print(f"Non-empty units: {(counts > 0).sum()}/{len(counts)}")
    print(f"Spike time samples: {st[:20]}")
