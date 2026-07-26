from simulation_engine.state import SimulationState
import pandas as pd
import streamlit as st


def render_drivers(
        state: SimulationState
    ):
    """
    Render driver information.
    """

    st.subheader("🚗 Drivers")

    drivers = state.drivers

    if not drivers:
        st.info("No drivers available.")
        return

    # ============================================================
    # Summary
    # ============================================================

    total = len(drivers)

    idle = sum(
        1
        for driver in drivers.values()
        if driver.status.name == "IDLE"
    )

    busy = total - idle

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Drivers", total)
    col2.metric("Idle", idle)
    col3.metric("Busy", busy)

    st.divider()

    # ============================================================
    # Driver Table
    # ============================================================

    rows = [
        driver.to_display_dict()
        for driver in drivers.values()
    ]

    df = pd.DataFrame(rows)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )