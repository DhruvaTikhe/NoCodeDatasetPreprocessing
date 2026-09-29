import duckdb
import os


def connect():
    return duckdb.connect()


def get_source(file_path):
    if file_path.lower().endswith(".parquet"):
        return f"read_parquet('{file_path}')"

    elif file_path.lower().endswith(".csv"):
        return f"read_csv_auto('{file_path}')"

    else:
        raise ValueError(f"Unsupported file type: {file_path}")

    
def preview(con, path, rows=10):
    source = get_source(path)
    return con.execute(f"""
        SELECT *
        FROM {source}
        LIMIT {rows}
    """).df()




def describe(con, path):
    source = get_source(path)

    return con.execute(f"""
        DESCRIBE
        SELECT *
        FROM {source}
    """).df()


def dataset_info(con, path, progress_callback=None):

    # ---------------------------------------------------------
    # Step 1: Read schema
    # ---------------------------------------------------------

    if progress_callback:
        progress_callback(0.10, "Reading dataset schema...")

    schema = describe(con,path)

    columns = schema["column_name"].tolist()

    # ---------------------------------------------------------
    # Step 2: Calculate row + non-null counts
    # ---------------------------------------------------------

    if progress_callback:
        progress_callback(0.25, "Calculating row and non-null counts...")

    count_expressions = []

    for column in columns:

        safe_column = '"' + column.replace('"', '""') + '"'

        count_expressions.append(
            f'COUNT({safe_column}) AS "{column}"'
        )

    source = get_source(path)
    count_query = f"""
        SELECT
            COUNT(*) AS row_count,
            {", ".join(count_expressions)}
            FROM {source}
    """

    counts = con.execute(count_query).fetchone()

    row_count = counts[0]

    non_null_counts = dict(
        zip(columns, counts[1:])
    )

    # ---------------------------------------------------------
    # Step 3: Build information table
    # ---------------------------------------------------------

    if progress_callback:
        progress_callback(0.70, "Preparing dataset information...")

    info_data = schema[["column_name", "column_type"]].copy()

    info_data.rename(
        columns={
            "column_name": "Column",
            "column_type": "Dtype"
        },
        inplace=True
    )

    info_data["Non-Null Count"] = (
        info_data["Column"].map(non_null_counts)
    )

    info_data["Null Count"] = (
        row_count - info_data["Non-Null Count"]
    )

    info_data = info_data[
        ["Column", "Non-Null Count", "Null Count", "Dtype"]
    ]

    # ---------------------------------------------------------
    # Step 4: Missing values
    # ---------------------------------------------------------

    if progress_callback:
        progress_callback(0.80, "Calculating missing values...")

    missing_count = int(
        info_data["Null Count"].sum()
    )

    if progress_callback:
        progress_callback(1.0, "Dataset information ready.")

    return info_data, row_count, missing_count


def duplicate_count(con, path, columns):

    column_list = ", ".join(
        '"' + col.replace('"', '""') + '"'
        for col in columns
    )

    source = get_source(path)
    result = con.execute(f"""
        SELECT
            COUNT(*) - COUNT(*) OVER () AS duplicate_count
        FROM (
            SELECT DISTINCT {column_list}
            FROM {source}
        )
    """).fetchone()

    return result[0]



