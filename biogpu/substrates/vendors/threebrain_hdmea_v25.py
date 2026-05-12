from __future__ import annotations
from .base_v25 import BioGPUVendorAdapterBase, BioGPUVendorCapability


class ThreeBrainHDMEAAdapter(BioGPUVendorAdapterBase):
    adapter_id = "threebrain_hdmea_class"

    @property
    def capability(self) -> BioGPUVendorCapability:
        return BioGPUVendorCapability(
            vendor_id=self.adapter_id,
            display_name="3Brain HD-MEA-class adapter",
            platform_class="high-density MEA platform",
            role_in_biogpu_a1="target high-resolution spatial BioGPU backend",
            recording_supported=True,
            stimulation_supported=True,
            raw_trace_supported=True,
            spike_stream_supported=True,
            ttl_sync_supported=True,
            environmental_sensors=["temperature_class", "stage_environment_class"],
            api_access_class="vendor SDK/backend required for live use",
            channel_count_class="HD-MEA class; 1024-4096+ channel target depending on device",
            live_backend_status="stub_only",
            boundary_notice="No address map, routing table, pinout or live stimulation settings are implemented in v2.5.",
        )
