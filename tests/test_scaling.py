import numpy as np
import pandas as pd
from sklearn.preprocessing import RobustScaler
from preprocessing import scaling

def test_minmax_one_column():
    out, _ = scaling.process(pd.DataFrame({"x": [10.0, 20.0, 30.0]}), ["x"], "Min-Max Scaling")
    assert np.allclose(out["x"], [0.0, 0.5, 1.0])

def test_minmax_multiple_columns_independently():
    df = pd.DataFrame({"x": [0, 10], "y": [100, 200]})
    out, _ = scaling.process(df, ["x", "y"], "Min-Max Scaling")
    assert np.allclose(out["x"], [0, 1])
    assert np.allclose(out["y"], [0, 1])

def test_robust_scaling_matches_sklearn():
    values = np.array([[1.0], [2.0], [3.0], [100.0]])
    out, _ = scaling.process(pd.DataFrame({"x": values[:, 0]}), ["x"], "Robust Scaling")
    expected = RobustScaler().fit_transform(values).ravel()
    assert np.allclose(out["x"], expected)

def test_constant_column_remains_finite():
    out, _ = scaling.process(pd.DataFrame({"x": [5.0, 5.0, 5.0]}), ["x"], "Min-Max Scaling")
    assert np.isfinite(out["x"]).all()
    assert (out["x"] == 0).all()

def test_no_columns_returns_message():
    df = pd.DataFrame({"x": [1, 2]})
    out, message = scaling.process(df, [], "Min-Max Scaling")
    pd.testing.assert_frame_equal(out, df)
    assert "No columns" in message

def test_invalid_method_returns_controlled_message():
    df = pd.DataFrame({"x": [1, 2]})
    out, message = scaling.process(df, ["x"], "invalid")
    assert isinstance(out, pd.DataFrame)
    assert "Unknown" in message
