import numpy as np
import pandas as pd
import pytest
from analysis.correlation import analyze

@pytest.mark.parametrize("method", ["Pearson", "Spearman", "Kendall"])
def test_correlation_matrix_for_supported_methods(method):
    df = pd.DataFrame({"a": [1, 2, 3, 4], "b": [2, 4, 6, 8], "text": ["a", "b", "c", "d"]})
    matrix, pairs, log = analyze(df, method=method, threshold=0.8)
    assert matrix.loc["a", "b"] == pytest.approx(1.0)
    assert len(pairs) == 1
    assert pairs.iloc[0]["Feature 1"] == "a"

def test_threshold_includes_high_correlation_pairs():
    df = pd.DataFrame({"a": [1, 2, 3], "b": [1, 2, 3], "c": [3, 2, 1]})
    _, pairs, _ = analyze(df, threshold=0.8)
    assert len(pairs) == 3

def test_negative_high_correlation_included_by_absolute_value():
    df = pd.DataFrame({"a": [1, 2, 3], "b": [3, 2, 1]})
    _, pairs, _ = analyze(df, threshold=0.8)
    assert len(pairs) == 1
    assert pairs.iloc[0]["Correlation"] < 0

def test_one_numeric_column_returns_empty_results():
    matrix, pairs, log = analyze(pd.DataFrame({"a": [1, 2], "s": ["x", "y"]}))
    assert matrix.empty and pairs.empty
    assert log["Changes"] == 0

def test_no_numeric_columns_returns_empty_results():
    matrix, pairs, log = analyze(pd.DataFrame({"s": ["x", "y"]}))
    assert matrix.empty and pairs.empty
    assert log["Changes"] == 0

def test_invalid_method_is_rejected():
    with pytest.raises((ValueError, KeyError)):
        analyze(pd.DataFrame({"a": [1, 2], "b": [2, 3]}), method="invalid")
