"""NSI-1.0 adapter for FinalSpark Neuroplatform.

Remote wetware computing platform:
- 4 MEAs, 4 organoids each, 8 electrodes = 32 channels per MEA
- 30 kHz sampling, 16-bit, 0.15 uV accuracy
- Stimulation: 10 nA – 2.5 mA
- Python API (private `neuroplatform` package) + InfluxDB backend
- >1000 organoids, >18 TB data, FREE for research

Reference: Jordan et al. (2024). Frontiers in AI. doi:10.3389/frai.2024.1376042

STATUS: SKELETON — awaits token + `neuroplatform` package access.
        All NSI-1.0 methods are structurally complete. Marked pending_token.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterator, Optional
import numpy as np
import json

from biogpu.nsi import (
    NSIAdapter, NSIDataset, NSIMetadata,
    _default_feature_vector, generate_feature_names,
)

# ---------------------------------------------------------------------------
# FinalSpark hardware constants (from Frontiers 2024 article + docs)
# ---------------------------------------------------------------------------
FINALSPARK_N_MEAS = 4
FINALSPARK_ORGANOIDS_PER_MEA = 4
FINALSPARK_ELECTRODES_PER_MEA = 8
FINALSPARK_TOTAL_CHANNELS = FINALSPARK_ELECTRODES_PER_MEA  # per MEA
FINALSPARK_SAMPLE_RATE_HZ = 30_000
FINALSPARK_BIT_DEPTH = 16
FINALSPARK_ACCURACY_UV = 0.15

# Stimulation range (from article)
FINALSPARK_STIM_MIN_NA = 10       # 10 nA
FINALSPARK_STIM_MAX_MA = 2.5      # 2.5 mA

# BioSDK Shannon safety limits (map to FinalSpark range)
BIOSDK_SAFE_CURRENT_UA = 100      # 100 uA
BIOSDK_SAFE_CHARGE_NC = 200       # 200 nC
BIOSDK_SAFE_FREQ_HZ = 500         # 500 Hz

# ---------------------------------------------------------------------------
# Adapter
# ---------------------------------------------------------------------------

class FinalSparkAdapter(NSIAdapter):
    """NSI-1.0 adapter for FinalSpark Neuroplatform.

    Connects to remote wetware via the `neuroplatform` Python package.
    Requires a token from FinalSpark (free for university research).

    Usage:
        adapter = FinalSparkAdapter(token="np_xxx...")
        ds = adapter.open("mea_0")          # open MEA 0
        meta = adapter.metadata("mea_0")     # read metadata
        for window in adapter.iter_windows("mea_0", window_s=1.0):
            features = adapter.feature_vector(window)
    """

    adapter_id = "finalspark_neuroplatform"
    vendor = "finalspark"
    modality = "mea_wetware"

    # ------------------------------------------------------------------
    # Safety limits (Shannon-based, enforced on stimulation)
    # ------------------------------------------------------------------
    SAFE_CURRENT_MAX_NA = 100_000     # 100 uA = 100,000 nA
    SAFE_CHARGE_MAX_NC = 200          # 200 nC
    SAFE_FREQ_MAX_HZ = 500            # 500 Hz
    SAFE_DURATION_MAX_S = 3600        # 1 hour

    def __init__(self, token: str | None = None):
        """
        Args:
            token: FinalSpark API token. If None, adapter operates in
                   metadata-only mode (no live data access).
        """
        self._token = token
        self._np = None                # neuroplatform module (lazy)
        self._experiment = None        # Experiment instance
        self._database = None          # Database instance
        self._connected = False

    # ------------------------------------------------------------------
    # Connection management
    # ------------------------------------------------------------------
    def connect(self) -> bool:
        """Connect to FinalSpark Neuroplatform using the configured token.

        Returns True if connected, False if token is missing or connection fails.
        """
        if not self._token:
            return False
        try:
            import neuroplatform as np_module
            self._np = np_module
            self._experiment = np_module.Experiment(self._token)
            self._database = self._experiment.database
            self._connected = True
            return True
        except ImportError:
            # neuroplatform package not installed (private FinalSpark env)
            return False
        except Exception:
            return False

    def disconnect(self):
        """Release neuroplatform resources."""
        self._connected = False
        self._experiment = None
        self._database = None

    @property
    def is_connected(self) -> bool:
        return self._connected

    # ------------------------------------------------------------------
    # NSI-1.0: open
    # ------------------------------------------------------------------
    def open(self, path: str | Path) -> NSIDataset:
        """Open a FinalSpark MEA for reading.

        Args:
            path: MEA identifier ("mea_0", "mea_1", "mea_2", "mea_3")
                  or a path to a local h5 raw recording.

        Returns:
            NSIDataset with metadata and data reference.
        """
        p = str(path)
        meta = self.metadata(p)

        if self._connected and self._database is not None:
            # Live data: fetch spike events as binned rate matrix
            try:
                spikes = self._database.get_spike_events(
                    mea_id=p,
                    duration_s=60.0,  # default: last 60s
                )
                # Convert spike events to rate matrix
                data = self._spikes_to_rate_matrix(spikes, n_channels=meta.channel_count)
            except Exception:
                data = np.zeros((meta.channel_count, 1000), dtype=np.float32)
        else:
            # Metadata-only mode
            data = np.zeros((meta.channel_count, 1000), dtype=np.float32)
            meta.extra["_warning"] = "no_token: metadata_only_mode"

        feature_names = generate_feature_names(meta.channel_count)

        return NSIDataset(
            metadata=meta,
            data=data,
            feature_names=feature_names,
            _adapter=self,
        )

    # ------------------------------------------------------------------
    # NSI-1.0: metadata
    # ------------------------------------------------------------------
    def metadata(self, path: str | Path) -> NSIMetadata:
        """Read metadata for a FinalSpark MEA.

        Works in metadata-only mode (no token required for static info).
        """
        p = str(path)

        # Determine MEA ID
        mea_id = p
        if p.startswith("mea_"):
            try:
                mea_idx = int(p.split("_")[1])
            except (ValueError, IndexError):
                mea_idx = 0
        else:
            mea_idx = 0

        # Fetch live metadata if connected
        extra = {
            "platform": "FinalSpark Neuroplatform",
            "mea_id": mea_id,
            "n_meas_total": FINALSPARK_N_MEAS,
            "organoids_per_mea": FINALSPARK_ORGANOIDS_PER_MEA,
            "electrodes_per_mea": FINALSPARK_ELECTRODES_PER_MEA,
            "sample_rate_hz": FINALSPARK_SAMPLE_RATE_HZ,
            "bit_depth": FINALSPARK_BIT_DEPTH,
            "accuracy_uv": FINALSPARK_ACCURACY_UV,
            "backend": "InfluxDB",
            "token_configured": self._token is not None,
            "connected": self._connected,
            "reference": "Jordan et al. (2024), Frontiers in AI, doi:10.3389/frai.2024.1376042",
        }

        # Add live metadata if connected
        if self._connected and self._database is not None:
            try:
                db_meta = self._database.get_metadata(mea_id=mea_id)
                if db_meta:
                    extra["live_metadata"] = db_meta
            except Exception:
                pass

        return NSIMetadata(
            source_path=p,
            source_format="neuroplatform_api",
            vendor=self.vendor,
            modality=self.modality,
            channel_count=FINALSPARK_TOTAL_CHANNELS,
            sample_rate_hz=FINALSPARK_SAMPLE_RATE_HZ,
            duration_s=None,  # continuous recording
            extra=extra,
        )

    # ------------------------------------------------------------------
    # NSI-1.0: iter_windows
    # ------------------------------------------------------------------
    def iter_windows(self, path: str | Path, window_s: float,
                     overlap: float = 0.0) -> Iterator[np.ndarray]:
        """Iterate over sliding windows of MEA data.

        When connected: fetches spike events, bins to rate matrix, slides windows.
        When offline: yields empty generator.
        """
        p = str(path)
        meta = self.metadata(p)
        sr = meta.sample_rate_hz
        window_samples = int(window_s * sr)
        stride = max(1, int(window_samples * (1.0 - overlap)))

        if not self._connected or self._database is None:
            return  # no data available

        try:
            # Fetch spike events
            spikes = self._database.get_spike_events(
                mea_id=p,
                duration_s=3600.0,  # up to 1 hour
            )
            if not spikes:
                return

            data = self._spikes_to_rate_matrix(
                spikes,
                n_channels=meta.channel_count,
                bin_ms=10.0,  # 10ms bins = 100 Hz rate
            )

            n_ch, n_bins = data.shape
            start = 0
            while start + window_samples <= n_bins:
                yield np.asarray(data[:, start:start + window_samples], dtype=np.float32)
                start += stride

        except Exception:
            return

    # ------------------------------------------------------------------
    # NSI-1.0: feature_vector
    # ------------------------------------------------------------------
    def feature_vector(self, window: np.ndarray,
                       feature_names: list[str] | None = None) -> np.ndarray:
        """Extract NSI-1.0 features from a window (reuses standard extractor)."""
        return _default_feature_vector(window)

    # ------------------------------------------------------------------
    # NSI-1.0: close
    # ------------------------------------------------------------------
    def close(self) -> None:
        """Release resources."""
        self.disconnect()

    # ------------------------------------------------------------------
    # FinalSpark-specific: stimulation safety check
    # ------------------------------------------------------------------
    def check_stimulation_safety(self, current_na: float, charge_nc: float,
                                  freq_hz: float, duration_s: float) -> dict:
        """Validate stimulation parameters against BioSDK Shannon limits.

        Args:
            current_na: Current in nanoamperes
            charge_nc: Charge in nanocoulombs
            freq_hz: Frequency in Hz
            duration_s: Duration in seconds

        Returns:
            Dict with 'safe' (bool), 'violations' (list of str), 'warnings' (list).
        """
        violations = []
        warnings = []

        if current_na > self.SAFE_CURRENT_MAX_NA:
            violations.append(
                f"Current {current_na} nA exceeds safe limit {self.SAFE_CURRENT_MAX_NA} nA"
            )
        if charge_nc > self.SAFE_CHARGE_MAX_NC:
            violations.append(
                f"Charge {charge_nc} nC exceeds safe limit {self.SAFE_CHARGE_MAX_NC} nC"
            )
        if freq_hz > self.SAFE_FREQ_MAX_HZ:
            violations.append(
                f"Frequency {freq_hz} Hz exceeds safe limit {self.SAFE_FREQ_MAX_HZ} Hz"
            )
        if duration_s > self.SAFE_DURATION_MAX_S:
            violations.append(
                f"Duration {duration_s}s exceeds safe limit {self.SAFE_DURATION_MAX_S}s"
            )

        # Warnings (within FinalSpark hardware range but near limits)
        if current_na > self.SAFE_CURRENT_MAX_NA * 0.8:
            warnings.append(f"Current at {current_na/self.SAFE_CURRENT_MAX_NA*100:.0f}% of safe limit")
        if charge_nc > self.SAFE_CHARGE_MAX_NC * 0.8:
            warnings.append(f"Charge at {charge_nc/self.SAFE_CHARGE_MAX_NC*100:.0f}% of safe limit")

        return {
            "safe": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "limits": {
                "current_max_na": self.SAFE_CURRENT_MAX_NA,
                "charge_max_nc": self.SAFE_CHARGE_MAX_NC,
                "freq_max_hz": self.SAFE_FREQ_MAX_HZ,
                "duration_max_s": self.SAFE_DURATION_MAX_S,
            },
            "finalspark_hardware_range": {
                "current": f"{FINALSPARK_STIM_MIN_NA} nA – {FINALSPARK_STIM_MAX_MA} mA",
                "note": "BioSDK limit (100 uA) is within FinalSpark range (10 nA – 2.5 mA)",
            },
        }

    # ------------------------------------------------------------------
    # Helper: spike events → rate matrix
    # ------------------------------------------------------------------
    def _spikes_to_rate_matrix(self, spikes, n_channels: int,
                                bin_ms: float = 10.0,
                                duration_s: float = 60.0) -> np.ndarray:
        """Convert spike events to binned rate matrix.

        Args:
            spikes: List of (channel, timestamp_ms) tuples or dict
            n_channels: Number of MEA channels
            bin_ms: Bin width in milliseconds
            duration_s: Total duration in seconds

        Returns:
            (n_channels, n_bins) rate matrix in Hz
        """
        n_bins = int(duration_s * 1000 / bin_ms)
        rate = np.zeros((n_channels, n_bins), dtype=np.float32)

        if isinstance(spikes, list):
            for ch, ts_ms in spikes:
                if 0 <= ch < n_channels:
                    bin_idx = int(ts_ms / bin_ms)
                    if 0 <= bin_idx < n_bins:
                        rate[ch, bin_idx] += 1
        elif isinstance(spikes, dict):
            for ch_str, timestamps in spikes.items():
                ch = int(ch_str) if ch_str.isdigit() else -1
                if 0 <= ch < n_channels:
                    for ts in timestamps:
                        bin_idx = int(float(ts) / bin_ms)
                        if 0 <= bin_idx < n_bins:
                            rate[ch, bin_idx] += 1

        # Convert to Hz
        rate = rate * 1000 / bin_ms
        return rate


# ---------------------------------------------------------------------------
# Hardware specification reference
# ---------------------------------------------------------------------------
FINALSPARK_SPECS = {
    "platform": "FinalSpark Neuroplatform",
    "version": "v2 (as of 2025 docs)",
    "meas": FINALSPARK_N_MEAS,
    "organoids_per_mea": FINALSPARK_ORGANOIDS_PER_MEA,
    "electrodes_per_mea": FINALSPARK_ELECTRODES_PER_MEA,
    "total_channels": FINALSPARK_TOTAL_CHANNELS,
    "sample_rate_hz": FINALSPARK_SAMPLE_RATE_HZ,
    "bit_depth": FINALSPARK_BIT_DEPTH,
    "accuracy_uv": FINALSPARK_ACCURACY_UV,
    "stimulation_range": f"{FINALSPARK_STIM_MIN_NA} nA – {FINALSPARK_STIM_MAX_MA} mA",
    "biosdk_safe_current_na": BIOSDK_SAFE_CURRENT_UA * 1000,
    "biosdk_safe_charge_nc": BIOSDK_SAFE_CHARGE_NC,
    "biosdk_safe_freq_hz": BIOSDK_SAFE_FREQ_HZ,
    "backend": "InfluxDB",
    "api": "neuroplatform (private Python package)",
    "documentation": "https://finalspark-np.github.io/np-docs/",
    "publication": "Jordan et al. (2024), Frontiers in AI, doi:10.3389/frai.2024.1376042",
    "github": "https://github.com/FinalSpark-np",
    "pricing": "FREE for university research, $1000/mo + $1000 setup for companies",
    "application": "https://finalspark.com/neuroplatform/",
}

# Auto-register (with pending_token status)
try:
    from biogpu.nsi.adapters import register_adapter
    register_adapter(FinalSparkAdapter)
except ImportError:
    pass
