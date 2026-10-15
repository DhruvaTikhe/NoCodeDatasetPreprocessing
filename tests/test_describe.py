import pandas as pd
from analysis.describe import analyze

def test_no_columns_describes_all_columns():
    df = pd.DataFrame({"num": [1, 2], "text": ["a", "b"]})
    result = analyze(df, [])
    assert set(result.index) == {"num", "text"}

def test_selected_columns_only():
    result = analyze(pd.DataFrame({"a": [1, 2], "b": [3, 4]}), ["b"])
    assert result.index.tolist() == ["b"]

def test_mixed_numeric_text_statistics():
    result = analyze(pd.DataFrame({"num": [1, 2], "text": ["a", "b"]}), ["num", "text"])
    assert "mean" in result.columns
    assert "unique" in result.columns

def test_empty_rows_returns_statistics_without_crash():
    result = analyze(pd.DataFrame({"a": pd.Series(dtype="float64")}), [])
    assert "a" in result.index
