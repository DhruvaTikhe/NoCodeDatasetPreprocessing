import pandas as pd


TITLE = "Value Counts"

COLUMN_TYPE = "all"

ALLOW_MULTISELECT = True


def analyze(df, columns):
    """
    Calculate value counts for selected columns.

    Does not modify the original DataFrame.
    """

    results = {}

    for column in columns:

        if column not in df.columns:
            continue

        counts = (
            df[column]
            .value_counts(dropna=False)
            .reset_index()
        )

        counts.columns = [
            column,
            "Count"
        ]

        results[column] = counts

    return results