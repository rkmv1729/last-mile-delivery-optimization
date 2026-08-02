import streamlit as st

from dashboard.components.cards import metric_cards
from dashboard.components.maps import (
    draw_h3_map,
    draw_heatmap_legend
)
from dashboard.components.plots import (
    draw_forecast_per_zone,
    draw_demand_distribution,
    draw_demand_density,
    draw_demand_change,
)
from dashboard.components.tables import (
    draw_forecast_table,
)

def show_demand_forecast(
    data: dict,
):
    """
    Display the Demand Forecast dashboard page.
    """

    st.title("📈 Demand Forecast")

    zone_forecast_df = data["zone_forecast_df"]
    zone_mapping_df = data["zone_mapping_df"]

    total_forecast = zone_forecast_df["forecast_demand"].sum()

    avg_forecast = (
        zone_forecast_df["forecast_demand"]
        .mean()
    )

    peak_row = zone_forecast_df.loc[
        zone_forecast_df["forecast_demand"].idxmax()
    ]

    zone_forecast_df["demand_change"] = (
        (
            zone_forecast_df["forecast_opportunity"] - 1
        )
        * 100
    )

    high_threshold = avg_forecast * 1.20

    metrics = {

        "Forecasted Orders":
            round(total_forecast, 2),

        "Operational Zones":
            zone_forecast_df["zone_id"].nunique(),

        "Peak Demand Zone":
            int(peak_row["zone_id"]),

        "Average Zone Demand":
            round(avg_forecast, 2),

        "High-Demand Zones":
            (
                zone_forecast_df["forecast_demand"]
                > high_threshold
            ).sum(),
    }

    metric_cards(metrics)

    st.divider()


    map_df = (
        zone_mapping_df
        .merge(
            zone_forecast_df,
            on="zone_id",
            how="left",
        )
    )

    map_df["forecast_demand"] = (
        map_df["forecast_demand"]
        .round(1)
    )

    map_df["demand_change"] = (
        map_df["demand_change"]
        .round(1)
    )

    col1, col2 = st.columns([14, 1])

    with col1:

        draw_h3_map(

            dataframe=map_df,

            color_column="forecast_demand",

            tooltip={
                "html": """
    <b>Zone:</b> {zone_id}<br>
    <b>Forecast:</b> {forecast_demand}<br>
    <b>Demand Change:</b> {demand_change}%
    """
            },
        )

    with col2:

        draw_heatmap_legend(
            minimum=map_df["forecast_demand"].min(),
            maximum=map_df["forecast_demand"].max(),
        )

    

    # --------------------------------------------------
    # Forecast Demand
    # --------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        draw_forecast_per_zone(
            zone_forecast_df,
        )

    with col2:

        draw_demand_distribution(
            zone_forecast_df,
        )

    col3, col4 = st.columns(2)

    with col3:

        draw_demand_density(
            zone_forecast_df,
            zone_mapping_df,
        )

    with col4:

        draw_demand_change(
            zone_forecast_df,
        )

    # --------------------------------------------------
    # Forecast Summary
    # --------------------------------------------------

    draw_forecast_table(
        zone_forecast_df,
        zone_mapping_df
    )

    st.divider()


    # --------------------------------------------------
    # Forecast Map
    # --------------------------------------------------

    