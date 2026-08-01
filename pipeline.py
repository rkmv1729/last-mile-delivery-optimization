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

ds = pd.Timestamp("1900-07-24")
shift = "Afternoon"


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
    model
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

    zone_mapping_df = run_ahsi(
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

    print(cell_forecast_df.columns.to_list())

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

    print(type(orders_df.loc[0, "products"]))
    print(orders_df.loc[0, "products"])

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

    # ------------------------------------------------------------
    # Dispatch
    # ------------------------------------------------------------

    selected_df, retained_df = run_dispatch(
        orders_df=orders_df,
        zone_forecast_df=zone_forecast_df,
        dispatch_centres_df=dispatch_centres_df,
        available_drivers=AVAILABLE_DRIVERS,
        available_vehicles=AVAILABLE_VEHICLES,
        vehicle_capacity=VEHICLE_CAPACITY
    )

    retained_orders_df = extract_retained_orders(      
        retained_batch_df=retained_df,
    )

    # ------------------------------------------------------------
    # Zone Assignment
    # ------------------------------------------------------------

    available_drivers_df = get_available_couriers(
        current_shift_df=current_shift_df
    )

    assignment_df, assignment_summary = run_assignment(
        selected_batches_df=selected_df,
        available_drivers_df=available_drivers_df,
        driver_familiarity_df=familiarity_df,
        zone_mapping_df=zone_mapping_df
    )

    return {
        "zone_mapping_df": zone_mapping_df,
        "zone_forecast_df": zone_forecast_df,
        "orders_df": orders_df,
        "selected_df": selected_df,
        "retained_orders_df": retained_orders_df,
        "assignment_df": assignment_df,
        "assignment_summary": assignment_summary
    }



def main():

    lade_hz_df = pd.read_parquet(
        DATA_DIR/"lade_hangzhou.parquet"
    )

    familiarity_df = pd.read_parquet(
        DATA_DIR/"driver_h3_cell_8_familiarity.parquet"
    )

    products_df = pd.read_csv(
        DATA_DIR/"products.csv"
    )

    dispatch_centres_df = pd.read_csv(
        DATA_DIR/"dispatch_centres.csv"
    )

    metadata = load_metadata(
        metadata_path=DATA_DIR/"models"/"model_metadata.json"
    )

    scaler = load_scaler(
        scaler_path=DATA_DIR/"models"/"demand_scaler.pkl"
    )

    model = load_forecast_model(
        model_path=DATA_DIR/"models"/"demand_lstm.pth",
        metadata=metadata
    )

    retained_orders_path = Path(
            DATA_DIR/"retained_orders.parquet"
        )
    
    if retained_orders_path.exists():
        retained_orders_df = pd.read_parquet(
            retained_orders_path
        )
    else:
        retained_orders_df = pd.DataFrame()

    

    # TODO: create ds, shift to pass into run_pipeline

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
    main()





    