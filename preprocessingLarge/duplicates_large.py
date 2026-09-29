import duckdb
from pathlib import Path
import uuid


TITLE = "Duplicates"
COLUMN_TYPE = "all"

METHODS = [
    "Drop Duplicates"
]

SHOW_CONSTANT = False
ALLOW_MULTISELECT = False


def processLargeDataset(
    dataset_path,
    columns=None,
    method=None,
    constant=None
):
    dataset_path = Path(dataset_path)

    output_path = dataset_path.parent / (
        f"{dataset_path.stem}_duplicates_{uuid.uuid4().hex[:8]}.parquet"
    )

    con = duckdb.connect()

    try:

        if dataset_path.suffix.lower() == ".parquet":
            source = f"read_parquet('{dataset_path}')"
        else:
            source = f"read_csv_auto('{dataset_path}')"

        con.execute(f"""
            COPY (
                SELECT DISTINCT *
                FROM {source}
            )
            TO '{output_path}'
            (FORMAT PARQUET)
        """)

    finally:
        con.close()

    log = "Removed duplicate rows."

    return str(output_path), log