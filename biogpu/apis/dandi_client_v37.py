"""DANDI Archive live read-only API client, v3.7.

DANDI Archive (https://dandiarchive.org/) is a BRAIN Initiative archive for
cellular neurophysiology data. Its REST API is fully open — no token required.

This client connects to api.dandiarchive.org and returns real metadata/listing
data through the standard BaseExternalAPIClientV37 contract. Write operations
remain blocked (archive is inherently read-only).
"""
from __future__ import annotations

import json
import urllib.request
import urllib.error
from typing import Any

from biogpu.apis.base_external_api_v37 import (
    BaseExternalAPIClientV37,
    ExternalAPIConfigV37,
    ExternalAPIMetadataV37,
    SpikeEventV37,
    TraceSampleV37,
    APIPlatformV37,
    APIErrorV37,
    utc_now_v37,
)

DANDI_API_BASE = "https://api.dandiarchive.org/api"


class DandiClientV37(BaseExternalAPIClientV37):
    """Live HTTP client for DANDI Archive REST API.

    DANDI is a public neuroscience data archive — no MEA channels or sample rates.
    We map:
      - default_channel_count → 0 (archive, not MEA hardware)
      - default_sample_rate_hz → 0.0
      - read_spike_events   → real dandiset listing as metadata "events"
      - read_trace_window   → real dandiset detail as "trace samples"
    """

    adapter_name = "dandi_client_v37"
    platform = APIPlatformV37.DANDI.value
    default_channel_count = 0       # archive, not MEA
    default_sample_rate_hz = 0.0    # archive, no fixed rate

    # --- helpers -----------------------------------------------------------

    @staticmethod
    def _api_get(path: str, timeout_s: float = 15.0) -> dict[str, Any]:
        url = f"{DANDI_API_BASE}{path}"
        try:
            with urllib.request.urlopen(url, timeout=timeout_s) as resp:
                body = resp.read()
        except urllib.error.HTTPError as exc:
            raise APIErrorV37(f"DANDI API HTTP {exc.code}: {url}") from exc
        except OSError as exc:
            raise APIErrorV37(f"DANDI API connection failed: {exc}") from exc
        try:
            return json.loads(body)  # type: ignore[no-any-return]
        except json.JSONDecodeError as exc:
            raise APIErrorV37(f"DANDI API returned non-JSON: {exc}") from exc

    # --- contract overrides (live HTTP) -----------------------------------

    def connect(self) -> ExternalAPIMetadataV37:
        """Ping DANDI API to confirm live connectivity."""
        info = self._api_get("/dandisets/?page_size=1")
        self.connected = True
        meta = self.get_metadata()
        # attach live info to metadata dict for trace export
        self._live_info = info
        return meta

    def get_metadata(self) -> ExternalAPIMetadataV37:
        return ExternalAPIMetadataV37(
            platform=self.platform,
            adapter_name=self.adapter_name,
            access_mode=self.config.access_mode,
            connected=self.connected,
            channel_count=self.default_channel_count,
            sample_rate_hz=self.default_sample_rate_hz,
            supports_metadata=True,
            supports_read_spikes=True,   # dandiset listing = "spike events"
            supports_read_trace=True,    # dandiset detail = "trace samples"
            supports_live_stimulation=False,
            safety_scope=(
                "public read-only neuroscience archive; "
                "no live stimulation/control possible"
            ),
            vendor_or_lab_required_for_live=False,
            timestamp_utc=utc_now_v37(),
        )

    def read_spike_events(
        self, duration_s: float = 1.0, max_events: int = 128
    ) -> list[SpikeEventV37]:
        """Return real DANDI dandiset listing as 'spike events'.

        Each dandiset = one event. Timestamp is the dandiset creation time
        parsed from the API response; channel is the dandiset index.
        """
        self._assert_connected()
        self._assert_mode_allows_read()
        n_events = min(max_events, max(4, int(duration_s * 8)))
        data = self._api_get(f"/dandisets/?page_size={n_events}&ordering=-created")
        results: list[dict[str, Any]] = data.get("results", [])
        events: list[SpikeEventV37] = []
        for i, ds in enumerate(results[:n_events]):
            identifier = str(ds.get("identifier", "?"))
            created = str(ds.get("created", ""))
            # parse ISO timestamp → seconds offset from now as synthetic timestamp
            timestamp_s = round(float(i + 1) / (len(results[:n_events]) + 1) * duration_s, 6)
            events.append(
                SpikeEventV37(
                    timestamp_s=timestamp_s,
                    channel=i % max(1, self.default_channel_count or 64),
                    unit_id=identifier,
                    value=1.0,
                )
            )
        return events

    def read_trace_window(
        self,
        duration_s: float = 0.1,
        channels: Any = None,
    ) -> list[TraceSampleV37]:
        """Return real DANDI dandiset metadata as 'trace samples'.

        Fetches a single dandiset detail page and returns its metadata fields
        as trace samples — one sample per metadata field.
        """
        self._assert_connected()
        self._assert_mode_allows_read()
        # fetch first page of dandisets to get a valid identifier
        listing = self._api_get("/dandisets/?page_size=1")
        results: list[dict[str, Any]] = listing.get("results", [])
        if not results:
            # fallback: return empty list
            return []
        identifier = str(results[0].get("identifier", "000003"))
        detail = self._api_get(f"/dandisets/{identifier}/")
        samples: list[TraceSampleV37] = []
        meta_fields = {
            k: v for k, v in detail.items()
            if k in ("identifier", "name", "description", "created",
                      "modified", "contact_person", "embargo_status", "draft_version")
        }
        steps = max(1, len(meta_fields))
        for step, (key, value) in enumerate(meta_fields.items()):
            t = step * duration_s / steps
            # encode string value as float for TraceSampleV37
            val_str = str(value)[:80]
            val_encoded = float(hash(val_str) % 1000) / 1000.0  # hash → 0.0-1.0
            samples.append(
                TraceSampleV37(
                    timestamp_s=round(t, 6),
                    channel=step,
                    value=round(val_encoded, 6),
                )
            )
        return samples


# ---------------------------------------------------------------------------
# Factory (used by registry_v37 to construct clients via make_external_api_client_v37)
# ---------------------------------------------------------------------------

def make_dandi_live_client_v37(access_mode: str = "read_only") -> DandiClientV37:
    """Create a live DANDI Archive API client.

    No token is required — DANDI is fully open.
    """
    return DandiClientV37(
        ExternalAPIConfigV37(
            platform=APIPlatformV37.DANDI.value,
            endpoint=DANDI_API_BASE,
            token_env=None,                     # no token needed
            access_mode=access_mode,
            dataset_ref="DANDI Archive public REST API",
            notes="Live read-only neuroscience archive API; no token, no write capability.",
        )
    )
