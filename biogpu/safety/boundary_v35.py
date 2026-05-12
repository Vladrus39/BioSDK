"""BioGPU v3.5 unified safety boundary.

This module centralizes the repository-level rule used across BioGPU-Core:
software/replay layers may describe abstract biological-compute intent, but must
not emit live wet-lab operating parameters, physical wiring/pinout instructions,
or executable cell-culture recipes.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Iterable

FORBIDDEN_LIVE_FIELDS_V35: frozenset[str] = frozenset({
    # stimulation/electrical parameters that belong only in approved vendor/lab SOPs
    "voltage", "stim_voltage", "stimulation_voltage", "pulse_voltage",
    "amplitude", "stim_amplitude", "stimulation_amplitude",
    "current", "stim_current", "stimulation_current",
    "pulse_width", "pulse_width_us", "pulse_width_ms", "pulse_duration",
    "frequency", "freq_hz", "charge", "charge_density", "charge_density_limit",
    # physical connection / hardware details that must come from vendor docs
    "pinout", "wiring", "wire_map", "electrode_pinout", "connector_pinout",
    # wet-lab operational recipe details
    "media_recipe", "incubation", "incubation_formula", "culturing_recipe",
    "cell_culture_recipe", "wetlab_recipe", "co2_percent", "serum_percent",
    "antibiotic_concentration", "growth_factor_concentration",
})

SAFE_SCOPE_V35: tuple[str, ...] = (
    "software/replay analysis",
    "metadata-only or read-only external API preparation",
    "abstract encoder/readout contracts",
    "result bundles, audit logs and benchmark manifests",
    "lab/vendor handoff checklists without executable SOP details",
)

OUT_OF_SCOPE_V35: tuple[str, ...] = (
    "live stimulation amplitude/current/voltage/pulse-width settings",
    "physical wiring or pinout procedures",
    "wet-lab culture recipes or incubation formulas",
    "claims of live BioGPU operation without approved lab evidence",
    "claims of GPU advantage without matched-task measurement",
)

class SafetyViolationV35(ValueError):
    """Raised when a payload contains forbidden live-lab fields."""

@dataclass(frozen=True)
class SafetyBoundaryReportV35:
    version: str
    safe_scope: tuple[str, ...]
    out_of_scope: tuple[str, ...]
    forbidden_field_count: int
    forbidden_fields_sample: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _norm_key(key: Any) -> str:
    return str(key).strip().lower().replace("-", "_").replace(" ", "_")


def find_forbidden_keys_v35(keys: Iterable[Any]) -> list[str]:
    """Return normalized forbidden keys found in an iterable of keys."""
    found = sorted({_norm_key(k) for k in keys if _norm_key(k) in FORBIDDEN_LIVE_FIELDS_V35})
    return found


def assert_no_forbidden_keys_v35(keys: Iterable[Any], *, context: str = "payload") -> None:
    found = find_forbidden_keys_v35(keys)
    if found:
        raise SafetyViolationV35(f"Unsafe live-lab field(s) are not allowed in {context}: {found}")


def _walk_payload(obj: Any, path: str, found: list[str]) -> None:
    if isinstance(obj, dict):
        for k, v in obj.items():
            nk = _norm_key(k)
            if nk in FORBIDDEN_LIVE_FIELDS_V35:
                found.append(f"{path}.{nk}" if path else nk)
            _walk_payload(v, f"{path}.{nk}" if path else nk, found)
    elif isinstance(obj, (list, tuple, set)):
        for i, v in enumerate(obj):
            _walk_payload(v, f"{path}[{i}]", found)


def assert_no_forbidden_payload_v35(obj: Any, *, context: str = "payload") -> None:
    """Recursively reject forbidden live-lab fields in dict/list payloads."""
    found: list[str] = []
    _walk_payload(obj, "", found)
    if found:
        raise SafetyViolationV35(f"Unsafe live-lab field(s) are not allowed in {context}: {sorted(found)}")


def safety_boundary_summary_v35() -> SafetyBoundaryReportV35:
    sample = tuple(sorted(FORBIDDEN_LIVE_FIELDS_V35)[:12])
    return SafetyBoundaryReportV35(
        version="v3.5",
        safe_scope=SAFE_SCOPE_V35,
        out_of_scope=OUT_OF_SCOPE_V35,
        forbidden_field_count=len(FORBIDDEN_LIVE_FIELDS_V35),
        forbidden_fields_sample=sample,
    )
