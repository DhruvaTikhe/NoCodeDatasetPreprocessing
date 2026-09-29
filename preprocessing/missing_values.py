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
            mean = df[col].mean()
            if type(mean) == type(df[col]):
                df[col] = df[col].fillna(df[col].mean())
            else:
                return "Wrong Datatype"

    elif method == "Median":

        for col in columns:
            df[col] = df[col].fillna(df[col].median())

    elif method == "Mode (supports Text)":

        for col in columns:
            df[col] = df[col].fillna(df[col].mode()[0])

    elif method == "Constant (supports Text)":

        for col in columns:
            value = constant_value

            # Convert constant according to column dtype
            if pd.api.types.is_numeric_dtype(df[col]):
                value = pd.to_numeric(value, errors="raise")

                # Preserve integer dtype where appropriate
                if pd.api.types.is_integer_dtype(df[col]):
                    value = int(value)

                elif pd.api.types.is_float_dtype(df[col]):
                    value = float(value)

            elif pd.api.types.is_bool_dtype(df[col]):
                value = str(value).lower() in ["true", "1", "yes"]

            df[col] = df[col].fillna(value)

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