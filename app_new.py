import streamlit as st

from preprocessing.registry import MODULES as MODULES
from analysis.registry import ANALYSIS_MODULES as ANALYSIS_MODULES

from utils.loader import *
from utils import loader 
from utils.session import *
from utils.profiler import *
from utils.exporter import *
import matplotlib.pyplot as plt
import seaborn as sns

#scalability imports
from utils import scalable_loader
from utils import dataset_manager
import os
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
    st.subheader("🧹 No-Code Preprocessor")
    st.caption("No-Code Dataset Cleaning and Preprocessing")

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
    # Dataset Path
    # -------------------------------------------------------------------------

    st.subheader("📂 Dataset Path")


    dataset_path = st.text_input(
        "Enter the path to your dataset without quotes",
        placeholder=r"only csv file accepted"
    )

    if dataset_path:
        st.write("Path entered:", dataset_path)
        st.write("Exists:", os.path.exists(dataset_path))
        st.write("Is file:", os.path.isfile(dataset_path))

    if st.button("Load Dataset"):

        if not dataset_path:
            st.warning("Please enter a dataset path.")

        elif not os.path.isfile(dataset_path):
            st.error("The specified file does not exist.")

        else:

            engine = dataset_manager.get_engine(
                os.path.getsize(dataset_path)
            )

            if engine == "pandas":

                df = loader.load_dataset(dataset_path)

                st.session_state.df = df
                st.session_state.dataset_engine = "pandas"
                st.session_state.dataset_path = dataset_path

            else:

                st.session_state.df = None
                st.session_state.dataset_engine = "duckdb"
                st.session_state.dataset_path = dataset_path

            st.success(f"Loaded: {os.path.basename(dataset_path)}")

    st.divider()

    # -------------------------------------------------------------------------
    # Dataset Preview
    # -------------------------------------------------------------------------

    with st.expander("📋 Dataset Preview", expanded=True):

        if has_dataframe():

            # Pandas dataset
            preview_df = get_dataframe().head(10)

            st.dataframe(
                preview_df,
                width="stretch",
                hide_index=True
            )

        elif st.session_state.get("dataset_engine") == "duckdb":

            # DuckDB dataset
            con = scalable_loader.connect()

            try:
                preview_df = scalable_loader.preview(
                    con,
                    st.session_state.dataset_path,
                    10
                )

                st.dataframe(
                    preview_df,
                    width="stretch",
                    hide_index=True
                )
            except:
                st.info("Failed to Preview. Please Retry.")

            finally:
                con.close()

        else:
            st.info("No dataset loaded. Enter a dataset path above.")

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

         
    # # -------------------------------------------------------------------------
    # # Dataset Information
    # # -------------------------------------------------------------------------
    # with st.expander("📋 Dataset Information", expanded=True):
    #     # with st.container(border=True):
    #     # st.subheader("📋 Dataset Information")

    #     if has_dataframe():

    #         df = get_dataframe()

    #         info_data = pd.DataFrame({
    #             "Column": df.columns,
    #             "Non-Null Count": df.notna().sum().values,
    #             "Null Count": df.isna().sum().values,
    #             "Dtype": df.dtypes.astype(str).values
    #         })

    #         # st.table(info_data)
    #         st.dataframe(
    #             info_data,
    #             width='stretch',
    #             hide_index=True
    #         )

    #         st.caption(
    #             f"{df.shape[0]:,} rows x {df.shape[1]:,} columns\n\n{dataset_summary(get_dataframe())['Missing Values']} Missing Values & {dataset_summary(get_dataframe())['Duplicate Rows']} Duplicate Rows"
    #         )

    #     elif st.session_state.get("dataset_engine") == "duckdb":

    #         con = scalable_loader.connect()

    #         try:

    #             info_data, row_count = scalable_loader.dataset_info(
    #                 con,
    #                 st.session_state.dataset_path
    #             )

    #             st.dataframe(
    #                 info_data,
    #                 width="stretch",
    #                 hide_index=True
    #             )

    #             column_count = len(info_data)
    #             missing_count = info_data["Null Count"].sum()

    #             duplicate_count = scalable_loader.duplicate_count(
    #                 con,
    #                 st.session_state.dataset_path,
    #                 info_data["Column"].tolist()
    #             )

    #             st.caption(
    #                 f"{row_count:,} rows x {column_count:,} columns\n\n"
    #                 f"{missing_count:,} Missing Values & "
    #                 f"{duplicate_count:,} Duplicate Rows"
    #             )

    #         finally:
    #             con.close()
    #     else:

    #         st.info("No dataset uploaded")


    # -------------------------------------------------------------------------
    # Dataset Information
    # -------------------------------------------------------------------------

    with st.expander("📋 Dataset Information", expanded=True):

        if has_dataframe():

            df = get_dataframe()

            info_data = pd.DataFrame({
                "Column": df.columns,
                "Non-Null Count": df.notna().sum().values,
                "Null Count": df.isna().sum().values,
                "Dtype": df.dtypes.astype(str).values
            })

            st.dataframe(
                info_data,
                width="stretch",
                hide_index=True
            )

            row_count = len(df)
            column_count = len(df.columns)
            missing_count = int(df.isna().sum().sum())
            duplicate_count = int(df.duplicated().sum())

            st.caption(
                f"{row_count:,} rows x {column_count:,} columns\n\n"
                f"{missing_count:,} Missing Values & "
                f"{duplicate_count:,} Duplicate Rows"
            )

        elif st.session_state.get("dataset_engine") == "duckdb":

            con = scalable_loader.connect()

            progress_bar = st.progress(
                0,
                text="Preparing dataset information..."
            )

            try:

                def update_progress(value, text):
                    progress_bar.progress(
                        value,
                        text=text
                    )

                # ---------------------------------------------------------
                # Calculate information
                # ---------------------------------------------------------

                info_data, row_count, missing_count = (
                    scalable_loader.dataset_info(
                        con,
                        st.session_state.dataset_path,
                        progress_callback=update_progress
                    )
                )

                # ---------------------------------------------------------
                # Render table
                # ---------------------------------------------------------

                update_progress(
                    0.90,
                    "Preparing dataset information table..."
                )

                st.dataframe(
                    info_data,
                    width="stretch",
                    hide_index=True
                )

                # ---------------------------------------------------------
                # Calculate duplicate rows
                # ---------------------------------------------------------

                update_progress(
                    0.92,
                    "Calculating duplicate rows..."
                )

                duplicate_count = scalable_loader.duplicate_count(
                    con,
                    st.session_state.dataset_path,
                    info_data["Column"].tolist()
                )

                # ---------------------------------------------------------
                # Final captions
                # ---------------------------------------------------------

                update_progress(
                    1.0,
                    "Dataset information ready."
                )

                column_count = len(info_data)

                st.caption(
                    f"{row_count:,} rows x "
                    f"{column_count:,} columns\n\n"
                    f"{missing_count:,} Missing Values & "
                    f"{duplicate_count:,} Duplicate Rows"
                )

            finally:
                con.close()

        else:

            st.info("No dataset loaded.")
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
