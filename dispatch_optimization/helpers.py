"""
helpers.py

Reusable helper functions for the Dispatch Layer.

Algorithm 5
-----------
- Retention Penalty
- Effective Priority Score (EPS)

Algorithm 6
-----------
- Batch Priority
- Vehicle Utilization
- Storage Pressure
- Forecast Opportunity
- Batch Utility Score (BUS)
"""

import numpy as np
import pandas as pd
from math import radians, sin, cos, sqrt, atan2

BUS_WEIGHTS = {
    "priority_score": 0.35,
    "vehicle_utilization": 0.20,
    "storage_pressure": 0.15,
    "retention_penalty": 0.20,
    "forecast_opportunity": 0.10,
}

EPS_ALPHA = 0.7
EPS_BETA = 0.3
MAX_PENALTY = 0.4
RETENTION_PENALTY_INCREMENT = 0.1


# ============================================================
# Algorithm 5 : EPS-Based Batch Formation
# ============================================================

def compute_retention_penalty(
    retention_cycles: int,
) -> float:
    """
    Computes retention penalty based on the number of
    previous dispatch retentions.
    """
    penalty = retention_cycles * RETENTION_PENALTY_INCREMENT
    return min(penalty, MAX_PENALTY)


def compute_eps(
    priority_score: float,
    retention_penalty: float,
) -> float:
    """
    Computes Effective Priority Score (EPS).
    Higher EPS products are batched first.
    """
    return (
        EPS_ALPHA * priority_score
        + EPS_BETA * retention_penalty
    )


# ============================================================
# Algorithm 6 : BUS Dispatch Optimization
# ============================================================

def compute_batch_priority(
    priority_scores,
):
    """
    Computes batch priority from the products
    contained within a batch.
    """
    if len(priority_scores) == 0:
        return 0.0

    return float(np.mean(priority_scores))


def compute_vehicle_utilization(
    batch_quantity: float,
    vehicle_capacity: float,
) -> float:
    """
    Computes percentage utilization of a vehicle.
    """

    if vehicle_capacity <= 0:
        return 0.0

    return min(batch_quantity / vehicle_capacity, 1.0)


def compute_storage_pressure(
    current_storage: float,
    storage_capacity: float,
) -> float:
    """
    Computes dispatch center storage pressure.
    """

    if storage_capacity <= 0:
        return 0.0

    return min(current_storage / storage_capacity, 1.0)


def compute_forecast_opportunity(
    zone_id,
    forecast_df,
):
    """
    Returns forecast opportunity score
    for a destination zone.
    """

    row = forecast_df.loc[
        forecast_df["zone_id"] == zone_id
    ]

    if row.empty:
        return 0.0

    return float(row.iloc[0]["forecast_opportunity"])


# ===================================================

def compute_bus_score(
    batch_priority: float,
    vehicle_utilization: float,
    storage_pressure: float,
    retention_penalty: float,
    forecast_opportunity: float,
) -> float:
    """
    Computes Batch Utility Score (BUS).
    """

    return (
        BUS_WEIGHTS["priority_score"] * batch_priority
        + BUS_WEIGHTS["vehicle_utilization"] * vehicle_utilization
        + BUS_WEIGHTS["storage_pressure"] * storage_pressure
        - BUS_WEIGHTS["retention_penalty"] * retention_penalty
        + BUS_WEIGHTS["forecast_opportunity"] * forecast_opportunity
    )


# ===================================================

def recycle_retained_orders(
    new_orders_df: pd.DataFrame,
    retained_orders_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Merges retained orders from the previous dispatch cycle
    with newly arrived orders.
    """

    if retained_orders_df.empty:
        return new_orders_df.copy()

    return pd.concat(
        [
            retained_orders_df,
            new_orders_df,
        ],
        ignore_index=True,
    )

# ===================================================

def enrich_orders(
    new_orders_df,
    products_df,
):
    """
    Add priority_score and load_factor to each product
    inside every order.
    """

    product_lookup = (
        products_df
        .set_index("product_id")
        [
            [
                "priority_score",
                "load_factor",
            ]
        ]
        .to_dict("index")
    )

    def enrich(products):

        enriched = []

        for product in products:

            meta = product_lookup[
                product["product_id"]
            ]

            enriched.append(
                {
                    **product,
                    "priority_score": meta[
                        "priority_score"
                    ],
                    "load_factor": meta[
                        "load_factor"
                    ],
                }
            )

        return enriched

    new_orders_df = new_orders_df.copy()

    new_orders_df["products"] = (
        new_orders_df["products"]
        .apply(enrich)
    )

    return new_orders_df



def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1))
        * cos(radians(lat2))
        * sin(dlon / 2) ** 2
    )

    return 2 * R * atan2(sqrt(a), sqrt(1 - a))



def assign_dispatch_centers(
    orders_df,
    dispatch_centers_df,
):
    centers = dispatch_centers_df.to_dict("records")

    dispatch_ids = []

    for order in orders_df.itertuples():

        nearest = min(
            centers,
            key=lambda dc: haversine(
                order.delivery_gps_lat,
                order.delivery_gps_lng,
                dc["gps_lat"],
                dc["gps_lng"],
            ),
        )

        dispatch_ids.append(
            nearest["dispatch_center_id"]
        )

    orders_df = orders_df.copy()
    orders_df["dispatch_center_id"] = dispatch_ids

    return orders_df