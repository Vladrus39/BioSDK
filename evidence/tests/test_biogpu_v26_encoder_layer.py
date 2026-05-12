import pytest

from biogpu.encoding.base_v26 import EncoderInput, AbstractBioPattern
from biogpu.encoding.spatial_v26 import SpatialEncoderV26
from biogpu.encoding.temporal_v26 import TemporalEncoderV26
from biogpu.encoding.rate_v26 import RateEncoderV26
from biogpu.encoding.hybrid_v26 import HybridEncoderV26
from biogpu.encoding.registry_v26 import build_encoder_registry_v26, encode_with_registry_v26


def test_spatial_encoder_outputs_normalized_pattern():
    p = SpatialEncoderV26().encode(EncoderInput(task_id="t", payload=[0, 1, 2]))
    assert p.kind == "spatial"
    assert len(p.target_groups) == 3
    assert max(abs(x) for x in p.weights) <= 1.0


def test_temporal_encoder_outputs_time_bins():
    p = TemporalEncoderV26(abstract_bin_s=0.2).encode(EncoderInput(task_id="t", payload=[1, 0, 1]))
    assert p.kind == "temporal"
    assert p.time_bins == [0.0, 0.2, 0.4]


def test_rate_encoder_maps_scores_to_weights():
    p = RateEncoderV26().encode(EncoderInput(task_id="t", payload={"a": 1.0, "b": 0.0}))
    assert p.weights == [1.0, -1.0]


def test_hybrid_encoder_combines_spatial_and_temporal():
    p = HybridEncoderV26().encode(EncoderInput(task_id="t", payload={"spatial": [0, 1], "temporal": [1, 0]}))
    assert p.kind == "hybrid"
    assert len(p.target_groups) == 4


def test_registry_contains_four_encoders():
    reg = build_encoder_registry_v26()
    assert {"spatial_v26", "temporal_v26", "rate_v26", "hybrid_v26"}.issubset(reg.keys())


def test_registry_encoder_call():
    p = encode_with_registry_v26("rate_v26", EncoderInput(task_id="t", payload={"x": 0.5}))
    assert p.kind == "rate"


def test_unsafe_metadata_is_rejected():
    with pytest.raises(ValueError):
        SpatialEncoderV26().encode(EncoderInput(task_id="bad", payload=[1], metadata={"voltage": "do not allow"}))


def test_pattern_rejects_unsafe_metadata():
    p = AbstractBioPattern(
        pattern_id="bad",
        kind="spatial",
        target_groups=["g"],
        time_bins=[0.0],
        weights=[0.1],
        readout_hint="x",
        metadata={"pulse_width": "unsafe"},
    )
    with pytest.raises(ValueError):
        p.validate()
