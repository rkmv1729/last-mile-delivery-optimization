import torch
import pandas as pd
import numpy as np
from config import SHIFT_MAPPING


# =====================================================
# Public helpers


def prepare_forecast_dataset(
    forecast_df: pd.DataFrame,
    scaler,
    metadata,
) -> tuple:
    """
    Prepare historical demand data for LSTM inference.

    Parameters
    ----------
    history_df : pd.DataFrame
        Historical demand containing:
            - h3_cell_8
            - shift
            - day_index
            - day_of_week
            - demand

    scaler
        Fitted MinMaxScaler used during model training.

    lookback : int
        Number of previous timesteps used by the LSTM.

    Returns
    -------
    tuple
        (
            X,
            forecast_index
        )
    """

    feature_df = _build_feature_matrix(forecast_df)

    scaled_df = _scale_features(
        feature_df,
        scaler,
        metadata
    )

    X, forecast_index = _create_sequences(
        scaled_df,
        feature_df,
        metadata
    )

    print("Forecast index:", len(forecast_index))
    print("Sequences:", len(X))

    return X, forecast_index


# =====================================================


def generate_demand_forecast(
    model,
    X: np.ndarray,
    forecast_index: pd.DataFrame,
) -> pd.DataFrame:
    """
    Generate cell-level demand forecasts using the trained LSTM model.

    Parameters
    ----------
    model
        Trained LSTM forecasting model.

    X : np.ndarray
        Input sequences of shape
        (samples, lookback, features).

    scaler
        Fitted MinMaxScaler used during training.

    forecast_index : pd.DataFrame
        Metadata corresponding to each prediction containing:
            - h3_cell_8
            - shift

    Returns
    -------
    pd.DataFrame
        Cell-level demand forecasts containing:
            - h3_cell_8
            - shift
            - predicted_demand
    """

    predictions = _run_inference(
        model,
        X,
    )

    # predictions = _inverse_scale_predictions(
    #     predictions,
    #     scaler,
    # )

    forecast_df = _create_forecast_dataframe(
        forecast_index,
        predictions,
    )

    return forecast_df



# =====================================================
# Private helpers

