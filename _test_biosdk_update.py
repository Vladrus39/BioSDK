import sys
sys.path.insert(0, r"C:\Users\vladi\Desktop\Braine\BiC OS\biogpu-core-v5_0_bic_os_first_mover_roadmap")

import biosdk
print(f"BioSDK v{biosdk.__version__}")
print(f"Adapters: {biosdk.list_adapters()}")

# Test evidence_bundle
import numpy as np
result = biosdk.readout(np.random.randn(50, 6), np.random.randint(0, 3, 50))
print(f"\nReadout: ba={result['balanced_accuracy']}")
print(f"  Per-class: {result['per_class']}")

path = biosdk.evidence_bundle(result, "outputs/_biosdk_test_bundle")
print(f"\nEvidence bundle: {path}")
import json
sig = json.load(open(path / "signature.json"))
print(f"  SHA256: {sig['bundle_sha256'][:16]}...")
print(f"  HMAC: {sig['signature_hmac_sha256'][:16]}...")

# Test open with auto-detect on MCS file
try:
    ds = biosdk.open("data/external/api_exports/mcs_mea2100/2014-07-09T10-17-35W8_Standard_all_500_Hz.h5")
    print(f"\nOpen MCS: {ds.metadata.channel_count}ch, {ds.metadata.sample_rate_hz}Hz")
except Exception as e:
    print(f"\nOpen MCS: {e}")
