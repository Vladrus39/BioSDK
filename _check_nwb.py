from pathlib import Path

BASE = Path(r"C:\Users\vladi\Desktop\Braine\BiC OS\biogpu-core-v5_0_bic_os_first_mover_roadmap")

# Check NWB files
nwb_dir = BASE / "data" / "external" / "nwb"
print(f"NWB dir exists: {nwb_dir.exists()}")
if nwb_dir.exists():
    for f in sorted(nwb_dir.rglob("*.nwb")):
        size_mb = f.stat().st_size / (1024*1024)
        try:
            rel = f.relative_to(BASE)
        except ValueError:
            rel = str(f)
        print(f"  {rel} ({size_mb:.1f} MB)")

# Check Tressoldi
t_dir = BASE / "data" / "external" / "tressoldi_h3"
print(f"\nTressoldi dir exists: {t_dir.exists()}")
if t_dir.exists():
    xlsx = list(t_dir.rglob("*.xlsx"))
    print(f"  XLSX files: {len(xlsx)}")
    for x in xlsx[:5]:
        print(f"    {x.name}")

# Check DANDI adapter
try:
    from biogpu.nsi.adapters.dandi import DandiNWBAdapter
    print("\nDANDI adapter: imported OK")
    
    ad = DandiNWBAdapter()
    nwb_path = nwb_dir / "dandi_000469" / "sub-20_ses-2_ecephys+image.nwb"
    if nwb_path.exists():
        print(f"\nOpening spike NWB: {nwb_path.name}")
        ds = ad.open(str(nwb_path))
        meta = ds.metadata
        print(f"  Channels: {meta.channel_count}")
        print(f"  Sample rate: {meta.sample_rate_hz} Hz")
        print(f"  Duration: {meta.duration_s:.0f}s")
        print(f"  Data shape: {ds.data.shape}")
        print(f"  Feature names: {len(ds.feature_names)}")
        
        # Get some windows
        n_windows = 0
        for w in ad.iter_windows(str(nwb_path), window_s=1.0):
            n_windows += 1
        print(f"  Windows (1s): {n_windows}")
    else:
        print(f"\nSpike NWB NOT FOUND at {nwb_path}")
        
except Exception as e:
    import traceback
    print(f"\nDANDI adapter ERROR: {e}")
    traceback.print_exc()
