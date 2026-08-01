import pandas as pd
from scipy.optimize import linear_sum_assignment


def hungarian_assignment(
    familiarity_matrix: pd.DataFrame
) -> pd.DataFrame:
    """
    Assign operational zones to couriers using the Hungarian Algorithm.

    Parameters
    ----------
    familiarity_matrix : pd.DataFrame
        Index   : courier_id
        Columns : zone_id
        Values  : familiarity_score

    Returns
    -------
    assignment_df : pd.DataFrame

        courier_id
        zone_id
        familiarity_score
    """

    if familiarity_matrix.empty:
        return pd.DataFrame(
            columns=[
                "courier_id",
                "zone_id",
                "familiarity_score"
            ]
        )

    familiarity = familiarity_matrix.to_numpy(dtype=float)

    max_familiarity = familiarity.max()

    cost_matrix = max_familiarity - familiarity

    row_idx, col_idx = linear_sum_assignment(cost_matrix)

    assignments = pd.DataFrame({
        "courier_id": familiarity_matrix.index[row_idx],
        "zone_id": familiarity_matrix.columns[col_idx],
        "familiarity_score": familiarity_matrix.to_numpy()[row_idx, col_idx]
    })

    return assignments.sort_values(
        "zone_id"
    ).reset_index(drop=True)



def summarize_assignments(
    assignment_df: pd.DataFrame
) -> dict:
    """
    Compute assignment statistics.

    Parameters
    ----------
    assignment_df

        courier_id
        zone_id
        familiarity_score

    Returns
    -------
    dict
    """

    if assignment_df.empty:
        return {
            "assigned_couriers": 0,
            "assigned_zones": 0,
            "mean_familiarity": 0.0,
            "min_familiarity": 0.0,
            "max_familiarity": 0.0
        }

    return {
        "assigned_couriers":
            assignment_df["courier_id"].nunique(),

        "assigned_zones":
            assignment_df["zone_id"].nunique(),

        "mean_familiarity":
            float(
                assignment_df["familiarity_score"].mean()
            ),

        "min_familiarity":
            float(
                assignment_df["familiarity_score"].min()
            ),

        "max_familiarity":
            float(
                assignment_df["familiarity_score"].max()
            )
    }