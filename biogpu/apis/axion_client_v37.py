from __future__ import annotations
from biogpu.apis.base_external_api_v37 import BaseExternalAPIClientV37, ExternalAPIConfigV37, APIPlatformV37

class AxionClientV37(BaseExternalAPIClientV37):
    adapter_name = "axion_client_v37"
    platform = APIPlatformV37.AXION.value
    default_channel_count = 768
    default_sample_rate_hz = 12_500.0


def make_axion_mock_client_v37(access_mode: str = "read_only") -> AxionClientV37:
    return AxionClientV37(ExternalAPIConfigV37(platform=APIPlatformV37.AXION.value, endpoint="mock://axion", token_env="AXION_TOKEN", access_mode=access_mode))
