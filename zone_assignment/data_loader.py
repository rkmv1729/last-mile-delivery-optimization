"""
===============================================================
ZONE ASSIGNMENT DATA LOADER
===============================================================

Loads all datasets required by the Zone Assignment layer.

Responsibilities
----------------
1. Load Driver Familiarity table
2. Load AHSI Cell Mapping
3. Accept Batch Orders from Dispatch Engine
4. Accept Available Drivers from Dispatch Engine
5. Perform basic validation

No processing or aggregation is performed here.

===============================================================
"""

import pandas as pd

from .config import (
    PROCESSED_FOLDER,
    DRIVER_FAMILIARITY_FILE,
    CELL_MAPPING_FILE,
)


class ZoneAssignmentDataLoader:
    """Loads datasets required for Zone Assignment."""

    def __init__(self): 

        pass

    # ==========================================================
    # Driver Familiarity
    # ==========================================================

    def load_driver_familiarity(self) -> pd.DataFrame:

        filepath = PROCESSED_FOLDER / DRIVER_FAMILIARITY_FILE

        if not filepath.exists():
            raise FileNotFoundError(
                f"Driver familiarity file not found:\n{filepath}"
            )

        df = pd.read_parquet(filepath)  

        required_columns = [
            "driver_id",
            "h3_cell_8",
            "familiarity_score"
        ]

        self._validate_columns(df, required_columns)

        return df

    # ==========================================================
    # Cell Mapping
    # ==========================================================

    def load_cell_mapping(self) -> pd.DataFrame:

        filepath = PROCESSED_FOLDER / CELL_MAPPING_FILE

        if not filepath.exists():
            raise FileNotFoundError(
                f"Cell mapping file not found:\n{filepath}"
            )

        df = pd.read_parquet(filepath)

        required_columns = [
            "h3_cell_8",
            "zone_id"
        ]

        self._validate_columns(df, required_columns)

        return df

    # ==========================================================
    # Batch Orders
    # ==========================================================

    @staticmethod
    def load_batch_orders(selected_batches: pd.DataFrame) -> pd.DataFrame:
        """
        Receives current dispatch batch from Dispatch Engine.
        """

        required_columns = [
            "batch_id",
            "zone_id"
        ]

        ZoneAssignmentDataLoader._validate_columns(
            selected_batches,
            required_columns
        )

        return selected_batches.copy()

    # ==========================================================
    # Available Drivers
    # ==========================================================

    @staticmethod
    def load_available_drivers(
        available_drivers: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Receives currently available drivers from Dispatch Engine.
        """

        required_columns = [
            "driver_id"
        ]

        ZoneAssignmentDataLoader._validate_columns(
            available_drivers,
            required_columns
        )

        return available_drivers.copy()

    # ==========================================================
    # Validation
    # ==========================================================

    @staticmethod
    def _validate_columns(
        df: pd.DataFrame,
        required_columns: list
    ) -> None:

        missing = set(required_columns) - set(df.columns)

        if missing:
            raise ValueError(
                f"Missing required columns: {sorted(missing)}"
            )