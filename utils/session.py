#maintain session to ensure only 1 dataframe is present in the memory
import streamlit as st


def initialize_session():

    defaults = {
        "df": None,
        "logs": [],
        "uploaded_filename": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def set_dataframe(df, filename=None):
    st.session_state.df = df

    if filename is not None:
        st.session_state.uploaded_filename = filename

#OLD
# def set_dataframe(df, filename):
#     st.session_state.df = df
#     st.session_state.uploaded_filename = filename


def get_dataframe():
    return st.session_state.df


def has_dataframe():
    return st.session_state.df is not None