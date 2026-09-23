import duckdb
import os


def connect():
    return duckdb.connect()


def save(uploaded_file):
    upload_dir = "data/uploads"
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(
        upload_dir,
        uploaded_file.name
    )

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return file_path


def preview(con, path, rows=10):
    return con.execute(f"""
        SELECT *
        FROM read_csv_auto('{path}')
        LIMIT {rows}
    """).df()


def dataset_info(con, path):

    schema = con.execute(f"""
        DESCRIBE
        SELECT *
        FROM read_csv_auto('{path}')
    """).df()

    row_count = con.execute(f"""
        SELECT COUNT(*)
        FROM read_csv_auto('{path}')
    """).fetchone()[0]

    return schema, row_count