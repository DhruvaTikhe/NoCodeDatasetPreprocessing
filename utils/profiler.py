#dataset summary
import pandas as pd


def dataset_summary(df: pd.DataFrame):

    memory = df.memory_usage(deep=True).sum() / 1024

    return {
        "Rows": len(df),
        "Columns": len(df.columns),
        "Missing Values": int(df.isna().sum().sum()),
        "Duplicate Rows": int(df.duplicated().sum()),
        # "Memory Usage": f"{memory:.2f} KB"
    }

