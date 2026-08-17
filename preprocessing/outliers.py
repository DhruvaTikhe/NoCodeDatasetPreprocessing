# import pandas as pd
# import numpy as np


# TITLE = "Outliers"

# COLUMN_TYPE = "numeric"

# METHODS = [
#     "Remove Outliers",
#     "Cap Outliers",
# ]

# SHOW_CONSTANT = False
# ALLOW_MULTISELECT = True


# def process(df, columns, method, **kwargs):

#     df = df.copy()

#     if not columns:
#         return df, {
#             "Operation": TITLE,
#             "Method": method,
#             "Changes": 0,
#             "Message": "No columns selected."
#         }

#     detection_method = kwargs.get("detection_method", "IQR")

#     threshold = kwargs.get("threshold", 3.0)

#     total_changes = 0
#     affected_columns = []

#     for column in columns:

#         # Make sure the selected column is numeric
#         if not pd.api.types.is_numeric_dtype(df[column]):
#             continue

#         series = df[column]

#         # Ignore NaN values while calculating boundaries
#         valid_values = series.dropna()

#         if valid_values.empty:
#             continue

#         # ---------------------------------------------------------
#         # IQR OUTLIER DETECTION
#         # ---------------------------------------------------------

#         if detection_method == "IQR":

#             Q1 = valid_values.quantile(0.25)
#             Q3 = valid_values.quantile(0.75)

#             IQR = Q3 - Q1

#             lower_bound = Q1 - 1.5 * IQR
#             upper_bound = Q3 + 1.5 * IQR

#         # ---------------------------------------------------------
#         # Z-SCORE OUTLIER DETECTION
#         # ---------------------------------------------------------

#         elif detection_method == "Z-Score":

#             mean = valid_values.mean()
#             std = valid_values.std()

#             # Avoid division by zero for constant columns
#             if std == 0 or pd.isna(std):
#                 continue

#             z_scores = (series - mean) / std

#             outlier_mask = z_scores.abs() > threshold

#             lower_bound = (
#                 mean - threshold * std
#             )

#             upper_bound = (
#                 mean + threshold * std
#             )

#         else:

#             raise ValueError(
#                 f"Unsupported detection method: {detection_method}"
#             )

#         # ---------------------------------------------------------
#         # CREATE OUTLIER MASK
#         # ---------------------------------------------------------

#         if detection_method == "IQR":

#             outlier_mask = (
#                 (series < lower_bound) |
#                 (series > upper_bound)
#             )

#             outlier_mask = outlier_mask.fillna(False)

#         # ---------------------------------------------------------
#         # HANDLE OUTLIERS
#         # ---------------------------------------------------------

#         outlier_count = int(outlier_mask.sum())

#         if outlier_count == 0:
#             continue

#         affected_columns.append(column)

#         if method == "Remove Outliers":

#             # Mark rows for removal
#             df = df.loc[~outlier_mask].copy()

#             total_changes += outlier_count

#         elif method == "Cap Outliers":

#             original_values = df.loc[
#                 outlier_mask,
#                 column
#             ].copy()

#             df.loc[outlier_mask, column] = (
#                 df.loc[outlier_mask, column]
#                 .clip(
#                     lower=lower_bound,
#                     upper=upper_bound
#                 )
#             )

#             changed_values = (
#                 original_values !=
#                 df.loc[outlier_mask, column]
#             )

#             total_changes += int(
#                 changed_values.sum()
#             )

#         else:

#             raise ValueError(
#                 f"Unsupported handling method: {method}"
#             )

#     # -------------------------------------------------------------
#     # LOG
#     # -------------------------------------------------------------

#     if affected_columns:

#         message = (
#             f"Handled {total_changes} outlier value(s) "
#             f"across {len(affected_columns)} column(s)."
#         )

#     else:

#         message = "No outliers detected."

#     log = {
#         "Operation": TITLE,
#         "Method": method,
#         "Detection": detection_method,
#         "Columns": ", ".join(affected_columns),
#         "Changes": total_changes,
#         "Message": message,
#     }

#     return df, log




#############################################
#############################################
# no detection, directly handling outliers
import pandas as pd


TITLE = "Outliers"

COLUMN_TYPE = "numeric"

METHODS = [
    "IQR",
    "Z-Score",
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

    # Combined mask:
    # True = row contains an outlier in at least one selected column
    outlier_mask = pd.Series(False, index=df.index)

    for column in columns:

        # Safety check
        if not pd.api.types.is_numeric_dtype(df[column]):
            continue

        series = df[column]

        # ---------------------------------------------------------
        # IQR METHOD
        # ---------------------------------------------------------

        if method == "IQR":

            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)

            iqr = q3 - q1

            lower_bound = q1 - (1.5 * iqr)
            upper_bound = q3 + (1.5 * iqr)

            column_outliers = (
                (series < lower_bound) |
                (series > upper_bound)
            )

        # ---------------------------------------------------------
        # Z-SCORE METHOD
        # ---------------------------------------------------------

        elif method == "Z-Score":

            mean = series.mean()
            std = series.std()

            # Constant column → no outliers
            if std == 0 or pd.isna(std):
                continue

            z_score = (series - mean) / std

            column_outliers = z_score.abs() > 3

        else:

            raise ValueError(
                f"Unsupported outlier detection method: {method}"
            )

        # NaN values should NOT be considered outliers
        column_outliers = column_outliers.fillna(False)

        # Combine with previous columns
        outlier_mask = outlier_mask | column_outliers

    # -------------------------------------------------------------
    # REMOVE OUTLIER ROWS
    # -------------------------------------------------------------

    rows_before = len(df)

    df = df.loc[~outlier_mask].copy()

    rows_removed = rows_before - len(df)

    # -------------------------------------------------------------
    # LOG
    # -------------------------------------------------------------

    log = {
        "Operation": TITLE,
        "Method": method,
        "Columns": ", ".join(columns),
        "Changes": rows_removed,
        "Message": (
            f"Removed {rows_removed} row(s) containing outliers."
        )
    }

    return df, log
#############################################
#############################################