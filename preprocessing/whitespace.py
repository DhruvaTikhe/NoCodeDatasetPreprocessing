import pandas as pd


TITLE = "Whitespace"

COLUMN_TYPE = "categorical"

METHODS = [
    "Trim Leading & Trailing",
    "Remove Extra Spaces",
    "Remove All Spaces",
]

SHOW_CONSTANT = False
ALLOW_MULTISELECT = True


def process(df, columns, method, **kwargs):

    df = df.copy()

    if not columns:
        return df, {
            "Operation": TITLE,
            "Method": method,
            "Changes": 0,
            "Message": "No columns selected."
        }

    changes = 0

    for column in columns:

        # Work only with non-null values
        mask = df[column].notna()

        original = df.loc[mask, column].astype(str)

        if method == "Trim Leading & Trailing":

            cleaned = original.str.strip()

        elif method == "Remove Extra Spaces":

            # Strip outer whitespace and collapse
            # multiple internal spaces into one
            cleaned = (
                original
                .str.strip()
                .str.replace(r"\s+", " ", regex=True)
            )

        elif method == "Remove All Spaces":

            cleaned = (
                original
                .str.replace(r"\s+", "", regex=True)
            )

        else:

            raise ValueError(
                f"Unsupported whitespace method: {method}"
            )

        # Count actual changes
        changes += int(
            (original != cleaned).sum()
        )

        df.loc[mask, column] = cleaned

    log = {
        "Operation": TITLE,
        "Method": method,
        "Columns": ", ".join(columns),
        "Changes": changes,
        "Message": (
            f"Cleaned whitespace in {changes} value(s)."
        )
    }

    return df, log