import pandas as pd
import pytest
from preprocessingLarge import redundant_large, duplicates_large, whitespace_large, casing_large, missing_values_large

def read_parquet(path):
    import duckdb
    con = duckdb.connect()
    try:
        return con.execute("SELECT * FROM read_parquet(?)", [str(path)]).df()
    finally:
        con.close()

def write_csv(tmp_path, df, name="input.csv"):
    path = tmp_path / name
    df.to_csv(path, index=False)
    return path

def test_redundant_large_csv_removes_selected_column(tmp_path):
    path = write_csv(tmp_path, pd.DataFrame({"keep": [1, 2], "remove": [3, 4]}))
    output, log = redundant_large.processLargeDataset(path, ["remove"], "Remove Columns")
    result = read_parquet(output)
    assert result.columns.tolist() == ["keep"]
    assert result["keep"].tolist() == [1, 2]

def test_redundant_large_cannot_remove_all_columns(tmp_path):
    path = write_csv(tmp_path, pd.DataFrame({"a": [1], "b": [2]}))
    with pytest.raises(ValueError, match="Cannot remove all columns"):
        redundant_large.processLargeDataset(path, ["a", "b"], "Remove Columns")

def test_redundant_large_no_columns_returns_original_path(tmp_path):
    path = write_csv(tmp_path, pd.DataFrame({"a": [1]}))
    output, message = redundant_large.processLargeDataset(path, [], "Remove Columns")
    assert str(output) == str(path)
    assert "No columns" in message

def test_duplicates_large_removes_duplicates(tmp_path):
    path = write_csv(tmp_path, pd.DataFrame({"a": [1, 1, 2], "b": ["x", "x", "y"]}))
    output, _ = duplicates_large.processLargeDataset(path)
    result = read_parquet(output)
    assert len(result) == 2
    assert not result.duplicated().any()

def test_duplicates_large_parquet_input(tmp_path):
    import duckdb
    path = tmp_path / "input.parquet"
    con = duckdb.connect()
    try:
        con.execute("COPY (SELECT * FROM (VALUES (1, 'a'), (1, 'a'), (2, 'b')) t(a,b)) TO ? (FORMAT PARQUET)", [str(path)])
    finally:
        con.close()
    output, _ = duplicates_large.processLargeDataset(path)
    assert len(read_parquet(output)) == 2

def test_whitespace_large_trims_string_only(tmp_path):
    path = write_csv(tmp_path, pd.DataFrame({"name": [" A ", " B "], "n": [1, 2]}))
    output, _ = whitespace_large.processLargeDataset(path, ["name", "n"], "Trim Leading and Trailing Whitespace")
    result = read_parquet(output)
    assert result["name"].tolist() == ["A", "B"]
    assert result["n"].tolist() == [1, 2]

def test_whitespace_large_no_columns_returns_original(tmp_path):
    path = write_csv(tmp_path, pd.DataFrame({"name": [" A "]}))
    output, message = whitespace_large.processLargeDataset(path, [], "Trim")
    assert str(output) == str(path)
    assert "No columns" in message

@pytest.mark.parametrize(("method", "expected"), [
    ("Lowercase", ["alice", "bob"]),
    ("Uppercase", ["ALICE", "BOB"]),
    ("Title Case", ["Alice", "Bob"]),
])
def test_casing_large_methods(tmp_path, method, expected):
    path = write_csv(tmp_path, pd.DataFrame({"name": ["ALICE", "bob"], "n": [1, 2]}))
    output, _ = casing_large.processLargeDataset(path, ["name"], method)
    result = read_parquet(output)
    assert result["name"].tolist() == expected
    assert result["n"].tolist() == [1, 2]

def test_casing_large_invalid_method_raises(tmp_path):
    path = write_csv(tmp_path, pd.DataFrame({"name": ["alice"]}))
    with pytest.raises(ValueError):
        casing_large.processLargeDataset(path, ["name"], "Invalid")

def test_casing_large_non_string_column_unchanged(tmp_path):
    path = write_csv(tmp_path, pd.DataFrame({"n": [1, 2]}))
    output, _ = casing_large.processLargeDataset(path, ["n"], "Lowercase")
    assert read_parquet(output)["n"].tolist() == [1, 2]

def test_missing_values_large_mean(tmp_path):
    path = write_csv(tmp_path, pd.DataFrame({"x": [10.0, None, 30.0]}))
    output, _ = missing_values_large.processLargeDataset(path, ["x"], "Mean")
    result = read_parquet(output)
    assert result["x"].tolist() == [10.0, 20.0, 30.0]

def test_missing_values_large_median(tmp_path):
    path = write_csv(tmp_path, pd.DataFrame({"x": [10.0, None, 100.0]}))
    output, _ = missing_values_large.processLargeDataset(path, ["x"], "Median")
    assert read_parquet(output)["x"].tolist() == [10.0, 55.0, 100.0]

def test_missing_values_large_constant_text_escapes_quotes(tmp_path):
    path = write_csv(tmp_path, pd.DataFrame({"name": ["A", None, "B"]}))
    output, _ = missing_values_large.processLargeDataset(path, ["name"], "Constant (supports Text)", constant="O'Brien")
    assert read_parquet(output)["name"].tolist() == ["A", "O'Brien", "B"]

def test_missing_values_large_drop_rows(tmp_path):
    path = write_csv(tmp_path, pd.DataFrame({"x": [1, None, 3], "y": ["a", "b", "c"]}))
    output, _ = missing_values_large.processLargeDataset(path, ["x"], "Drop Rows (supports Text)")
    result = read_parquet(output)
    assert len(result) == 2
    assert result["x"].notna().all()

def test_missing_values_large_forward_backward_fill(tmp_path):
    path = write_csv(tmp_path, pd.DataFrame({"x": [1.0, None, None, 4.0]}))
    forward, _ = missing_values_large.processLargeDataset(path, ["x"], "Forward Fill (supports Text)")
    backward, _ = missing_values_large.processLargeDataset(path, ["x"], "Backward Fill (supports Text)")
    assert read_parquet(forward)["x"].tolist() == [1.0, 1.0, 1.0, 4.0]
    assert read_parquet(backward)["x"].tolist() == [1.0, 4.0, 4.0, 4.0]

def test_missing_values_large_missing_constant_rejected(tmp_path):
    path = write_csv(tmp_path, pd.DataFrame({"x": [1, None]}))
    with pytest.raises(ValueError):
        missing_values_large.processLargeDataset(path, ["x"], "Constant (supports Text)")

def test_missing_values_large_mean_text_rejected(tmp_path):
    path = write_csv(tmp_path, pd.DataFrame({"x": ["a", None]}))
    with pytest.raises(ValueError):
        missing_values_large.processLargeDataset(path, ["x"], "Mean")

def test_missing_values_large_no_columns_returns_original(tmp_path):
    path = write_csv(tmp_path, pd.DataFrame({"x": [1, None]}))
    output, message = missing_values_large.processLargeDataset(path, [], "Mean")
    assert str(output) == str(path)
    assert "No columns" in message
