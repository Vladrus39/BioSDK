from __future__ import annotations
from .base_v25 import BioGPUVendorAdapterBase, BioGPUVendorCapability


class MCSMEA2100Adapter(BioGPUVendorAdapterBase):
    adapter_id = "mcs_mea2100_class"

    @property
    def capability(self) -> BioGPUVendorCapability:
        return BioGPUVendorCapability(
            vendor_id=self.adapter_id,
            display_name="Multi Channel Systems MEA2100-class adapter",
            platform_class="bridge MEA recording/stimulation platform",
            role_in_biogpu_a1="first bridge backend for 60-channel-class MEA replay/live transition",
            recording_supported=True,
            stimulation_supported=True,
            raw_trace_supported=True,
            spike_stream_supported=True,
            ttl_sync_supported=True,
            environmental_sensors=["temperature_class"],
            api_access_class="vendor SDK/backend required for live use",
            channel_count_class="60-channel bridge class; higher-density variants require separate backend",
            live_backend_status="stub_only",
            boundary_notice="No vendor commands, pinouts or live stimulation settings are implemented in v2.5.",
        )
