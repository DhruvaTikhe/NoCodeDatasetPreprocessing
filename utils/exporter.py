#export to_csv() to_excel()

from io import BytesIO
import pandas as pd

def to_csv_bytes(df: pd.DataFrame) -> bytes:

    return df.to_csv(index=False).encode("utf-8")


def to_excel_bytes(df: pd.DataFrame) -> bytes:
    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Cleaned Dataset")

    output.seek(0)
    return output.getvalue()


def generate_filename(original_filename: str, extension: str) -> str:
    if "." in original_filename:
        original_filename = original_filename.rsplit(".", 1)[0]

    return f"{original_filename}_cleaned.{extension}"