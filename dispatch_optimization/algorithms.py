import numpy as np


"""
algorithms.py

Algorithm 5
------------
EPS-Based Batch Formation

Algorithm 6
------------
BUS-Based Dispatch Optimization
"""

import pandas as pd

from helpers import (
    compute_retention_penalty,
    compute_eps,
    compute_batch_priority,
    compute_vehicle_utilization,
    compute_storage_pressure,
    compute_forecast_opportunity,
    compute_bus_score,
)

from pulp import (
    LpProblem,
    LpVariable,
    LpMaximize,
    lpSum,
    LpBinary,
    PULP_CBC_CMD,
)

VEHICLE_CAPACITY = 250

def form_batches(
    orders_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Algorithm 5:
    EPS-Based Batch Formation
    """

    orders_df = orders_df.copy()


    # --------------------------------------------------
    # Step 1 : Compute Order Priority
    # --------------------------------------------------

    order_priorities = []
    total_loads = []
    total_quantities = []

    for order in orders_df.itertuples():

        products = order.products

        total_quantity = sum(
            p["quantity"] for p in products
        )

        total_load = sum(
            p["quantity"] * p["load_factor"]
            for p in products
        )

        if total_load == 0:
            priority = 0.0

        else:
            priority = sum(
                (
                    (p["quantity"] * p["load_factor"]) / total_load
                )
                * p["priority_score"]
                for p in products
            )

        order_priorities.append(priority)
        total_quantities.append(total_quantity)
        total_loads.append(total_load)

    orders_df["total_quantity"] = total_quantities
    orders_df["order_priority"] = order_priorities
    orders_df["total_load"] = total_loads

    # --------------------------------------------------
    # Step 2 : Retention Penalty
    # --------------------------------------------------

    orders_df["retention_penalty"] = (
        orders_df["retention_cycles"]
        .apply(compute_retention_penalty)
    )

    # --------------------------------------------------
    # Step 3 : EPS
    # --------------------------------------------------

    orders_df["eps"] = orders_df.apply(
        lambda row: compute_eps(
            row.order_priority,
            row.retention_penalty,
        ),
        axis=1,
    )

    # --------------------------------------------------
    # Step 4 : Sort Orders
    # --------------------------------------------------

    orders_df = orders_df.sort_values(
        "eps",
        ascending=False,
    )

    # --------------------------------------------------
    # Step 5 : Greedy Batch Formation
    # --------------------------------------------------

    batches = []
    batch_id = 1

    grouped = orders_df.groupby(
        ["dispatch_center_id", "zone_id"]
    )

    for (
        dispatch_center_id,
        zone_id,
    ), group in grouped:

        current_orders = []
        current_load = 0.0
        current_quantity = 0

        for order in group.itertuples():

            if (
                current_load + order.total_load
                <= VEHICLE_CAPACITY
            ):

                current_orders.append(order)

                current_load += order.total_load
                current_quantity += order.total_quantity

            else:

                batches.append({
                    "batch_id": batch_id,
                    "dispatch_center_id": dispatch_center_id,
                    "zone_id": zone_id,
                    "orders": current_orders,
                    "order_count": len(current_orders),
                    "total_load": current_load,
                    "total_quantity": current_quantity,

                    "batch_priority": compute_batch_priority(
                        [o.order_priority for o in current_orders]
                    ),

                    "retention_penalty": max(
                        [o.retention_penalty for o in current_orders],
                        default=0.0,
                    ),

                    "created_time": current_orders[0].accept_gps_time,
                })

                batch_id += 1

                current_orders = [order]
                current_quantity = order.total_quantity

        if current_orders:

            batches.append({
                "batch_id": batch_id,
                "dispatch_center_id": dispatch_center_id,
                "zone_id": zone_id,
                "orders": current_orders,
                "order_count": len(current_orders),
                "total_load": current_load,
                "total_quantity": current_quantity,

                "batch_priority": compute_batch_priority(
                    [o.order_priority for o in current_orders]
                ),

                "retention_penalty": max(
                    [o.retention_penalty for o in current_orders],
                    default=0.0,
                ),

                "created_time": current_orders[0].accept_gps_time,
            })

            batch_id += 1

    return pd.DataFrame(batches)


# =====================================================

def dispatch_batches(
    batch_df,
    forecast_df,
    available_drivers: int,
    available_vehicles: int,
    dispatch_centres_df
):
    """
    Algorithm 6:
    BUS-Based Dispatch Optimization
    """

    dispatch_records = []

    for batch in batch_df.itertuples():

        # ------------------------------------------
        # Step 1 : Batch Priority
        # ------------------------------------------

        batch_priority = batch.batch_priority

        # ------------------------------------------
        # Step 2 : Vehicle Utilization
        # ------------------------------------------

        vehicle_utilization = compute_vehicle_utilization(
            batch.total_load,
            VEHICLE_CAPACITY,
        )

        # ------------------------------------------
        # Step 3 : Storage Pressure
        # ------------------------------------------

        dispatch_center = dispatch_centres_df.loc[
            dispatch_centres_df["dispatch_center_id"]
            == batch.dispatch_center_id
        ].iloc[0]

        storage_pressure = compute_storage_pressure(
            dispatch_center.current_storage,
            dispatch_center.storage_capacity,
        )

        # ------------------------------------------
        # Step 4 : Retention Penalty
        # ------------------------------------------

        retention_penalty = batch.retention_penalty

        # ------------------------------------------
        # Step 5 : Forecast Opportunity
        # ------------------------------------------

        forecast_opportunity = compute_forecast_opportunity(
            batch.zone_id,
            forecast_df,
        )

        # ------------------------------------------
        # Step 6 : Batch Utility Score (BUS)
        # ------------------------------------------

        bus_score = compute_bus_score(
            batch_priority=batch_priority,
            vehicle_utilization=vehicle_utilization,
            storage_pressure=storage_pressure,
            retention_penalty=retention_penalty,
            forecast_opportunity=forecast_opportunity,
        )

        dispatch_records.append(
            {
                "batch_id": batch.batch_id,
                "dispatch_center_id": batch.dispatch_center_id,
                "zone_id": batch.zone_id,
                "bus_score": bus_score,
                "order_count": batch.order_count,
                "total_quantity": batch.total_quantity,
                "total_load": batch.total_load,
                "batch_priority": batch_priority,
                "vehicle_utilization": vehicle_utilization,
                "storage_pressure": storage_pressure,
                "retention_penalty": retention_penalty,
                "forecast_opportunity": forecast_opportunity,
            }
        )

    
    optimization_df = pd.DataFrame(dispatch_records)

    # --------------------------------------------------
    # Step 7 : Binary Integer Linear Programming
    # --------------------------------------------------

    problem = LpProblem(
        "BUS_Dispatch",
        LpMaximize,
    )

    decision = {
        row.batch_id: LpVariable(
            f"x_{row.batch_id}",
            cat=LpBinary,
        )
        for row in optimization_df.itertuples()
    }

    problem += lpSum(
        row.bus_score * decision[row.batch_id]
        for row in optimization_df.itertuples()
    )

    problem += (
        lpSum(decision.values())
        <= available_vehicles
    )

    problem += (
        lpSum(decision.values())
        <= available_drivers
    )

    problem.solve(
        PULP_CBC_CMD(msg=False)
    )

    # --------------------------------------------------
    # Step 8 : Extract Optimal Decisions
    # --------------------------------------------------

    dispatch_df = optimization_df.copy()

    dispatch_df["decision"] = dispatch_df["batch_id"].apply(
        lambda batch_id: (
            "DISPATCH"
            if decision[batch_id].value() == 1
            else "RETAIN"
        )
    )

    dispatch_df.to_csv("dispatch.csv")

    selected_batch_ids = dispatch_df.loc[
        dispatch_df["decision"] == "DISPATCH",
        "batch_id",
    ]

    retained_batch_ids = dispatch_df.loc[
        dispatch_df["decision"] == "RETAIN",
        "batch_id",
    ]

    selected_batch_df = batch_df[
        batch_df["batch_id"].isin(selected_batch_ids)
    ].reset_index(drop=True)

    retained_batch_df = batch_df[
        batch_df["batch_id"].isin(retained_batch_ids)
    ].reset_index(drop=True)

    return (
        selected_batch_df,
        retained_batch_df,
    )



def extract_retained_orders(
    retained_batch_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Extracts retained orders from retained batches.

    Increments the retention cycle of every retained order
    before returning them for the next dispatch cycle.
    """
    

    retained_orders = []

    for batch in retained_batch_df.itertuples():

        for order in batch.orders:

            order_dict = order._asdict()

            order_dict["retention_cycles"] += 1

            retained_orders.append(order_dict)

    return pd.DataFrame(retained_orders)