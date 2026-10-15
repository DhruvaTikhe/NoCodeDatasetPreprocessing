import pandas as pd
from preprocessing import duplicates

def test_exact_duplicate_rows_removed():
    df = pd.DataFrame({"a": [1, 1, 2], "b": ["x", "x", "y"]})
    result, log = duplicates.process(df, [], "Drop Duplicates")
    assert len(result) == 2
    assert not result.duplicated().any()

def test_no_duplicates_returns_same_rows():
    df = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
    result, log = duplicates.process(df, [], "Drop Duplicates")
    pd.testing.assert_frame_equal(result.reset_index(drop=True), df.reset_index(drop=True))
    assert log["Changes"] == 0

def test_duplicate_rows_containing_null_are_deduplicated_like_pandas():
    df = pd.DataFrame({"a": [1, 1, None, None], "b": ["x", "x", "z", "z"]})
    result, _ = duplicates.process(df, [], "Drop Duplicates")
    assert len(result) == 2
    assert not result.duplicated().any()

def test_method_argument_does_not_change_drop_duplicates_behavior():
    df = pd.DataFrame({"a": [1, 1]})
    result, _ = duplicates.process(df, [], "Any UI method")
    assert len(result) == 1
