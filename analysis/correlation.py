# analysis/correlation.py

import pandas as pd


TITLE = "High Correlation"

METHODS = [
    "Pearson",
    "Spearman",
    "Kendall",
]

DEFAULT_THRESHOLD = 0.80


def analyze(df, method="Pearson", threshold=DEFAULT_THRESHOLD):
    """
    Analyze correlations between numerical columns.

    The original DataFrame is not modified.

    Returns:
        correlation_matrix
        highly_correlated
        log
    """

    # ---------------------------------------------------------
    # Select numerical columns only
    # ---------------------------------------------------------

    numeric_df = df.select_dtypes(include="number")

    if numeric_df.shape[1] < 2:

        log = {
            "Operation": TITLE,
            "Method": method,
            "Changes": 0,
            "Message": (
                "At least two numerical columns "
                "are required for correlation analysis."
            )
        }

        return (
            pd.DataFrame(),
            pd.DataFrame(),
            log
        )

    # ---------------------------------------------------------
    # Calculate correlation matrix
    # ---------------------------------------------------------

    correlation_matrix = numeric_df.corr(
        method=method.lower()
    )

    # ---------------------------------------------------------
    # Find highly correlated feature pairs
    # ---------------------------------------------------------

    highly_correlated = []

    columns = correlation_matrix.columns

    for i in range(len(columns)):

        for j in range(i + 1, len(columns)):

            feature_1 = columns[i]
            feature_2 = columns[j]

            correlation = correlation_matrix.loc[
                feature_1,
                feature_2
            ]

            if (
                pd.notna(correlation)
                and abs(correlation) >= threshold
            ):

                highly_correlated.append({
                    "Feature 1": feature_1,
                    "Feature 2": feature_2,
                    "Correlation": round(
                        correlation,
                        4
                    )
                })

    highly_correlated_df = pd.DataFrame(
        highly_correlated
    )

    # ---------------------------------------------------------
    # Create log
    # ---------------------------------------------------------

    log = {
        "Operation": TITLE,
        "Method": method,
        "Columns": ", ".join(numeric_df.columns),
        "Changes": 0,
        "Message": (
            f"Found {len(highly_correlated_df)} "
            f"highly correlated feature pair(s)."
        )
    }

    return (
        correlation_matrix,
        highly_correlated_df,
        log
    )



#OLD CODE


# import pandas as pd


# TITLE = "High Correlation"

# COLUMN_TYPE = "numeric"

# METHODS = [
#     "Pearson",
#     "Spearman",
#     "Kendall",
# ]

# THRESHOLD = 0.8


# def analyze(df, method="Pearson", threshold=THRESHOLD):
#     """
#     Analyze correlations between numerical columns.

#     This function does NOT modify the DataFrame.

#     Returns:
#         correlation_matrix
#         highly_correlated
#         log
#     """

#     # ---------------------------------------------------------
#     # Select numerical columns only
#     # ---------------------------------------------------------

#     numeric_df = df.select_dtypes(include="number")

#     if numeric_df.shape[1] < 2:

#         return (
#             pd.DataFrame(),
#             pd.DataFrame(),
#             {
#                 "Operation": TITLE,
#                 "Method": method,
#                 "Changes": 0,
#                 "Message": (
#                     "At least two numerical columns "
#                     "are required for correlation analysis."
#                 )
#             }
#         )

#     # ---------------------------------------------------------
#     # Calculate correlation
#     # ---------------------------------------------------------

#     correlation_matrix = numeric_df.corr(
#         method=method.lower()
#     )

#     # ---------------------------------------------------------
#     # Find highly correlated feature pairs
#     # ---------------------------------------------------------

#     highly_correlated = []

#     columns = correlation_matrix.columns

#     for i in range(len(columns)):

#         for j in range(i + 1, len(columns)):

#             feature_1 = columns[i]
#             feature_2 = columns[j]

#             correlation = correlation_matrix.loc[
#                 feature_1,
#                 feature_2
#             ]

#             if (
#                 pd.notna(correlation)
#                 and abs(correlation) >= threshold
#             ):

#                 highly_correlated.append({
#                     "Feature 1": feature_1,
#                     "Feature 2": feature_2,
#                     "Correlation": round(
#                         correlation,
#                         4
#                     )
#                 })

#     highly_correlated_df = pd.DataFrame(
#         highly_correlated
#     )

#     # ---------------------------------------------------------
#     # Log
#     # ---------------------------------------------------------

#     log = {
#         "Operation": TITLE,
#         "Method": method,
#         "Columns": ", ".join(numeric_df.columns),
#         "Changes": 0,
#         "Message": (
#             f"Found {len(highly_correlated_df)} "
#             f"highly correlated feature pair(s)."
#         )
#     }

#     return (
#         correlation_matrix,
#         highly_correlated_df,
#         log
#     )