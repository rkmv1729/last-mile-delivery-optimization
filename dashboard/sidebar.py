import streamlit as st

def render_filters(df):
    """
    Render global dashboard filters.
    """

    st.sidebar.markdown("## 🔎 Filters")

    available_dates = sorted(df["date"].unique())

    selected_date = st.sidebar.selectbox(
        "📅 Date",
        available_dates
    )

    shift_options = {
        0: "Morning",
        1: "Afternoon",
        2: "Evening"
    }

    selected_shift = st.sidebar.selectbox(
        "🕒 Shift",
        options=list(shift_options.keys()),
        format_func=lambda x: shift_options[x]
    )

    st.session_state["selected_date"] = selected_date
    st.session_state["selected_shift"] = selected_shift