from demand_forecast.helpers import (
    prepare_forecast_dataset,
    generate_demand_forecast,
)

from demand_forecast.algorithms import *


def run_forecast(
    forecast_df,
    model,
    metadata,
    scaler,
):

    X, forecast_index = prepare_forecast_dataset(
        forecast_df=forecast_df,
        scaler=scaler,
        metadata=metadata
    )

    cell_forecast_df = generate_demand_forecast(
        model=model,
        X=X,
        forecast_index=forecast_index,
    )

    return cell_forecast_df
    


    


 