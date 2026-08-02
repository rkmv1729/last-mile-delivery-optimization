import pandas as pd
from helpers import *
from ahsi.run_ahsi import run_ahsi
from demand_forecast.run_forecast import run_forecast
from dispatch_optimization.run_dispatch import run_dispatch
from zone_assignment.run_assignment import run_assignment
from config import *

# TODO (Simulation Engine):
# Deserialize the 'products' column after reading
# retained_orders.parquet before calling
# recycle_retained_orders().

default_date = pd.Timestamp("1900-07-24")
default_shift = "Afternoon"


def run_pipeline(
    lade_hz_df,
    retained_orders_df,
    products_df,
    familiarity_df,
    dispatch_centres_df,
    ds,
    shift,
    metadata,
    scaler,
    model,
):
    """
    Execute the complete last-mile delivery pipeline.

    Returns
    -------
    dict
        Outputs from all layers.
    """

    # ------------------------------------------------------------
    # Prepare Operational State
    # ------------------------------------------------------------

    current_shift_df, forecast_df = prepare_operational_state(
        lade_df=lade_hz_df,
        metadata=metadata,
        ds=ds,
        shift=shift
    )   

    # ------------------------------------------------------------
    # AHSI
    # ------------------------------------------------------------

    h3_demand_df = build_h3_demand(
        current_shift_df=current_shift_df
    )

    zone_mapping_df, history_df = run_ahsi(
        h3_demand_df=h3_demand_df,
        num_zones=NUM_ZONES,
        seed_spacing=SEED_SPACING
    )

    current_shift_zone_df = attach_zone_ids(
        current_shift_df=current_shift_df,
        zone_mapping_df=zone_mapping_df
    )

    # ------------------------------------------------------------
    # Demand Forecast
    # ------------------------------------------------------------

    cell_forecast_df = run_forecast(
        forecast_df=forecast_df,
        model=model,
        metadata=metadata,
        scaler=scaler
    )

    cell_forecast_df = denormalize_dataframe(
        df=cell_forecast_df,
        scaler=scaler,
        metadata=metadata,
        columns_to_denormalize=[
            "predicted_demand"
        ],
        column_mapping={
            "predicted_demand":"demand"
        }
    )

    zone_forecast_df = build_zone_forecast(
        cell_forecast_df=cell_forecast_df,
        forecast_df=forecast_df,
        zone_mapping_df=zone_mapping_df
    )

    # ------------------------------------------------------------
    # Orders
    # ------------------------------------------------------------

    orders_df = generate_orders(
        h3_demand_df=h3_demand_df,
        current_shift_df=current_shift_df,
        zone_mapping_df=zone_mapping_df,
        products_df=products_df,
        max_quantity_per_item=MAX_QTY_PER_ITEM
    )

    orders_df = enrich_orders(
        new_orders_df=orders_df,
        products_df=products_df
    )

    orders_df = assign_dispatch_centers(
        new_orders_df=orders_df,
        dispatch_centers_df=dispatch_centres_df
    )

    orders_df = recycle_retained_orders(
        new_orders_df=orders_df,
        retained_orders_df=retained_orders_df,
    )

    print("Orders entering dispatch:", len(orders_df))
    print("Previously retained:", len(retained_orders_df))
    print("New orders:", len(orders_df))

    available_drivers_df = get_available_couriers(
        current_shift_df=current_shift_df
    )


    # ------------------------------------------------------------
    # Dispatch
    # ------------------------------------------------------------

    selected_df, retained_df = run_dispatch(
        orders_df=orders_df,
        zone_forecast_df=zone_forecast_df,
        dispatch_centres_df=dispatch_centres_df,
        available_drivers=len(available_drivers_df),
        available_vehicles=len(available_drivers_df),
        vehicle_capacity=VEHICLE_CAPACITY
    )

    print("Selected batches:", len(selected_df))
    print("Retained batches:", len(retained_df))

    print(
        "Selected orders:",
        selected_df["order_count"].sum()
    )

    print(
        "Retained orders:",
        retained_df["order_count"].sum()
    )

    retained_orders_df = extract_retained_orders(      
        retained_batch_df=retained_df,
    )

    # ------------------------------------------------------------
    # Zone Assignment
    # ------------------------------------------------------------

    

    assignment_df, assignment_summary = run_assignment(
        selected_batches_df=selected_df,
        available_drivers_df=available_drivers_df,
        driver_familiarity_df=familiarity_df,
        zone_mapping_df=zone_mapping_df
    )

    return {
        "zone_mapping_df": zone_mapping_df,
        "ahsi_history_df": history_df,
        "zone_forecast_df": zone_forecast_df,
        "orders_df": orders_df,
        "selected_df": selected_df,
        "retained_orders_df": retained_orders_df,
        "retained_df": retained_df,
        "assignment_df": assignment_df,
        "assignment_summary": assignment_summary
    }



def main(
    ds,
    shift,
    resources
):

    lade_hz_df = resources["lade_hz_df"]
    familiarity_df = resources["familiarity_df"]
    products_df = resources["products_df"]
    dispatch_centres_df = resources["dispatch_centres_df"]
    metadata = resources["metadata"]
    scaler = resources["scaler"]
    model = resources["model"]

    retained_orders_path = Path(
        DATA_DIR/"retained_orders.parquet"
    )
    
    if retained_orders_path.exists():
        retained_orders_df = pd.read_parquet(
            retained_orders_path
        )
    else:
        retained_orders_df = pd.DataFrame()

    retained_orders_df = deserialize_object_column(
        retained_orders_df,
        column="products",
    )

    results = run_pipeline(
        lade_hz_df = lade_hz_df,
        retained_orders_df=retained_orders_df,
        products_df=products_df,
        familiarity_df=familiarity_df,
        dispatch_centres_df=dispatch_centres_df,
        ds=ds,
        shift=shift,
        metadata=metadata,
        scaler=scaler,
        model=model
    )

    results["zone_mapping_df"].to_parquet(
        DATA_DIR/"zone_mapping.parquet",
        index=False,
    )

    results["ahsi_history_df"].to_parquet(
        DATA_DIR/"ahsi_algorithm.parquet",
        index=False,
    )

    results["zone_forecast_df"].to_parquet(
        DATA_DIR/"zone_forecast.parquet",
        index=False,
    )

    orders_to_save = serialize_object_column(
        results["orders_df"],
        column="products",
    )                                                       

    orders_to_save.to_parquet(
        DATA_DIR / "orders.parquet",
        index=False,
    )

    selected_batches_to_save = replace_objects_with_ids(
        results["selected_df"],
        source_column="orders",
        id_key="order_id",
        target_column="order_ids",
    )

    selected_batches_to_save.to_parquet(
        DATA_DIR / "selected_batches.parquet",
        index=False,
    )

    retained_batches_to_save = replace_objects_with_ids(
        results["retained_df"],
        source_column="orders",
        id_key="order_id",
        target_column="order_ids",
    )

    retained_batches_to_save.to_parquet(
        DATA_DIR / "retained_batches.parquet",
        index=False,
    )

    retained_orders_to_save = serialize_object_column(
        results["retained_orders_df"],
        column="products",
    )

    retained_orders_to_save.to_parquet(
        DATA_DIR/"retained_orders.parquet",
        index=False
    )

    results["assignment_df"].to_parquet(
        DATA_DIR/"zone_assignment.parquet",
        index=False
    )

    print(results["assignment_summary"])


if __name__ == "__main__":

    from dashboard.loader import load_static_resources

    resources = load_static_resources()

    main(
        default_date,
        default_shift,
        resources,
    )





    