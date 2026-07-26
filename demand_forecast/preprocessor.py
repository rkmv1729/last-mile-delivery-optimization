"""
Preprocessor
------------
Prepares runtime data for LSTM inference.
"""

import joblib
import torch
import pandas as pd

from demand_forecast.config import (
    SCALER_PATH,
    SCALE_COLUMNS,
    FEATURE_COLUMNS,
    LOOKBACK,
    DEVICE,
)


class Preprocessor:
    """
    Runtime preprocessing before LSTM inference.
    """

    def __init__(self):

        self.scaler = joblib.load(
            SCALER_PATH
        )

    # ---------------------------------------------------------
    # Scaling
    # ---------------------------------------------------------

    def scale_features(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:

        df = df.copy()

        df[SCALE_COLUMNS] = self.scaler.transform(
            df[SCALE_COLUMNS]
        )

        return df

    # ---------------------------------------------------------
    # Sequence Validation
    # ---------------------------------------------------------

    def validate_history(
        self,
        df: pd.DataFrame,
    ):

        if len(df) < LOOKBACK:

            raise ValueError(
                f"At least {LOOKBACK} observations required."
            )

    # ---------------------------------------------------------
    # Sequence Creation
    # ---------------------------------------------------------

    def create_sequences(
        self,
        df: pd.DataFrame,
    ) -> dict[str, list]:

        sequences = {}

        grouped = df.groupby(
            "h3_cell_8"
        )

        for _, group in grouped:

            group = (
                group
                .sort_values(
                    ["date", "shift"]
                )
                .reset_index(drop=True)
            )

            if len(group) < LOOKBACK:
                continue

            sequence = (
                group
                .iloc[-LOOKBACK:][FEATURE_COLUMNS]
                .values
            )

            sequences["h3_cell_8"] = sequence

        if len(sequences) == 0:

            raise ValueError(
                "No valid inference sequences created."
            )

        return sequences

    # ---------------------------------------------------------
    # Tensor Conversion
    # ---------------------------------------------------------

    # TODO : update the return type and input types
    def to_tensor(
        self,
        sequences,
    ):
        
        cell_ids = list(sequences.keys())

        tensor = torch.tensor(
            list(sequences.values()),
            dtype=torch.float32,
            device=DEVICE,
        )

        return cell_ids, tensor

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def preprocess(
        self,
        df: pd.DataFrame,
    ):

        self.validate_history(df)

        df = self.scale_features(df)

        sequences = self.create_sequences(df)

        cell_ids, tensor = self.to_tensor(
            sequences
        )

        return cell_ids, tensor