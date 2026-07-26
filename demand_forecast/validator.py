"""
Demand Forecast Validator
-------------------------
Validates runtime input before demand forecasting.
"""

import pandas as pd

from demand_forecast.config import (
    LOOKBACK,
    REQUIRED_COLUMNS,
)

# TODO: in some other files, validations are performed , remove them and 
# if not present here, add them


class DemandValidator:
    """
    Validates demand forecast inputs.
    """

    # ---------------------------------------------------------
    # DataFrame Validation
    # ---------------------------------------------------------

    def validate_inputs(
        self,
        df: pd.DataFrame,
    ):
        """
        Validate input DataFrame.
        """

        if df.empty:
            raise ValueError(
                "Input DataFrame is empty."
            )

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
    # Sequence Validation
    # ---------------------------------------------------------

    def validate_sequences(
        self,
        sequences: dict,
    ):
        """
        Ensure sequences are available for prediction.
        """

        if not sequences:
            raise ValueError(
                "No valid H3 sequences available."
            )

    # ---------------------------------------------------------
    # History Validation
    # ---------------------------------------------------------

    def validate_history(
        self,
        history: pd.DataFrame,
    ):
        """
        Ensure every H3 cell has enough history.
        """

        grouped = history.groupby("h3_cell_8")

        insufficient = []

        for h3_cell, group in grouped:

            if len(group) < LOOKBACK:
                insufficient.append(h3_cell)

        if insufficient:
            raise ValueError(
                f"Insufficient history for {len(insufficient)} H3 cells."
            )

    # ---------------------------------------------------------
    # Prediction Validation
    # ---------------------------------------------------------

    def validate_predictions(
        self,
        predictions: dict,
    ):
        """
        Validate prediction dictionary.
        """

        if not predictions:
            raise ValueError(
                "Prediction dictionary is empty."
            )

        for h3_cell, demand in predictions.items():

            if demand is None:
                raise ValueError(
                    f"Prediction missing for {h3_cell}."
                )

            if demand < 0:
                raise ValueError(
                    f"Negative prediction for {h3_cell}."
                )