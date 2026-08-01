import pandas as pd
import streamlit as st


def prepare_zone_statistics(
    zone_mapping_df: pd.DataFrame,
    orders_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Compute summary statistics for each operational zone.

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
            - cells
            - orders
    """

    return (
        orders_df
        .groupby(
            "zone_id",
            as_index=False,
        )
        .agg(
            cells=("h3_cell_8", "nunique"),
            orders=("order_id", "count"),
        )
        .sort_values("zone_id")
    )



def draw_zone_statistics(
    zone_mapping_df: pd.DataFrame,
    orders_df: pd.DataFrame,
):
    """
    Display operational zone statistics.
    """

    zone_statistics = prepare_zone_statistics(
        zone_mapping_df,
        orders_df,
    )

    st.subheader("Zone Statistics")

    st.dataframe(
        zone_statistics,
        hide_index=True,
        use_container_width=True,
    )


def prepare_forecast_table(
    zone_forecast_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Prepare zone-level demand forecast table.

    Parameters
    ----------
    zone_forecast_df
        Forecast dataframe containing:
            - zone_id
            - forecast_demand
            - forecast_opportunity

    Returns
    -------
    pd.DataFrame
        Sorted forecast table.
    """

    return (
        zone_forecast_df[
            [
                "zone_id",
                "forecast_demand",
                "forecast_opportunity",
            ]
        ]
        .sort_values("zone_id")
        .reset_index(drop=True)
    )


def draw_forecast_table(
    zone_forecast_df: pd.DataFrame,
):
    """
    Display zone-level demand forecast table.
    """

    forecast_table = prepare_forecast_table(
        zone_forecast_df
    )

    st.subheader("Forecast Summary")

    st.dataframe(
        forecast_table,
        hide_index=True,
        use_container_width=True,
    )

def prepare_assignment_table(
    zone_assignment_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Prepare assignment summary table.
    """

    return (
        zone_assignment_df[
            [
                "zone_id",
                "courier_id",
                "familiarity_score",
            ]
        ]
        .sort_values("zone_id")
        .reset_index(drop=True)
    )

def draw_assignment_table(
    zone_assignment_df: pd.DataFrame,
):
    """
    Display operational zone assignments.
    """

    assignment_df = (
        prepare_assignment_table(
            zone_assignment_df
        )
    )

    st.subheader(
        "Zone Assignments"
    )

    st.dataframe(
        assignment_df,
        hide_index=True,
        use_container_width=True,
    )

def prepare_dispatch_table(
    selected_batches_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Prepare dispatch batch summary.
    """

    return (
        selected_batches_df[
            [
                "batch_id",
                "dispatch_center_id",
                "zone_id",
                "order_count",
                "total_load",
                "batch_priority",
                "retention_penalty",
            ]
        ]
        .sort_values("batch_priority", ascending=False)
        .reset_index(drop=True)
    )

def draw_dispatch_table(
    selected_batches_df: pd.DataFrame,
):
    """
    Display selected dispatch batches.
    """

    dispatch_df = prepare_dispatch_table(
        selected_batches_df
    )

    st.subheader(
        "Selected Dispatch Batches"
    )

    st.dataframe(
        dispatch_df,
        hide_index=True,
        use_container_width=True,
    )


def prepare_retained_orders_table(
    retained_orders_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Prepare retained orders summary.
    """

    return (
        retained_orders_df[
            [
                "order_id",
                "zone_id",
                "retention_cycles",
                "order_priority",
                "retention_penalty",
                "eps",
            ]
        ]
        .sort_values(
            "retention_penalty",
            ascending=False,
        )
        .reset_index(drop=True)
    )

def draw_retained_orders_table(
    retained_orders_df: pd.DataFrame,
):
    """
    Display retained orders.
    """

    retained_df = (
        prepare_retained_orders_table(
            retained_orders_df
        )
    )

    st.subheader(
        "Retained Orders"
    )

    st.dataframe(
        retained_df,
        hide_index=True,
        use_container_width=True,
    )