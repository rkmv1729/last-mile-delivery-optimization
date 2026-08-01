import torch
import torch.nn as nn


class DemandForecastLSTM(nn.Module):

    def __init__(self, 
        input_size,
        hidden_size,
        num_layers,
        dropout
    ):

        super().__init__()

        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout
        )

        self.dropout = nn.Dropout(0.2)

        self.fc1 = nn.Linear(64, 32)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(32, 1)

    def forward(self, x):

        out, _ = self.lstm(x)

        out = out[:, -1, :]      # equivalent to out[:, -1] here

        out = self.dropout(out)

        out = self.relu(self.fc1(out))

        out = self.fc2(out)

        return out
    

def load_model(model_path, device="cpu"):
    model = DemandForecastLSTM()
    state_dict = torch.load(model_path, map_location=device)

    print(state_dict.keys())
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    model.eval()
    return model