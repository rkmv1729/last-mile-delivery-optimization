from demand_forecast.validator import DemandValidator
from demand_forecast.feature_engineering import FeatureEngineer
from demand_forecast.preprocessor import Preprocessor
from demand_forecast.inference import InferenceEngine
from demand_forecast.predictor import DemandPredictor

from common.logs.logger import setup_logger
from demand_forecast.config import LOG_FILE

from time import perf_counter

import pandas as pd

# ---------------------------------------------------------
# Initialize Components
# ---------------------------------------------------------

validator = DemandValidator()
feature_engineer = FeatureEngineer()
model = InferenceEngine()
preprocessor = Preprocessor()
predictor = DemandPredictor()

logger = setup_logger(LOG_FILE)

def run_demand_forecast(
    forecast_df: pd.DataFrame,
) -> pd.DataFrame:
    """Execute the complete Demand Forecast pipeline."""

    start_time = perf_counter()

    try:

        logger.info("Loaded demand history...")

        logger.info("Validating input...")
        validator.validate_inputs(
            forecast_df
        )

        logger.info("Generating features...")
        features_df = feature_engineer.generate_features(
            forecast_df
        )

        logger.info("Preprocessing features...")
        cell_ids, model_inputs = preprocessor.preprocess(
            features_df
        )

        logger.info("Running demand forecasting model...")
        predictions = model.predict(
            cell_ids, model_inputs
        )

        logger.info("Formatting predictions...")
        forecast = predictor.process_predictions(
            predictions
        )

        logger.info("Validating output...")
        validator.validate_predictions(
            forecast
        )

        return forecast

    except Exception as e:

        logger.exception(
            "Demand Forecast failed."
        )

        raise

    finally:

        elapsed = perf_counter() - start_time

        logger.info(
            f"Demand Forecast completed in {elapsed:.2f} seconds."
        )