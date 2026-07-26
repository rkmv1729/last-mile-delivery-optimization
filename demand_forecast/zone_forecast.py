"""
Zone Forecast Aggregator
------------------------
Aggregates H3 demand predictions into AHSI operational zones.
"""

from collections import defaultdict

import numpy as np


class ZoneForecastAggregator:
    """
    Aggregate H3 predictions into zone forecasts.
    """

    def __init__(self):
        pass

    # ---------------------------------------------------------
    # Compute Historical Weights
    # ---------------------------------------------------------

    def compute_weights(
        self,
        history_df,
    ):
        """
        Compute normalized weights for every H3 cell.

        Weight =
            0.5 * Historical Demand +
            0.3 * Demand Variability +
            0.2 * Centrality

        Returns
        -------
        dict
            {
                h3_cell : weight
            }
        """

        stats = (
            history_df
            .groupby("h3_cell_8")["demand"]
            .agg(["mean", "std"])
            .fillna(0)
        )

        stats["mean_norm"] = (
            stats["mean"] /
            stats["mean"].sum()
        )

        if stats["std"].sum() == 0:
            stats["std_norm"] = 0
        else:
            stats["std_norm"] = (
                stats["std"] /
                stats["std"].sum()
            )

        # Placeholder until AHSI exposes graph centrality
        stats["centrality"] = 1.0

        stats["centrality_norm"] = (
            stats["centrality"] /
            stats["centrality"].sum()
        )

        stats["weight"] = (
            0.5 * stats["mean_norm"]
            + 0.3 * stats["std_norm"]
            + 0.2 * stats["centrality_norm"]
        )

        stats["weight"] /= stats["weight"].sum()

        return stats["weight"].to_dict()

    # ---------------------------------------------------------
    # Aggregate Zone Forecast
    # ---------------------------------------------------------

    def aggregate(
        self,
        predictions,
        zone_mapping,
        weights,
    ):
        """
        Parameters
        ----------
        predictions

            {
                h3_cell : predicted_orders
            }

        zone_mapping

            {
                h3_cell : zone_id
            }

        weights

            {
                h3_cell : weight
            }

        Returns
        -------
        dict
        """

        zone_orders = defaultdict(float)

        weighted_score = defaultdict(float)

        cell_predictions = defaultdict(dict)

        for h3_cell, demand in predictions.items():

            zone = zone_mapping[h3_cell]

            zone_orders[zone] += demand

            weighted_score[zone] += (
                weights.get(h3_cell, 0.0)
                * demand
            )

            cell_predictions[zone][h3_cell] = demand

        results = {}

        for zone in zone_orders:

            results[zone] = {

                "forecast_demand": int(
                    round(zone_orders[zone])
                ),

                "forecast_score": round(
                    weighted_score[zone],
                    3,
                ),

                "cell_predictions":
                    cell_predictions[zone],
            }

        return results