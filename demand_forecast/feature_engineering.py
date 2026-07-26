"""
Feature Engineering
-------------------
Generates runtime features for the Demand Forecast layer.

This module transforms aggregated shift-wise demand data into the
same feature representation used during LSTM training.

Input:
    date
    shift
    h3_cell_8
    demand

Output:
    Original columns +
    shift_sin
    shift_cos
    dow_sin
    dow_cos
    day_index
"""

import numpy as np
import pandas as pd

from demand_forecast.config import (
    SHIFT_MAPPING,
    REQUIRED_COLUMNS,
)


class FeatureEngineer:
    """
    Runtime feature engineering for demand forecasting.
    """

    def __init__(self):
        pass

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------

    def validate_dataframe(
        self,
        df: pd.DataFrame,
    ) -> None:

        missing = [
            column
            for column in REQUIRED_COLUMNS
            if column not in df.columns
        ]

        if missing:
            raise ValueError(
                f"Missing required columns: {missing}"
            )

    # ---------------------------------------------------------
    # Shift Encoding
    # ---------------------------------------------------------

    def encode_shift(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:

        df = df.copy()

        df["shift_id"] = df["shift"].map(
            SHIFT_MAPPING
        )

        df["shift_sin"] = np.sin(
            2 * np.pi * df["shift_id"] / 3
        )

        df["shift_cos"] = np.cos(
            2 * np.pi * df["shift_id"] / 3
        )

        return df

    # ---------------------------------------------------------
    # Day-of-Week Encoding
    # ---------------------------------------------------------

    def encode_day_of_week(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:

        df = df.copy()

        df["date"] = pd.to_datetime(df["date"])

        df["day_of_week"] = (
            df["date"]
            .dt
            .dayofweek
        )

        df["dow_sin"] = np.sin(
            2 * np.pi * df["day_of_week"] / 7
        )

        df["dow_cos"] = np.cos(
            2 * np.pi * df["day_of_week"] / 7
        )

        return df

    # ---------------------------------------------------------
    # Day Index
    # ---------------------------------------------------------

    def generate_day_index(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:

        df = df.copy()

        unique_days = sorted(
            df["date"].unique()
        )

        mapping = {
            day: idx
            for idx, day in enumerate(unique_days)
        }

        df["day_index"] = (
            df["date"]
            .map(mapping)
            .astype(int)
        )

        return df

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def generate_features(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Generate all runtime forecasting features.
        """

        self.validate_dataframe(df)

        df = self.encode_shift(df)
        df = self.encode_day_of_week(df)
        df = self.generate_day_index(df)

        return df