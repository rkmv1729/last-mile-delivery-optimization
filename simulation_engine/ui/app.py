"""
Streamlit Application
---------------------
Main entry point for the delivery simulation UI.
"""

import streamlit as st

from simulation_engine.engine import SimulationEngine

from simulation_engine.ui.tables import render_tables
from simulation_engine.ui.sidebar import render_sidebar
from simulation_engine.ui.map_view import render_map
from simulation_engine.ui.tabs.operations import render_operations
from simulation_engine.ui.tabs.drivers import render_drivers
from simulation_engine.ui.tabs.zones import render_zones
from simulation_engine.ui.tabs.dispatch import render_dispatch
from simulation_engine.ui.tabs.statistics import render_statistics
from simulation_engine.ui.tabs.events import render_events


# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="Delivery Simulation",
    page_icon="🚚",
    layout="wide",
)

st.title("🚚 Delivery Simulation Dashboard")



# ---------------------------------------------------------
# Session State
# ---------------------------------------------------------

if "placement_mode" not in st.session_state:
    st.session_state.placement_mode = False

if "selected_location" not in st.session_state:
    st.session_state.selected_location = None

if "current_order_items" not in st.session_state:
    st.session_state.current_order_items = []

if "operations_mode" not in st.session_state:
    st.session_state.operations_mode = "new_order"



if "engine" not in st.session_state:
    st.session_state.engine = SimulationEngine()

engine = st.session_state.engine
state = engine.state


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

render_sidebar(engine, state)



# ---------------------------------------------------------
# Simulation Map
# ---------------------------------------------------------

render_map(state)


# ---------------------------------------------------------
# Simulation Workspace
# ---------------------------------------------------------

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
    [
        "Operations",
        "Statistics",
        "Events",
        "Drivers",
        "Zones",
        "Dispatch",
        "🛠 Tables",
    ]
)

with tab1:
    render_operations(engine, state)

with tab2:
    render_statistics(state)

with tab3:
    render_events(state)

with tab4:
    render_drivers(state)

with tab5:
    render_zones(state)

with tab6:
    render_dispatch(state)

with tab7:
    render_tables(state)

