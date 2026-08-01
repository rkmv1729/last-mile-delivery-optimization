from dispatch_optimization.algorithms import *


def run_dispatch(
    orders_df: pd.DataFrame,
    zone_forecast_df: pd.DataFrame,
    dispatch_centres_df: pd.DataFrame,
    available_drivers,
    available_vehicles,
    vehicle_capacity
):
    """
    Runs the complete Dispatch Layer.
    """

    # ----------------------------------------
    # Algorithm 5 : EPS Batch Formation
    # ----------------------------------------

    batch_df = form_batches(
        orders_df=orders_df,
        vehicle_capacity=vehicle_capacity
    )


    # ----------------------------------------
    # Algorithm 6 : BUS Dispatch Optimization
    # ----------------------------------------

    selected_batches_df, retained_batches_df = dispatch_batches(
        batch_df=batch_df,
        forecast_df=zone_forecast_df,
        dispatch_centres_df=dispatch_centres_df,
        available_vehicles=available_vehicles,
        available_drivers=available_drivers,
        vehicle_capacity=vehicle_capacity
    )

    return (
        selected_batches_df,
        retained_batches_df,
    )
