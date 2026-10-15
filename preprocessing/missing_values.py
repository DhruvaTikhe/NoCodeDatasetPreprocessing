"""Missing-value preprocessing operations for NoCodePrep."""

import pandas as pd

TITLE = "Missing Values"
COLUMN_TYPE = "all"
METHODS = [
    "Mean",
    "Median",
    "Mode (supports Text)",
    "Constant (supports Text)",
    "Forward Fill (supports Text)",
    "Backward Fill (supports Text)",
    "Drop Rows (supports Text)",
]
SHOW_CONSTANT = True
ALLOW_MULTISELECT = True


def _boolean_constant(value):
    """Convert common textual/numeric boolean tokens to bool."""
    if isinstance(value, bool):
        return value
    if value is None or pd.isna(value):
        raise ValueError("A boolean constant must be true/false, yes/no, or 1/0.")

    normalized = str(value).strip().lower()
    if normalized in {"true", "1", "yes", "y", "on"}:
        return True
    if normalized in {"false", "0", "no", "n", "off"}:
        return False
    raise ValueError(
        f"Cannot interpret {value!r} as a boolean constant. "
        "Use true/false, yes/no, or 1/0."
    )


def process(df: pd.DataFrame, columns, method, constant_value=None):
    """Apply a missing-value method and return (cleaned_df, operation_log)."""
    df = df.copy()
    columns = list(columns or [])
    before = int(df.isna().sum().sum())

    if not columns:
        return df, {
            "Operation": TITLE,
            "Method": method,
            "Changes": 0,
        }

    missing_columns = [column for column in columns if column not in df.columns]
    if missing_columns:
        raise KeyError(f"Selected column(s) not found: {missing_columns}")

    if method == "Mean":
        for col in columns:
            if df[col].isna().all():
                raise ValueError(f"Cannot fill '{col}' with mean: column has no non-null values.")
            if not pd.api.types.is_numeric_dtype(df[col]):
                return "Wrong Datatype"
            mean = df[col].mean()
            if pd.isna(mean):
                raise ValueError(f"Cannot fill '{col}' with mean: column has no non-null values.")
            df[col] = df[col].fillna(mean)

    elif method == "Median":
        for col in columns:
            if not pd.api.types.is_numeric_dtype(df[col]):
                raise TypeError(f"Median imputation requires a numeric column: '{col}'.")
            median = df[col].median()
            if pd.isna(median):
                raise ValueError(f"Cannot fill '{col}' with median: column has no non-null values.")
            df[col] = df[col].fillna(median)

    elif method == "Mode (supports Text)":
        for col in columns:
            modes = df[col].mode(dropna=True)
            if modes.empty:
                raise ValueError(f"Cannot fill '{col}' with mode: column has no non-null values.")
            df[col] = df[col].fillna(modes.iloc[0])

    elif method == "Constant (supports Text)":
        for col in columns:
            value = constant_value
            if pd.api.types.is_bool_dtype(df[col]):
                value = _boolean_constant(value)
            elif pd.api.types.is_integer_dtype(df[col]):
                value = int(pd.to_numeric(value, errors="raise"))
            elif pd.api.types.is_float_dtype(df[col]):
                value = float(pd.to_numeric(value, errors="raise"))
            elif pd.api.types.is_numeric_dtype(df[col]):
                value = pd.to_numeric(value, errors="raise")
            df[col] = df[col].fillna(value)

    elif method == "Forward Fill (supports Text)":
        df[columns] = df[columns].ffill()

    elif method == "Backward Fill (supports Text)":
        df[columns] = df[columns].bfill()

    elif method == "Drop Rows (supports Text)":
        df = df.dropna(subset=columns)

    else:
        raise ValueError(f"Unsupported missing-value method: {method}")

    after = int(df.isna().sum().sum())
    log = {
        "Operation": TITLE,
        "Method": method,
        "Changes": int(before - after),
    }
    return df, log
