from sklearn.preprocessing import StandardScaler

TITLE = "Normalization"

COLUMN_TYPE = "numeric"

METHODS = [
    "Z-Score Normalization"
]

SHOW_CONSTANT = False
ALLOW_MULTISELECT = True


def process(df, columns, method, **kwargs):

    if not columns:
        return df, "No columns selected for normalization."

    if method == "Z-Score Normalization":
        scaler = StandardScaler()

    else:
        return df, f"Unknown normalization method: {method}"

    # Apply Z-score normalization to selected columns
    df[columns] = scaler.fit_transform(df[columns])

    log = (
        f"{method} applied to {len(columns)} column(s): "
        f"{', '.join(columns)}"
    )

    return df, log