"""Conformance tests for FinalSpark NSI-1.0 adapter.

Tests the adapter skeleton WITHOUT requiring a real token or hardware.
All tests use metadata-only mode (token=None).

NSI-1.0 Conformance Protocol:
    1. Adapter registration
    2. metadata() returns valid NSIMetadata
    3. open() returns NSIDataset with correct shapes
    4. feature_vector() returns correct dimensions
    5. iter_windows() yields valid arrays (when data available)
    6. Safety gates: check_stimulation_safety()
    7. Feature naming consistency
    8. Graceful failure without token
"""
import sys
sys.path.insert(0, r"C:\Users\vladi\Desktop\Braine\BiC OS\biogpu-core-v5_0_bic_os_first_mover_roadmap")

from biogpu.nsi.adapters.finalspark import FinalSparkAdapter, FINALSPARK_SPECS
import numpy as np

PASS, FAIL = 0, 0

def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  [PASS] {name}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name} — {detail}")

print("=" * 60)
print("FinalSpark NSI-1.0 Conformance Tests")
print("(metadata-only mode — no token)")
print("=" * 60)

ad = FinalSparkAdapter(token=None)

# ─── Test 1: Adapter registration ───
print("\n--- Test 1: Adapter Registration ---")
check("adapter_id is 'finalspark_neuroplatform'",
      ad.adapter_id == "finalspark_neuroplatform", ad.adapter_id)
check("vendor is 'finalspark'",
      ad.vendor == "finalspark", ad.vendor)
check("modality is 'mea_wetware'",
      ad.modality == "mea_wetware", ad.modality)

# ─── Test 2: Metadata without token ───
print("\n--- Test 2: Metadata (no token) ---")
meta = ad.metadata("mea_0")
check("channel_count == 8", meta.channel_count == 8, str(meta.channel_count))
check("sample_rate_hz == 30000", meta.sample_rate_hz == 30000, str(meta.sample_rate_hz))
check("source_format is 'neuroplatform_api'",
      meta.source_format == "neuroplatform_api", meta.source_format)
check("vendor is 'finalspark'",
      meta.vendor == "finalspark", meta.vendor)
check("token_configured is False",
      meta.extra.get("token_configured") == False, str(meta.extra.get("token_configured")))
check("extra contains platform info",
      "platform" in meta.extra and "FinalSpark" in meta.extra["platform"])

# ─── Test 3: Metadata for different MEAs ───
print("\n--- Test 3: Metadata for all 4 MEAs ---")
for mea_id in ["mea_0", "mea_1", "mea_2", "mea_3"]:
    m = ad.metadata(mea_id)
    check(f"metadata({mea_id}) returns valid NSIMetadata",
          m.channel_count == 8 and m.sample_rate_hz == 30000)

# ─── Test 4: open() without token ───
print("\n--- Test 4: open() without token (metadata-only) ---")
ds = ad.open("mea_0")
check("open() returns NSIDataset", ds is not None)
check("dataset has metadata", ds.metadata is not None)
check("dataset has data (zeros — no token)", ds.data is not None)
check("data shape is (8, 1000) — zeros placeholder",
      ds.data.shape == (8, 1000), str(ds.data.shape))
check("feature_names generated", len(ds.feature_names) > 0)
check("feature_names count matches channels",
      len(ds.feature_names) == 8 * 6, str(len(ds.feature_names)))

# ─── Test 5: feature_vector() ───
print("\n--- Test 5: feature_vector() on synthetic window ---")
window = np.random.randn(8, 30000).astype(np.float32)  # 8ch x 1s @ 30kHz
fv = ad.feature_vector(window)
check("feature_vector returns ndarray", isinstance(fv, np.ndarray))
check("feature dimension = 48 (8ch x 6feat)",
      len(fv) == 48, str(len(fv)))
check("features are finite", np.isfinite(fv).all())
check("RMS >= 0", fv[0] >= 0, str(fv[0]))  # RMS is always positive

# ─── Test 6: Safety gates — safe params ───
print("\n--- Test 6: Safety gates — SAFE parameters ---")
safe = ad.check_stimulation_safety(
    current_na=50_000,   # 50 uA
    charge_nc=100,       # 100 nC
    freq_hz=200,         # 200 Hz
    duration_s=600,      # 10 min
)
check("safe params: safe=True", safe["safe"] == True)
check("safe params: 0 violations", len(safe["violations"]) == 0)
check("safe params: returns limits", "limits" in safe)

# ─── Test 7: Safety gates — unsafe params ───
print("\n--- Test 7: Safety gates — UNSAFE parameters ---")
unsafe = ad.check_stimulation_safety(
    current_na=150_000,  # 150 uA — VIOLATION
    charge_nc=300,       # 300 nC — VIOLATION
    freq_hz=1000,        # 1000 Hz — VIOLATION
    duration_s=7200,     # 2 hours — VIOLATION
)
check("unsafe params: safe=False", unsafe["safe"] == False)
check("unsafe params: 4 violations", len(unsafe["violations"]) == 4,
      f"got {len(unsafe['violations'])}")
check("current violation detected",
      any("Current" in v for v in unsafe["violations"]))
check("charge violation detected",
      any("Charge" in v for v in unsafe["violations"]))
check("frequency violation detected",
      any("Frequency" in v for v in unsafe["violations"]))
check("duration violation detected",
      any("Duration" in v for v in unsafe["violations"]))

# ─── Test 8: Connection fails gracefully ───
print("\n--- Test 8: Connection without neuroplatform package ---")
connected = ad.connect()
check("connect() returns False (no package)", connected == False)
check("is_connected is False", ad.is_connected == False)

# ─── Test 9: iter_windows() without token ───
print("\n--- Test 9: iter_windows() without token (empty) ---")
windows = list(ad.iter_windows("mea_0", window_s=1.0))
check("iter_windows returns empty (no token)", len(windows) == 0)

# ─── Test 10: Hardware specs reference ───
print("\n--- Test 10: FINALSPARK_SPECS reference ---")
check("specs has platform name", "FinalSpark" in FINALSPARK_SPECS["platform"])
check("specs: 4 MEAs", FINALSPARK_SPECS["meas"] == 4)
check("specs: 8 electrodes", FINALSPARK_SPECS["electrodes_per_mea"] == 8)
check("specs: 30 kHz", FINALSPARK_SPECS["sample_rate_hz"] == 30000)
check("specs: 16-bit", FINALSPARK_SPECS["bit_depth"] == 16)
check("specs: publication doi", "10.3389" in FINALSPARK_SPECS["publication"])

# ─── SUMMARY ───
print("\n" + "=" * 60)
print(f"RESULTS: {PASS} PASS, {FAIL} FAIL — {PASS}/{PASS+FAIL} conformance tests")
if FAIL == 0:
    print("STATUS: ALL TESTS PASS — adapter skeleton is NSI-1.0 conformant")
else:
    print(f"STATUS: {FAIL} FAILURES — adapter needs fixes")
print("=" * 60)
