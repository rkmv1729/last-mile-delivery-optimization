import streamlit as st

from dashboard.components.cards import metric_cards
from dashboard.components.plots import draw_orders_per_zone
from dashboard.components.tables import draw_zone_statistics
from dashboard.components.maps import draw_h3_map


def show_ahsi(
    data: dict,
):
    """
    Display the AHSI dashboard page.
    """

    st.title("📍 Adaptive H3 Spatial Indexing")

    zone_mapping_df = data["zone_mapping_df"]
    orders_df = data["orders_df"]

    total_zones = (
        zone_mapping_df["zone_id"]
        .nunique()
    )

    total_cells = (
        zone_mapping_df["h3_cell_8"]
        .nunique()
    )

    cells_per_zone = (
        zone_mapping_df
        .groupby("zone_id")["h3_cell_8"]
        .nunique()
    )

    orders_per_zone = (
        orders_df
        .groupby("zone_id")["order_id"]
        .count()
    )

    metrics = {

        "Zones":
            total_zones,

        "H3 Cells":
            total_cells,

        "Avg Cells / Zone":
            round(
                cells_per_zone.mean(),
                2,
            ),

        "Avg Orders / Zone":
            round(
                orders_per_zone.mean(),
                2,
            ),
    }

    metric_cards(metrics)

    st.divider()

    # -----------------------------------------------------
    # Orders per Zone
    # -----------------------------------------------------

    draw_orders_per_zone(
        zone_mapping_df=zone_mapping_df,
        orders_df=orders_df,
    )

    st.divider()

    # -----------------------------------------------------
    # Zone Statistics
    # -----------------------------------------------------

    draw_zone_statistics(
        zone_mapping_df=zone_mapping_df,
        orders_df=orders_df,
    )

    st.divider()

    # -----------------------------------------------------
    # Prepare Map Data
    # -----------------------------------------------------

    zone_orders = (
        orders_df
        .groupby(
            "h3_cell_8",
            as_index=False,
        )
        .agg(
            orders=("order_id", "count")
        )
    )

    map_df = (
        zone_mapping_df
        .merge(
            zone_orders,
            on="h3_cell_8",
            how="left",
        )
    )

    map_df["orders"] = (
        map_df["orders"]
        .fillna(0)
        .astype(int)
    )

    # -----------------------------------------------------
    # Operational Zone Map
    # -----------------------------------------------------

    draw_h3_map(
        dataframe=map_df,
        color_column="zone_id",
        tooltip={
            "html": """
                <b>Zone:</b> {zone_id}<br>
                <b>Cell:</b> {h3_cell_8}<br>
                <b>Orders:</b> {orders}
            """
        },
    )