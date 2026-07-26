"""
===============================================================
ZONE FAMILIARITY COMPUTATION
===============================================================

Converts Driver-H3 familiarity into Driver-Zone familiarity.

Workflow
--------
Driver × H3-8 Familiarity
            +
H3-8 → Final Cell Mapping
            ↓
Driver × Final Cell Familiarity

Current Aggregation
-------------------
Mean familiarity of all H3-8 cells belonging to the
same operational cell.

===============================================================
"""

import pandas as pd

from .config import FAMILIARITY_AGGREGATION


class ZoneFamiliarity:
    """Build Driver × Zone familiarity matrix."""

    def __init__(
        self,
        driver_familiarity: pd.DataFrame,
        cell_mapping: pd.DataFrame
    ):

        self.driver_familiarity = driver_familiarity.copy()
        self.cell_mapping = cell_mapping.copy()

    # ==========================================================
    # Public API
    # ==========================================================

    def build(self) -> pd.DataFrame:
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

        df = self._merge_mapping()

        df = self._aggregate(df)

        return df.sort_values(
            ["courier_id", "final_cell"]
        ).reset_index(drop=True)

    # ==========================================================
    # Merge Mapping
    # ==========================================================

    def _merge_mapping(self) -> pd.DataFrame:

        df = self.driver_familiarity.merge(
            self.cell_mapping,
            on="h3_cell_8",
            how="inner"
        )

        return df

    # ==========================================================
    # Aggregate Familiarity
    # ==========================================================

    def _aggregate(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:

        method = FAMILIARITY_AGGREGATION.lower()

        if method == "mean":

            return (
                df.groupby(
                    ["courier_id", "final_cell"],
                    as_index=False
                )["familiarity_score"]
                .mean()
            )

        elif method == "median":

            return (
                df.groupby(
                    ["courier_id", "final_cell"],
                    as_index=False
                )["familiarity_score"]
                .median()
            )

        elif method == "max":

            return (
                df.groupby(
                    ["courier_id", "final_cell"],
                    as_index=False
                )["familiarity_score"]
                .max()
            )

        else:

            raise ValueError(
                f"Unknown aggregation method: "
                f"{FAMILIARITY_AGGREGATION}"
            )

    # ==========================================================
    # Build Driver × Zone Matrix
    # ==========================================================

    @staticmethod
    def build_matrix(
        zone_familiarity: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Converts long format into Driver × Zone matrix.

        Returns
        -------
        Index   : courier_id
        Columns : final_cell
        Values  : familiarity_score
        """

        matrix = zone_familiarity.pivot_table(
            index="courier_id",
            columns="final_cell",
            values="familiarity_score",
            fill_value=0.0
        )

        matrix = matrix.sort_index(axis=0)
        matrix = matrix.sort_index(axis=1)

        return matrix