import json
from datetime import datetime, timezone

path = r"C:\Users\vladi\Desktop\Braine\BiC OS\biogpu-core-v5_0_bic_os_first_mover_roadmap\PROJECT_STATUS_V85.json"
with open(path, "r", encoding="utf-8") as f:
    s = json.load(f)

now = datetime.now(timezone.utc).isoformat()

s["version"] = "v9.4"
s["session_date"] = "2026-05-12"
s["generated_at"] = now

# Add FinalSpark adapter
s["nsi_adapters_v90"]["total_certified"] = 6
s["nsi_adapters_v90"]["adapters"]["finalspark_neuroplatform"] = {
    "tests": "0/0 (skeleton, pending token)",
    "modality": "mea_wetware",
    "vendor": "FinalSpark",
    "note": "Structurally complete. Awaits neuroplatform package + token.",
}
s["nsi_adapters_certified"].append(
    "finalspark_neuroplatform (MEA wetware, 8ch, 30kHz, PENDING TOKEN)"
)

s["finalspark_adapter_v94"] = {
    "adapter_id": "finalspark_neuroplatform",
    "status": "skeleton_complete",
    "blocked_by": "neuroplatform_package_private + finalspark_token",
    "file": "biogpu/nsi/adapters/finalspark/__init__.py",
    "features": [
        "full_nsi_1_0_protocol",
        "metadata_without_token",
        "spike_to_rate_matrix",
        "shannon_safety_gates_mapped",
        "stimulation_safety_check",
    ],
    "hardware": {
        "meas": 4,
        "organoids_per_mea": 4,
        "electrodes_per_mea": 8,
        "channels": 8,
        "sample_rate_hz": 30000,
        "bit_depth": 16,
        "accuracy_uv": 0.15,
        "stimulation_range": "10 nA – 2.5 mA",
    },
    "safety_mapping": {
        "biosdk_current_limit_na": 100000,
        "biosdk_charge_limit_nc": 200,
        "biosdk_freq_limit_hz": 500,
        "biosdk_duration_limit_s": 3600,
        "finalspark_range": "10 nA – 2.5 mA",
        "note": "BioSDK limit (100 uA) is within FinalSpark range",
    },
    "integration_repos": {
        "np_docs": "https://finalspark-np.github.io/np-docs/ (27 stars)",
        "np_utils": "https://github.com/FinalSpark-np/np-utils (16 stars)",
        "live_mea": "https://github.com/FinalSpark-np/LiveMEA (13 stars)",
        "publication": "Jordan et al. (2024), Frontiers in AI, doi:10.3389/frai.2024.1376042",
    },
    "next_step": "await_token_then_certify",
}

# Update gaps
s["honest_gaps_closed_this_session"].extend([
    "finalspark_nsi_adapter_skeleton_v94",
    "finalspark_shannon_safety_mapping_v94",
])

s["honest_gaps_remaining"] = [
    "cross_dataset_classification_accuracy_mcs_no_labels",
    "external_api_validation_awaiting_finalspark_token",
    "closed_loop_hardware_still_required",
    "zero_beta_participants_but_packet_ready",
]

s["next_actions_priority"] = [
    "certify_finalspark_adapter_when_token_arrives",
    "send_beta_invite_packet_to_potential_participants",
    "check_finalspark_email_for_token_response",
    "closed_loop_hardware_integration_with_finalspark",
    "cross_dataset_classification_with_labels",
]

s["bio_compute_pipeline"]["nsi_certified_adapters"] = 6

# Add FinalSpark reference details
s["references"].append({
    "title": "FinalSpark np-utils: Neuroplatform Utilities",
    "url": "https://github.com/FinalSpark-np/np-utils",
    "year": 2025,
    "stars": 16,
    "relevance": "StimParamLoader, SpikeSorting (ICA/PCA + HDBSCAN), CrossCorrelogram, StimScan. Complementary to BioSDK NSI-1.0 pipeline.",
})
s["references"].append({
    "title": "FinalSpark LiveMEA",
    "url": "https://github.com/FinalSpark-np/LiveMEA",
    "year": 2025,
    "stars": 13,
    "relevance": "Live MEA data recording utility. Python + TypeScript + Rust ports.",
})

with open(path, "w", encoding="utf-8") as f:
    json.dump(s, f, indent=2, ensure_ascii=False)

print("PROJECT_STATUS_V85.json updated to v9.4")
print(f"NSI adapters: {s['bio_compute_pipeline']['nsi_certified_adapters']}")
print(f"FinalSpark adapter: {s['finalspark_adapter_v94']['status']}")
