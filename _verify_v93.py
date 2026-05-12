import json
r = json.load(open(r"outputs/v92_cross_modal_classification/V93_CROSS_MODAL_CLASSIFICATION.json", encoding="utf-8"))
print(f"Best classifier: {r['honest_summary']['best_classifier']}")
print(f"Best accuracy: {r['honest_summary']['best_balanced_accuracy']}")
print(f"Chance: {r['honest_summary']['chance_level']}")
print(f"Improvement: {r['honest_summary']['improvement_factor']}x")

# Verify PROJECT_STATUS_V85.json
s = json.load(open("PROJECT_STATUS_V85.json", encoding="utf-8"))
print(f"\nProject version: {s['version']}")
print(f"Cross-modal classification: {s.get('cross_modal_classification_v93', {}).get('results', {}).get('RandomForest_balanced_accuracy_cv')}")
print(f"Beta packet: {s.get('beta_invite_packet_v93', {}).get('created')}")
print(f"Gaps remaining: {len(s['honest_gaps_remaining'])}")
for g in s['honest_gaps_remaining']:
    print(f"  - {g}")
