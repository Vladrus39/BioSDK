from __future__ import annotations
from biogpu.apis.base_external_api_v37 import BaseExternalAPIClientV37, ExternalAPIConfigV37, APIPlatformV37

class MCSBridgeClientV37(BaseExternalAPIClientV37):
    adapter_name = "mcs_bridge_client_v37"
    platform = APIPlatformV37.MCS.value
    default_channel_count = 60
    default_sample_rate_hz = 20_000.0


def make_mcs_mock_client_v37(access_mode: str = "read_only") -> MCSBridgeClientV37:
    return MCSBridgeClientV37(ExternalAPIConfigV37(platform=APIPlatformV37.MCS.value, endpoint="mock://mcs_mea2100", token_env="MCS_TOKEN", access_mode=access_mode, dataset_ref="Zenodo 14363732 lineage-compatible"))
