import pandas as pd
from pathlib import Path

from algorithms import (
    form_batches,
    dispatch_batches,
    extract_retained_orders
)

from helpers import (
    enrich_orders,
    recycle_retained_orders,
    assign_dispatch_centers
)

AVAILABLE_VEHICLES = 100
AVAILABLE_DRIVERS = 200


def run_dispatch(
    new_orders_df: pd.DataFrame,
    retained_orders_df: pd.DataFrame,
    forecast_df: pd.DataFrame,
    dispatch_centres_df: pd.DataFrame,
    products_df: pd.DataFrame
):
    """
    Runs the complete Dispatch Layer.
    """

    new_orders_df = enrich_orders(
        new_orders_df,
        products_df,
    )

    new_orders_df = assign_dispatch_centers(
        new_orders_df,
        dispatch_centres_df,
    )

    orders_df = recycle_retained_orders(
        new_orders_df=new_orders_df,
        retained_orders_df=retained_orders_df,
    )

    # ----------------------------------------
    # Algorithm 5 : EPS Batch Formation
    # ----------------------------------------

    batch_df = form_batches(
        orders_df=orders_df,
    )


    # ----------------------------------------
    # Algorithm 6 : BUS Dispatch Optimization
    # ----------------------------------------

    selected_batches_df, retained_batches_df = dispatch_batches(
        batch_df=batch_df,
        forecast_df=forecast_df,
        dispatch_centres_df=dispatch_centres_df,
        available_vehicles=AVAILABLE_VEHICLES,
        available_drivers=AVAILABLE_DRIVERS 
    )

    return (
        selected_batches_df,
        retained_batches_df,
    )


if __name__ == "__main__":

    new_orders_df = pd.read_parquet("inputs/orders01.parquet")
    products_df = pd.read_parquet("inputs/products.parquet")
    retained_orders_path = Path(
        "outputs/retained_orders.parquet"
    )

    if retained_orders_path.exists():
        retained_orders_df = pd.read_parquet(
            retained_orders_path
        )
    else:
        retained_orders_df = pd.DataFrame()

    forecast_df = pd.read_parquet("inputs/forecast_opportunity.parquet")
    dispatch_centres_df = pd.read_parquet("inputs/dispatch_centres.parquet")

    selected_batches_df, retained_batches_df = run_dispatch(
        new_orders_df=new_orders_df,
        retained_orders_df=retained_orders_df,
        forecast_df=forecast_df,
        dispatch_centres_df=dispatch_centres_df,
        products_df=products_df
    )

    retained_orders_df = extract_retained_orders(      
        retained_batches_df,
    )


    selected_df = selected_batches_df.copy()

    selected_df["orders"] = selected_df["orders"].apply(
        lambda orders: [o.order_id for o in orders]
    )

    selected_df.to_parquet(
        "outputs/selected_batches.parquet",
        index=False,
    )

    retained_orders_df.to_parquet(
        "outputs/retained_orders.parquet",
        index=False,
    )

    print("selected: ", len(selected_batches_df))
    print("retained: ", len(retained_batches_df))


    print("Saved files")