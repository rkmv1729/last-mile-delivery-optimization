"""
===============================================================
ZONE ASSIGNMENT ENGINE
===============================================================

Orchestrates the complete Zone Assignment workflow.

Pipeline
--------
Load Inputs
      ↓
Build Zone Familiarity
      ↓
Build Driver × Zone Matrix
      ↓
Optimize Assignments
      ↓
Validate
      ↓
Return Assignments

===============================================================
"""

from .familiarity import ZoneFamiliarity
from .optimizer import ZoneAssignmentOptimizer
from .validator import ZoneAssignmentValidator


class ZoneAssignmentEngine:
    """
    Main orchestration engine for Zone Assignment.
    """

    def __init__( 
        self,
        driver_familiarity, 
        cell_mapping,
        batch_orders,
        available_drivers
    ): 

        self.driver_familiarity = driver_familiarity
        self.cell_mapping = cell_mapping
        self.batch_orders = batch_orders
        self.available_drivers = available_drivers   

    # ==========================================================
    # Run Complete Assignment
    # ==========================================================

    def run(self):
        """
        Executes the complete Zone Assignment pipeline.

        Returns
        -------
        assignments : DataFrame
        """

        # ------------------------------------------------------
        # Build Zone Familiarity
        # ------------------------------------------------------

        familiarity_builder = ZoneFamiliarity(
            self.driver_familiarity,
            self.cell_mapping
        )

        zone_familiarity = familiarity_builder.build()

        # ------------------------------------------------------
        # Keep only available drivers
        # ------------------------------------------------------

        zone_familiarity = zone_familiarity[
            zone_familiarity["courier_id"].isin(
                self.available_drivers["courier_id"]
            )
        ]

        # ------------------------------------------------------
        # Keep only operational cells present in current batch
        # ------------------------------------------------------

        active_zones = (
            self.batch_orders["final_cell"]
            .drop_duplicates()
            .tolist()
        )

        zone_familiarity = zone_familiarity[
            zone_familiarity["final_cell"].isin(active_zones)
        ]

        # ------------------------------------------------------
        # Build Familiarity Matrix
        # ------------------------------------------------------

        familiarity_matrix = ZoneFamiliarity.build_matrix(
            zone_familiarity
        )

        # ------------------------------------------------------
        # Optimize
        # ------------------------------------------------------

        optimizer = ZoneAssignmentOptimizer(
            familiarity_matrix
        )

        assignments = optimizer.optimize()

        # ------------------------------------------------------
        # Validate
        # ------------------------------------------------------

        validator = ZoneAssignmentValidator(
            assignments,
            self.available_drivers
        )

        validator.validate()

        return assignments

    # ==========================================================
    # Run + Summary
    # ==========================================================

    def run_with_summary(self):
        """
        Executes assignment and returns summary statistics.
        """

        assignments = self.run()

        summary = ZoneAssignmentOptimizer.summarize(
            assignments
        )

        return assignments, summary