from __future__ import annotations
from .base_v25 import BioGPUVendorAdapterBase, BioGPUVendorCapability


class AxionMaestroAdapter(BioGPUVendorAdapterBase):
    adapter_id = "axion_maestro_class"

    @property
    def capability(self) -> BioGPUVendorCapability:
        return BioGPUVendorCapability(
            vendor_id=self.adapter_id,
            display_name="Axion Maestro-class adapter",
            platform_class="multiwell MEA screening platform",
            role_in_biogpu_a1="parallel culture screening and stability/replicate benchmark backend",
            recording_supported=True,
            stimulation_supported=True,
            raw_trace_supported=True,
            spike_stream_supported=True,
            ttl_sync_supported=True,
            environmental_sensors=["temperature_class", "co2_class", "humidity_class"],
            api_access_class="vendor SDK/export pipeline required for live use",
            channel_count_class="multiwell MEA class; exact channels depend on plate type",
            live_backend_status="stub_only",
            boundary_notice="No plate pinout, well-specific stimulation recipe or live settings are implemented in v2.5.",
        )
