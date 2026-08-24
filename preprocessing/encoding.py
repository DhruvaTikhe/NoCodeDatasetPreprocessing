import pandas as pd
from sklearn.preprocessing import LabelEncoder


TITLE = "Encoding"

COLUMN_TYPE = "categorical"

METHODS = [
    "One-Hot Encoding",
    "Label Encoding",
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

    # Make sure selected columns actually exist
    columns = [
        column for column in columns
        if column in df.columns
    ]

    if not columns:
        return df, {
            "Operation": TITLE,
            "Method": method,
            "Changes": 0,
            "Message": "Selected columns were not found."
        }

    # =============================================================
    # ONE-HOT ENCODING
    # =============================================================

    if method == "One-Hot Encoding":

        original_columns = columns.copy()

        encoded_df = pd.get_dummies(
            df[columns],
            prefix=columns,
            dtype=int
        )

        # Remove original categorical columns
        df = df.drop(columns=columns)

        # Add encoded columns
        df = pd.concat(
            [df, encoded_df],
            axis=1
        )

        new_columns = list(encoded_df.columns)

        log = {
            "Operation": TITLE,
            "Method": method,
            "Columns": ", ".join(original_columns),
            "Changes": len(new_columns),
            "Message": (
                f"Encoded {len(original_columns)} column(s) "
                f"into {len(new_columns)} column(s)."
            )
        }

        return df, log

    # =============================================================
    # LABEL ENCODING
    # =============================================================

    elif method == "Label Encoding":

        encoded_columns = []

        for column in columns:

            # Preserve missing values
            mask = df[column].notna()

            encoder = LabelEncoder()

            # Convert values to strings so mixed categorical
            # values don't cause comparison errors
            values = df.loc[mask, column].astype(str)

            df.loc[mask, column] = encoder.fit_transform(values)

            # Convert encoded column to integer
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            ).astype("Int64")

            encoded_columns.append(column)

        log = {
            "Operation": TITLE,
            "Method": method,
            "Columns": ", ".join(encoded_columns),
            "Changes": len(encoded_columns),
            "Message": (
                f"Label encoded {len(encoded_columns)} column(s)."
            )
        }

        return df, log

    # =============================================================
    # INVALID METHOD
    # =============================================================

    else:

        raise ValueError(
            f"Unsupported encoding method: {method}"
        )
