"""
stats.py

Utility functions for computing statistics on the
H3 demand table.
"""

import pandas as pd

# TODO : Not immediately required for us, but include h3_8 stats as well

def compute_demand_statistics(
    h3_demand: pd.DataFrame
    ) -> dict [str, float | int]:
    """
    Compute summary statistics for the H3 demand table.

    Parameters
    ----------
    h3_demand : pandas.DataFrame
        Input dataframe containing an 'orders_h3_7' column.

    Returns
    -------
    dict
        Summary statistics describing the demand distribution.
    """

    required_columns = {"orders_h3_7"}

    missing = required_columns - set(h3_demand.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    orders = h3_demand["orders_h3_7"]

    # TODO : check if len(h3_demand) actually is number of h3 cells
    stats = {
        "h3_cells": len(h3_demand),
        "total_orders": int(orders.sum()),
        "mean": round(orders.mean(), 2),
        "std": round(orders.std(), 2),
        "min": int(orders.min()),
        "p25": round(orders.quantile(0.25), 2),
        "p50": round(orders.quantile(0.50), 2),
        "p75": round(orders.quantile(0.75), 2),
        "p90": round(orders.quantile(0.90), 2),
        "p95": round(orders.quantile(0.95), 2),
        "p99": round(orders.quantile(0.99), 2),
        "max": int(orders.max())
    }

    return stats