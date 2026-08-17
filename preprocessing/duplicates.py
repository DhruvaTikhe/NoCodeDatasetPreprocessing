TITLE = "Duplicates"

COLUMN_TYPE = "all"      # all, numeric, categorical, datetime

METHODS = [
    "Drop Duplicates"
]

SHOW_CONSTANT = False
ALLOW_MULTISELECT = False

import pandas as pd

def process(df: pd.DataFrame, columns, method, **kwargs):

    before = len(df)

    df = df.drop_duplicates()

    removed = before - len(df)

    return df, {
        "Operation": TITLE,
        "Method": method,
        "Changes": removed
    }