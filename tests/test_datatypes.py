import pandas as pd
import pytest
from preprocessing import datatypes

def test_integer_conversion_uses_nullable_integer_dtype():
    result, _ = datatypes.process(pd.DataFrame({"x": ["1", "2"]}), ["x"], "Integer")
    assert str(result["x"].dtype) == "Int64"
    assert result["x"].tolist() == [1, 2]

def test_invalid_integer_values_become_missing():
    result, _ = datatypes.process(pd.DataFrame({"x": ["1", "bad"]}), ["x"], "Integer")
    assert result["x"].iloc[0] == 1
    assert pd.isna(result["x"].iloc[1])

def test_float_conversion():
    result, _ = datatypes.process(pd.DataFrame({"x": ["1.5", "2"]}), ["x"], "Float")
    assert result["x"].tolist() == [1.5, 2.0]

def test_string_conversion():
    result, _ = datatypes.process(pd.DataFrame({"x": [1, 2]}), ["x"], "String")
    assert str(result["x"].dtype) == "string"
    assert result["x"].tolist() == ["1", "2"]

@pytest.mark.parametrize(("values", "expected"), [
    (["true", "false", "yes", "no", "y", "n"], [True, False, True, False, True, False]),
    (["0", "1"], [True, False]),
])
def test_boolean_conversion(values, expected):
    result, _ = datatypes.process(pd.DataFrame({"x": values}), ["x"], "Boolean")
    assert result["x"].tolist() == expected

def test_datetime_conversion_invalid_to_nat():
    result, _ = datatypes.process(pd.DataFrame({"x": ["2024-01-01", "not-a-date"]}), ["x"], "Datetime")
    assert pd.api.types.is_datetime64_any_dtype(result["x"])
    assert pd.isna(result["x"].iloc[1])

def test_category_conversion():
    result, _ = datatypes.process(pd.DataFrame({"x": ["a", "b"]}), ["x"], "Category")
    assert isinstance(result["x"].dtype, pd.CategoricalDtype)

def test_unsupported_method_reports_error():
    result, log = datatypes.process(pd.DataFrame({"x": ["1"]}), ["x"], "Unsupported")
    assert "error" in log["Message"].lower() or "Errors" in log

def test_no_columns_is_noop():
    df = pd.DataFrame({"x": ["1"]})
    result, log = datatypes.process(df, [], "Integer")
    pd.testing.assert_frame_equal(result, df)
    assert log["Changes"] == 0

def test_mixed_valid_invalid_columns_converts_valid_and_logs_invalid():
    df = pd.DataFrame({"valid": ["1", "2"], "bad": ["a", "b"]})
    result, log = datatypes.process(df, ["valid", "absent"], "Integer")
    assert result["valid"].tolist() == [1, 2]
    assert "absent" in log.get("Errors", "") or "error" in log["Message"].lower()
