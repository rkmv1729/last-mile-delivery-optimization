import streamlit as st
import folium
from streamlit_folium import st_folium
import h3


DEFAULT_LOCATION = [30.2741, 120.1551]  # Hangzhou


def render_map(state):
    """
    Render the simulation map.
    """

    # ------------------------------------------------------------
    # Base Map
    # ------------------------------------------------------------

    sim_map = folium.Map(
        location=DEFAULT_LOCATION,
        zoom_start=11,
        control_scale=True,
    )

    # ------------------------------------------------------------
    # Dispatch Centres
    # ------------------------------------------------------------

    for center in state.dispatch_centers.values():
        folium.Marker(
            location=[center.latitude, center.longitude],
            popup=f"Dispatch Centre {center.center_id}",
            tooltip=center.name,
            icon=folium.Icon(color="blue", icon="home"),
        ).add_to(sim_map)

    # ------------------------------------------------------------
    # Orders
    # ------------------------------------------------------------

    for order in state.orders.values():

        product_text = "<br>".join(
            f"{p.item_id} × {p.quantity}"
            for p in order.products
        )

        popup = folium.Popup(
            f"""
            <b>Order {order.order_id}</b><br>
            Customer: {order.customer_id}<br>
            Status: {order.status.name}<br><br>
            <b>Products</b><br>
            {product_text}
            """,
            max_width=250,
        )

        folium.CircleMarker(
            location=[order.latitude, order.longitude],
            radius=5,
            color="red",
            fill=True,
            fill_opacity=0.8,
            tooltip=f"Order {order.order_id}",
            popup=popup,
        ).add_to(sim_map)


    # ------------------------------------------------------------
    # Zones (AHSI)
    # ------------------------------------------------------------

    for zone in state.zones.values():

        for cell in zone.h3_cells:

            boundary = h3.cell_to_boundary(cell)

            folium.Polygon(
                locations=boundary,
                color="green",
                weight=2,
                fill=True,
                fill_opacity=0.15,
                popup=f"Zone {zone.zone_id}",
            ).add_to(sim_map)

        folium.Marker(
            location=[zone.centroid_latitude, zone.centroid_longitude],
            tooltip=zone.zone_id,
            icon=folium.DivIcon(
                html=f"<div style='font-size:10pt'><b>{zone.zone_id}</b></div>"
            ),
        ).add_to(sim_map)



    # ------------------------------------------------------------
    # Render
    # ------------------------------------------------------------

    map_data = st_folium(
        sim_map,
        use_container_width=True,
        height=650,
    )

    if (
        st.session_state.placement_mode
        and map_data.get("last_clicked")
    ):
        st.session_state.selected_location = (
            map_data["last_clicked"]
        )

        st.session_state.placement_mode = False
        

    return st.session_state.selected_location