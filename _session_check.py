"""Quick session check — prints project status."""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('PROJECT_STATUS_V85.json', encoding='utf-8') as f:
    s = json.load(f)

print(f"Version: {s['version']}")
print(f"NSI conformance: {s['bio_compute_pipeline']['nsi_conformance_tests_pass']}")
print(f"Evidence bundle: {s['bio_compute_pipeline']['evidence_bundle_verified']}")
print(f"Cross-modal features: {s['bio_compute_pipeline']['cross_modal_features_extracted']}")
print()
print(f"Gaps remaining: {len(s['honest_gaps_remaining'])}")
for g in s['honest_gaps_remaining']:
    print(f"  - {g}")
print()
print(f"NSI adapters certified: {len(s['nsi_adapters_certified'])}")
print(f"GitHub: {'https://github.com/Vladrus39/BioSDK'}")
print(f"PyPI: https://test.pypi.org/project/biosdk/")
print(f"Deploy: python _deploy.py")
