from __future__ import annotations
from biogpu.apis.base_external_api_v37 import BaseExternalAPIClientV37, ExternalAPIConfigV37, APIPlatformV37

class FinalSparkClientV37(BaseExternalAPIClientV37):
    adapter_name = "finalspark_client_v37"
    platform = APIPlatformV37.FINALSPARK.value
    default_channel_count = 64
    default_sample_rate_hz = 20_000.0


def make_finalspark_mock_client_v37(access_mode: str = "read_only") -> FinalSparkClientV37:
    return FinalSparkClientV37(ExternalAPIConfigV37(platform=APIPlatformV37.FINALSPARK.value, endpoint="mock://finalspark", token_env="FINALSPARK_TOKEN", access_mode=access_mode))
