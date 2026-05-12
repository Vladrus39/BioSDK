from __future__ import annotations
from .base_v25 import BioGPUVendorAdapterBase, BioGPUVendorCapability


class FinalSparkRemoteWetwareAdapter(BioGPUVendorAdapterBase):
    adapter_id = "finalspark_remote_wetware_class"

    @property
    def capability(self) -> BioGPUVendorCapability:
        return BioGPUVendorCapability(
            vendor_id=self.adapter_id,
            display_name="Remote wetware API-class adapter",
            platform_class="remote wetware/MEA service class",
            role_in_biogpu_a1="external proof-of-integration backend when direct lab hardware is unavailable",
            recording_supported=True,
            stimulation_supported=True,
            raw_trace_supported=False,
            spike_stream_supported=True,
            ttl_sync_supported=False,
            environmental_sensors=["provider_managed_environment"],
            api_access_class="provider API contract required for live use",
            channel_count_class="provider-defined remote wetware class",
            live_backend_status="stub_only",
            boundary_notice="No provider-specific request schema or live stimulation settings are implemented in v2.5.",
        )
