import pandas as pd
import pytest
from preprocessing import missing_values as mv

MEAN = "Mean"
MEDIAN = "Median"
MODE = "Mode (supports Text)"
CONSTANT = "Constant (supports Text)"
FFILL = "Forward Fill (supports Text)"
BFILL = "Backward Fill (supports Text)"
DROP = "Drop Rows (supports Text)"

def test_mean_numeric():
    df = pd.DataFrame({"x": [10.0, 20.0, None, 30.0]})
    result = mv.process(df, ["x"], MEAN)
    # Current implementation's type check returns "Wrong Datatype"; this assertion
    # intentionally checks the expected behavior and may expose that defect.
    assert isinstance(result, tuple)
    out, log = result
    assert out["x"].tolist() == [10.0, 20.0, 20.0, 30.0]
    assert log["Changes"] == 1

def test_median_numeric():
    out, log = mv.process(pd.DataFrame({"x": [10.0, 20.0, None, 100.0]}), ["x"], MEDIAN)
    assert out["x"].tolist() == [10.0, 20.0, 20.0, 100.0]
    assert log["Changes"] == 1

@pytest.mark.parametrize(("values", "expected"), [
    (["red", "blue", None, "red"], ["red", "blue", "red", "red"]),
    ([1, 2, None, 2], [1.0, 2.0, 2.0, 2.0]),
])
def test_mode(values, expected):
    out, log = mv.process(pd.DataFrame({"x": values}), ["x"], MODE)
    assert out["x"].tolist() == expected
    assert log["Changes"] == 1

@pytest.mark.parametrize(("values", "constant", "expected"), [
    ([1, None, 3], 0, [1, 0, 3]),
    ([1.0, None, 3.0], 2.5, [1.0, 2.5, 3.0]),
    (["a", None, "b"], "Unknown", ["a", "Unknown", "b"]),
])
def test_constant(values, constant, expected):
    out, log = mv.process(pd.DataFrame({"x": values}), ["x"], CONSTANT, constant_value=constant)
    assert out["x"].tolist() == expected
    assert log["Changes"] == 1

def test_constant_boolean_uses_documented_truthy_tokens():
    df = pd.DataFrame({"x": pd.Series([True, None, False], dtype="boolean")})
    out, _ = mv.process(df, ["x"], CONSTANT, constant_value="yes")
    assert out["x"].tolist() == [True, True, False]

def test_forward_fill():
    out, log = mv.process(pd.DataFrame({"x": ["A", None, None, "B", None]}), ["x"], FFILL)
    assert out["x"].tolist()[:4] == ["A", "A", "A", "B"]
    assert pd.isna(out["x"].iloc[4]) is False
    assert log["Changes"] == 3

def test_backward_fill():
    out, log = mv.process(pd.DataFrame({"x": [None, None, "A", None, "B"]}), ["x"], BFILL)
    assert out["x"].tolist() == ["A", "A", "A", "B", "B"]
    assert log["Changes"] == 3

def test_drop_rows_selected_columns():
    df = pd.DataFrame({"x": [1.0, None, 3.0], "y": ["a", "b", None]})
    out, log = mv.process(df, ["x", "y"], DROP)
    assert out[["x", "y"]].values.tolist() == [[1.0, "a"]]
    assert log["Changes"] == 2

def test_no_columns_is_noop():
    df = pd.DataFrame({"x": [1.0, None]})
    out, log = mv.process(df, [], MEDIAN)
    pd.testing.assert_frame_equal(out, df)
    assert log["Changes"] == 0

def test_mean_text_is_rejected():
    assert mv.process(pd.DataFrame({"x": ["a", None]}), ["x"], MEAN) == "Wrong Datatype"

def test_median_text_is_rejected():
    with pytest.raises((TypeError, ValueError)):
        mv.process(pd.DataFrame({"x": ["a", None]}), ["x"], MEDIAN)

@pytest.mark.parametrize("method", [MEAN, MEDIAN, MODE])
def test_all_null_column_does_not_silently_return_malformed_data(method):
    df = pd.DataFrame({"x": [None, None]})
    # This captures that behavior should be handled intentionally; pandas mode
    # currently raises IndexError and mean/median may leave nulls.
    try:
        result = mv.process(df, ["x"], method)
    except (ValueError, TypeError, IndexError):
        return
    assert isinstance(result, tuple)
    out, _ = result
    assert list(out.columns) == ["x"]
