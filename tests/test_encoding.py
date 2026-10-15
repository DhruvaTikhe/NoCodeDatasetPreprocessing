import pandas as pd
import pytest
from preprocessing import encoding

def test_one_hot_one_column_replaces_original():
    out, log = encoding.process(pd.DataFrame({"color": ["red", "blue", "red"]}), ["color"], "One-Hot Encoding")
    assert "color" not in out.columns
    assert set(out.columns) == {"color_blue", "color_red"}
    assert out.sum().sum() == 3

def test_one_hot_multiple_columns():
    df = pd.DataFrame({"color": ["red", "blue"], "size": ["S", "L"], "n": [1, 2]})
    out, _ = encoding.process(df, ["color", "size"], "One-Hot Encoding")
    assert "color" not in out.columns and "size" not in out.columns
    assert "n" in out.columns
    assert any(c.startswith("color_") for c in out.columns)
    assert any(c.startswith("size_") for c in out.columns)

def test_one_hot_each_category_has_indicator():
    out, _ = encoding.process(pd.DataFrame({"c": ["a", "b", "c"]}), ["c"], "One-Hot Encoding")
    assert set(out.columns) == {"c_a", "c_b", "c_c"}
    assert (out.sum(axis=1) == 1).all()

def test_label_encoding_one_column():
    out, _ = encoding.process(pd.DataFrame({"c": ["red", "blue", "red"]}), ["c"], "Label Encoding")
    assert pd.api.types.is_integer_dtype(out["c"].dtype)
    assert out["c"].nunique() == 2

def test_label_encoding_multiple_columns_independently():
    df = pd.DataFrame({"a": ["x", "y"], "b": ["small", "large"]})
    out, _ = encoding.process(df, ["a", "b"], "Label Encoding")
    assert pd.api.types.is_integer_dtype(out["a"].dtype)
    assert pd.api.types.is_integer_dtype(out["b"].dtype)

def test_label_encoding_mixed_types():
    out, _ = encoding.process(pd.DataFrame({"c": ["1", 2, "a"]}), ["c"], "Label Encoding")
    assert out["c"].notna().all()

def test_label_encoding_preserves_missing_values():
    out, _ = encoding.process(pd.DataFrame({"c": ["a", None, "b"]}), ["c"], "Label Encoding")
    assert pd.isna(out["c"].iloc[1])

def test_invalid_column_list_is_safe_noop():
    df = pd.DataFrame({"a": ["x"]})
    out, log = encoding.process(df, ["missing"], "One-Hot Encoding")
    pd.testing.assert_frame_equal(out, df)
    assert "not found" in log["Message"].lower()

def test_invalid_method_raises_value_error():
    with pytest.raises(ValueError):
        encoding.process(pd.DataFrame({"c": ["x"]}), ["c"], "invalid")
