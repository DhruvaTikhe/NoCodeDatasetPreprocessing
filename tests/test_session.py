import pandas as pd
import streamlit as st
from utils import session

def test_initialize_session_sets_defaults(monkeypatch):
    state = {}
    monkeypatch.setattr(st, "session_state", state)
    session.initialize_session()
    assert state["df"] is None
    assert state["logs"] == []
    assert state["uploaded_filename"] is None

def test_initialize_session_preserves_existing_values(monkeypatch):
    existing_df = pd.DataFrame({"x": [1]})
    state = {"df": existing_df, "logs": ["existing"], "uploaded_filename": "old.csv"}
    monkeypatch.setattr(st, "session_state", state)
    session.initialize_session()
    assert state["df"] is existing_df
    assert state["logs"] == ["existing"]
    assert state["uploaded_filename"] == "old.csv"

def test_set_dataframe_without_filename(monkeypatch):
    state = {}
    monkeypatch.setattr(st, "session_state", state)
    df = pd.DataFrame({"x": [1]})
    session.set_dataframe(df)
    assert state["df"] is df

def test_set_dataframe_with_filename(monkeypatch):
    state = {}
    monkeypatch.setattr(st, "session_state", state)
    df = pd.DataFrame({"x": [1]})
    session.set_dataframe(df, "sample.csv")
    assert state["df"] is df
    assert state["uploaded_filename"] == "sample.csv"

def test_get_dataframe(monkeypatch):
    df = pd.DataFrame({"x": [1]})
    monkeypatch.setattr(st, "session_state", {"df": df})
    assert session.get_dataframe() is df

def test_has_dataframe(monkeypatch):
    monkeypatch.setattr(st, "session_state", {"df": None})
    assert session.has_dataframe() is False
    monkeypatch.setattr(st, "session_state", {"df": pd.DataFrame({"x": [1]})})
    assert session.has_dataframe() is True
