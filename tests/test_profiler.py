import pandas as pd
from utils.profiler import dataset_summary

def test_dataset_summary_counts_rows_columns_missing_duplicates():
    df = pd.DataFrame({"a": [1, 1, None], "b": ["x", "x", "z"]})
    summary = dataset_summary(df)
    assert summary["Rows"] == 3
    assert summary["Columns"] == 2
    assert summary["Missing Values"] == 1
    assert summary["Duplicate Rows"] == 1

def test_dataset_summary_empty_dataframe():
    summary = dataset_summary(pd.DataFrame())
    assert summary["Rows"] == 0
    assert summary["Columns"] == 0
    assert summary["Missing Values"] == 0
    assert summary["Duplicate Rows"] == 0
