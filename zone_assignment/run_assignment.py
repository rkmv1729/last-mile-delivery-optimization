"""
Zone Assignment Layer

Inputs
------
batch_df
    batch_id
    zone_id

available_couriers_df
    courier_id

driver_familiarity_df
    courier_id
    h3_cell_8
    familiarity_score

cell_mapping_df
    h3_cell_8
    zone_id

Outputs
-------
assignment_df
    courier_id
    zone_id
    familiarity_score

summary
    Assignment statistics
"""

from helpers import prepare_inputs
from algorithms import (
    hungarian_assignment,
    summarize_assignments
)


def run_assignment(
    batch_df,
    available_drivers_df,
    driver_familiarity_df,
    cell_mapping_df,
    aggregation="mean"
):
    """
    Execute the complete zone assignment pipeline.
    """

    familiarity_matrix = prepare_inputs(
        batch_df=batch_df,
        available_drivers_df=available_drivers_df,
        driver_familiarity_df=driver_familiarity_df,
        cell_mapping_df=cell_mapping_df,
        aggregation=aggregation
    )

    assignment_df = hungarian_assignment(
        familiarity_matrix
    )

    summary = summarize_assignments(
        assignment_df
    )

    return assignment_df, summary

if __name__ == "__main__":

    import pandas as pd

    # ------------------------------------------------------------------
    # Input Files
    # ------------------------------------------------------------------

    batch_df = pd.read_parquet(
        "inputs/batch_df.parquet"
    )

    available_couriers_df = pd.read_parquet(
        "inputs/available_drivers.parquet"
    )

    courier_familiarity_df = pd.read_parquet(
        "inputs/driver_cell_familiarity.parquet"
    )

    cell_mapping_df = pd.read_parquet(
        "inputs/zone_mapping.parquet"
    )

    # ------------------------------------------------------------------
    # Run Zone Assignment
    # ------------------------------------------------------------------

    assignment_df, summary = run_assignment(
        batch_df=batch_df,
        available_drivers_df=available_couriers_df,
        driver_familiarity_df=courier_familiarity_df,
        cell_mapping_df=cell_mapping_df
    )

    # ------------------------------------------------------------------
    # Save Outputs
    # ------------------------------------------------------------------

    assignment_df.to_parquet(
        "outputs/zone_assignments.parquet",
        index=False
    )

    # ------------------------------------------------------------------
    # Display Summary
    # ------------------------------------------------------------------

    print("\n========== Zone Assignment ==========")

    print(f"Assigned Couriers : {summary['assigned_couriers']}")
    print(f"Assigned Zones    : {summary['assigned_zones']}")
    print(f"Mean Familiarity  : {summary['mean_familiarity']:.3f}")
    print(f"Min Familiarity   : {summary['min_familiarity']:.3f}")
    print(f"Max Familiarity   : {summary['max_familiarity']:.3f}")

    print("\nSample Assignments\n")
    print(assignment_df.head())