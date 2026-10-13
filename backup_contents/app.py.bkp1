import streamlit as st
from preprocessing.registry import MODULES
from utils.loader import *
from utils.session import *
from utils.profiler import *
from utils.exporter import *
# -----------------------------------------------------------------------------
# Page Configuration
# -----------------------------------------------------------------------------

st.set_page_config(
    page_title="NoCodePrep",
    page_icon="🧹",
    layout="wide"
)
initialize_session()
# -----------------------------------------------------------------------------
# Header
# -----------------------------------------------------------------------------

header_left, header_right = st.columns([8, 2])

with header_left:
    st.title("🧹 No-Code Preprocessor")
    st.subheader("No-Code Dataset Cleaning and Preprocessing")

with header_right:
    st.success("🟢 Ready")

st.divider()

# -----------------------------------------------------------------------------
# Main Layout
# -----------------------------------------------------------------------------

left_col, right_col = st.columns([7, 3], gap="large")

# =============================================================================
# LEFT PANEL
# =============================================================================

with left_col:

    # -------------------------------------------------------------------------
    # Upload Dataset
    # -------------------------------------------------------------------------

    st.subheader("📂 Upload Dataset")

    uploaded_file = st.file_uploader(
    "Choose a CSV or Excel file",
    type=["csv", "xlsx"]
    )

    if uploaded_file is not None:

    # Load only if this is a new upload
        if (
            st.session_state.df is None
            or st.session_state.uploaded_filename != uploaded_file.name
        ):
            df = load_dataset(uploaded_file)
            set_dataframe(df, uploaded_file.name)

        st.success(f"Loaded {uploaded_file.name}")
    st.divider()

    # -------------------------------------------------------------------------
    # Dataset Preview
    # -------------------------------------------------------------------------

    with st.expander("📋 Dataset Preview", expanded=True):
        if has_dataframe():
            st.dataframe(
                get_dataframe().head(10),
                width='stretch',
                hide_index=True
            )
        else:
            st.info("Upload a dataset to preview it.")

    st.divider()

    # -------------------------------------------------------------------------
    # Preprocessing Modules
    # -------------------------------------------------------------------------

    modules = [
        "Missing Values",
        "Duplicates",
        # "Incorrect Data Types",
        # "Inconsistent Entries",
        # "Outliers",
        # "Invalid Data",
        # "High Correlation",
        # "Redundant Columns",
        # "Class Imbalance",
        # "Mixed Formatting",
        # "Case & Spacing",
        # "Encoding",
        # "Scaling",
        # "Normalization",
        # "Feature Selection"
    ]
    
    if has_dataframe():
        df = get_dataframe()

        for module in MODULES:
            with st.expander(module.TITLE):
                columns = df.columns.tolist()
                if module.COLUMN_TYPE == "numeric":
                    columns = df.select_dtypes(include="number").columns.tolist()

                elif module.COLUMN_TYPE == "categorical":
                    columns = df.select_dtypes(exclude="number").columns.tolist()

                else:
                    columns = df.columns.tolist()
                # st.markdown(module.METHODS)
                # st.markdown(columns)

                if module.ALLOW_MULTISELECT:
                    selected_columns = st.multiselect(
                        "Columns",
                        columns,
                        key=f"{module.TITLE}_columns"
                    )

                method = st.selectbox(
                    "Methods",
                    module.METHODS,
                    key=f"{module.TITLE}_methods"
                )

                constant = None
                if module.SHOW_CONSTANT:
                    constant = st.text_input(
                        "Constant Value",
                        key=f"{module.TITLE}_constant"
                    )

                if st.button("Apply", key=f"{module.TITLE}_apply"):

                    new_df, log = module.process(
                        get_dataframe(),
                        selected_columns,
                        method,
                        constant_value=constant,
                    )

                    set_dataframe(new_df)

                    st.session_state.logs.append(log)

                    st.rerun()
# =============================================================================
# RIGHT PANEL
# =============================================================================

with right_col:

    # -------------------------------------------------------------------------
    # AI Summary
    # -------------------------------------------------------------------------

    st.write("")

    with st.container(border=True):
        st.write("AI Summary")

    st.write("")

    # -------------------------------------------------------------------------
    # Dataset Summary
    # -------------------------------------------------------------------------

    with st.container(border=True):

        st.subheader("📊 Dataset Summary")
        if has_dataframe():
            summary = dataset_summary(get_dataframe())
            st.table(summary)
        else:
            st.info("No dataset uploaded")
    st.write("")

    # -------------------------------------------------------------------------
    # Logs & History
    # -------------------------------------------------------------------------

    with st.container(border=True):

        st.subheader("📝 Logs & History")

        st.info("THIS IS PLACEHOLDER")

# -----------------------------------------------------------------------------
# Footer
# -----------------------------------------------------------------------------

st.divider()


if has_dataframe():

    # df = get_dataframe() #OLD
    df = st.session_state.df
    st.write(get_dataframe().head(10))
    csv_bytes = to_csv_bytes(df)
    excel_bytes = to_excel_bytes(df)

    filename = st.session_state.uploaded_filename

    col1, col2, col3= st.columns([2,2,6])

    with col1:
        st.download_button(
            label="💾 Save CSV",
            data=csv_bytes,
            file_name=generate_filename(filename, "csv"),
            mime="text/csv",
            width='stretch',
        )

    with col2:
        st.download_button(
            label="📄 Save XLSX",
            data=excel_bytes,
            file_name=generate_filename(filename, "xlsx"),
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width='stretch',
        )
    with col3:
        st.progress(0)
