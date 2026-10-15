"""Remove rows containing numeric outliers using IQR or Z-score detection."""

import pandas as pd

TITLE = "Outliers"
COLUMN_TYPE = "numeric"
METHODS = ["IQR", "Z-Score"]
SHOW_CONSTANT = False
ALLOW_MULTISELECT = True


def process(df, columns, method, **kwargs):
    """Remove rows with outliers in any selected numeric column.

    Current UI contract: method is ``"IQR"`` or ``"Z-Score"``.
    Backward-compatible contract: method may be ``"Remove Outliers"`` with
    ``detection_method="IQR"`` or ``"Z-Score"``.
    """
    df = df.copy()
    columns = list(columns or [])

    if method == "Remove Outliers":
        detection_method = kwargs.get("detection_method", "IQR")
    else:
        detection_method = method

    threshold = float(kwargs.get("threshold", 3.0))
    if threshold <= 0:
        raise ValueError("Z-score threshold must be greater than zero.")

    if not columns:
        return df, {
            "Operation": TITLE,
            "Method": method,
            "Changes": 0,
            "Message": "No columns selected.",
        }

    missing_columns = [col for col in columns if col not in df.columns]
    if missing_columns:
        raise KeyError(f"Selected column(s) not found: {missing_columns}")

    if detection_method not in {"IQR", "Z-Score"}:
        raise ValueError(f"Unsupported outlier detection method: {detection_method}")

    outlier_mask = pd.Series(False, index=df.index)
    affected_columns = []

    for column in columns:
        series = df[column]
        if not pd.api.types.is_numeric_dtype(series):
            continue

        valid = series.dropna()
        if valid.empty:
            continue

        if detection_method == "IQR":
            q1 = valid.quantile(0.25)
            q3 = valid.quantile(0.75)
            iqr = q3 - q1
            # A constant column has IQR 0; values equal to the constant remain.
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            column_mask = (series < lower_bound) | (series > upper_bound)
        else:
            mean = valid.mean()
            std = valid.std()
            if pd.isna(std) or std == 0:
                continue
            column_mask = ((series - mean) / std).abs() > threshold

        column_mask = column_mask.fillna(False)
        if column_mask.any():
            affected_columns.append(column)
            outlier_mask |= column_mask

    rows_removed = int(outlier_mask.sum())
    result = df.loc[~outlier_mask].copy()
    log = {
        "Operation": TITLE,
        "Method": method,
        "Detection": detection_method,
        "Columns": ", ".join(affected_columns),
        "Changes": rows_removed,
        "Message": f"Removed {rows_removed} row(s) containing outliers.",
    }
    return result, log
