"""
===============================================================
ZONE ASSIGNMENT OPTIMIZER
===============================================================

Solves the Driver ↔ Zone assignment problem.

Objective
---------
Assign exactly one available driver to each operational zone
while maximizing the overall familiarity score.

Optimization
------------
Maximum Weight Bipartite Matching
(Hungarian Algorithm)

===============================================================
"""

import numpy as np
import pandas as pd

from scipy.optimize import linear_sum_assignment


class ZoneAssignmentOptimizer:
    """
    Solves Driver ↔ Zone assignment using the Hungarian Algorithm.
    """

    def __init__(self, familiarity_matrix: pd.DataFrame):

        self.matrix = familiarity_matrix.copy()

    # ==========================================================
    # Public API
    # ==========================================================

    def optimize(self) -> pd.DataFrame:
        """
        Returns
        -------
        DataFrame

        Columns
        -------
        courier_id
        final_cell
        familiarity_score
        """

        if self.matrix.empty:
            return pd.DataFrame(
                columns=[
                    "courier_id",
                    "final_cell",
                    "familiarity_score"
                ]
            )

        drivers = self.matrix.index.to_numpy()
        zones = self.matrix.columns.to_numpy()

        familiarity = self.matrix.to_numpy(dtype=float)

        # ------------------------------------------------------
        # Hungarian minimizes cost.
        # Convert familiarity -> cost.
        # ------------------------------------------------------

        max_score = familiarity.max()

        cost_matrix = max_score - familiarity

        row_ind, col_ind = linear_sum_assignment(cost_matrix)

        assignments = pd.DataFrame({
            "courier_id": drivers[row_ind],
            "final_cell": zones[col_ind],
            "familiarity_score": familiarity[row_ind, col_ind]
        })

        assignments = assignments.sort_values(
            "final_cell"
        ).reset_index(drop=True)

        return assignments

    # ==========================================================
    # Summary
    # ==========================================================

    @staticmethod
    def summarize(assignments: pd.DataFrame) -> dict:

        if assignments.empty:

            return {
                "assigned_drivers": 0,
                "assigned_zones": 0,
                "mean_familiarity": 0.0,
                "min_familiarity": 0.0,
                "max_familiarity": 0.0
            }

        return {
            "assigned_drivers": assignments["courier_id"].nunique(),
            "assigned_zones": assignments["final_cell"].nunique(),
            "mean_familiarity": round(
                assignments["familiarity_score"].mean(),
                4
            ),
            "min_familiarity": round(
                assignments["familiarity_score"].min(),
                4
            ),
            "max_familiarity": round(
                assignments["familiarity_score"].max(),
                4
            )
        }