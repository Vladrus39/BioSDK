"""Read-only dataset importer skeletons for BioGPU-Core v4.2.

These importers define stable contracts and lightweight schema checks. They do
not perform large downloads or live lab actions in this environment.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Any, Dict, List, Optional
import json

try:
    from biogpu.safety.governance_v35 import assert_safe_payload_v35
except Exception:  # pragma: no cover
    assert_safe_payload_v35 = None

UNSAFE_IMPORT_FIELDS_V42 = {
    "voltage", "amplitude", "current", "pulse_width", "frequency", "charge_density",
    "pinout", "wiring", "electrode_actuation", "live_stimulation", "media_recipe",
    "incubation_formula", "culturing_recipe", "environment_control", "perfusion_control",
}


@dataclass
class DatasetImportRequestV42:
    dataset_id: str
    importer_id: str
    source_uri: str
    mode: str = "read_only_replay"
    local_cache_dir: Optional[str] = None
    options: Dict[str, Any] = field(default_factory=dict)

    def validate_safety(self) -> List[str]:
        errors: List[str] = []
        if self.mode not in {"metadata_only", "read_only_replay", "live_shadow_read_only"}:
            errors.append(f"Unsupported or unsafe mode for v4.2: {self.mode}")
        flat = json.dumps(asdict(self), sort_keys=True).lower()
        for field in sorted(UNSAFE_IMPORT_FIELDS_V42):
            if field.lower() in flat:
                errors.append(f"unsafe field not allowed in v4.2 import request: {field}")
        if assert_safe_payload_v35 is not None:
            try:
                assert_safe_payload_v35(asdict(self))
            except Exception as exc:  # safety module may raise custom exceptions
                errors.append(str(exc))
        return errors


@dataclass
class DatasetImportResultV42:
    dataset_id: str
    importer_id: str
    status: str
    produces: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    output_refs: List[str] = field(default_factory=list)
    live_control_performed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class BaseDatasetImporterV42:
    importer_id = "base_v42"
    produces = "BioGPUTrace"
    supported_modes = {"metadata_only", "read_only_replay", "live_shadow_read_only"}
    supported_extensions: List[str] = []

    def validate_request(self, req: DatasetImportRequestV42) -> List[str]:
        errors = req.validate_safety()
        if req.importer_id != self.importer_id:
            errors.append(f"request importer_id={req.importer_id} does not match {self.importer_id}")
        if req.mode not in self.supported_modes:
            errors.append(f"mode {req.mode} is not supported by {self.importer_id}")
        return errors

    def inspect(self, req: DatasetImportRequestV42) -> DatasetImportResultV42:
        errors = self.validate_request(req)
        if errors:
            return DatasetImportResultV42(req.dataset_id, self.importer_id, "blocked", self.produces, warnings=errors)
        return DatasetImportResultV42(
            dataset_id=req.dataset_id,
            importer_id=self.importer_id,
            status="metadata_ready",
            produces=self.produces,
            metadata={
                "source_uri": req.source_uri,
                "mode": req.mode,
                "supported_extensions": self.supported_extensions,
                "contract_only": True,
            },
            warnings=["v4.2 skeleton: no large download or live API call performed"],
            live_control_performed=False,
        )

    def import_readonly(self, req: DatasetImportRequestV42) -> DatasetImportResultV42:
        return self.inspect(req)


class ZenodoPreprocessedImporterV42(BaseDatasetImporterV42):
    importer_id = "zenodo_preprocessed_v42"
    produces = "BioGPUFeatureMatrix"
    supported_extensions = ["zip", "csv", "json", "npz"]


class ZenodoRawHDF5ImporterV42(BaseDatasetImporterV42):
    importer_id = "zenodo_raw_hdf5_v42"
    produces = "BioGPURawTrace + stimulus_windows.csv"
    supported_extensions = ["zip", "h5", "hdf5"]

    def inspect(self, req: DatasetImportRequestV42) -> DatasetImportResultV42:
        res = super().inspect(req)
        res.metadata.update({"power_pc_required": True, "expected_size_class": "tens_of_GB", "ttl_detection_required": True})
        return res


class DandiNWBImporterV42(BaseDatasetImporterV42):
    importer_id = "dandi_nwb_v42"
    produces = "BioGPUTaskAlignedTrace"
    supported_extensions = ["nwb", "dandiset_asset"]

    def inspect(self, req: DatasetImportRequestV42) -> DatasetImportResultV42:
        res = super().inspect(req)
        res.metadata.update({"requires_nwb_units": True, "requires_intervals_or_trials": True, "requires_stimulus_metadata": True})
        return res


class AllenSDKImporterV42(BaseDatasetImporterV42):
    importer_id = "allen_visual_coding_v42"
    produces = "BioGPUOrientationBenchmarkTrace"
    supported_extensions = ["allensdk_cache", "nwb"]

    def inspect(self, req: DatasetImportRequestV42) -> DatasetImportResultV42:
        res = super().inspect(req)
        res.metadata.update({"requires_allensdk": True, "benchmark_targets": ["orientation", "temporal_frequency", "natural_movie"]})
        return res


class FinalSparkExportImporterV42(BaseDatasetImporterV42):
    importer_id = "finalspark_export_v42"
    produces = "BioGPUTrace from read-only remote wetware export"
    supported_extensions = ["hdf5", "h5", "api_trace", "spike_events"]

    def validate_request(self, req: DatasetImportRequestV42) -> List[str]:
        errors = super().validate_request(req)
        if req.mode == "live_shadow_read_only" and not req.options.get("read_only_token_expected", False):
            errors.append("FinalSpark live-shadow mode requires read_only_token_expected=true in v4.2 skeleton")
        return errors


class VendorExportImporterV42(BaseDatasetImporterV42):
    importer_id = "vendor_export_v42"
    produces = "BioGPUTrace from vendor export"
    supported_extensions = ["csv", "h5", "hdf5", "nwb", "vendor_export_folder"]


class UserUploadImporterV42(BaseDatasetImporterV42):
    importer_id = "user_upload_v42"
    produces = "BioGPUTrace with validation warnings"
    supported_extensions = ["csv", "json", "nwb", "h5", "hdf5", "zip"]


def build_importer_catalog_v42() -> Dict[str, BaseDatasetImporterV42]:
    importers = [
        ZenodoPreprocessedImporterV42(),
        ZenodoRawHDF5ImporterV42(),
        DandiNWBImporterV42(),
        AllenSDKImporterV42(),
        FinalSparkExportImporterV42(),
        VendorExportImporterV42(),
        UserUploadImporterV42(),
    ]
    return {i.importer_id: i for i in importers}
