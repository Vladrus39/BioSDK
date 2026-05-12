from __future__ import annotations
from dataclasses import asdict, dataclass, field
from typing import Any, Literal
from biogpu.runtime.contracts import BioGPUJob, BioGPUResult, BioGPUTrace
AdapterMode = Literal['dry_run','vendor_backend_required']
@dataclass(frozen=True)
class LiveMEAAdapterConfig:
    adapter_name: str='LiveMEASubstrateAdapter'
    mode: AdapterMode='dry_run'
    vendor: str|None=None
    device_id: str|None=None
    channel_count: int|None=None
    sampling_rate_hz: float|None=None
    stimulation_supported: bool=False
    recording_supported: bool=False
    ttl_sync_supported: bool=False
    environmental_sensors: list[str]=field(default_factory=lambda:['temperature','medium_status'])
    safety_notice: str='Dry-run only. Real hardware use requires vendor backend, validated stimulation limits and approved lab protocol.'
    def to_dict(self): return asdict(self)
class LiveMEASubstrateAdapter:
    def __init__(self, config: LiveMEAAdapterConfig|None=None): self.config=config or LiveMEAAdapterConfig(); self.connected=False
    def connect(self):
        if self.config.mode!='dry_run': raise NotImplementedError('Real vendor backend is not implemented in v1.9.')
        self.connected=True
    def health_check(self)->dict[str,Any]:
        return {'type':'LiveMEASubstrateAdapter','connected':self.connected,'mode':self.config.mode,'live_hardware':False,'config':self.config.to_dict(),'required_for_real_use':['vendor SDK backend','stimulation safety limits','TTL/raw synchronization','environmental monitoring','experiment audit logging','ethics/biosafety approval']}
    def run_job(self, job: BioGPUJob)->BioGPUResult:
        if not self.connected: self.connect()
        trace=BioGPUTrace(job_id=job.job_id, source='LiveMEASubstrateAdapter dry-run placeholder', culture=None, recording=None, target_electrode=(job.input_payload or {}).get('target_electrode'), response_features=[], feature_names=[], metadata={'dry_run':True,'no_live_stimulation_performed':True,'safety_notice':self.config.safety_notice,'input_payload':job.input_payload})
        return BioGPUResult(job_id=job.job_id, prediction=None, confidence=None, metrics={'dry_run':True}, trace=trace, metadata={'note':'Live MEA backend is a contract only in v1.9.'})
    def close(self): self.connected=False
