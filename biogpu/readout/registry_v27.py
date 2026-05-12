from __future__ import annotations
from typing import Dict
from biogpu.readout.centroid_v27 import CentroidReadoutV27
from biogpu.readout.linear_v27 import LogisticL2ReadoutV27, LinearSVMReadoutV27
from biogpu.readout.online_v27 import OnlineCentroidReadoutV27


def build_readout_registry_v27() -> Dict[str, object]:
    return {
        "centroid_v27": CentroidReadoutV27(),
        "logistic_l2_v27": LogisticL2ReadoutV27(),
        "linear_svm_v27": LinearSVMReadoutV27(),
        "online_centroid_v27": OnlineCentroidReadoutV27(),
    }


def registry_summary_v27() -> list[dict[str, str]]:
    return [
        {"decoder_id": rid, "kind": getattr(obj, "kind", "unknown"), "class": obj.__class__.__name__}
        for rid, obj in build_readout_registry_v27().items()
    ]
