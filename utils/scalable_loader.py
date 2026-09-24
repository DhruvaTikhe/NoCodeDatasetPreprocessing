import duckdb
import os


def connect():
    return duckdb.connect()


def preview(con, path, rows=10):
    return con.execute(f"""
        SELECT *
        FROM read_csv_auto('{path}')
        LIMIT {rows}
    """).df()


def dataset_info(con, path):

    # Get schema
    schema = con.execute(f"""
        DESCRIBE
        SELECT *
        FROM read_csv_auto('{path}')
    """).df()

    # Build expressions for null/non-null counts
    columns = schema["column_name"].tolist()

    count_expressions = []

    for column in columns:
        safe_column = '"' + column.replace('"', '""') + '"'

        count_expressions.append(
            f'COUNT({safe_column}) AS "{column}"'
        )

    count_query = f"""
        SELECT
            COUNT(*) AS row_count,
            {", ".join(count_expressions)}
        FROM read_csv_auto('{path}')
    """

    counts = con.execute(count_query).fetchone()

    row_count = counts[0]

    non_null_counts = dict(
        zip(columns, counts[1:])
    )

    info = schema[["column_name", "column_type"]].copy()

    info.rename(
        columns={
            "column_name": "Column",
            "column_type": "Dtype"
        },
        inplace=True
    )

    info["Non-Null Count"] = info["Column"].map(non_null_counts)
    info["Null Count"] = row_count - info["Non-Null Count"]

    info = info[
        ["Column", "Non-Null Count", "Null Count", "Dtype"]
    ]

    return info, row_count



def dataset_info(con, path, progress_callback=None):

    # ---------------------------------------------------------
    # Step 1: Read schema
    # ---------------------------------------------------------

    if progress_callback:
        progress_callback(0.10, "Reading dataset schema...")

    schema = con.execute(f"""
        DESCRIBE
        SELECT *
        FROM read_csv_auto('{path}')
    """).df()

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

    count_query = f"""
        SELECT
            COUNT(*) AS row_count,
            {", ".join(count_expressions)}
        FROM read_csv_auto('{path}')
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

    result = con.execute(f"""
        SELECT
            COUNT(*) - COUNT(*) OVER () AS duplicate_count
        FROM (
            SELECT DISTINCT {column_list}
            FROM read_csv_auto('{path}')
        )
    """).fetchone()

    return result[0]


#dead functions since not uploading datasets anymore
# def save(uploaded_file):
#     upload_dir = "data/uploads"
#     os.makedirs(upload_dir, exist_ok=True)

#     file_path = os.path.join(
#         upload_dir,
#         uploaded_file.name
#     )

#     with open(file_path, "wb") as f:
#         f.write(uploaded_file.getbuffer())

#     return file_path