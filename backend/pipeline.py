from backend.dataframe import orders_to_dataframe
from backend.spatial import add_h3_features
from backend.temporal import add_temporal_features
from backend.utility import aggregate_h3_demand

from typing import List

import pandas as pd

from backend.interface import create_ahsi_input, create_demand_forecast_inputs
from ahsi.run import run_ahsi

from simulation_engine.entities.order import Order

from demand_forecast.run import run_demand_forecast
from demand_forecast.history_manager import HistoryManager
from demand_forecast.zone_forecast import ZoneForecastAggregator

from common.logs.logger import setup_logger
from demand_forecast.config import LOG_FILE

logger = setup_logger(LOG_FILE)


def process_orders(
    orders_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Process simulation orders through the AHSI pipeline.

    Parameters
    ----------
    orders_df : pd.DataFrame
        Simulation orders.

    Returns
    -------
    tuple[pd.DataFrame, pd.DataFrame]
        Processed orders and operational zone mapping.
    """

    if orders_df.empty:
        return None, None

    # Backend preprocessing
    orders_df = add_h3_features(orders_df)
    orders_df = add_temporal_features(orders_df)

    # Prepare AHSI input
    ahsi_input = create_ahsi_input(orders_df)

    # Run AHSI
    zone_mapping = run_ahsi(ahsi_input)

    # Map each order to its operational zone
    order_zone_map = {}

    for _, order in orders_df.iterrows():

        order_zone_map[order["order_id"]] = {
            "zone_id": None,          # TODO: Replace with actual assigned zone
            "h3_cell_7": order["h3_cell_7"],
            "h3_cell_8": order["h3_cell_8"],
        }

    return zone_mapping, order_zone_map


def process_forecast(
    orders_df: pd.DataFrame,
    history_manager: HistoryManager,
    aggregator: ZoneForecastAggregator,
    zone_mapping: pd.DataFrame,
    end_of_day: bool,
) -> pd.DataFrame | None:
    """
    Run the complete demand forecasting pipeline.
    """

    if orders_df.empty:
        return None

    # Aggregate current demand at H3 resolution 8 
    h3_demand = aggregate_h3_demand(
        orders_df,
        resolution=8,
    )

    # Update temporal features
    h3_demand = add_temporal_features(
        h3_demand,
    )

    # Prepare demand forecast inputs
    forecast_df = create_demand_forecast_inputs(
        h3_demand,
        history_manager,
    )

    predictions = run_demand_forecast(
            forecast_df
    )
    
    weights = aggregator.compute_weights(
        history_manager.history_df
    )

    forecast = aggregator.aggregate(
        predictions,
        zone_mapping,
        weights
    )

    if end_of_day:
        history_manager.update(
            h3_demand
        )

    return forecast


