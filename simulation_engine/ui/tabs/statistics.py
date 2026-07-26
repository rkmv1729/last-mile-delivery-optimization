from simulation_engine.state import SimulationState
import streamlit as st


def render_statistics(
        state: SimulationState
    ):
    """
    Render Simulation Statistics tab.
    """

    st.subheader("📊 Simulation Statistics")

    # ============================================================
    # Orders
    # ============================================================

    total_orders = len(state.orders)

    placed_orders = sum(
        1
        for order in state.orders.values()
        if order.status.name == "PLACED"
    )

    batched_orders = sum(
        1
        for order in state.orders.values()
        if order.status.name == "BATCHED"
    )

    completed_orders = sum(
        1
        for order in state.orders.values()
        if order.status.name == "COMPLETED"
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Orders", total_orders)
    col2.metric("Pending", placed_orders)
    col3.metric("Active", batched_orders)
    col4.metric("Completed", completed_orders)

    st.divider()

    # ============================================================
    # Resources
    # ============================================================

    total_drivers = len(state.drivers)
    idle_drivers = sum(
        1
        for driver in state.drivers.values()
        if driver.status.name == "IDLE"
    )
    busy_drivers = total_drivers - idle_drivers

    total_vehicles = len(state.vehicles)
    total_zones = len(state.zones)
    total_dispatch_centres = len(state.dispatch_centers)

    col1, col2, col3 = st.columns(3)

    col1.metric("Drivers", total_drivers)
    col2.metric("Available Drivers", idle_drivers)
    col3.metric("Busy Drivers", busy_drivers)
    

    col1, col2, col3 = st.columns(3)

    col1.metric("Vehicles", total_vehicles)
    col2.metric("Zones", total_zones)
    col3.metric("Dispatch Centres", total_dispatch_centres)

    st.divider()

    # ============================================================
    # Simulation
    # ============================================================

    st.markdown("### ⚙️ Simulation")

    col1, col2, col3 = st.columns(3)

    col1.metric("Current Tick", state.current_tick)

    col2.metric(
        "Simulation Time",
        state.current_time.strftime("%H:%M:%S")
    )

    col3.metric(
        "Current Shift",
        state.current_shift.name
    )

    st.divider()

    # ============================================================
    # Scheduler
    # ============================================================

    st.markdown("### ⏳ Scheduler")

    col1, col2 = st.columns(2)

    col1.metric(
        "Pending Events",
        len(state.scheduler.event_queue),
    )

    col2.metric(
        "Processed Events",
        len(state.event_history),
    )

    st.divider()

    # ============================================================
    # Quick Overview
    # ============================================================

    st.markdown("### 📋 Overview")

    st.write(f"**Orders:** {total_orders}")
    st.write(f"**Drivers:** {total_drivers}")
    st.write(f"**Vehicles:** {total_vehicles}")
    st.write(f"**Zones:** {total_zones}")
    st.write(f"**Dispatch Centres:** {total_dispatch_centres}")
    st.write(f"**Simulation Tick:** {state.current_tick}")