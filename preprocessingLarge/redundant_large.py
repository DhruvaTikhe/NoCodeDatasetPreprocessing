import duckdb
from pathlib import Path
import uuid


TITLE = "Redundant"
COLUMN_TYPE = "all"

METHODS = [
    "Remove Columns"
]

SHOW_CONSTANT = False
ALLOW_MULTISELECT = True


def processLargeDataset(
    dataset_path,
    columns,
    method,
    constant=None
):
    if not columns:
        return dataset_path, "No columns selected."

    dataset_path = Path(dataset_path)

    output_path = dataset_path.parent / (
        f"{dataset_path.stem}_redundant_{uuid.uuid4().hex[:8]}.parquet"
    )

    con = duckdb.connect()

    try:
        # Get all columns
        if dataset_path.suffix.lower() == ".parquet":
            source = f"read_parquet('{dataset_path}')"
        else:
            source = f"read_csv_auto('{dataset_path}')"

        schema = con.execute(
            f"DESCRIBE SELECT * FROM {source}"
        ).fetchall()

        all_columns = [row[0] for row in schema]

        # Prevent removing every column
        remaining_columns = [
            col for col in all_columns
            if col not in columns
        ]

        if not remaining_columns:
            raise ValueError(
                "Cannot remove all columns from the dataset."
            )

        def quote_identifier(name):
            return '"' + name.replace('"', '""') + '"'

        select_columns = ", ".join(
            quote_identifier(col)
            for col in remaining_columns
        )

        con.execute(f"""
            COPY (
                SELECT {select_columns}
                FROM {source}
            )
            TO '{output_path}'
            (FORMAT PARQUET)
        """)

    finally:
        con.close()

    log = (
        f"Removed {len(columns)} redundant column(s): "
        f"{', '.join(columns)}"
    )

    return str(output_path), log