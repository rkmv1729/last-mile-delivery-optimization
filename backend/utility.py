import pandas as pd

def aggregate_h3_demand(
    orders_df: pd.DataFrame,
    resolution: int,
) -> pd.DataFrame:
    """
    Aggregate current demand by H3 cell.

    Parameters
    ----------
    orders_df : pd.DataFrame
        Orders from the simulation.

    resolution : int
        H3 resolution to aggregate at.

    Returns
    -------
    pd.DataFrame
        Demand aggregated by H3 cell.
    """

    h3_column = f"h3_cell_{resolution}"

    h3_demand = (
        orders_df
        .groupby(h3_column)
        .size()
        .reset_index(name="demand")
    )

    return h3_demand