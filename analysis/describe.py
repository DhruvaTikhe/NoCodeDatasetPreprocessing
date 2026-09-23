import pandas as pd


TITLE = "Describe"

COLUMN_TYPE = "all"

ALLOW_MULTISELECT = True


def analyze(df, columns):
    """
    Generate descriptive statistics for selected columns.

    Does not modify the original DataFrame.
    """

    if not columns:
        columns = df.columns.tolist()

    selected_df = df[columns]

    description = selected_df.describe(
        include="all"
    ).transpose()

    return description