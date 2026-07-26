"""
Dispatch Engine Data Loader

Loads input data required by the dispatch engine.
"""

import pandas as pd

from config import (
    TRANSFER_PRODUCTS_FILE,
    RETAINED_PRODUCTS_FILE,
    DISPATCH_CENTER_STATE_FILE,
    DEMAND_FORECAST_FILE, 
)


class DispatchDataLoader:

    def _load_parquet(self, file_path):
        try:
            return pd.read_parquet(file_path)
        except Exception as e:
            raise FileNotFoundError(
                f"Unable to load {file_path}"
            ) from e

    def load_transfer_products(self):
        """
        Load products transferred from
        Product Transfer Layer.
        """

        self._load_parquet(
            TRANSFER_PRODUCTS_FILE
        )

    def load_retained_products(self):
        """
        Load retained products from
        previous dispatch cycle.
        """

        self._load_parquet(
            RETAINED_PRODUCTS_FILE
        )

    def load_dispatch_center_state(self):
        """
        Load dispatch center inventory
        and capacity information.
        """

        self._load_parquet(
            DISPATCH_CENTER_STATE_FILE
        )

    def load_forecast(self):
        """
        Load demand forecast generated
        by Demand Forecast Layer.
        """

        self._load_parquet(
            DEMAND_FORECAST_FILE
        )