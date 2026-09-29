# DuckDB dataset path
#         ↓
# DuckDB transformation
#         ↓
# Parquet output
#         ↓
# st.session_state.dataset_path
#         ↓
# next module operates on that Parquet


# EXAMPLE:
# flight.csv
#    ↓
# trim whitespace
#    ↓
# flight_trimmed.parquet
#    ↓
# casing
#    ↓
# flight_trimmed_casing.parquet


import duckdb
import os
import uuid


# -------------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------------

def quote_identifier(name):
    """Safely quote a DuckDB column name."""
    return '"' + str(name).replace('"', '""') + '"'


def get_reader(path):
    """Return the appropriate DuckDB reader for the dataset."""

    path = path.replace("'", "''")

    if path.lower().endswith(".parquet"):
        return f"read_parquet('{path}')"

    return f"read_csv_auto('{path}')"


def output_path(input_path, operation):

    directory = os.path.dirname(input_path)
    filename = os.path.splitext(
        os.path.basename(input_path)
    )[0]

    unique_id = uuid.uuid4().hex[:8]

    return os.path.join(
        directory,
        f"{filename}_{operation}_{unique_id}.parquet"
    )


def execute_to_parquet(con, query, output_path):
    """Execute a transformation and write the result to Parquet."""

    output_path_sql = output_path.replace("'", "''")

    con.execute(f"""
        COPY (
            {query}
        )
        TO '{output_path_sql}'
        (FORMAT PARQUET)
    """)

    return output_path