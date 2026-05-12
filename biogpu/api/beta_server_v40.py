
from __future__ import annotations

from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from biogpu.beta.architecture_v40 import build_beta_release_architecture_v40, VERSION

app = FastAPI(title="BioGPU-Core Beta Server", version=VERSION)

class BetaRunRequestV40(BaseModel):
    dataset_id: str = Field(default="zenodo_14363732_preprocessed")
    mode: str = Field(default="replay")
    benchmark: str = Field(default="target_vs_random_electrode")
    decoder: str = Field(default="centroid_v27")
    shuffle_controls: int = Field(default=12, ge=0, le=1000)

SAFE_BETA_MODES = {"mock", "replay", "read_only_import", "metadata", "read_only_live", "live_shadow"}
BLOCKED_TERMS = {"voltage", "amplitude", "current", "pulse_width", "frequency", "pinout", "wiring", "stimulation"}

@app.get("/health")
def health() -> Dict[str, Any]:
    return {"status": "ok", "project": "BioGPU-Core", "version": VERSION, "service": "beta_server_v40"}

@app.get("/v40/architecture")
def architecture() -> Dict[str, Any]:
    return build_beta_release_architecture_v40()

@app.get("/v40/release-channels")
def release_channels() -> Dict[str, Any]:
    arch = build_beta_release_architecture_v40()
    return {"channels": arch["release_channels"]}

@app.get("/v40/datasets")
def datasets() -> Dict[str, Any]:
    arch = build_beta_release_architecture_v40()
    return {"dataset_expansion": arch["dataset_expansion"]}

@app.post("/v40/runs/validate")
def validate_run(req: BetaRunRequestV40) -> Dict[str, Any]:
    if req.mode not in SAFE_BETA_MODES:
        raise HTTPException(status_code=403, detail=f"Mode {req.mode!r} is not allowed in v4.0 beta gate")
    req_text = req.model_dump_json().lower()
    found = sorted(term for term in BLOCKED_TERMS if term in req_text)
    if found:
        raise HTTPException(status_code=403, detail={"blocked_terms": found, "reason": "v4.0 beta is read-only/replay only"})
    return {
        "status": "accepted_for_beta_validation",
        "live_output_performed": False,
        "message": "This endpoint validates a safe beta run request; actual job queue execution is planned for v4.3.",
        "request": req.model_dump(),
    }
