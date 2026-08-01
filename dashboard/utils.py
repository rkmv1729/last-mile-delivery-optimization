import streamlit as st


def get_filtered_df(df):

    return df[
        (df["date"] == st.session_state["selected_date"]) &
        (df["shift_id"] == st.session_state["selected_shift"])
    ].copy()