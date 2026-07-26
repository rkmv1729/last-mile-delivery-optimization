"""
Tables
------
Display simulation entities in tabular format.
"""

import pandas as pd
import streamlit as st
from simulation_engine.state import SimulationState


def render_tables(
    state: SimulationState
):
    """
    Render simulation data tables.
    """

    st.subheader("Simulation Data")

    tabs = st.tabs([
        "Orders",
        "Drivers",
        "Batches",
        "Zones",
        "Dispatch Centres",
    ])

    # ---------------------------------------------------------
    # Orders
    # ---------------------------------------------------------

    with tabs[0]:
        if state.orders:
            df = pd.DataFrame(
                [order.to_display_dict() for order in state.orders.values()]
            )
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No orders available.")

    # ---------------------------------------------------------
    # Drivers
    # ---------------------------------------------------------

    with tabs[1]:
        if state.drivers:
            df = pd.DataFrame(
                [driver.to_display_dict() for driver in state.drivers.values()]
            )
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No drivers available.")

    # ---------------------------------------------------------
    # Batches
    # ---------------------------------------------------------

    with tabs[2]:
        if state.batches:
            df = pd.DataFrame(
                [batch.to_display_dict() for batch in state.batches.values()]
            )
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No batches available.")

    # ---------------------------------------------------------
    # Zones
    # ---------------------------------------------------------

    with tabs[3]:
        if state.zones:
            df = pd.DataFrame(
                [zone.to_display_dict() for zone in state.zones.values()]
            )
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No zones available.")

    # ---------------------------------------------------------
    # Dispatch Centres
    # ---------------------------------------------------------

    with tabs[4]:
        if state.dispatch_centers:
            df = pd.DataFrame(
                [
                    center.to_display_dict()
                    for center in state.dispatch_centers.values()
                ]
            )
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No dispatch centres available.")