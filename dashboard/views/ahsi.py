import streamlit as st

from dashboard.components.cards import metric_cards
from dashboard.components.plots import (
    draw_orders_per_zone,
    draw_cells_per_zone,
    draw_workload_vs_cells,
    draw_refinement_history,
    draw_workload_deviation
)
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
    history_df = data["ahsi_history_df"]

    total_zones = (
        zone_mapping_df["zone_id"]
        .nunique()
    )

    total_cells = (
        zone_mapping_df["h3_cell_8"]
        .nunique()
    )

    orders_per_zone = (
        orders_df
        .groupby("zone_id")["order_id"]
        .count()
    )

    target_workload = orders_per_zone.mean()

    max_deviation = (
        orders_per_zone
        .sub(target_workload)
        .abs()
        .max()
    )

    mean_deviation = (
        orders_per_zone
        .sub(target_workload)
        .abs()
        .mean()
    )

    metrics = {

        "Operational Zones":
            total_zones,

        "Active H3-8 Cells":
            total_cells,

        "Target Workload":
            f"{target_workload:.1f}",

        "Mean Target Deviation":
            f"{mean_deviation:.1f}",

        "Max Target Deviation":
            f"{max_deviation:.1f}",
    }

    metric_cards(metrics)

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

    st.divider()

    draw_refinement_history(
        history_df
    )

    # -----------------------------------------------------
    # Orders per Zone
    # -----------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:
        draw_orders_per_zone(
            zone_mapping_df=zone_mapping_df,
            orders_df=orders_df,
        )

    with col2:
        draw_cells_per_zone(
            zone_mapping_df
        )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        draw_workload_vs_cells(
            zone_mapping_df,
            orders_df,
        )

    with col2:
        draw_workload_deviation(
            zone_mapping_df,
            orders_df
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

    