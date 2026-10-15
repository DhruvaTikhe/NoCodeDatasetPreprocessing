import pandas as pd
import pytest
from preprocessing import outliers

def test_iqr_removes_obvious_outlier():
    df = pd.DataFrame({"x": [10, 11, 12, 11, 10, 1000]})
    out, log = outliers.process(df, ["x"], "Remove Outliers", detection_method="IQR")
    assert 1000 not in out["x"].tolist()
    assert len(out) < len(df)

def test_iqr_no_outliers_keeps_rows():
    df = pd.DataFrame({"x": [10, 11, 12, 13, 14]})
    out, _ = outliers.process(df, ["x"], "Remove Outliers", detection_method="IQR")
    assert len(out) == len(df)

def test_zscore_removes_extreme_value():
    df = pd.DataFrame({"x": [10, 11, 12, 11, 10, 1000]})
    out, _ = outliers.process(df, ["x"], "Remove Outliers", detection_method="Z-Score", threshold=2)
    assert 1000 not in out["x"].tolist()

def test_constant_column_no_rows_removed():
    df = pd.DataFrame({"x": [5, 5, 5, 5]})
    out, _ = outliers.process(df, ["x"], "Remove Outliers", detection_method="Z-Score")
    assert len(out) == len(df)

def test_multiple_columns_removes_row_if_any_selected_is_outlier():
    df = pd.DataFrame({"a": [1, 2, 3, 4, 1000], "b": [1, 2, 3, 4, 5]})
    out, _ = outliers.process(df, ["a", "b"], "Remove Outliers", detection_method="IQR")
    assert 1000 not in out["a"].tolist()

def test_nan_not_classified_as_outlier():
    df = pd.DataFrame({"x": [1.0, 2.0, 3.0, None, 4.0]})
    out, _ = outliers.process(df, ["x"], "Remove Outliers", detection_method="IQR")
    assert out["x"].isna().sum() == 1

def test_non_numeric_selected_column_is_skipped():
    df = pd.DataFrame({"x": ["a", "b", "c"]})
    out, _ = outliers.process(df, ["x"], "Remove Outliers", detection_method="IQR")
    assert len(out) == 3

def test_invalid_detection_method_raises_value_error():
    with pytest.raises(ValueError):
        outliers.process(pd.DataFrame({"x": [1, 2, 3]}), ["x"], "Remove Outliers", detection_method="invalid")

def test_no_columns_no_rows_removed():
    df = pd.DataFrame({"x": [1, 2]})
    out, _ = outliers.process(df, [], "Remove Outliers")
    assert len(out) == len(df)
