import json
from datetime import datetime, timezone

path = r"C:\Users\vladi\Desktop\Braine\BiC OS\biogpu-core-v5_0_bic_os_first_mover_roadmap\PROJECT_STATUS_V85.json"
with open(path, "r", encoding="utf-8") as f:
    s = json.load(f)

now = datetime.now(timezone.utc).isoformat()

# Update version
s["version"] = "v9.3"
s["session_date"] = "2026-05-12"
s["generated_at"] = now

# Add cross-modal classification v9.3
s["cross_modal_classification_v93"] = {
    "benchmark": "cross_modal_classification_v93",
    "n_datasets": 6,
    "n_windows": 269,
    "common_features": 6,
    "chance_level": 0.1667,
    "results": {
        "RandomForest_balanced_accuracy_cv": 0.9433,
        "RandomForest_std": 0.0389,
        "LogisticRegression_balanced_accuracy_cv": 0.7006,
        "SVM_RBF_balanced_accuracy_cv": 0.6872,
        "improvement_over_chance": "5.7x",
        "hardest_class": "sleep_psg (recall 0.82)",
        "easiest_classes": "giroldini_mea, gcp2_coherence, dandi_allen, mcs_mea2100 (recall 1.00)",
    },
    "feature_importance": {
        "ZC_ch1": 0.2387,
        "MAV_ch1": 0.1848,
        "VAR_ch1": 0.1580,
        "PEAK_ch1": 0.1493,
        "RMS_ch1": 0.1363,
        "SKEW_ch1": 0.1330,
    },
    "honest_interpretation": "NSI-1.0 first-6 features are sufficient to distinguish modalities with 94.3% accuracy. Modality identity is preserved.",
    "output": "outputs/v92_cross_modal_classification/V93_CROSS_MODAL_CLASSIFICATION.json",
}

# Add beta invite packet
s["beta_invite_packet_v93"] = {
    "created": True,
    "file": "beta/BETA_INVITE_PACKET_V93.md",
    "includes": [
        "positioning_as_Vulkan_for_wetware",
        "quickstart_v93",
        "5_certified_adapters",
        "cross_modal_validation_94_3_percent",
        "closed_loop_ready",
        "feedback_form",
    ],
    "note": "Ready to send to potential beta participants. Includes FinalSpark reference.",
}

# Update honest gaps
s["honest_gaps_closed_this_session"].extend([
    "cross_modal_classification_94_3_percent_v93",
    "beta_invite_packet_created_v93",
])

s["honest_gaps_remaining"] = [
    "cross_dataset_classification_accuracy_mcs_no_labels",
    "external_api_validation_awaiting_finalspark_token",
    "closed_loop_hardware_still_required",
    "zero_beta_participants_but_packet_ready",
]

# Update next actions
s["next_actions_priority"] = [
    "send_beta_invite_packet_to_potential_participants",
    "check_finalspark_email_for_token_response",
    "closed_loop_hardware_integration_when_token_available",
    "cross_dataset_classification_with_labels",
    "nsi_adapter_for_finalspark_neuroplatform",
]

# Update bio compute pipeline
s["bio_compute_pipeline"]["cross_modal_classification_accuracy"] = 0.9433
s["bio_compute_pipeline"]["cross_modal_classification_chance"] = 0.1667
s["bio_compute_pipeline"]["cross_modal_classification_improvement"] = "5.7x"
s["bio_compute_pipeline"]["beta_invite_packet_created"] = True

# Add FinalSpark reference
s["references"].append({
    "title": "FinalSpark Neuroplatform Documentation",
    "url": "https://finalspark-np.github.io/np-docs/welcome.html",
    "year": 2025,
    "relevance": "Python API for remote wetware. Closed-loop reading+stimulating. InfluxDB. NSI-1.0 adapter target.",
})

with open(path, "w", encoding="utf-8") as f:
    json.dump(s, f, indent=2, ensure_ascii=False)

print("PROJECT_STATUS_V85.json updated to v9.3")
print(f"Version: {s['version']}")
print(f"Cross-modal classification: {s['cross_modal_classification_v93']['results']['RandomForest_balanced_accuracy_cv']}")
print(f"Beta packet: {s['beta_invite_packet_v93']['created']}")
print(f"Gaps remaining: {len(s['honest_gaps_remaining'])}")
