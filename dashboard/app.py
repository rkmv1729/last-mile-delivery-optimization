import streamlit as st

from config import DASHBOARD_TITLE

from dashboard.loader import (
    load_data,
    load_static_resources
)

from dashboard.views.home import show_home
from dashboard.views.ahsi import show_ahsi
from dashboard.views.demand_forecast import show_demand_forecast
from dashboard.views.dispatch_optimization import show_dispatch_optimization
from dashboard.views.zone_assignment import show_zone_assignment
from datetime import date
from pipeline import main



st.set_page_config(
    page_title=DASHBOARD_TITLE,
    page_icon="🚚",
    layout="wide",
)


data = load_data()
resources = load_static_resources()

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Select Layer",
    (
        "Home",
        "AHSI",
        "Demand Forecast",
        "Dispatch Optimization",
        "Zone Assignment",
    ),
)

st.sidebar.divider()

st.sidebar.subheader("Simulation")

selected_date = st.sidebar.date_input(
    "Date",
    value=date(1900, 5, 1),
    min_value=date(1900, 5, 1),
    max_value=date(1900, 10, 31),
)

selected_shift = st.sidebar.selectbox(
    "Shift",
    [
        "Morning",
        "Afternoon",
        "Evening",
    ],
)

run_clicked = st.sidebar.button(
    "▶ Run Pipeline",
    use_container_width=True,
)

if run_clicked:

    main(
        str(selected_date),
        selected_shift,
        resources
    )

    st.cache_data.clear()

    data = load_data()

    st.success("Pipeline completed successfully.")

    st.rerun()


if page == "Home":
    show_home(data)

elif page == "AHSI":
    show_ahsi(data)

elif page == "Demand Forecast":
    show_demand_forecast(data)

elif page == "Dispatch Optimization":
    show_dispatch_optimization(data)

elif page == "Zone Assignment":
    show_zone_assignment(data)