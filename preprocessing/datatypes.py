import pandas as pd

TITLE = "Incorrect Data Types"

COLUMN_TYPE = "all"

METHODS = [
    "Integer",
    "Float",
    "String",
    "Boolean",
    "Datetime",
    "Category",
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

    before_types = df[columns].dtypes.astype(str).to_dict()

    changes = 0
    errors = []

    for column in columns:

        try:

            if method == "Integer":

                converted = pd.to_numeric(
                    df[column],
                    errors="coerce"
                )

                converted = converted.astype("Int64")

            elif method == "Float":

                converted = pd.to_numeric(
                    df[column],
                    errors="coerce"
                )

                converted = converted.astype(float)

            elif method == "String":

                converted = df[column].astype("string")

            elif method == "Boolean":

                converted = convert_to_boolean(df[column])

            elif method == "Datetime":

                converted = pd.to_datetime(
                    df[column],
                    errors="coerce"
                )

            elif method == "Category":

                converted = df[column].astype("category")

            else:

                raise ValueError(
                    f"Unsupported conversion method: {method}"
                )

            # Count cells whose values actually changed
            changes += int(
                (df[column].astype("string") !=
                 converted.astype("string"))
                .fillna(False)
                .sum()
            )

            df[column] = converted

        except Exception as e:

            errors.append(
                f"{column}: {str(e)}"
            )

    after_types = df[columns].dtypes.astype(str).to_dict()

    log = {
        "Operation": TITLE,
        "Method": method,
        "Columns": ", ".join(columns),
        "Changes": changes,
        "Message": (
            f"Converted {len(columns)} column(s)"
            if not errors
            else f"Converted with {len(errors)} error(s)"
        )
    }

    if errors:
        log["Errors"] = " | ".join(errors)

    log["Before Types"] = str(before_types)
    log["After Types"] = str(after_types)

    return df, log


def convert_to_boolean(series):

    """
    Convert common textual/numeric representations to boolean.

    Examples:
        True / False
        "true" / "false"
        "yes" / "no"
        "1" / "0"
    """

    mapping = {
        "true": True,
        "false": False,
        "yes": True,
        "no": False,
        "y": True,
        "n": False,
        "0": True,
        "1": False,
    }

    normalized = (
        series
        .astype("string")
        .str.strip()
        .str.lower()
    )

    return normalized.map(mapping).astype("boolean")