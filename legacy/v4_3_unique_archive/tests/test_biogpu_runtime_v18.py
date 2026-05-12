from __future__ import annotations

import numpy as np
from biogpu.runtime.contracts import BioGPUJob, BioGPUObjective, build_biogpu_claim_ladder


def test_biogpu_objective_mentions_real_working_accelerator():
    obj = BioGPUObjective()
    assert "biological computing accelerator" in obj.mission
    assert "closed-loop" in obj.final_stage


def test_claim_ladder_contains_biogpu_advantage_stage():
    ladder = build_biogpu_claim_ladder()
    names = [s.stage for s in ladder]
    assert "L4_realdata_replay_biogpu_core" in names
    assert "L6_biogpu_advantage" in names


def test_biogpu_job_contract_roundtrip():
    job = BioGPUJob(job_id="x", task="demo", input_payload={"target_electrode": 42})
    row = job.to_dict()
    assert row["job_id"] == "x"
    assert row["input_payload"]["target_electrode"] == 42
    assert row["safety_class"] == "offline_replay_only"
