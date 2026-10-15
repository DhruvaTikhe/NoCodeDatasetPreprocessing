import pandas as pd
from analysis.value_counts import analyze

def test_one_column_counts_with_count_column():
    result = analyze(pd.DataFrame({"x": ["a", "b", "a"]}), ["x"])
    assert result["x"].columns.tolist() == ["x", "Count"]
    assert dict(zip(result["x"]["x"], result["x"]["Count"])) == {"a": 2, "b": 1}

def test_multiple_columns_return_dictionary_per_column():
    result = analyze(pd.DataFrame({"x": ["a", "a"], "y": [1, 2]}), ["x", "y"])
    assert set(result) == {"x", "y"}

def test_missing_values_are_included():
    result = analyze(pd.DataFrame({"x": ["a", None, "a"]}), ["x"])
    assert result["x"]["Count"].sum() == 3

def test_invalid_column_is_skipped():
    result = analyze(pd.DataFrame({"x": [1]}), ["missing"])
    assert result == {}

def test_empty_selection_returns_empty_dictionary():
    assert analyze(pd.DataFrame({"x": [1]}), []) == {}
