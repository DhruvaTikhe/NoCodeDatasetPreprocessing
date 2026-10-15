TITLE = "Casing"

COLUMN_TYPE = "categorical"      # all, numeric, categorical, datetime

METHODS = [
    "Lowercase",
    "Uppercase",
    "Title Case",
    "Capitalize",
]

SHOW_CONSTANT = False
ALLOW_MULTISELECT = True

import pandas as pd


def process(df: pd.DataFrame, columns, method, **kwargs):

    before = len(df)

    if method == "Lowercase":
        for col in columns:
            df[col] = df[col].apply(
                lambda x: x.lower() if isinstance(x, str) else x
            )

    elif method == "Uppercase":
        for col in columns:
            df[col] = df[col].apply(
                lambda x: x.upper() if isinstance(x, str) else x
            )

    elif method == "Title Case":
        for col in columns:
            df[col] = df[col].apply(
                lambda x: x.title() if isinstance(x, str) else x
            )

    elif method == "Capitalize":
        for col in columns:
            df[col] = df[col].apply(
                lambda x: x.capitalize() if isinstance(x, str) else x
            )

    removed = before - len(df)

    return df, {
        "Operation": TITLE,
        "Method": method,
        "Changes": removed
    }