from simulation_engine.engine import SimulationEngine
import pandas as pd
import streamlit as st


def render_events(
        engine: SimulationEngine
    ):
    """
    Render simulation event history.
    """

    state = engine.state

    st.subheader("📅 Simulation Events")

    events = state.event_history

    if not events:
        st.info("No events have been processed yet.")
        return

    rows = []

    for event in reversed(events):

        event_type = getattr(event.event_type, "name", str(event.event_type))

        rows.append(
            {
                "Scheduled Time": event.scheduled_time,
                "Priority": event.priority,
                "Event": event_type,
                "Payload": ", ".join(
                    f"{k}={v}"
                    for k, v in event.payload.items()
                ) if isinstance(event.payload, dict) else str(event.payload),
            }
        )

    df = pd.DataFrame(rows)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    st.markdown("### Event Summary")

    col1, col2 = st.columns(2)

    col1.metric(
        "Processed Events",
        len(events),
    )

    scheduler = engine.scheduler

    pending = 0

    if scheduler is not None:
        pending = scheduler.event_queue

    col2.metric(
        "Pending Events",
        pending,
    )