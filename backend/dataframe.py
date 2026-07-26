"""
backend/dataframe.py

Utilities for converting simulation entities into pandas DataFrames.
"""

import pandas as pd

from simulation_engine.entities.order import Order


def orders_to_dataframe(
    orders: list[Order],
) -> pd.DataFrame:
    """
    Convert simulation orders into a pandas DataFrame.

    Parameters
    ----------
    orders : list[Order]
        List of simulation Order objects.

    Returns
    -------
    pd.DataFrame
        DataFrame representation of the orders.
    """

    if not orders:
        return pd.DataFrame()

    return pd.DataFrame(
        [order.to_dict() for order in orders]
    )