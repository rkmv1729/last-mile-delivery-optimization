"""
validator.py

Validation utilities for the Adaptive H3 Spatial Indexing (AHSI) layer.
"""

import pandas as pd

from config import (
    H3_RESOLUTION,
    CHILD_RESOLUTION
)

# TODO : validation already checks required columns and dtypes, so safely remove
# them from other functions if any
# TODO : update requried cols if you change your merge-split strategy

def validate_input(h3_demand: pd.DataFrame) -> None:
    """
    Validate the input H3 demand table.

    Checks
    ------
    - Required columns exist
    - No missing values
    - No duplicate H3 cells
    - Orders are numeric
    - Orders are non-negative
    """

    required_columns = {"h3_cell_7", "orders_h3_7"}

    missing = required_columns - set(h3_demand.columns)
    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    if h3_demand.isnull().any().any():
        raise ValueError("Input contains missing values.")

    if h3_demand.duplicated(
        subset=["h3_cell_7", "h3_cell_8"]
        ).any():
        raise ValueError("Duplicate H3 cells found.")

    if not pd.api.types.is_numeric_dtype(h3_demand["orders_h3_7"]):
        raise ValueError("'orders_h3_7' must be numeric.")

    if (h3_demand["orders_h3_7"] < 0).any():
        raise ValueError("'orders_h3_7' cannot contain negative values.")


def validate_output(zone_mapping: pd.DataFrame) -> None:
    """
    Validate the generated zone mapping.

    Checks
    ------
    - Required columns exist
    - No missing values
    - Every H3 cell has exactly one zone assignment
    - Zone IDs are not empty
    """

    required_columns = {
        "zone_id",
        "cell_id",
        "resolution",
        "parent_cell"
    }

    missing = required_columns - set(zone_mapping.columns)
    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    if zone_mapping.isnull().any().any():
        raise ValueError("Output contains missing values.")

    if zone_mapping.duplicated(
        subset=["cell_id", "resolution"]
    ).any():
        raise ValueError(
            "Duplicate operational cells found."
        )

    if (zone_mapping["zone_id"].astype(str).str.strip() == "").any():
        raise ValueError("Empty zone IDs found.")

    # Resolution must be valid
    if not zone_mapping["resolution"].isin(
        [H3_RESOLUTION,CHILD_RESOLUTION]).all():
        raise ValueError("Invalid H3 resolution found.")