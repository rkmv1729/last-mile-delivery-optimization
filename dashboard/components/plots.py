import pandas as pd
import streamlit as st

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



def draw_orders_per_zone(
    zone_mapping_df: pd.DataFrame,
    orders_df: pd.DataFrame,
):
    """
    Display total orders across operational zones.
    """

    zone_orders = prepare_orders_per_zone(
        zone_mapping_df,
        orders_df,
    )

    st.subheader("Orders per Zone")

    st.bar_chart(
        data=zone_orders,
        x="zone_id",
        y="orders",
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
    zone_forecast_df: pd.DataFrame,
):
    """
    Display forecast demand across operational zones.
    """

    forecast_df = prepare_forecast_per_zone(
        zone_forecast_df
    )

    st.subheader("Forecast Demand per Zone")

    st.bar_chart(
        data=forecast_df,
        x="zone_id",
        y="forecast_demand",
        use_container_width=True,
    )


def prepare_forecast_opportunity(
    zone_forecast_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Prepare Forecast Opportunity scores for visualization.

    Parameters
    ----------
    zone_forecast_df
        Forecast dataframe containing:
            - zone_id
            - forecast_opportunity

    Returns
    -------
    pd.DataFrame
        Columns:
            - zone_id
            - forecast_opportunity
    """

    return (
        zone_forecast_df[
            [
                "zone_id",
                "forecast_opportunity",
            ]
        ]
        .sort_values("zone_id")
        .reset_index(drop=True)
    )

def draw_forecast_opportunity(
    zone_forecast_df: pd.DataFrame,
):
    """
    Display Forecast Opportunity scores across zones.
    """

    opportunity_df = (
        prepare_forecast_opportunity(
            zone_forecast_df
        )
    )

    st.subheader("Forecast Opportunity")

    st.bar_chart(
        data=opportunity_df,
        x="zone_id",
        y="forecast_opportunity",
        use_container_width=True,
    )



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