from io import BytesIO
import pandas as pd
from utils.exporter import to_csv_bytes, to_excel_bytes, generate_filename

def test_csv_bytes_are_utf8_without_index():
    df = pd.DataFrame({"name": ["Ásha"], "age": [20]})
    data = to_csv_bytes(df)
    assert isinstance(data, bytes)
    text = data.decode("utf-8")
    assert "Ásha" in text
    assert "0," not in text

def test_excel_bytes_are_valid_and_sheet_named_cleaned_dataset():
    data = to_excel_bytes(pd.DataFrame({"a": [1]}))
    loaded = pd.read_excel(BytesIO(data), sheet_name="Cleaned Dataset")
    assert loaded.to_dict("records") == [{"a": 1}]

def test_generate_csv_filename():
    assert generate_filename("original.csv", "csv") == "original_cleaned.csv"

def test_generate_xlsx_filename():
    assert generate_filename("original.xlsx", "xlsx") == "original_cleaned.xlsx"
