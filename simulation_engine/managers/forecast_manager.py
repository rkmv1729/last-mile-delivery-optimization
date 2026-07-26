from simulation_engine.state import SimulationState
from simulation_engine.config import FORECAST_INTERVAL
import pandas as pd


class ForecastManager:
    """
    Manages demand forecasting within the simulation.
    """

    def __init__(self, backend):
        self.backend = backend

    # ------------------------------------------------------------------
    # Forecast Generation
    # ------------------------------------------------------------------

    def update_forecast(
        self,
        state: SimulationState,
    ):
        """
        Update demand forecasts for all operational zones.
        """

        if self.forecast_engine is None:
            return

        forecasts = self.forecast_engine.predict(
            state.zones.values(),
            state.current_time,
        )

        state.forecasts = forecasts

        for zone_id, predicted_demand in forecasts.items():

            if zone_id in state.zones:
                state.zones[zone_id].predicted_demand = predicted_demand

        state.log(
            f"Updated demand forecasts for {len(forecasts)} zones."
        )

    def update(
        self,
        state: SimulationState,
        orders_df: pd.DataFrame
    ):
        if state.tick % FORECAST_INTERVAL != 0:
            return 

        forecast_results = self.backend.process_forecast(
            orders_df,
        )

        return forecast_results

    def update_zones(
        self,
        state: SimulationState,
        forecast_results: pd.DataFrame,
    ):
        """
        Update simulation zones with forecast results.
        """

        for _, row in forecast_results.iterrows():

            zone = state.zones.get(
                row["zone_id"],
            )

            if zone is None:
                continue

            zone.predicted_demand = row["predicted_demand"]
            zone.forecast_score = row["forecast_score"]

    # ------------------------------------------------------------------
    # Forecast Lookup
    # ------------------------------------------------------------------

    def get_zone_forecast(
        self,
        state: SimulationState,
        zone_id: str,
    ):

        zone = state.zones.get(zone_id)

        if zone is None:
            return None

        return zone.predicted_demand

    def get_all_forecasts(
        self,
        state: SimulationState,
    ):

        return {
            zone.zone_id: zone.predicted_demand
            for zone in state.zones.values()
        }