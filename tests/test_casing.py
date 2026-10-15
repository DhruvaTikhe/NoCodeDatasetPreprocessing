import pandas as pd
from preprocessing import casing

def test_lowercase():
    result, _ = casing.process(pd.DataFrame({"x": ["AbC"]}), ["x"], "Lowercase")
    assert result["x"].tolist() == ["abc"]

def test_uppercase():
    result, _ = casing.process(pd.DataFrame({"x": ["AbC"]}), ["x"], "Uppercase")
    assert result["x"].tolist() == ["ABC"]

def test_title_case():
    result, _ = casing.process(pd.DataFrame({"x": ["hello WORLD"]}), ["x"], "Title Case")
    assert result["x"].tolist() == ["Hello World"]

def test_capitalize_direct_call():
    result, _ = casing.process(pd.DataFrame({"x": ["hello WORLD"]}), ["x"], "Capitalize")
    assert result["x"].tolist() == ["Hello world"]

def test_non_string_and_null_values_are_safe():
    df = pd.DataFrame({"x": [" Ab ", None, 12]})
    result, _ = casing.process(df, ["x"], "Lowercase")
    assert result["x"].iloc[0] == " ab "
    assert pd.isna(result["x"].iloc[1])
    assert result["x"].iloc[2] == 12
