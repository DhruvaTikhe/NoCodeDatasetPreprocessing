import pandas as pd
import pytest
from preprocessing import redundant

def test_remove_one_column():
    df = pd.DataFrame({"keep": [1, 2], "remove": [3, 4]})
    result, log = redundant.process(df, ["remove"], "Remove Columns")
    assert list(result.columns) == ["keep"]
    assert result["keep"].tolist() == [1, 2]
    assert len(result) == 2

def test_remove_multiple_columns():
    df = pd.DataFrame({"a": [1], "b": [2], "c": [3]})
    result, _ = redundant.process(df, ["a", "c"], "Remove Columns")
    assert list(result.columns) == ["b"]

def test_invalid_column_raises_controlled_error():
    df = pd.DataFrame({"a": [1]})
    with pytest.raises((KeyError, ValueError)):
        redundant.process(df, ["missing"], "Remove Columns")

def test_no_columns_selected_is_noop():
    df = pd.DataFrame({"a": [1]})
    result, _ = redundant.process(df, [], "Remove Columns")
    pd.testing.assert_frame_equal(result, df)
