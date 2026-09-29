import duckdb
from pathlib import Path
import uuid


TITLE = "Missing Values"
COLUMN_TYPE = "all"

METHODS = [
    "Mean",
    "Median",
    "Mode (supports Text)",
    "Constant (supports Text)",
    "Forward Fill (supports Text)",
    "Backward Fill (supports Text)",
    "Drop Rows (supports Text)"
]

SHOW_CONSTANT = True
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
        f"{dataset_path.stem}_missing_{uuid.uuid4().hex[:8]}.parquet"
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

        all_columns = [row[0] for row in schema]

        type_map = {
            row[0]: row[1].lower()
            for row in schema
        }

        def quote_identifier(name):
            return '"' + name.replace('"', '""') + '"'

        # ------------------------------------------------
        # DROP ROWS
        # ------------------------------------------------

        if method == "Drop Rows (supports Text)":

            conditions = " AND ".join(
                f"{quote_identifier(col)} IS NOT NULL"
                for col in columns
            )

            con.execute(f"""
                COPY (
                    SELECT *
                    FROM {source}
                    WHERE {conditions}
                )
                TO '{output_path}'
                (FORMAT PARQUET)
            """)

        # ------------------------------------------------
        # CONSTANT
        # ------------------------------------------------

        elif method == "Constant (supports Text)":

            if constant is None or constant == "":
                raise ValueError(
                    "Please provide a constant value."
                )

            select_parts = []

            for col in all_columns:

                quoted = quote_identifier(col)

                if col in columns:

                    dtype = type_map[col]

                    if any(x in dtype for x in [
                        "int",
                        "decimal",
                        "double",
                        "float",
                        "numeric"
                    ]):
                        try:
                            value = float(constant)
                            expression = (
                                f"COALESCE({quoted}, {value})"
                            )
                        except ValueError:
                            raise ValueError(
                                f"'{constant}' is not a valid "
                                f"numeric value for {col}."
                            )

                    else:
                        escaped = constant.replace("'", "''")

                        expression = (
                            f"COALESCE("
                            f"{quoted}, "
                            f"'{escaped}'"
                            f")"
                        )

                    select_parts.append(
                        f"{expression} AS {quoted}"
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

        # ------------------------------------------------
        # MEAN
        # ------------------------------------------------

        elif method == "Mean":

            select_parts = []

            for col in all_columns:

                quoted = quote_identifier(col)

                if col in columns:

                    dtype = type_map[col]

                    if not any(x in dtype for x in [
                        "int",
                        "decimal",
                        "double",
                        "float",
                        "numeric"
                    ]):
                        raise ValueError(
                            f"Mean can only be used on "
                            f"numeric column: {col}"
                        )

                    expression = (
                        f"COALESCE("
                        f"{quoted}, "
                        f"AVG({quoted}) OVER ()"
                        f")"
                    )

                    select_parts.append(
                        f"{expression} AS {quoted}"
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

        # ------------------------------------------------
        # MEDIAN
        # ------------------------------------------------

        elif method == "Median":

            select_parts = []

            for col in all_columns:

                quoted = quote_identifier(col)

                if col in columns:

                    dtype = type_map[col]

                    if not any(x in dtype for x in [
                        "int",
                        "decimal",
                        "double",
                        "float",
                        "numeric"
                    ]):
                        raise ValueError(
                            f"Median can only be used on "
                            f"numeric column: {col}"
                        )

                    expression = (
                        f"COALESCE("
                        f"{quoted}, "
                        f"MEDIAN({quoted}) OVER ()"
                        f")"
                    )

                    select_parts.append(
                        f"{expression} AS {quoted}"
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

        # ------------------------------------------------
        # MODE
        # ------------------------------------------------

        elif method == "Mode (supports Text)":

            select_parts = []

            for col in all_columns:

                quoted = quote_identifier(col)

                if col in columns:

                    mode_expression = (
                        f"MODE() WITHIN GROUP "
                        f"(ORDER BY {quoted}) OVER ()"
                    )

                    expression = (
                        f"COALESCE("
                        f"{quoted}, "
                        f"{mode_expression}"
                        f")"
                    )

                    select_parts.append(
                        f"{expression} AS {quoted}"
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

        # ------------------------------------------------
        # FORWARD / BACKWARD FILL
        # ------------------------------------------------

        elif method in ("Forward Fill (supports Text)", "Backward Fill (supports Text)"):

            # Create an internal row ordering.
            base_query = f"""
                SELECT *,
                       ROW_NUMBER() OVER () AS __nocodeprep_row
                FROM {source}
            """

            select_parts = []

            for col in all_columns:

                quoted = quote_identifier(col)

                if col in columns:

                    if method == "Forward Fill":

                        expression = f"""
                            LAST_VALUE({quoted} IGNORE NULLS)
                            OVER (
                                ORDER BY __nocodeprep_row
                                ROWS BETWEEN
                                    UNBOUNDED PRECEDING
                                    AND CURRENT ROW
                            )
                        """

                    else:

                        expression = f"""
                            FIRST_VALUE({quoted} IGNORE NULLS)
                            OVER (
                                ORDER BY __nocodeprep_row
                                ROWS BETWEEN
                                    CURRENT ROW
                                    AND UNBOUNDED FOLLOWING
                            )
                        """

                    select_parts.append(
                        f"{expression} AS {quoted}"
                    )

                else:
                    select_parts.append(quoted)

            select_clause = ", ".join(select_parts)

            con.execute(f"""
                COPY (
                    SELECT {select_clause}
                    FROM (
                        {base_query}
                    )
                )
                TO '{output_path}'
                (FORMAT PARQUET)
            """)

        else:
            raise ValueError(
                f"Unknown missing value method: {method}"
            )

    finally:
        con.close()

    log = (
        f"Applied '{method}' to "
        f"{len(columns)} column(s)."
    )

    return str(output_path), log