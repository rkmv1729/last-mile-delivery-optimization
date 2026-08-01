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

from zone_assignment.helpers import prepare_inputs

from zone_assignment.algorithms import (
    hungarian_assignment,
    summarize_assignments
)


def run_assignment(
    selected_batches_df,
    available_drivers_df,
    driver_familiarity_df,
    zone_mapping_df,
    aggregation="mean"
):
    """
    Execute the complete zone assignment pipeline.
    """

    familiarity_matrix = prepare_inputs(
        selected_batches_df=selected_batches_df,
        available_drivers_df=available_drivers_df,
        driver_familiarity_df=driver_familiarity_df,
        zone_mapping_df=zone_mapping_df,
        aggregation=aggregation
    )

    assignment_df = hungarian_assignment(
        familiarity_matrix
    )

    summary = summarize_assignments(
        assignment_df
    )

    return assignment_df, summary

