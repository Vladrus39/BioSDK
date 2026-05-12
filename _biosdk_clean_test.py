import biosdk, numpy as np

MCS = r"C:\Users\vladi\Desktop\Braine\BiC OS\biogpu-core-v5_0_bic_os_first_mover_roadmap\data\external\api_exports\mcs_mea2100\2014-07-09T10-17-35W8_Standard_all_500_Hz.h5"

ds = biosdk.open(MCS)
print(f"Vendor: {ds.metadata.vendor}, Channels: {ds.metadata.channel_count}, Rate: {ds.metadata.sample_rate_hz} Hz")

X = biosdk.features(ds, window_s=0.5, max_windows=3)
print(f"Feature shape: {X.shape}, dtype: {X.dtype}")
assert X.shape == (3, 102), f"Expected (3, 102), got {X.shape}"
assert X.dtype == np.float32
assert np.all(np.isfinite(X)), "NaN in features!"
print("FEATURE EXTRACTION OK")