def _build_feature_matrix(
    forecast_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Construct the feature matrix required for inference.
    """

    print(forecast_df.columns.to_list())

    feature_df = (
        forecast_df
        .sort_values(
            by=["h3_cell_8", "day_index", "shift"]
        )
        .reset_index(drop=True)
    )

    feature_df = compute_rolling_features(feature_df)
    feature_df = compute_demand_diff(feature_df)
    feature_df = compute_growth_rate(feature_df)
    feature_df = compute_cyclical_features(feature_df)

    print("Feature Matrix")
    print(feature_df.shape)
    print(feature_df.isna().sum())

    return feature_df


# =====================================================

def _scale_features(
    feature_df: pd.DataFrame,
    scaler,
    metadata
) -> pd.DataFrame:
    """
    Scale input features using the fitted MinMaxScaler.
    """

    scaled_df = feature_df.copy()
    print(scaled_df.columns.tolist())
    scaled_df["shift"] = encode_shift(scaled_df)

    scaled_df[metadata["feature_columns"]] = scaler.transform(
        scaled_df[metadata["feature_columns"]]
    )

    print(
        scaled_df.groupby("h3_cell_8")
        .size()
        .describe()
    )

    return scaled_df

# =====================================================

def _create_sequences(
    scaled_df: pd.DataFrame,
    feature_df: pd.DataFrame,
    metadata
):
    """
    Create one inference sequence per active H3 cell.
    """

    X = []
    forecast_index = []

    print("Scaled DF:", scaled_df.shape)
    print("Unique cells:", scaled_df["h3_cell_8"].nunique())

    print(
        scaled_df.groupby("h3_cell_8")
        .size()
        .describe()
    )

    print(
        scaled_df.groupby("h3_cell_8")
        .size()
        .sort_values(ascending=False)
        .head(10)
    )

    scaled_groups = scaled_df.groupby("h3_cell_8")
    feature_groups = feature_df.groupby("h3_cell_8")

    for h3_cell in scaled_groups.groups:

        scaled_group = (
            scaled_groups.get_group(h3_cell)
            .sort_values(["day_index", "shift"])
            .reset_index(drop=True)
        )

        feature_group = (
            feature_groups.get_group(h3_cell)
            .sort_values(["day_index", "shift"])
            .reset_index(drop=True)
        )

        if len(scaled_group) < metadata["lookback"]:
            continue

        values = (
            scaled_group[metadata["feature_columns"]]
            .tail(metadata["lookback"])
            .to_numpy()
        )

        X.append(values)

        last_row = feature_group.iloc[-1]

        NEXT_SHIFT = {
            "Morning": "Afternoon",
            "Afternoon": "Evening",
            "Evening": "Morning",
        }

        forecast_index.append(
            {
                "h3_cell_8": h3_cell,
                "day_index": last_row["day_index"]
                + (1 if last_row["shift"] == "Evening" else 0),
                "shift": NEXT_SHIFT[last_row["shift"]],
            }
        )

    X = np.asarray(X, dtype=np.float32)

    forecast_index = pd.DataFrame(forecast_index)

    return X, forecast_index

# =====================================================

def _run_inference(
    model,
    X: np.ndarray,
    device: str = "cpu",
) -> np.ndarray:
    """
    Generate predictions using the trained LSTM model.

    Parameters
    ----------
    model
        Trained LSTM model.

    X : np.ndarray
        Input sequences.

    device : str, default="cpu"

    Returns
    -------
    np.ndarray
        Predicted scaled demand.
    """

    X = torch.tensor(
        X,
        dtype=torch.float32,
        device=device,
    )

    with torch.no_grad():
        predictions = model(X)

    return predictions.cpu().numpy().flatten()


# =====================================================


# def _inverse_scale_predictions(
#     predictions: np.ndarray,
#     scaler,
#     metadata
# ) -> np.ndarray:
#     """
#     Convert scaled predictions back to the original demand scale.
#     """

#     dummy = np.zeros(
#         (len(predictions), len(metadata["feature_columns"])),
#         dtype=float,
#     )

#     dummy[:, 0] = predictions

#     predictions = scaler.inverse_transform(dummy)[:, 0]

#     predictions = np.clip(
#         predictions,
#         a_min=0,
#         a_max=None,
#     )

#     return predictions

# =====================================================

def _create_forecast_dataframe(
    forecast_index: pd.DataFrame,
    predictions: np.ndarray,
) -> pd.DataFrame:
    """
    Create the final cell-level forecast dataframe.
    """

    forecast_df = forecast_index.copy()

    forecast_df["predicted_demand"] = predictions

    return forecast_df



# =====================================================

def compute_rolling_features(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Compute rolling mean and rolling std using
    the previous 3 observations.
    """

    print(df.columns.tolist())

    grouped = df.groupby("h3_cell_8")["demand"]

    df["rolling_mean_3"] = (
        grouped
        .transform(lambda x: x.shift(1).rolling(3, min_periods=1).mean())
        .fillna(0)
    )

    df["rolling_std_3"] = (
        grouped
        .transform(lambda x: x.shift(1).rolling(3, min_periods=1).std())
        .fillna(0)
    )

    print("Rolling features",df["rolling_mean_3"].isna().sum())

    return df


# =====================================================

def compute_demand_diff(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Compute first-order demand difference.
    """

    df["demand_diff"] = (
        df.groupby("h3_cell_8")["demand"]
        .diff()
        .fillna(0)
    )

    return df


# =====================================================

def compute_growth_rate(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Compute demand growth rate.
    """

    previous = (
        df.groupby("h3_cell_8")["demand"]
        .shift(1)
    )

    df["growth_rate"] = (
        (df["demand"] - previous)
        / (previous.replace(0, np.nan)+1)
    )

    df["growth_rate"] = (
        df["growth_rate"]
        .replace([np.inf, -np.inf], 0)
        .fillna(0)
    )

    return df


# =====================================================

def compute_cyclical_features(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Encode day of week cyclically.
    """

    df["dow_sin"] = np.sin(
        2 * np.pi * df["day_of_week"] / 7
    )

    df["dow_cos"] = np.cos(
        2 * np.pi * df["day_of_week"] / 7
    )

    return df



def encode_shift(
    df: pd.DataFrame,
    column: str = "shift",
) -> pd.Series:
    """
    Encode shift labels into integers.
    """

    return (
        df[column]
        .map(SHIFT_MAPPING)
        .astype("int8")
    )




