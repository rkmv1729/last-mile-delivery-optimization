import pandas as pd

# NOt useful anymore, drop this file
def aggregate_zone_forecast(
    cell_forecast_df: pd.DataFrame,
    zone_mapping_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Aggregate H3 cell-level demand forecasts into operational zone forecasts.

    Parameters
    ----------
    cell_forecast_df : pd.DataFrame
        Cell-level demand forecasts containing:
            - h3_cell_8
            - shift
            - predicted_demand

    zone_mapping_df : pd.DataFrame
        Mapping between H3 cells and operational zones containing:
            - h3_cell_8
            - zone_id

    Returns
    -------
    pd.DataFrame
        Zone-level demand forecasts containing:
            - zone_id
            - shift
            - forecast_demand
    """

    zone_forecast_df = (
        cell_forecast_df
        .merge(zone_mapping_df, on="h3_cell_8", how="left")
        .groupby(["zone_id", "shift"], as_index=False)["predicted_demand"]
        .sum()
        .rename(columns={"predicted_demand": "forecast_demand"})
    )

    return zone_forecast_df


# =====================================================

def compute_forecast_opportunity(
    zone_forecast_df: pd.DataFrame,
    history_df: pd.DataFrame,
    zone_mapping_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Compute the Forecast Opportunity (FO) score for each operational zone.

    Forecast Opportunity measures how much higher (or lower) the predicted
    demand is compared to the historical average demand for the same zone
    and shift.

    Parameters
    ----------
    zone_forecast_df : pd.DataFrame
        Zone-level demand forecasts containing:
            - zone_id
            - shift
            - forecast_demand

    history_df : pd.DataFrame
        Historical zone demand containing:
            - zone_id
            - shift
            - demand

    Returns
    -------
    pd.DataFrame
        Zone forecast dataframe containing:
            - zone_id
            - shift
            - forecast_demand
            - forecast_opportunity
    """

    history_df = history_df.merge(
        zone_mapping_df,
        on="h3_cell_8",
        how="left",
    )

    # Historical mean demand
    historical_mean = (
        history_df
        .groupby(
            ["zone_id", "shift"],
            as_index=False,
        )["demand"]
        .mean()
        .rename(columns={"demand": "historical_mean"})
    )

    # Join with forecast
    forecast_df = (
        zone_forecast_df
        .merge(
            historical_mean,
            on=["zone_id", "shift"],
            how="left",
        )
    )

    # Prevent divide-by-zero
    forecast_df["historical_mean"] = (
        forecast_df["historical_mean"]
        .fillna(1e-6)
        .clip(lower=1e-6)
    )

    # Raw opportunity ratio
    forecast_df["forecast_opportunity"] = (
        forecast_df["forecast_demand"]
        / forecast_df["historical_mean"]
    )

    # Min-Max normalization
    fo = forecast_df["forecast_opportunity"]

    if fo.max() > fo.min():
        forecast_df["forecast_opportunity"] = (
            (fo - fo.min())
            / (fo.max() - fo.min())
        )
    else:
        forecast_df["forecast_opportunity"] = 0.5

    return forecast_df[
        [
            "zone_id",
            "shift",
            "forecast_demand",
            "forecast_opportunity",
        ]
    ]