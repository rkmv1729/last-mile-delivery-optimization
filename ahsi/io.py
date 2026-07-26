"""
data_loader.py

Utility functions for loading input datasets required by the
Adaptive H3 Spatial Indexing (AHSI) layer.
"""

from pathlib import Path

import pandas as pd


"""
io.py

Input/output utilities for the Adaptive H3 Spatial Indexing (AHSI) layer.
"""

import pandas as pd

from config import AHSI_COLUMNS


def load_h3_demand(
    h3_demand: pd.DataFrame,
) -> pd.DataFrame:
    """
    Validate the input dataframe supplied to the AHSI layer.

    Parameters
    ----------
    h3_demand : pandas.DataFrame
        Backend dataframe containing the columns required
        by the AHSI layer.

    Returns
    -------
    pandas.DataFrame
        Validated dataframe.

    Raises
    ------
    ValueError
        If required columns are missing.
    """

    missing = set(AHSI_COLUMNS) - set(h3_demand.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    return h3_demand.copy()


def save_zone_mapping(
    zone_mapping: pd.DataFrame,
    output_path: Path
) -> None:
    """
    Save the operational zone mapping.

    Parameters
    ----------
    zone_mapping : pd.DataFrame
        Operational zone schema.

    output_path : Path
        Destination parquet file.
    """

    output_path.parent.mkdir(parents=True, exist_ok=True)

    zone_mapping.to_parquet(output_path, index=False)
 

