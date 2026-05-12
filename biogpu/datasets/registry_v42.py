"""BioGPU-Core v4.2 dataset registry.

This module is intentionally lightweight and safe: it does not download data,
open vendor sessions, or perform live biological control. It describes which
sources the SDK can support and what must happen on the power-PC/API stages.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
import csv
import json


class DatasetSourceKindV42(str, Enum):
    PUBLIC_ARCHIVE = "public_archive"
    API_READ_ONLY = "api_read_only"
    VENDOR_EXPORT = "vendor_export"
    USER_UPLOAD = "user_upload"
    LAB_APPROVED = "lab_approved"


class DatasetAccessModeV42(str, Enum):
    METADATA_ONLY = "metadata_only"
    READ_ONLY_REPLAY = "read_only_replay"
    LIVE_SHADOW_READ_ONLY = "live_shadow_read_only"
    APPROVED_LIVE_CONTROL = "approved_live_control"


@dataclass(frozen=True)
class DatasetImportPlanV42:
    importer_id: str
    expected_input_formats: List[str]
    produces: str
    power_pc_required: bool
    external_credentials_required: bool
    live_control_required: bool
    validation_steps: List[str] = field(default_factory=list)
    notes: str = ""

    def validate(self) -> List[str]:
        errors: List[str] = []
        if not self.importer_id:
            errors.append("importer_id is required")
        if not self.expected_input_formats:
            errors.append(f"{self.importer_id}: expected_input_formats cannot be empty")
        if self.live_control_required:
            errors.append(f"{self.importer_id}: v4.2 import plans must not require live control")
        return errors


@dataclass(frozen=True)
class DatasetRegistryEntryV42:
    dataset_id: str
    display_name: str
    source_kind: DatasetSourceKindV42
    access_mode: DatasetAccessModeV42
    status: str
    import_plan: DatasetImportPlanV42
    primary_benchmarks: List[str]
    claim_level: str
    beta_release_priority: str
    blockers: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)

    def validate(self) -> List[str]:
        errors: List[str] = []
        if not self.dataset_id:
            errors.append("dataset_id is required")
        if self.access_mode == DatasetAccessModeV42.APPROVED_LIVE_CONTROL:
            errors.append(f"{self.dataset_id}: v4.2 registry cannot expose approved live control")
        errors.extend(self.import_plan.validate())
        if self.beta_release_priority not in {"P0", "P1", "P2", "P3"}:
            errors.append(f"{self.dataset_id}: beta_release_priority must be P0/P1/P2/P3")
        return errors

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["source_kind"] = self.source_kind.value
        d["access_mode"] = self.access_mode.value
        return d


class BioGPUDatasetRegistryV42:
    def __init__(self, entries: Iterable[DatasetRegistryEntryV42]):
        self.entries: Dict[str, DatasetRegistryEntryV42] = {e.dataset_id: e for e in entries}

    def validate(self) -> List[str]:
        errors: List[str] = []
        if not self.entries:
            return ["registry cannot be empty"]
        for entry in self.entries.values():
            errors.extend(entry.validate())
        if len(self.entries) != len(set(self.entries.keys())):
            errors.append("duplicate dataset_id detected")
        return errors

    def by_priority(self, priority: str) -> List[DatasetRegistryEntryV42]:
        return [e for e in self.entries.values() if e.beta_release_priority == priority]

    def by_access_mode(self, access_mode: DatasetAccessModeV42) -> List[DatasetRegistryEntryV42]:
        return [e for e in self.entries.values() if e.access_mode == access_mode]

    def to_list(self) -> List[Dict[str, Any]]:
        return [self.entries[k].to_dict() for k in sorted(self.entries)]

    def write_json(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_list(), ensure_ascii=False, indent=2), encoding="utf-8")

    def write_csv(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        fields = [
            "dataset_id", "display_name", "source_kind", "access_mode", "status",
            "importer_id", "produces", "power_pc_required", "external_credentials_required",
            "live_control_required", "primary_benchmarks", "claim_level", "beta_release_priority",
            "blockers"
        ]
        with path.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            for e in self.entries.values():
                w.writerow({
                    "dataset_id": e.dataset_id,
                    "display_name": e.display_name,
                    "source_kind": e.source_kind.value,
                    "access_mode": e.access_mode.value,
                    "status": e.status,
                    "importer_id": e.import_plan.importer_id,
                    "produces": e.import_plan.produces,
                    "power_pc_required": e.import_plan.power_pc_required,
                    "external_credentials_required": e.import_plan.external_credentials_required,
                    "live_control_required": e.import_plan.live_control_required,
                    "primary_benchmarks": ";".join(e.primary_benchmarks),
                    "claim_level": e.claim_level,
                    "beta_release_priority": e.beta_release_priority,
                    "blockers": ";".join(e.blockers),
                })


def build_default_dataset_registry_v42() -> BioGPUDatasetRegistryV42:
    entries = [
        DatasetRegistryEntryV42(
            dataset_id="zenodo_14363732_preprocessed",
            display_name="Zenodo 14363732 preprocessed MEA spike-times/features",
            source_kind=DatasetSourceKindV42.PUBLIC_ARCHIVE,
            access_mode=DatasetAccessModeV42.READ_ONLY_REPLAY,
            status="available_in_project_compact",
            import_plan=DatasetImportPlanV42(
                importer_id="zenodo_preprocessed_v42",
                expected_input_formats=["zip", "csv", "json", "npz"],
                produces="BioGPUTrace/BioGPUFeatureMatrix",
                power_pc_required=False,
                external_credentials_required=False,
                live_control_required=False,
                validation_steps=["schema_check", "culture_lineage_parse", "feature_matrix_shape", "shuffled_baseline"],
                notes="Primary current real-data source used by v3.2-v3.6.",
            ),
            primary_benchmarks=["pulse_window_readout", "lineage_strict_replay", "shuffle_controls"],
            claim_level="software_replay_only",
            beta_release_priority="P0",
            blockers=[],
        ),
        DatasetRegistryEntryV42(
            dataset_id="zenodo_14363732_raw_hdf5",
            display_name="Zenodo 14363732 raw MEA HDF5/TTL reconstruction",
            source_kind=DatasetSourceKindV42.PUBLIC_ARCHIVE,
            access_mode=DatasetAccessModeV42.READ_ONLY_REPLAY,
            status="deferred_power_pc",
            import_plan=DatasetImportPlanV42(
                importer_id="zenodo_raw_hdf5_v42",
                expected_input_formats=["zip", "h5", "hdf5"],
                produces="BioGPURawTrace + reconstructed stimulus_windows.csv",
                power_pc_required=True,
                external_credentials_required=False,
                live_control_required=False,
                validation_steps=["hdf5_tree_scan", "ttl_channel_detection", "raw_vs_preprocessed_alignment", "pulse_window_rebuild"],
                notes="Large raw archive; should run on workstation/server, not lightweight chat environment.",
            ),
            primary_benchmarks=["raw_pulse_reconstruction", "preprocessed_consistency", "latency_window_sensitivity"],
            claim_level="raw_data_validation_pending",
            beta_release_priority="P0",
            blockers=["download_large_archive", "inspect_hdf5_schema", "ttl_or_protocol_mapping"],
        ),
        DatasetRegistryEntryV42(
            dataset_id="dandi_nwb_discovery",
            display_name="DANDI/NWB task-aligned discovery datasets",
            source_kind=DatasetSourceKindV42.PUBLIC_ARCHIVE,
            access_mode=DatasetAccessModeV42.READ_ONLY_REPLAY,
            status="skeleton_ready_discovery_needed",
            import_plan=DatasetImportPlanV42(
                importer_id="dandi_nwb_v42",
                expected_input_formats=["nwb", "dandiset_asset"],
                produces="BioGPUTaskAlignedTrace",
                power_pc_required=True,
                external_credentials_required=False,
                live_control_required=False,
                validation_steps=["dandiset_search", "nwb_units_check", "intervals_trials_stimulus_check", "task_window_export"],
                notes="Use DANDI discovery to find datasets with units + intervals/trials/stimulus.",
            ),
            primary_benchmarks=["task_aligned_readout", "trial_category_decoding", "cross_session_generalization"],
            claim_level="multi_dataset_validation_pending",
            beta_release_priority="P1",
            blockers=["select_3_to_5_dandisets", "download_sample_assets", "schema_variance_handling"],
        ),
        DatasetRegistryEntryV42(
            dataset_id="allen_visual_coding_orientation",
            display_name="Allen Brain Observatory / AllenSDK visual-coding benchmark",
            source_kind=DatasetSourceKindV42.PUBLIC_ARCHIVE,
            access_mode=DatasetAccessModeV42.READ_ONLY_REPLAY,
            status="skeleton_ready_download_needed",
            import_plan=DatasetImportPlanV42(
                importer_id="allen_visual_coding_v42",
                expected_input_formats=["allensdk_cache", "nwb"],
                produces="BioGPUOrientationBenchmarkTrace",
                power_pc_required=True,
                external_credentials_required=False,
                live_control_required=False,
                validation_steps=["stimulus_presentations_extract", "spike_times_extract", "orientation_label_map", "heldout_session_split"],
                notes="Maps naturally to orientation-like synthetic benchmarks.",
            ),
            primary_benchmarks=["orientation_decoding", "temporal_frequency_decoding", "natural_movie_response_profile"],
            claim_level="external_neurophysiology_validation_pending",
            beta_release_priority="P1",
            blockers=["install_allensdk", "cache_size_budget", "select_sessions"],
        ),
        DatasetRegistryEntryV42(
            dataset_id="finalspark_readonly_export",
            display_name="FinalSpark read-only/export/live-shadow data",
            source_kind=DatasetSourceKindV42.API_READ_ONLY,
            access_mode=DatasetAccessModeV42.LIVE_SHADOW_READ_ONLY,
            status="mock_client_ready_credentials_needed",
            import_plan=DatasetImportPlanV42(
                importer_id="finalspark_export_v42",
                expected_input_formats=["hdf5", "api_trace", "spike_events"],
                produces="BioGPUTrace from remote wetware read-only stream/export",
                power_pc_required=False,
                external_credentials_required=True,
                live_control_required=False,
                validation_steps=["metadata_read", "electrode_list_read", "spike_event_read", "hdf5_export_parse", "read_only_safety_gate"],
                notes="No actuation in v4.2; first enterprise bridge to external wetware platform.",
            ),
            primary_benchmarks=["live_shadow_readout", "activity_profile", "result_bundle_from_external_api"],
            claim_level="api_readonly_validation_pending",
            beta_release_priority="P1",
            blockers=["partner_access", "api_token", "data_use_terms"],
        ),
        DatasetRegistryEntryV42(
            dataset_id="vendor_exports_mcs_3brain_axion",
            display_name="Vendor export adapters: MCS / 3Brain / Axion",
            source_kind=DatasetSourceKindV42.VENDOR_EXPORT,
            access_mode=DatasetAccessModeV42.READ_ONLY_REPLAY,
            status="schema_skeleton_ready_vendor_samples_needed",
            import_plan=DatasetImportPlanV42(
                importer_id="vendor_export_v42",
                expected_input_formats=["csv", "h5", "hdf5", "nwb", "vendor_export_folder"],
                produces="BioGPUTrace/BioGPURawTrace from vendor-exported recordings",
                power_pc_required=False,
                external_credentials_required=False,
                live_control_required=False,
                validation_steps=["sample_export_collection", "schema_inference", "channel_map_parse", "trace_or_spike_export"],
                notes="Read-only/export only; live driver mode remains gated for later approved add-on.",
            ),
            primary_benchmarks=["vendor_export_replay", "cross_vendor_trace_normalization"],
            claim_level="vendor_portability_pending",
            beta_release_priority="P2",
            blockers=["obtain_sample_exports", "vendor_schema_docs"],
        ),
        DatasetRegistryEntryV42(
            dataset_id="user_uploaded_neural_data",
            display_name="User-uploaded spike/NWB/HDF5/CSV data for beta testers",
            source_kind=DatasetSourceKindV42.USER_UPLOAD,
            access_mode=DatasetAccessModeV42.READ_ONLY_REPLAY,
            status="planned_hosted_server_feature",
            import_plan=DatasetImportPlanV42(
                importer_id="user_upload_v42",
                expected_input_formats=["csv", "json", "nwb", "h5", "hdf5", "zip"],
                produces="BioGPUTrace with validation warnings",
                power_pc_required=False,
                external_credentials_required=False,
                live_control_required=False,
                validation_steps=["file_type_check", "schema_detect", "safety_scan", "preview_report", "manual_mapping_if_needed"],
                notes="Important for private beta, enterprise pilots, and vendor/lab feedback.",
            ),
            primary_benchmarks=["custom_replay", "custom_readout", "validation_report"],
            claim_level="customer_validation_input",
            beta_release_priority="P1",
            blockers=["hosted_upload_security", "schema_mapping_ui"],
        ),
    ]
    return BioGPUDatasetRegistryV42(entries)
