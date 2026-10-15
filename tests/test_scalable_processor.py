import pandas as pd
import duckdb
from utils.scalable_processor import quote_identifier, get_reader, output_path, execute_to_parquet

def test_quote_identifier_simple_and_embedded_quote():
    assert quote_identifier("column") == '"column"'
    assert quote_identifier('a"b') == '"a""b"'

def test_get_reader_csv_and_parquet():
    assert get_reader("data.csv").startswith("read_csv_auto(")
    assert get_reader("data.parquet").startswith("read_parquet(")

def test_output_path_is_unique_and_contains_operation(tmp_path):
    src = tmp_path / "data.csv"
    p1 = output_path(str(src), "trim")
    p2 = output_path(str(src), "trim")
    assert p1 != p2
    assert "trim" in p1
    assert p1.endswith(".parquet")

def test_execute_to_parquet_creates_readable_file(tmp_path):
    con = duckdb.connect()
    target = tmp_path / "out.parquet"
    try:
        returned = execute_to_parquet(con, "SELECT 1 AS a UNION ALL SELECT 2 AS a", str(target))
        assert returned == str(target)
        assert target.exists()
        assert con.execute(f"SELECT * FROM read_parquet('{target}') ORDER BY a").fetchall() == [(1,), (2,)]
    finally:
        con.close()
