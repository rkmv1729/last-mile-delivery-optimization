import streamlit as st

from dashboard.components.cards import metric_cards
from dashboard.components.maps import draw_h3_map
from dashboard.components.plots import (
    draw_courier_assignments,
    draw_familiarity_distribution,
)
from dashboard.components.tables import (
    draw_assignment_table,
)

def show_zone_assignment(
    data: dict,
):
    """
    Display the Zone Assignment dashboard page.
    """

    st.title("👷 Zone Assignment")

    zone_assignment_df = data["zone_assignment_df"]
    zone_mapping_df = data["zone_mapping_df"]


    metrics = {

        "Assigned Drivers":
            zone_assignment_df[
                "courier_id"
            ].nunique(),

        "Assigned Zones":
            zone_assignment_df[
                "zone_id"
            ].nunique(),

        "Average Familiarity":
            round(
                zone_assignment_df[
                    "familiarity_score"
                ].mean(),
                3,
            ),

        "Maximum Familiarity":
            round(
                zone_assignment_df[
                    "familiarity_score"
                ].max(),
                2,
            ),
    }

    metric_cards(metrics)

    st.divider()

    draw_courier_assignments(
        zone_assignment_df,
    )

    st.divider()

    draw_familiarity_distribution(
        zone_assignment_df,
    )

    st.divider()


    draw_assignment_table(
        zone_assignment_df,
    )

    st.divider()


    map_df = (
        zone_mapping_df
        .merge(
            zone_assignment_df,
            on="zone_id",
            how="left",
        )
    )

    draw_h3_map(

        dataframe=map_df,

        color_column="courier_id",

        tooltip={
            "html": """
    <b>Zone:</b> {zone_id}<br>
    <b>Courier:</b> {courier_id}<br>
    <b>Familiarity:</b> {familiarity_score}
    """
        },
    )