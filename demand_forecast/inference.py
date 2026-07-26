"""
Inference Engine
----------------
Loads the trained demand forecasting model and performs
forward inference for all H3 cells.

Input:
    cell_ids : List[str]
    sequences : Tensor
        Shape -> (num_cells, LOOKBACK, INPUT_SIZE)

Output:
    {
        h3_cell: predicted_demand
    }
"""

import torch

from demand_forecast.config import (
    DEVICE,
    MODEL_PATH,
    INPUT_SIZE,
    HIDDEN_SIZE,
    NUM_LAYERS,
    OUTPUT_SIZE,
)

from demand_forecast.model import DemandLSTM


class InferenceEngine:
    """
    Handles model loading and demand prediction.
    """

    def __init__(self):
        self.model = self.load_model()

    # ---------------------------------------------------------
    # Model Loading
    # ---------------------------------------------------------

    def load_model(self):
        """
        Load trained LSTM model.
        """

        model = DemandLSTM(
            input_size=INPUT_SIZE,
            hidden_size=HIDDEN_SIZE,
            num_layers=NUM_LAYERS,
            output_size=OUTPUT_SIZE,
        )

        model.load_state_dict(
            torch.load(
                MODEL_PATH,
                map_location=DEVICE,
            )
        )

        model.to(DEVICE)
        model.eval()

        return model

    # ---------------------------------------------------------
    # Prediction
    # ---------------------------------------------------------

    def predict(
        self,
        cell_ids,
        sequences,
    ):
        """
        Predict demand for every H3 cell.

        Parameters
        ----------
        cell_ids : list[str]

        sequences : Tensor
            Shape:
                (num_cells, LOOKBACK, INPUT_SIZE)

        Returns
        -------
        dict
            {
                h3_cell : predicted_demand
            }
        """

        with torch.no_grad():

            predictions = self.model(sequences)

            predictions = (
                predictions
                .cpu()
                .numpy()
                .flatten()
            )

        return dict(
            zip(
                cell_ids,
                predictions,
            )
        )