"""
History Manager
---------------
Maintains the rolling history used by the Demand Forecast layer.
"""

from datetime import timedelta

import pandas as pd

from demand_forecast.config import (
    WEIGHT_HISTORY_DAYS,
)


class HistoryManager:
    """
    Maintains rolling historical demand.
    """

    def __init__(self):

        self.history_df = None

    # ---------------------------------------------------------
    # Initialize
    # ---------------------------------------------------------

    def initialize(
        self,
        historical_df: pd.DataFrame,
        current_date,
    ):
        """
        Load the initial rolling history.
        """

        start_date = (
            current_date
            - timedelta(days=WEIGHT_HISTORY_DAYS)
        )

        self.history_df = historical_df[
            historical_df["date"] >= start_date
        ].copy()

        return self.history_df

    # ---------------------------------------------------------
    # Update
    # ---------------------------------------------------------

    def update(
        self,
        new_data: pd.DataFrame,
    ):
        """
        Add newly completed simulation demand.
        """

        self.history_df = pd.concat(
            [
                self.history_df,
                new_data,
            ],
            ignore_index=True,
        )

        latest_date = self.history_df["date"].max()

        cutoff = (
            latest_date
            - timedelta(days=WEIGHT_HISTORY_DAYS)
        )

        self.history_df = self.history_df[
            self.history_df["date"] >= cutoff
        ].copy()

        self.history_df.reset_index(
            drop=True,
            inplace=True,
        )

        return self.history_df

    # ---------------------------------------------------------
    # Get History
    # ---------------------------------------------------------

    def get_history(
        self,
    ):
        """
        Return the current rolling history.
        """

        return self.history_df.copy()