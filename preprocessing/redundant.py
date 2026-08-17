import pandas as pd

TITLE = "Redundant"

COLUMN_TYPE = "all"      # all, numeric, categorical, datetime

METHODS = [
    "Remove Columns"
]

SHOW_CONSTANT = False
ALLOW_MULTISELECT = True


def process(df: pd.DataFrame, columns, method, **kwargs):

    before = len(df)

    df = df.drop(columns=columns,axis=1)

    removed = before - len(df)

    return df, {
        "Operation": TITLE,
        "Method": method,
        "Changes": removed
    }