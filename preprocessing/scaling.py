from sklearn.preprocessing import MinMaxScaler, RobustScaler

TITLE = "Scaling"

COLUMN_TYPE = "numeric"

METHODS = [
    "Min-Max Scaling",
    "Robust Scaling"
]

SHOW_CONSTANT = False
ALLOW_MULTISELECT = True


def process(df, columns, method, **kwargs):

    if not columns:
        return df, "No columns selected for scaling."

    if method == "Min-Max Scaling":
        scaler = MinMaxScaler() #(x-xmin / xmax-xmin)

    elif method == "Robust Scaling":
        scaler = RobustScaler() #(x-median(x) / IQR(x))

    else:
        return df, f"Unknown scaling method: {method}"

    # Fit and transform selected columns
    df[columns] = scaler.fit_transform(df[columns])

    log = f"{method} applied to {len(columns)} column(s): {', '.join(columns)}"

    return df, log
