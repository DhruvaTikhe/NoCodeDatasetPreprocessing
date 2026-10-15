import pandas as pd
import pytest
import duckdb
from utils import scalable_loader as sl

def test_get_source_csv_and_parquet():
    assert sl.get_source("x.csv").startswith("read_csv_auto(")
    assert sl.get_source("x.parquet").startswith("read_parquet(")

def test_unsupported_extension_raises():
    with pytest.raises(ValueError):
        sl.get_source("x.json")

def test_preview_limits_rows(tmp_path):
    path = tmp_path / "x.csv"
    pd.DataFrame({"a": range(15), "b": list("abcdefghijklmno")}).to_csv(path, index=False)
    con = sl.connect()
    try:
        out = sl.preview(con, str(path), rows=10)
        assert len(out) == 10
        assert out.columns.tolist() == ["a", "b"]
    finally:
        con.close()

def test_describe_returns_schema(tmp_path):
    path = tmp_path / "x.csv"
    pd.DataFrame({"a": [1, 2], "b": ["x", "y"]}).to_csv(path, index=False)
    con = sl.connect()
    try:
        schema = sl.describe(con, str(path))
        assert {"column_name", "column_type"}.issubset(schema.columns)
    finally:
        con.close()

def test_dataset_info_row_and_null_counts(tmp_path):
    path = tmp_path / "x.csv"
    pd.DataFrame({"a": [1, None, 3], "b": ["x", "y", "z"]}).to_csv(path, index=False)
    con = sl.connect()
    try:
        info, row_count, missing_count = sl.dataset_info(con, str(path))
        assert "Column" in info.columns
        assert info["Null Count"].sum() == 1
        assert info["Non-Null Count"].sum() == 5
        assert row_count == 3
        assert missing_count == 1
    finally:
        con.close()

def test_dataset_info_progress_callback_finishes_at_one(tmp_path):
    path = tmp_path / "x.csv"
    pd.DataFrame({"a": [1, 2]}).to_csv(path, index=False)
    seen = []
    con = sl.connect()
    try:
        sl.dataset_info(con, str(path), lambda progress, message: seen.append((progress, message)))
    finally:
        con.close()
    assert seen and seen[-1][0] == 1.0

def test_duplicate_count(tmp_path):
    path = tmp_path / "x.csv"
    pd.DataFrame({"a": [1, 1, 2], "b": ["x", "x", "y"]}).to_csv(path, index=False)
    con = sl.connect()
    try:
        # The implementation's definition is validated against exact duplicate rows.
        count = sl.duplicate_count(con, str(path), [])
        assert count == 1
    finally:
        con.close()
