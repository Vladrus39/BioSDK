import json
from pathlib import Path

# Load status
s = json.load(open('PROJECT_STATUS_V85.json', encoding='utf-8'))
print(f"Version: {s['version']}")
print(f"NSI conformance: {s['bio_compute_pipeline']['nsi_conformance_tests_pass']}")
print(f"Evidence bundle: {s['bio_compute_pipeline']['evidence_bundle_verified']}")
print(f"Cross-modal features: {s['bio_compute_pipeline']['cross_modal_features_extracted']}")

# Gaps remaining
print(f"\nGaps remaining: {len(s['honest_gaps_remaining'])}")
for g in s['honest_gaps_remaining']:
    print(f"  - {g}")

# NSI adapters
print(f"\nNSI adapters certified: {s['nsi_adapters_v90']['total_certified']}")
print(f"Conformance total: {s['nsi_adapters_v90']['conformance_total']}")

# Cross-modal
print(f"\nCross-modal feature dims: {s['bio_compute_pipeline']['cross_modal_feature_dims']}")

# Tressoldi
t = s['tressoldi_classification_v91']
print(f"\nTressoldi EEG classification:")
print(f"  Within-pair mean: {t['results']['within_pair_mean_balanced_acc']}")
print(f"  Cross-pair LOPO: {t['results']['cross_pair_lopo_balanced_acc']}")

# Cross-modal analysis
cm = s['cross_modal_analysis_v92']
print(f"\nCross-modal analysis:")
print(f"  MEA cluster corr: {cm['findings']['mea_cluster_correlation']}")
print(f"  EEG cluster corr: {cm['findings']['eeg_cluster_correlation']}")
print(f"  Cross-modal corr: {cm['findings']['cross_modal_correlation']}")

# FinalSpark
fs = s['external_api_platforms_v89']['platforms']['finalspark_remote_wetware']
print(f"\nFinalSpark:")
print(f"  Application: {fs['application_status']}")
print(f"  Token configured: {fs['token_configured']}")
print(f"  Note: {fs['note']}")

# Next actions
print(f"\nNext actions priority:")
for a in s['next_actions_priority']:
    print(f"  - {a}")
