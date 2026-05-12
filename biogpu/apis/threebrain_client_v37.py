from __future__ import annotations
from biogpu.apis.base_external_api_v37 import BaseExternalAPIClientV37, ExternalAPIConfigV37, APIPlatformV37

class ThreeBrainClientV37(BaseExternalAPIClientV37):
    adapter_name = "threebrain_client_v37"
    platform = APIPlatformV37.THREEBRAIN.value
    default_channel_count = 4096
    default_sample_rate_hz = 20_000.0


def make_threebrain_mock_client_v37(access_mode: str = "read_only") -> ThreeBrainClientV37:
    return ThreeBrainClientV37(ExternalAPIConfigV37(platform=APIPlatformV37.THREEBRAIN.value, endpoint="mock://threebrain", token_env="THREEBRAIN_TOKEN", access_mode=access_mode))
