import streamlit as st

from dashboard.components.cards import metric_cards
from dashboard.components.maps import draw_h3_map
from dashboard.components.plots import (
    draw_forecast_opportunity,
    draw_forecast_per_zone,
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

    metrics = {

        "Total Forecast":
            round(
                zone_forecast_df[
                    "forecast_demand"
                ].sum(),
                2,
            ),

        "Average Forecast":
            round(
                zone_forecast_df[
                    "forecast_demand"
                ].mean(),
                2,
            ),

        "Peak Forecast":
            round(
                zone_forecast_df[
                    "forecast_demand"
                ].max(),
                2,
            ),

        "Peak Opportunity":
            round(
                zone_forecast_df[
                    "forecast_opportunity"
                ].max(),
                2,
            ),
    }

    metric_cards(metrics)

    st.divider()

    # --------------------------------------------------
    # Forecast Demand
    # --------------------------------------------------

    draw_forecast_per_zone(
        zone_forecast_df,
    )

    st.divider()

    # --------------------------------------------------
    # Forecast Opportunity
    # --------------------------------------------------

    draw_forecast_opportunity(
        zone_forecast_df,
    )

    st.divider()

    # --------------------------------------------------
    # Forecast Summary
    # --------------------------------------------------

    draw_forecast_table(
        zone_forecast_df,
    )

    st.divider()


    # --------------------------------------------------
    # Forecast Map
    # --------------------------------------------------

    map_df = (
        zone_mapping_df
        .merge(
            zone_forecast_df,
            on="zone_id",
            how="left",
        )
    )

    draw_h3_map(

        dataframe=map_df,

        color_column="zone_id",

        tooltip={
            "html": """
    <b>Zone:</b> {zone_id}<br>
    <b>Forecast:</b> {forecast_demand}<br>
    <b>Opportunity:</b> {forecast_opportunity}
    """
            },
    )