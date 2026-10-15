from utils.dataset_manager import get_engine

def test_file_at_20_mb_uses_pandas():
    assert get_engine(20 * 1024 * 1024) == "pandas"

def test_file_over_20_mb_uses_duckdb():
    assert get_engine(20 * 1024 * 1024 + 1) == "duckdb"
