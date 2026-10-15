"""DuckDB helpers for previewing and profiling CSV/Parquet datasets."""

import os
import duckdb


def connect():
    return duckdb.connect()


def _sql_string(value):
    """Escape a path for use as a DuckDB SQL string literal."""
    return "'" + str(value).replace("'", "''") + "'"


def get_source(file_path):
    path = os.fspath(file_path)
    lower_path = path.lower()
    escaped_path = _sql_string(path)
    if lower_path.endswith(".parquet"):
        return f"read_parquet({escaped_path})"
    if lower_path.endswith(".csv"):
        return f"read_csv_auto({escaped_path})"
    raise ValueError(f"Unsupported file type: {file_path}")


def preview(con, path, rows=10):
    if not isinstance(rows, int) or rows < 0:
        raise ValueError("rows must be a non-negative integer")
    source = get_source(path)
    return con.execute(f"SELECT * FROM {source} LIMIT {rows}").df()


def describe(con, path):
    source = get_source(path)
    return con.execute(f"DESCRIBE SELECT * FROM {source}").df()


def dataset_info(con, path, progress_callback=None):
    """Return (column_info_dataframe, row_count, total_missing_cells)."""
    if progress_callback:
        progress_callback(0.10, "Reading dataset schema...")
    schema = describe(con, path)
    columns = schema["column_name"].tolist()

    if progress_callback:
        progress_callback(0.25, "Calculating row and non-null counts...")

    source = get_source(path)
    count_expressions = [
        f'COUNT("{column.replace(chr(34), chr(34) * 2)}") AS "{column.replace(chr(34), chr(34) * 2)}"'
        for column in columns
    ]
    if count_expressions:
        count_query = (
            f"SELECT COUNT(*) AS row_count, {', '.join(count_expressions)} "
            f"FROM {source}"
        )
        counts = con.execute(count_query).fetchone()
        row_count = int(counts[0])
        non_null_counts = dict(zip(columns, counts[1:]))
    else:
        row_count = int(con.execute(f"SELECT COUNT(*) FROM {source}").fetchone()[0])
        non_null_counts = {}

    if progress_callback:
        progress_callback(0.70, "Preparing dataset information...")

    info_data = schema[["column_name", "column_type"]].copy()
    info_data.rename(columns={"column_name": "Column", "column_type": "Dtype"}, inplace=True)
    info_data["Non-Null Count"] = info_data["Column"].map(non_null_counts).astype("int64")
    info_data["Null Count"] = row_count - info_data["Non-Null Count"]
    info_data = info_data[["Column", "Non-Null Count", "Null Count", "Dtype"]]

    if progress_callback:
        progress_callback(0.80, "Calculating missing values...")
    missing_count = int(info_data["Null Count"].sum())

    if progress_callback:
        progress_callback(1.0, "Dataset information ready.")
    return info_data, row_count, missing_count


def duplicate_count(con, path, columns):
    """Count duplicate rows based on selected columns, or all columns if empty."""
    source = get_source(path)
    columns = list(columns or [])
    if not columns:
        columns = describe(con, path)["column_name"].tolist()
    if not columns:
        return 0

    quoted_columns = ", ".join(
        '"' + str(column).replace('"', '""') + '"'
        for column in columns
    )
    total_rows = int(con.execute(f"SELECT COUNT(*) FROM {source}").fetchone()[0])
    unique_rows = int(
        con.execute(
            f"SELECT COUNT(*) FROM (SELECT DISTINCT {quoted_columns} FROM {source})"
        ).fetchone()[0]
    )
    return total_rows - unique_rows
