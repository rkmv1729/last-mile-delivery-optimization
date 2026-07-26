"""
threshold.py

Adaptive threshold selection for AHSI.
"""

import pandas as pd

from ahsi.config import (
    INITIAL_SPARSE_PERCENTILE,
    INITIAL_HOTSPOT_PERCENTILE
)

def compute_thresholds(
        h3_demand: pd.DataFrame,
    ) -> tuple[float, float]:
    """
    Compute adaptive sparse and hotspot demand thresholds.

    Args:
        h3_demand (pd.DataFrame):
            DataFrame containing H3 demand values.

        sparse_percentile (float):
            Percentile used to identify sparse cells.

        hotspot_percentile (float):
            Percentile used to identify hotspot cells.

    Returns
    -------
        tuple[float, float]
            Sparse demand threshold and hotspot demand threshold.
    """ 

    if "orders_h3_7" not in h3_demand.columns:
        raise ValueError(
            "Input dataframe must contain an 'orders' column."
        )
    
    orders = h3_demand["orders_h3_7"]

    # ------------------------------------------------------------------
    # Initial heuristic (can be replaced later)
    # ------------------------------------------------------------------
    sparse_percentile = INITIAL_SPARSE_PERCENTILE
    hotspot_percentile = INITIAL_HOTSPOT_PERCENTILE

    sparse_orders = int(orders.quantile(sparse_percentile / 100))
    hotspot_orders = int(orders.quantile(hotspot_percentile / 100))

    return sparse_orders, hotspot_orders