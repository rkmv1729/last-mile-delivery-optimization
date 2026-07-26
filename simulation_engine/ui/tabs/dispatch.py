from simulation_engine.state import SimulationState
import pandas as pd
import streamlit as st


def render_dispatch(
        state: SimulationState
    ):
    """
    Render dispatch information.
    """

    st.subheader("🚚 Dispatch")

    # ============================================================
    # Summary
    # ============================================================

    total_centres = len(state.dispatch_centers)
    total_batches = len(state.batches)
    total_vehicles = len(state.vehicles)

    col1, col2, col3 = st.columns(3)

    col1.metric("Dispatch Centres", total_centres)
    col2.metric("Batches", total_batches)
    col3.metric("Vehicles", total_vehicles)

    st.divider()

    # ============================================================
    # Dispatch Centres
    # ============================================================

    st.markdown("### Dispatch Centres")

    if state.dispatch_centers:

        df = pd.DataFrame(
            [
                centre.to_display_dict()
                for centre in state.dispatch_centers.values()
            ]
        )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )

    else:
        st.info("No dispatch centres available.")

    st.divider()

    # ============================================================
    # Batches
    # ============================================================

    st.markdown("### Dispatch Batches")

    if state.batches:

        df = pd.DataFrame(
            [
                batch.to_display_dict()
                for batch in state.batches.values()
            ]
        )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )

    else:
        st.info("No dispatch batches available.")