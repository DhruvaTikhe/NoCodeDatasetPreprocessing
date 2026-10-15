import pandas as pd
import pytest
from utils.loader import load_dataset

def test_load_valid_csv(tmp_path):
    path = tmp_path / "sample.csv"
    path.write_text("name,age\nAsha,20\nRavi,30\n", encoding="utf-8")
    df = load_dataset(str(path))
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (2, 2)
    assert df["name"].tolist() == ["Asha", "Ravi"]

def test_load_valid_xlsx(tmp_path):
    path = tmp_path / "sample.xlsx"
    pd.DataFrame({"name": ["Asha"], "age": [20]}).to_excel(path, index=False)
    df = load_dataset(str(path))
    assert df.to_dict("records") == [{"name": "Asha", "age": 20}]

def test_unsupported_extension_raises_value_error(tmp_path):
    path = tmp_path / "sample.json"
    path.write_text('{"a":1}', encoding="utf-8")
    with pytest.raises(ValueError, match="Unsupported file format"):
        load_dataset(str(path))

def test_malformed_csv_does_not_return_corrupted_dataframe(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text('a,b\n1,2\n3,"unterminated\n', encoding="utf-8")
    with pytest.raises((ValueError, pd.errors.ParserError, UnicodeDecodeError)):
        load_dataset(str(path))
