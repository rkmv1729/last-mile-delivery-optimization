from simulation_engine.state import SimulationState
import pandas as pd
import streamlit as st


def render_zones(
        state: SimulationState
    ):
    """
    Render zone information.
    """

    st.subheader("🗺️ Operational Zones")

    zones = getattr(state, "zones", {})

    if not zones:
        st.info("No operational zones available.")
        return

    # ============================================================
    # Summary
    # ============================================================

    active_zones = len(zones)

    st.metric("Operational Zones", active_zones)

    st.divider()

    # ============================================================
    # Zone Table
    # ============================================================

    df = pd.DataFrame(
        [
            zone.to_display_dict()
            for zone in zones.values()
        ]
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )