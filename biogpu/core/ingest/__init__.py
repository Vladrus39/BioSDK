"""BioGPU Core v2.0 — Universal data ingest.

Supported formats: HDF5 (.h5), NWB (.nwb), EDF (.edf), CSV (.csv),
EEGLAB (.set/.fdt), NumPy (.npy), JSON (.json).
"""
from biogpu.core.ingest.loader_v2 import (
    IngestResult,
    load_dataset,
    detect_format,
    list_available_datasets,
    SUPPORTED_FORMATS,
)
__all__ = [
    "IngestResult", "load_dataset", "detect_format",
    "list_available_datasets", "SUPPORTED_FORMATS",
]
