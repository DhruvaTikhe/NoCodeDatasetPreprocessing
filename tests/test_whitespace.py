import pandas as pd
import pytest
from preprocessing import whitespace

def test_trim_outer_whitespace():
    df = pd.DataFrame({"name": [" A ", "B  "]})
    result, _ = whitespace.process(df, ["name"], "Trim")
    assert result["name"].tolist() == ["A", "B"]

def test_remove_extra_spaces_direct_call():
    df = pd.DataFrame({"name": ["A   B", "  C  D "]})
    result, _ = whitespace.process(df, ["name"], "Remove Extra Spaces")
    assert result["name"].tolist() == ["A B", "C D"]

def test_remove_all_spaces_direct_call():
    df = pd.DataFrame({"name": ["A B", " C  D "]})
    result, _ = whitespace.process(df, ["name"], "Remove All Spaces")
    assert result["name"].tolist() == ["AB", "CD"]

def test_multiple_columns_cleaned():
    df = pd.DataFrame({"a": [" x "], "b": [" y "], "n": [2]})
    result, _ = whitespace.process(df, ["a", "b"], "Trim")
    assert result["a"].iloc[0] == "x"
    assert result["b"].iloc[0] == "y"
    assert result["n"].iloc[0] == 2

def test_null_values_remain_null():
    df = pd.DataFrame({"name": [" A ", None]})
    result, _ = whitespace.process(df, ["name"], "Trim")
    assert result["name"].iloc[0] == "A"
    assert pd.isna(result["name"].iloc[1])

def test_invalid_method_raises_value_error():
    with pytest.raises(ValueError):
        whitespace.process(pd.DataFrame({"a": [" x "]}), ["a"], "Bad method")
