import duckdb
from pathlib import Path
import uuid


TITLE = "Whitespace"
COLUMN_TYPE = "categorical"

METHODS = [
    "Trim Leading and Trailing Whitespace"
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
        f"{dataset_path.stem}_whitespace_{uuid.uuid4().hex[:8]}.parquet"
    )

    con = duckdb.connect()

    try:

        if dataset_path.suffix.lower() == ".parquet":
            source = f"read_parquet('{dataset_path}')"
        else:
            source = f"read_csv_auto('{dataset_path}')"

        schema = con.execute(
            f"DESCRIBE SELECT * FROM {source}"
        ).fetchall()

        string_columns = {
            row[0]
            for row in schema
            if row[1].lower() in (
                "varchar",
                "text",
                "string"
            )
        }

        # Only trim selected string columns
        selected_string_columns = [
            col for col in columns
            if col in string_columns
        ]

        all_columns = [row[0] for row in schema]

        def quote_identifier(name):
            return '"' + name.replace('"', '""') + '"'

        select_parts = []

        for col in all_columns:

            quoted = quote_identifier(col)

            if col in selected_string_columns:
                select_parts.append(
                    f"TRIM({quoted}) AS {quoted}"
                )
            else:
                select_parts.append(quoted)

        select_clause = ", ".join(select_parts)

        con.execute(f"""
            COPY (
                SELECT {select_clause}
                FROM {source}
            )
            TO '{output_path}'
            (FORMAT PARQUET)
        """)

    finally:
        con.close()

    log = (
        f"Trimmed whitespace from "
        f"{len(selected_string_columns)} column(s)."
    )

    return str(output_path), log