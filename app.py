import streamlit as st
from preprocessing.registry import MODULES
from analysis.registry import MODULES as ANALYSIS_MODULES
from utils.loader import *
from utils.session import *
from utils.profiler import *
from utils.exporter import *
import matplotlib.pyplot as plt
import seaborn as sns
# -----------------------------------------------------------------------------
# Page Configuration
# -----------------------------------------------------------------------------

st.set_page_config(
    page_title="NoCodePrep",
    page_icon="🧹",
    layout='wide'
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

left_col, right_col = st.columns([6, 4], gap='medium')

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

    #UNCOMMENT FOR DATASET PREVIEW ORIGINAL
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
                # st.markdown(module.METHODS) #debug
                # st.markdown(columns) #debug

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

    # st.write("")

    # with st.container(border=True):
    #     st.write("AI Summary")

    # st.write("")

    # -------------------------------------------------------------------------
    # Dataset Summary
    # -------------------------------------------------------------------------

    # with st.expander("📋 Dataset Summary", expanded=True):
    #     # st.subheader("📊 Dataset Summary")
    #     if has_dataframe():
    #         summary = dataset_summary(get_dataframe())
    #         st.dataframe(
    #             summary,
    #             width='stretch',

    #             hide_index=False
    #         )
    #     else:
    #         st.info("No dataset uploaded")
    # st.write("")

# -------------------------------------------------------------------------
# Analysis
# -------------------------------------------------------------------------

    with st.expander("📊 Analysis", expanded=False):

        if has_dataframe():

            df = get_dataframe()

            for module in ANALYSIS_MODULES:

                st.markdown(f"### {module.TITLE}")

                # -------------------------------------------------------------
                # Select columns
                # -------------------------------------------------------------

                columns = df.columns.tolist()

                if module.COLUMN_TYPE == "numeric":

                    columns = (
                        df.select_dtypes(include="number")
                        .columns
                        .tolist()
                    )

                elif module.COLUMN_TYPE == "categorical":

                    columns = (
                        df.select_dtypes(exclude="number")
                        .columns
                        .tolist()
                    )

                # -------------------------------------------------------------
                # DESCRIPTION
                # -------------------------------------------------------------

                if module.TITLE == "Describe":

                    selected_columns = st.multiselect(
                        "Columns",
                        columns,
                        key=f"{module.TITLE}_columns"
                    )

                    if st.button(
                        "Analyze",
                        key=f"{module.TITLE}_analyze"
                    ):

                        result = module.analyze(
                            df,
                            selected_columns
                        )

                        st.session_state.describe_result = result

                        st.rerun()

                    if "describe_result" in st.session_state:

                        st.dataframe(
                            st.session_state.describe_result,
                            width="stretch"
                        )

                # -------------------------------------------------------------
                # VALUE COUNTS
                # -------------------------------------------------------------

                elif module.TITLE == "Value Counts":

                    selected_columns = st.multiselect(
                        "Columns",
                        columns,
                        key=f"{module.TITLE}_columns"
                    )

                    if st.button(
                        "Analyze",
                        key=f"{module.TITLE}_analyze"
                    ):

                        result = module.analyze(
                            df,
                            selected_columns
                        )

                        st.session_state.value_counts_result = result

                        st.rerun()

                    if "value_counts_result" in st.session_state:

                        results = (
                            st.session_state.value_counts_result
                        )

                        for column, counts in results.items():

                            st.markdown(
                                f"**{column}**"
                            )

                            st.dataframe(
                                counts,
                                width="stretch",
                                hide_index=True
                            )

                # -------------------------------------------------------------
                # CORRELATION
                # -------------------------------------------------------------

                elif module.TITLE == "High Correlation":

                    method = st.selectbox(
                        "Technique",
                        module.METHODS,
                        key=f"{module.TITLE}_analysis_method"
                    )

                    threshold = st.slider(
                        "Correlation Threshold",
                        min_value=0.50,
                        max_value=1.00,
                        value=0.80,
                        step=0.05,
                        key=f"{module.TITLE}_threshold"
                    )

                    if st.button(
                        "Analyze",
                        key=f"{module.TITLE}_analyze"
                    ):

                        matrix, highly_correlated, log = module.analyze(
                            df,
                            method=method,
                            threshold=threshold
                        )

                        st.session_state.correlation_matrix = matrix

                        st.session_state.highly_correlated = (
                            highly_correlated
                        )

                        st.session_state.correlation_method = method

                        st.session_state.logs.append(log)

                        st.rerun()

                    # ---------------------------------------------------------
                    # Display correlation results
                    # ---------------------------------------------------------

                    if "correlation_matrix" in st.session_state:

                        matrix = (
                            st.session_state.correlation_matrix
                        )

                        if not matrix.empty:

                            st.subheader(
                                f"{st.session_state.correlation_method} "
                                "Correlation Heatmap"
                            )

                            fig, ax = plt.subplots(
                                figsize=(10, 7)
                            )

                            sns.heatmap(
                                matrix,
                                annot=True,
                                fmt=".2f",
                                center=0,
                                vmin=-1,
                                vmax=1,
                                ax=ax
                            )

                            ax.set_title(
                                f"{st.session_state.correlation_method} "
                                "Correlation Matrix"
                            )

                            st.pyplot(
                                fig,
                                width="stretch"
                            )

                            plt.close(fig)

                            st.subheader(
                                "Highly Correlated Features"
                            )

                            highly_correlated = (
                                st.session_state.highly_correlated
                            )

                            if highly_correlated.empty:

                                st.info(
                                    "No highly correlated feature pairs found."
                                )

                            else:

                                st.dataframe(
                                    highly_correlated,
                                    width="stretch",
                                    hide_index=True
                                )

                        else:

                            st.warning(
                                "At least two numerical columns are "
                                "required for correlation analysis."
                            )

        else:

            st.info(
                "Upload a dataset to use analysis tools."
            )

    # -------------------------------------------------------------------------
    # Logs & History
    # -------------------------------------------------------------------------

    # with st.container(border=True):

    #     st.subheader("📝 Logs & History")

    #     st.info("THIS IS PLACEHOLDER")

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

    col1, col2, col3= st.columns([1,1,8])

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
