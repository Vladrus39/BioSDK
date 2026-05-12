from __future__ import annotations
from typing import Callable
from biogpu.apis.base_external_api_v37 import APIPlatformV37, BaseExternalAPIClientV37
from biogpu.apis.finalspark_client_v37 import make_finalspark_mock_client_v37
from biogpu.apis.threebrain_client_v37 import make_threebrain_mock_client_v37
from biogpu.apis.axion_client_v37 import make_axion_mock_client_v37
from biogpu.apis.mcs_bridge_v37 import make_mcs_mock_client_v37
from biogpu.apis.dandi_client_v37 import make_dandi_live_client_v37

MOCK_CLIENT_FACTORIES_V37: dict[str, Callable[[str], BaseExternalAPIClientV37]] = {
    APIPlatformV37.FINALSPARK.value: make_finalspark_mock_client_v37,
    APIPlatformV37.THREEBRAIN.value: make_threebrain_mock_client_v37,
    APIPlatformV37.AXION.value: make_axion_mock_client_v37,
    APIPlatformV37.MCS.value: make_mcs_mock_client_v37,
    APIPlatformV37.DANDI.value: make_dandi_live_client_v37,
}


def list_external_api_platforms_v37() -> list[str]:
    return sorted(MOCK_CLIENT_FACTORIES_V37)


def make_external_api_client_v37(platform: str, access_mode: str = "read_only") -> BaseExternalAPIClientV37:
    try:
        return MOCK_CLIENT_FACTORIES_V37[platform](access_mode)
    except KeyError as exc:
        raise ValueError(f"Unknown BioGPU v3.7 external API platform: {platform}") from exc
