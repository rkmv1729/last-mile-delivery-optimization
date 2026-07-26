"""
===============================================================
ZONE ASSIGNMENT
===============================================================

Public interface for the Zone Assignment layer.

This module is invoked by the Dispatch Engine whenever a batch
is ready for processing.

Workflow
--------
Dispatch Engine
      ↓
Zone Assignment
      ↓
Driver ↔ Operational Cell Assignments
      ↓
Dispatch Engine

===============================================================
"""

from pathlib import Path

from .data_loader import ZoneAssignmentDataLoader
from .assignment_engine import ZoneAssignmentEngine


class ZoneAssignment:
    """
    Public API for the Zone Assignment layer.
    """

    def __init__(self):

        self.loader = ZoneAssignmentDataLoader()

        # ------------------------------------------------------
        # Static datasets (loaded once)
        # ------------------------------------------------------

        self.driver_familiarity = (
            self.loader.load_driver_familiarity()
        )

        self.cell_mapping = (
            self.loader.load_cell_mapping()
        )

    # ==========================================================
    # Assign Drivers
    # ==========================================================

    def assign(
        self,
        batch_orders,
        available_drivers
    ):
        """
        Assign one driver to each operational cell.

        Parameters
        ----------
        batch_orders : DataFrame
            Current dispatch batch.

        available_drivers : DataFrame
            Drivers currently available.

        Returns
        -------
        assignments : DataFrame
        """

        batch_orders = self.loader.load_batch_orders(
            batch_orders
        )

        available_drivers = (
            self.loader.load_available_drivers(
                available_drivers
            )
        )

        engine = ZoneAssignmentEngine(
            driver_familiarity=self.driver_familiarity,
            cell_mapping=self.cell_mapping,
            batch_orders=batch_orders,
            available_drivers=available_drivers
        )

        assignments = engine.run()

        return assignments

    # ==========================================================
    # Assign + Summary
    # ==========================================================

    def assign_with_summary(
        self,
        batch_orders,
        available_drivers
    ):
        """
        Executes assignment and returns summary statistics.
        """

        batch_orders = self.loader.load_batch_orders(
            batch_orders
        )

        available_drivers = (
            self.loader.load_available_drivers(
                available_drivers
            )
        )

        engine = ZoneAssignmentEngine(
            driver_familiarity=self.driver_familiarity,
            cell_mapping=self.cell_mapping,
            batch_orders=batch_orders,
            available_drivers=available_drivers
        )

        assignments, summary = engine.run_with_summary()

        return assignments, summary

    # ==========================================================
    # Helpers
    # ==========================================================

    def log(self, message: str):
        """
        Add an entry to simulation history.
        """

        self.event_history.append(message)