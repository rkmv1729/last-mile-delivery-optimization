"""
spatial.py

Spatial feature engineering utilities.

Converts GPS coordinates into H3 indices.
"""

import h3
import pandas as pd

from config import (
    H3_RESOLUTION,
    CHILD_RESOLUTION,
)


def gps_to_h3(
    latitude: float,
    longitude: float,
    resolution: int,
) -> str:
    """
    Convert GPS coordinates to an H3 cell.

    Parameters
    ----------
    latitude : float
        Latitude.

    longitude : float
        Longitude.

    resolution : int
        H3 resolution.

    Returns
    -------
    str
        H3 cell index.
    """

    return h3.latlng_to_cell(
        latitude,
        longitude,
        resolution,
    )


def add_h3_features(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Add H3 features to a dataframe.

    Parameters
    ----------
    dataframe : pd.DataFrame
        Input dataframe containing latitude and longitude.

    Returns
    -------
    pd.DataFrame
        Dataframe with H3 features added.
    """

    required_columns = {
        "latitude",
        "longitude",
    }

    missing = required_columns - set(dataframe.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    if dataframe[["latitude", "longitude"]].isnull().any().any():
        raise ValueError(
            "Latitude/Longitude contains missing values."
        )

    dataframe = dataframe.copy()

    dataframe[f"h3_cell_{H3_RESOLUTION}"] = dataframe.apply(
        lambda row: gps_to_h3(
            row["latitude"],
            row["longitude"],
            H3_RESOLUTION,
        ),
        axis=1,
    )

    dataframe[f"h3_cell_{CHILD_RESOLUTION}"] = dataframe.apply(
        lambda row: gps_to_h3(
            row["latitude"],
            row["longitude"],
            CHILD_RESOLUTION,
        ),
        axis=1,
    )

    return dataframe