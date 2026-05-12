import sys
sys.path.insert(0, r"C:\Users\vladi\Desktop\Braine\BiC OS\biogpu-core-v5_0_bic_os_first_mover_roadmap")

# Test import
from biogpu.nsi.adapters.finalspark import FinalSparkAdapter, FINALSPARK_SPECS

# Metadata-only mode (no token)
ad = FinalSparkAdapter(token=None)
print(f"Adapter ID: {ad.adapter_id}")
print(f"Vendor: {ad.vendor}")
print(f"Modality: {ad.modality}")
print(f"Connected: {ad.is_connected}")

# Test metadata (should work without token)
meta = ad.metadata("mea_0")
print(f"\nMetadata (no token):")
print(f"  Channels: {meta.channel_count}")
print(f"  Sample rate: {meta.sample_rate_hz} Hz")
print(f"  Format: {meta.source_format}")
print(f"  Token configured: {meta.extra['token_configured']}")
print(f"  Connected: {meta.extra['connected']}")

# Test safety check
safety = ad.check_stimulation_safety(
    current_na=50_000,   # 50 uA — safe
    charge_nc=100,       # 100 nC — safe
    freq_hz=200,         # 200 Hz — safe
    duration_s=600,      # 10 min — safe
)
print(f"\nSafety check (safe params): {safety['safe']} (violations: {len(safety['violations'])})")

safety2 = ad.check_stimulation_safety(
    current_na=150_000,  # 150 uA — VIOLATION
    charge_nc=300,       # 300 nC — VIOLATION
    freq_hz=1000,        # 1000 Hz — VIOLATION
    duration_s=7200,     # 2 hours — VIOLATION
)
print(f"Safety check (unsafe params): {safety2['safe']} (violations: {len(safety2['violations'])})")
for v in safety2['violations']:
    print(f"  - {v}")

# Test connection attempt (will fail without neuroplatform package)
connected = ad.connect()
print(f"\nConnection attempt: {connected} (expected: False — no neuroplatform package)")

# List all adapters
from biogpu.nsi.adapters import list_adapters
adapters = list_adapters()
print(f"\nAll adapters ({len(adapters)}):")
for a in adapters:
    print(f"  - {a}")

# Hardware specs
print(f"\nFinalSpark specs:")
for k, v in FINALSPARK_SPECS.items():
    print(f"  {k}: {v}")
