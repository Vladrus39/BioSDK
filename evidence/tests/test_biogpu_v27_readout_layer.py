from biogpu.readout.base_v27 import ReadoutFeatureBatch
from biogpu.readout.registry_v27 import build_readout_registry_v27


def test_registry_has_expected_readouts():
    reg = build_readout_registry_v27()
    assert {"centroid_v27", "logistic_l2_v27", "linear_svm_v27", "online_centroid_v27"}.issubset(reg)


def test_centroid_predicts_simple_classes():
    batch = ReadoutFeatureBatch(["f0", "f1"], [[1,0], [0.9,0.1], [0,1], [0.1,0.9]], ["A", "A", "B", "B"])
    dec = build_readout_registry_v27()["centroid_v27"].fit(batch)
    assert dec.predict_one([1,0]).prediction == "A"
    assert dec.predict_one([0,1]).prediction == "B"


def test_batch_validation_rejects_bad_width():
    batch = ReadoutFeatureBatch(["f0"], [[1,2]], ["A"])
    try:
        batch.validate()
    except ValueError as e:
        assert "feature_names" in str(e)
    else:
        raise AssertionError("expected ValueError")
