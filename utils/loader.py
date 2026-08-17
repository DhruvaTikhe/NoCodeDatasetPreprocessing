#load dataset
import pandas as pd


SUPPORTED_TYPES = ["csv", "xlsx"]


def load_dataset(uploaded_file):

    if uploaded_file is None:
        return None

    extension = uploaded_file.name.split(".")[-1].lower()

    if extension == "csv":
        return pd.read_csv(uploaded_file)

    if extension == "xlsx":
        return pd.read_excel(uploaded_file)

    raise ValueError(f"Unsupported file type: {extension}")