import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

def prepare_orders_per_zone(
    zone_mapping_df: pd.DataFrame,
    orders_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Aggregate total orders for each operational zone.

    Parameters
    ----------
    zone_mapping_df
        Zone mapping containing:
            - h3_cell_8
            - zone_id

    orders_df
        Orders dataframe containing:
            - order_id
            - h3_cell_8

    Returns
    -------
    pd.DataFrame
        Columns:
            - zone_id
            - orders
    """

    return (
        orders_df
        .groupby(
            "zone_id",
            as_index=False,
        )
        .agg(
            orders=("order_id", "count")
        )
        .sort_values("zone_id")
    )


# orders per zone plot (AHSI workload balance performance)
def draw_orders_per_zone(
    zone_mapping_df: pd.DataFrame,
    orders_df: pd.DataFrame,
):
    """
    Display workload across operational zones.
    """

    zone_orders = prepare_orders_per_zone(
        zone_mapping_df,
        orders_df,
    )

    target = zone_orders["orders"].mean()

    fig = px.bar(
        zone_orders,
        x="zone_id",
        y="orders",
        labels={
            "zone_id": "Zone",
            "orders": "Orders"
        },
    )

    fig.add_hline(
        y=target,
        line_dash="dash",
        annotation_text=f"Target = {target:.1f}",
        annotation_position="top left",
    )

    fig.update_layout(
        title="Zone Workload Distribution",
        xaxis_title="Zone",
        yaxis_title="Orders",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )


# number of cells per zone (AHSI spatial expansion performance)
def draw_cells_per_zone(
    zone_mapping_df: pd.DataFrame,
):
    """
    Display number of H3 cells in each zone.
    """

    cells = (
        zone_mapping_df
        .groupby(
            "zone_id",
            as_index=False,
        )
        .agg(
            cells=("h3_cell_8", "nunique")
        )
    )

    fig = px.bar(
        cells,
        x="zone_id",
        y="cells",
        labels={
            "zone_id": "Zone",
            "cells": "H3 Cells"
        },
    )

    fig.update_layout(
        title="Cells per Zone",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )


# workload per cells 
def draw_workload_vs_cells(
    zone_mapping_df: pd.DataFrame,
    orders_df: pd.DataFrame,
):
    """
    Relationship between workload and zone size.
    """

    cells = (
        zone_mapping_df
        .groupby(
            "zone_id",
            as_index=False,
        )
        .agg(
            cells=("h3_cell_8", "nunique")
        )
    )

    orders = (
        orders_df
        .groupby(
            "zone_id",
            as_index=False,
        )
        .agg(
            orders=("order_id", "count")
        )
    )

    scatter_df = (
        cells.merge(
            orders,
            on="zone_id"
        )
    )

    fig = px.scatter(
        scatter_df,
        x="cells",
        y="orders",
        labels={
            "cells": "H3 Cells",
            "orders": "Orders"
        },
    )

    fig.update_traces(
        textposition="top center"
    )

    fig.update_layout(
        title="Workload vs Zone Size",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

# algorithm iteration steps
def draw_refinement_history(
    history_df: pd.DataFrame,
):
    """
    Display convergence during boundary refinement.
    """

    fig = px.line(
        history_df,
        x="iteration",
        y="std_deviation",
        markers=True,
        labels={
            "iteration": "Refinement Pass",
            "std_deviation": "Std. Deviation"
        },
    )

    fig.update_layout(
        title="Boundary Refinement Convergence",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )


def draw_workload_deviation(
    zone_mapping_df: pd.DataFrame,
    orders_df: pd.DataFrame,
):
    """
    Display workload deviation from the target workload
    for each operational zone.
    """

    zone_orders = (
        orders_df
        .groupby(
            "zone_id",
            as_index=False,
        )
        .agg(
            orders=("order_id", "count")
        )
        .sort_values("zone_id")
    )

    target = zone_orders["orders"].mean()

    zone_orders["deviation"] = (
        zone_orders["orders"] - target
    )

    fig = px.bar(
        zone_orders,
        x="zone_id",
        y="deviation",
        labels={
            "zone_id": "Zone",
            "deviation": "Deviation (Orders)"
        },
        text=zone_orders["deviation"].round(1),
    )

    fig.add_hline(
        y=0,
        line_dash="dash",
    )

    fig.update_traces(
        textposition="outside",
    )

    fig.update_layout(
        title="Workload Deviation from Target",
        xaxis_title="Operational Zone",
        yaxis_title="Deviation (Orders)",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )



def prepare_forecast_per_zone(
    zone_forecast_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Prepare forecast demand for visualization.
    """

    return (
        zone_forecast_df[
            [
                "zone_id",
                "forecast_demand",
            ]
        ]
        .sort_values("zone_id")
        .reset_index(drop=True)
    )

def draw_forecast_per_zone(
    zone_forecast_df,
):

    forecast_df = prepare_forecast_per_zone(
        zone_forecast_df
    )

    fig = px.bar(
        forecast_df,
        x="zone_id",
        y="forecast_demand",
        labels={
            "zone_id": "Zone",
            "forecast_demand": "Forecast Demand",
        },
    )

    fig.update_layout(
        title="Forecast Demand by Zone",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )



def draw_demand_distribution(
    zone_forecast_df,
):

    fig = px.histogram(
        zone_forecast_df,
        x="forecast_demand",
        nbins=20,
    )

    fig.update_layout(
        title="Forecast Demand Distribution",
        xaxis_title="Forecast Demand",
        yaxis_title="Zones",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )



def draw_demand_density(
    zone_forecast_df,
    zone_mapping_df,
):

    cells = (
        zone_mapping_df
        .groupby(
            "zone_id",
            as_index=False,
        )
        .agg(
            cells=("h3_cell_8", "nunique")
        )
    )

    scatter_df = (
        zone_forecast_df
        .merge(
            cells,
            on="zone_id",
        )
    )

    fig = px.scatter(
        scatter_df,
        x="cells",
        y="forecast_demand",
        labels={
            "cells": "H3 Cells",
            "forecast_demand": "Forecast Demand",
        },
    )

    fig.update_layout(
        title="Demand Density vs Zone Size",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )




# def prepare_forecast_opportunity(
#     zone_forecast_df: pd.DataFrame,
# ) -> pd.DataFrame:
#     """
#     Prepare Forecast Opportunity scores for visualization.

#     Parameters
#     ----------
#     zone_forecast_df
#         Forecast dataframe containing:
#             - zone_id
#             - forecast_opportunity

#     Returns
#     -------
#     pd.DataFrame
#         Columns:
#             - zone_id
#             - forecast_opportunity
#     """

    

#     return (
#         zone_forecast_df[
#             [
#                 "zone_id",
#                 "forecast_opportunity",
#             ]
#         ]
#         .sort_values("zone_id")
#         .reset_index(drop=True)
#     )


def draw_demand_change(
    zone_forecast_df,
):

    fig = px.bar(
        zone_forecast_df,
        x="zone_id",
        y="demand_change",
        labels={
            "zone_id": "Zone",
            "demand_change": "Demand Change (%)",
        },
    )

    fig.add_hline(
        y=0,
        line_dash="dash",
    )

    fig.update_layout(
        title="Forecast Demand Change",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

# def draw_forecast_opportunity(
#     zone_forecast_df: pd.DataFrame,
# ):
#     """
#     Display Forecast Opportunity scores across zones.
#     """

#     opportunity_df = (
#         prepare_forecast_opportunity(
#             zone_forecast_df
#         )
#     )

#     st.subheader("Forecast Opportunity")

#     st.bar_chart(
#         data=opportunity_df,
#         x="zone_id",
#         y="forecast_opportunity",
#         use_container_width=True,
#     )



def prepare_courier_assignments(
    zone_assignment_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Prepare number of zones assigned to each courier.
    """

    return (
        zone_assignment_df
        .groupby(
            "courier_id",
            as_index=False,
        )
        .agg(
            assigned_zones=("zone_id", "count")
        )
        .sort_values("courier_id")
    )



def draw_courier_assignments(
    zone_assignment_df: pd.DataFrame,
):
    """
    Display number of zones assigned to each courier.
    """

    assignment_df = prepare_courier_assignments(
        zone_assignment_df
    )

    st.subheader(
        "Zones Assigned per Courier"
    )

    st.bar_chart(
        data=assignment_df,
        x="courier_id",
        y="assigned_zones",
        use_container_width=True,
    )



def prepare_familiarity_distribution(
    zone_assignment_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Prepare familiarity scores for visualization.

    Parameters
    ----------
    zone_assignment_df
        Assignment dataframe containing:
            - familiarity_score

    Returns
    -------
    pd.DataFrame
        Familiarity scores.
    """

    return (
        zone_assignment_df[
            [
                "familiarity_score",
            ]
        ]
        .copy()
    )


def draw_familiarity_distribution(
    zone_assignment_df: pd.DataFrame,
):
    """
    Display familiarity score distribution.
    """

    st.subheader("Familiarity Distribution")

    st.bar_chart(
        zone_assignment_df["familiarity_score"]
    )


def prepare_dispatch_summary(
    selected_batches_df: pd.DataFrame,
    retained_batches_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Prepare dispatch summary.
    """

    return pd.DataFrame(
        {
            "Status": [
                "Selected",
                "Retained",
            ],
            "Batches": [
                len(selected_batches_df),
                len(retained_batches_df),
            ],
        }
    )



def draw_dispatch_summary(
    selected_batches_df: pd.DataFrame,
    retained_batches_df: pd.DataFrame,
):
    """
    Display dispatch summary.
    """

    dispatch_df = prepare_dispatch_summary(
        selected_batches_df,
        retained_batches_df,
    )

    st.subheader(
        "Selected vs Retained Batches"
    )

    st.bar_chart(
        dispatch_df,
        x="Status",
        y="Batches",
        use_container_width=True,
    )



def prepare_batch_priority(
    selected_batches_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Prepare batch priority.
    """

    return (
        selected_batches_df[
            [
                "batch_id",
                "batch_priority",
            ]
        ]
        .sort_values(
            "batch_priority",
            ascending=False,
        )
        .reset_index(drop=True)
    )




def draw_batch_priority(
    selected_batches_df: pd.DataFrame,
):
    """
    Display batch priority.
    """

    priority_df = (
        prepare_batch_priority(
            selected_batches_df
        )
    )

    st.subheader(
        "Batch Priority"
    )

    st.bar_chart(
        priority_df,
        x="batch_id",
        y="batch_priority",
        use_container_width=True,
    )