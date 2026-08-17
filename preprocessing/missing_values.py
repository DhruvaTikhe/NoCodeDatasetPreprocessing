TITLE = "Missing Values"

COLUMN_TYPE = "all"      # all, numeric, categorical, datetime

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

import pandas as pd
def process(df: pd.DataFrame, columns, method, constant_value=None):

    df = df.copy()

    before = df.isna().sum().sum()

    if method == "Mean":

        for col in columns:
            df[col] = df[col].fillna(df[col].mean())

    elif method == "Median":

        for col in columns:
            df[col] = df[col].fillna(df[col].median())

    elif method == "Mode (supports Text)":

        for col in columns:
            df[col] = df[col].fillna(df[col].mode()[0])

    elif method == "Constant (supports Text)":

        for col in columns:
            df[col] = df[col].fillna(constant_value)

    elif method == "Forward Fill (supports Text)":

        df[columns] = df[columns].ffill()

    elif method == "Backward Fill (supports Text)":

        df[columns] = df[columns].bfill()

    elif method == "Drop Rows (supports Text)":

        df = df.dropna(subset=columns)

    after = df.isna().sum().sum()

    log = {
        "Operation": TITLE,
        "Method": method,
        "Changes": int(before - after)
    }

    return df, log