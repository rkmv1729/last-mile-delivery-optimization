"""
helper.py

Utility functions for preparing layer-specific inputs from the
backend master dataframe.
"""

import pandas as pd

from config import (
    AHSI_COLUMNS,
    DEMAND_FORECAST_COLUMNS
)

# TODO : check history df also contains required columns


def create_ahsi_input(
    master_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Prepare the input dataframe required by the AHSI layer.

    Parameters
    ----------
    master_df : pandas.DataFrame
        Backend master dataframe.

    Returns
    -------
    pandas.DataFrame
        Aggregated H3 demand table containing order counts
        at H3-7 and H3-8 resolutions.
    """

    h3_df = master_df.loc[:, AHSI_COLUMNS].copy()

    # ---------------------------------------------------------
    # Aggregate demand at H3 Resolution 7
    # ---------------------------------------------------------

    h3_7_demand = (
        h3_df
        .groupby("h3_cell_7", as_index=False)
        .size()
        .rename(columns={"size": "orders_h3_7"})
    )

    # ---------------------------------------------------------
    # Aggregate demand at H3 Resolution 8
    # ---------------------------------------------------------

    h3_8_demand = (
        h3_df
        .groupby(
            ["h3_cell_7", "h3_cell_8"],
            as_index=False,
        )
        .size()
        .rename(columns={"size": "orders_h3_8"})
    )

    # ---------------------------------------------------------
    # Merge both demand tables
    # ---------------------------------------------------------

    ahsi_inputs = h3_8_demand.merge(
        h3_7_demand,
        on="h3_cell_7",
        how="left",
    )

    return ahsi_inputs



def create_demand_forecast_inputs(
    orders_df: pd.DataFrame,
    history_manager: pd.DataFrame,
    historical_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Prepare rolling historical demand for the Demand Forecast layer.

    Parameters
    ----------
    orders_df : pd.DataFrame
        Orders after spatial and temporal preprocessing.
    history_manager : HistoryManager
        Maintains the rolling historical demand window.

    Returns
    -------
    pd.DataFrame
        Historical demand dataframe ready for the
        DemandForecastEngine.
    """

     # ---------------------------------------------------------
    # Required columns
    # ---------------------------------------------------------
    required_columns = DEMAND_FORECAST_COLUMNS

    missing = [
        column
        for column in required_columns
        if column not in orders_df.columns
    ]

    if missing:
        raise ValueError(
            "Missing required columns for Demand Forecast: "
            f"{missing}"
        )

    if orders_df.empty:
        raise ValueError(
            "Orders DataFrame is empty."
        )

    # ---------------------------------------------------------
    # Aggregate current observations
    # ---------------------------------------------------------
    current_df = (
        orders_df
        .groupby(
            [
                "date",
                "weekday",
                "shift",
                "h3_cell_8",
            ],
            as_index=False,
        )
        .size()
        .rename(
            columns={
                "size": "demand",
            }
        )
    )

    # ---------------------------------------------------------
    # Load rolling history
    # ---------------------------------------------------------
    history_df = history_manager.get_history()

    history_required = DEMAND_FORECAST_COLUMNS.append("demand")

    missing = [
        c
        for c in history_required
        if c not in history_df.columns
    ]

    if missing:
        raise ValueError(
            "HistoryManager returned invalid history. "
            f"Missing columns: {missing}"
        )

    # ---------------------------------------------------------
    # Combine history + current observations
    # ---------------------------------------------------------
    forecast_df = (
        pd.concat(
            [
                history_df,
                current_df,
            ],
            ignore_index=True,
        )
        .sort_values(
            [
                "date",
                "shift",
                "h3_cell_8",
            ]
        )
        .reset_index(drop=True)
    )

    return forecast_df