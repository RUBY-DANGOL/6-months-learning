from churn_mlops.data import load_data
from churn_mlops.modeling import CANDIDATES, make_pipeline
from churn_mlops.monitoring import build_slices


def test_data_and_three_genuinely_different_candidates():
    X, y = load_data()
    assert len(X) > 7000 and set(y.unique()) == {0, 1}
    assert len(CANDIDATES) >= 3
    assert len({(c.family, tuple(sorted(c.params.items()))) for c in CANDIDATES}) == len(CANDIDATES)
    assert hasattr(make_pipeline(X, CANDIDATES[0]), "predict_proba")


def test_engineered_drift_is_material():
    reference, current = build_slices()
    mean_shift = current.MonthlyCharges.mean() - reference.MonthlyCharges.mean()
    assert mean_shift > 15
    assert (current.Contract == "Month-to-month").mean() > 0.65

