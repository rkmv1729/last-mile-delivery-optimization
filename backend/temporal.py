"""
temporal.py

Temporal feature engineering utilities.

Extracts temporal features from timestamps.
"""

import pandas as pd


def _get_shift(hour: int) -> str:
    """
    Convert hour to operational shift.
    """

    if 6 <= hour < 14:
        return "Morning"

    if 14 <= hour < 18:
        return "Afternoon"

    return "Evening"


def add_temporal_features(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Add temporal features to a dataframe.

    Parameters
    ----------
    dataframe : pd.DataFrame
        Input dataframe containing timestamps.

    Returns
    -------
    pd.DataFrame
        Dataframe with temporal features added.
    """

    if "timestamp" not in dataframe.columns:
        raise ValueError(
            "Missing required column: 'timestamp'"
        )

    dataframe = dataframe.copy()

    # TODO : do not hardcode the format, fix it later
    dataframe["timestamp"] = pd.to_datetime(
        dataframe["timestamp"], format = "%y-%m-%d %H:%M:%S"
    )

    if dataframe["timestamp"].isnull().any():
        raise ValueError(
            "Invalid timestamps found."
        )

    dataframe["date"] = dataframe["timestamp"].dt.date

    dataframe["hour"] = (
        dataframe["timestamp"]
        .dt.hour
    )

    dataframe["weekday"] = (
        dataframe["timestamp"]
        .dt.weekday
    )

    dataframe["shift"] = (
        dataframe["hour"]
        .apply(_get_shift)
    )

    return dataframe