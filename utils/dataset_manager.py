
def get_engine(file_size):

    if file_size <= 500 * 1024 * 1024:
        return "pandas"

    return "duckdb"