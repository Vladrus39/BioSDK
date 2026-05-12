
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import re
from biogpu.schemas import SpikeTrain, StimPattern
from biogpu.substrates.base import ComputeSubstrateAdapter

@dataclass
class ZenodoMEA2100Config:
    root_path: str
    spike_glob: str = "**/*.txt"
    delimiter: str | None = None
    time_unit: str = "s"
    default_unit_id: int = 0
    window_start_s: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

def _time_to_seconds(value: float, unit: str) -> float:
    u = unit.lower()
    if u in {"s", "sec", "second", "seconds"}: return float(value)
    if u in {"ms", "millisecond", "milliseconds"}: return float(value)/1000.0
    if u in {"us", "µs", "microsecond", "microseconds"}: return float(value)/1_000_000.0
    raise ValueError(f"Unsupported time unit: {unit}")

def _split_line(line: str, delimiter: str | None) -> list[str]:
    line=line.strip()
    if not line or line.startswith('#'): return []
    if delimiter: return [p.strip() for p in line.split(delimiter) if p.strip()]
    return [p for p in re.split(r"[,;\s]+", line) if p]

def _try_float(token: str) -> float | None:
    try: return float(token)
    except (TypeError, ValueError): return None

def parse_spike_txt(path: str | Path, default_unit_id: int = 0, time_unit: str = "s", delimiter: str | None = None) -> SpikeTrain:
    unit_ids=[]; spike_times=[]; p=Path(path)
    with p.open('r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            parts=_split_line(line, delimiter)
            nums=[_try_float(x) for x in parts]
            vals=[x for x in nums if x is not None]
            if not vals: continue
            if len(vals)==1:
                unit=default_unit_id; t=vals[0]
            else:
                first,second=vals[0], vals[1]
                if abs(first-round(first)) < 1e-6 and first >= 0:
                    unit=int(round(first)); t=second
                else:
                    unit=default_unit_id; t=first
            unit_ids.append(int(unit)); spike_times.append(_time_to_seconds(float(t), time_unit))
    return SpikeTrain(unit_ids, spike_times, metadata={"source_path": str(p), "parser": "zenodo_mea2100_txt", "time_unit_out": "s"})

def inspect_spike_txt_folder(root_path: str | Path, spike_glob: str = "**/*.txt") -> dict[str, Any]:
    root=Path(root_path); files=sorted(root.glob(spike_glob)) if root.exists() else []
    return {"root_path": str(root), "exists": root.exists(), "spike_glob": spike_glob, "txt_file_count": len(files), "total_bytes": sum(f.stat().st_size for f in files if f.is_file()), "sample_files": [str(f) for f in files[:10]]}

class ZenodoMEA2100SpikeTxtAdapter(ComputeSubstrateAdapter):
    def __init__(self, config: ZenodoMEA2100Config):
        self.config=config; self._connected=False; self._files=[]; self._cursor=0
    def connect(self) -> None:
        root=Path(self.config.root_path)
        if not root.exists(): raise FileNotFoundError(f"Zenodo MEA root path does not exist: {root}")
        self._files=sorted([p for p in root.glob(self.config.spike_glob) if p.is_file()])
        if not self._files: raise FileNotFoundError(f"No spike txt files found under {root} with glob {self.config.spike_glob}")
        self._connected=True; self._cursor=0
    def configure(self, config: dict[str, Any]) -> None:
        for k,v in config.items():
            if hasattr(self.config,k): setattr(self.config,k,v)
    def send_stimulation(self, pattern: StimPattern) -> None:
        self._last_stim_pattern=pattern
    def read_spikes(self, window_ms: float) -> SpikeTrain:
        if not self._connected: self.connect()
        path=self._files[self._cursor % len(self._files)]; self._cursor+=1
        spikes=parse_spike_txt(path, self.config.default_unit_id, self.config.time_unit, self.config.delimiter)
        start=float(self.config.window_start_s); end=start+float(window_ms)/1000.0 if window_ms else None
        if end is not None:
            pairs=[(u,t) for u,t in zip(spikes.unit_ids, spikes.spike_times) if start <= t <= end]
            spikes=SpikeTrain([u for u,t in pairs], [t for u,t in pairs], metadata={**spikes.metadata, "window_s": [start,end]})
        return spikes
    def read_raw(self, window_ms: float):
        raise NotImplementedError("Raw HDF5 support is dataset-specific; this adapter reads preprocessed spike TXT only.")
    def health_check(self) -> dict[str, Any]:
        return {"adapter": "ZenodoMEA2100SpikeTxtAdapter", "mode": "offline_public_dataset", "connected": self._connected, "source": "Zenodo record 14363732 compatible", **inspect_spike_txt_folder(self.config.root_path, self.config.spike_glob)}
    def close(self) -> None:
        self._connected=False
