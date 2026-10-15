import numpy as np
import pandas as pd
from preprocessing import normalization

def test_zscore_one_column_has_mean_zero_and_std_one_population():
    out, _ = normalization.process(pd.DataFrame({"x": [1.0, 2.0, 3.0]}), ["x"], "Z-Score Normalization")
    assert np.isclose(out["x"].mean(), 0, atol=1e-9)
    assert np.isclose(out["x"].std(ddof=0), 1, atol=1e-9)

def test_zscore_multiple_columns_independently():
    df = pd.DataFrame({"x": [1.0, 2.0, 3.0], "y": [10.0, 20.0, 30.0]})
    out, _ = normalization.process(df, ["x", "y"], "Z-Score Normalization")
    assert np.isclose(out["x"].mean(), 0, atol=1e-9)
    assert np.isclose(out["y"].mean(), 0, atol=1e-9)

def test_constant_column_transforms_to_zero():
    out, _ = normalization.process(pd.DataFrame({"x": [5.0, 5.0, 5.0]}), ["x"], "Z-Score Normalization")
    assert np.allclose(out["x"], [0, 0, 0])

def test_no_columns_returns_message():
    df = pd.DataFrame({"x": [1, 2]})
    out, message = normalization.process(df, [], "Z-Score Normalization")
    pd.testing.assert_frame_equal(out, df)
    assert "No columns" in message

def test_invalid_method_returns_controlled_message():
    out, message = normalization.process(pd.DataFrame({"x": [1, 2]}), ["x"], "invalid")
    assert isinstance(out, pd.DataFrame)
    assert "Unknown" in message
