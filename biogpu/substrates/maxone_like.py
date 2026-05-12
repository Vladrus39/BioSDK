from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from biogpu.substrates.real_mea_base import RealMEAConfig, RealMEAVendorNeutralAdapter, RealMEACapabilities


@dataclass
class MaxOneLikeConfig(RealMEAConfig):
    """Dry-run reference config inspired by HD-MEA platforms.

    This class does not implement any vendor SDK and does not communicate with
    hardware. It freezes the fields that BioGPU would need from a MaxOne-like
    backend: electrode count, sample rate, dense maps and closed-loop capability.
    """

    substrate_id: str = "maxone_like_dry_run"
    dry_run: bool = True
    require_lab_approval: bool = True
    vendor: str = "MaxOne-like-reference"
    model: str = "HD-MEA dry-run placeholder"
    electrode_count: int = 26400
    sample_rate_hz: float = 20000.0
    electrode_pitch_um: float = 17.5
    metadata: dict[str, Any] = field(default_factory=lambda: {"reference_only": True})


class MaxOneLikeDryRunAdapter(RealMEAVendorNeutralAdapter):
    """Vendor-specific placeholder for future MaxOne-like integration.

    It is intentionally dry-run only. A real implementation would need the
    manufacturer's SDK/API, lab approval and validated safety constraints.
    """

    def __init__(self, config: MaxOneLikeConfig | None = None):
        super().__init__(config or MaxOneLikeConfig())
        self._capabilities = RealMEACapabilities(
            vendor=self.config.vendor,
            model=self.config.model,
            electrode_count=self.config.electrode_count,
            supports_stimulation=False,
            supports_recording=True,
            supports_raw_stream=False,
            supports_closed_loop=False,
            max_sample_rate_hz=getattr(self.config, "sample_rate_hz", None),
            metadata={
                "mode": "dry_run",
                "electrode_pitch_um": getattr(self.config, "electrode_pitch_um", None),
                "reference_only": True,
                "warning": "No vendor SDK loaded; no hardware communication performed.",
            },
        )
