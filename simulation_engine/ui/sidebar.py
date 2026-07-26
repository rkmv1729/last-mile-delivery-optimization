"""
Sidebar
-------
Simulation controls and status panel.
"""

import streamlit as st


def render_sidebar(engine, state):
    """
    Render the simulation sidebar.
    """

    st.sidebar.header("Simulation Controls")

    # ---------------------------------------------------------
    # Control Buttons
    # ---------------------------------------------------------

    col1, col2 = st.sidebar.columns(2)

    with col1:
        if st.sidebar.button("▶ Start"):
            engine.start()

    with col2:
        if st.sidebar.button("⏸ Pause"):
            engine.pause()

    if st.sidebar.button("⏹ Reset", use_container_width=True):
        engine.reset()

    if st.sidebar.button("⏭ Tick", use_container_width=True):
        engine.step()

    st.sidebar.divider()

    # ---------------------------------------------------------
    # Simulation Speed
    # ---------------------------------------------------------

    st.sidebar.subheader("Simulation Speed")

    speed = st.sidebar.slider(
        "Speed",
        min_value=1,
        max_value=10,
        value=engine.scheduler.speed,
        step=1,
    )

    engine.scheduler.speed = speed

    st.sidebar.divider()

    # ---------------------------------------------------------
    # Simulation Status
    # ---------------------------------------------------------

    st.sidebar.subheader("Simulation Status")

    st.sidebar.write(
        f"**Current Time:** {state.current_time}"
    )

    st.sidebar.write(
        f"**Current Shift:** {state.current_shift}"
    )

    st.sidebar.metric(
        f"**Current Tick:** {state.tick}"
    )

    st.sidebar.divider()

    # Scheduler

    st.sidebar.subheader("Scheduler")

    status = "🟢 Running" if engine.scheduler.running else "🔴 Paused"

    st.sidebar.write(f"**Status:** {status}")

    st.sidebar.metric(
        f"**Pending Events:** {engine.scheduler.queue_size()}"
    )
