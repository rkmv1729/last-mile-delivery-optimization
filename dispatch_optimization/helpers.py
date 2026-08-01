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
from config import (
    BUS_WEIGHTS,
    EPS_ALPHA,
    RETENTION_PENALTY_INCREMENT,
    MAX_PENALTY
)



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
        + (1-EPS_ALPHA) * retention_penalty
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
    batch_load: float,
    vehicle_capacity: float,
) -> float:
    """
    Computes percentage utilization of a vehicle.
    """

    if vehicle_capacity <= 0:
        return 0.0

    return min(batch_load / vehicle_capacity, 1.0)


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



