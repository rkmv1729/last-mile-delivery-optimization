"""
Demand Forecast Model
---------------------
Defines the LSTM architecture used for demand forecasting.

This model is shared by both:
    - train.py
    - inference.py
"""

import torch
import torch.nn as nn


class DemandLSTM(nn.Module):

    def __init__(
        self,
        input_size=6,
        hidden_size=64,
        num_layers=2,
        output_size=1,
        dropout=0.2,
    ):
        super().__init__()

        self.hidden_size = hidden_size
        self.num_layers = num_layers

        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout,
            batch_first=True,
        )

        self.fc = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size // 2, output_size),
        )

    # ---------------------------------------------------------
    # Forward Pass
    # ---------------------------------------------------------

    def forward(
        self,
        x,
    ):
        """
        Parameters
        ----------
        x : Tensor
            Shape:
                (batch_size, lookback, input_size)

        Returns
        -------
        Tensor
            Shape:
                (batch_size, output_size)
        """

        batch_size = x.size(0)

        h0 = torch.zeros(
            self.num_layers,
            batch_size,
            self.hidden_size,
            device=x.device,
        )

        c0 = torch.zeros(
            self.num_layers,
            batch_size,
            self.hidden_size,
            device=x.device,
        )

        output, _ = self.lstm(
            x,
            (h0, c0),
        )

        output = output[:, -1, :]

        output = self.fc(output)

        return output