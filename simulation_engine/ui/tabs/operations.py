from simulation_engine.engine import SimulationEngine
from simulation_engine.state import SimulationState
from simulation_engine.managers.order_manager import OrderManager
from simulation_engine.config import PRODUCTS

import streamlit as st

import pandas as pd

def render_operations(
    engine: SimulationEngine
):
    """
    Render Operations tab.
    """

    state = engine.state
    order_manager = engine.order_manager

    if "operations_mode" not in st.session_state:
        st.session_state.operations_mode = "new"

    if "selected_location" not in st.session_state:
        st.session_state.selected_location = None

    if "current_order_items" not in st.session_state:
        st.session_state.current_order_items = []

    if "placement_mode" not in st.session_state:
        st.session_state.placement_mode = False

    st.subheader("Operations")


    # Place or view orders
    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "➕ New Order",
            use_container_width=True,
        ):
            st.session_state.operations_mode = "new"

    with col2:
        if st.button(
            "📦 View Orders",
            use_container_width=True,
        ):
            st.session_state.operations_mode = "view"

    # New order placed or view order
    if st.session_state.operations_mode == "new":
        render_new_order(
            state,
            order_manager,
        )
    else:
        render_view_orders(state)

 


def render_new_order(
    state: SimulationState,
    order_manager: OrderManager,
):
    """
    Render New Order interface.
    """
 
    st.markdown("### 🛒 New Order")

    # ============================================================
    # Delivery Location
    # ============================================================

    st.markdown("#### 📍 Delivery Location")

    if st.session_state.selected_location is None:

        st.info("Click **Select Location**, then click on the map.")

    else:

        lat, lon = st.session_state.selected_location

        st.success(
            f"Selected Location\n\nLatitude : {lat:.6f}\n\nLongitude : {lon:.6f}"
        )

    if st.button(
        "📍 Select Location",
        use_container_width=True,
    ):
        st.session_state.placement_mode = True

    st.divider()

    # ============================================================
    # Products
    # ============================================================

    st.markdown("#### 📦 Products")

    col1, col2 = st.columns([3, 1])

    with col1:

        product = st.selectbox(
            "Product",
            PRODUCTS,
        )

    with col2:

        quantity = st.number_input(
            "Quantity",
            min_value=1,
            value=1,
            step=1,
        )

    if st.button(
        "➕ Add Product",
        use_container_width=True,
    ):

        st.session_state.current_order_items.append(
            {
                "product": product,
                "quantity": quantity,
            }
        )

    # ============================================================
    # Current Products
    # ============================================================

    if st.session_state.current_order_items:

        st.markdown("#### Current Order")

        for idx, item in enumerate(st.session_state.current_order_items):

            c1, c2, c3 = st.columns([4, 1, 1])

            c1.write(item["product"])

            c2.write(item["quantity"])

            if c3.button(
                "❌",
                key=f"remove_product_{idx}",
            ):
                st.session_state.current_order_items.pop(idx)
                st.rerun()

    else:

        st.info("No products added.")

    st.divider()

    # ============================================================
    # Place Order
    # ============================================================

    if st.button(
        "✅ Place Order",
        use_container_width=True,
        type="primary",
    ):

        if st.session_state.selected_location is None:

            st.error("Please select a delivery location.")
            return

        if len(st.session_state.current_order_items) == 0:

            st.error("Please add at least one product.")
            return

        lat, lon = st.session_state.selected_location

        try:

            order_manager.create_order(
            state=state,
            customer_id="USER_001",      # TODO(Post-Submission): Dynamic customer selection
            products=st.session_state.current_order_items,
            latitude=lat,
            longitude=lon,
        )

            st.success("Order placed successfully!")

            # Reset UI
            st.session_state.selected_location = None
            st.session_state.current_order_items = []
            st.session_state.placement_mode = False

            st.rerun()

        except Exception as e:

            st.error(f"Failed to place order.\n\n{e}")
    



def render_view_orders(
    state: SimulationState,
):
    """
    Render View Orders interface.
    """

    st.markdown("### 📦 Orders")

    if not state.orders:
        st.info("No orders have been placed yet.")
        return

    # ============================================================
    # Summary
    # ============================================================

    total_orders = len(state.orders)

    pending_orders = sum(
        1 for order in state.orders.values()
        if order.status.name == "PENDING"
    )

    active_orders = sum(
        1 for order in state.orders.values()
        if order.status.name == "ACTIVE"
    )

    completed_orders = sum(
        1 for order in state.orders.values()
        if order.status.name == "COMPLETED"
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total", total_orders)
    col2.metric("Pending", pending_orders)
    col3.metric("Active", active_orders)
    col4.metric("Completed", completed_orders)

    st.divider()

    # ============================================================
    # Order Selection
    # ============================================================

    order_ids = list(state.orders.keys())

    selected_order_id = st.selectbox(
        "Select Order",
        order_ids,
    )

    order = state.orders[selected_order_id]

    # ============================================================
    # Order Details
    # ============================================================

    st.subheader(f"Order {order.order_id}")

    left, right = st.columns(2)

    with left:

        st.markdown("#### General")

        st.write(f"**Status:** {order.status.name}")

        st.write(f"**Customer:** {order.customer_id}")

        st.write(f"**Created:** {order.created_time}")

        st.write(f"**Priority:** {order.priority}")

    with right:

        st.markdown("#### Delivery")

        st.write(f"**Latitude:** {order.latitude:.6f}")

        st.write(f"**Longitude:** {order.longitude:.6f}")

        st.write(f"**Zone:** {order.zone_id}")

        st.write(f"**Driver:** {order.driver_id}")

    st.divider()

    # ============================================================
    # Products
    # ============================================================

    st.markdown("#### Products")

    product_rows = []

    for item in order.products:

        product_rows.append(
            {
                "Product": item.product_name,
                "Quantity": item.quantity,
            }
        )

    st.dataframe(
        pd.DataFrame(product_rows),
        use_container_width=True,
        hide_index=True,
    )
    