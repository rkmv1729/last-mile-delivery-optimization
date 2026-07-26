"""
Demand Predictor
----------------
Post-processes raw model predictions before they are
used by downstream backend layers.

Input:
    {
        h3_cell: predicted_demand
    }

Output:
    {
        h3_cell: processed_demand
    }
"""

from demand_forecast.config import MIN_DEMAND


class DemandPredictor:
    """
    Post-processes demand predictions.
    """

    def __init__(self):
        pass

    # ---------------------------------------------------------
    # Prediction Processing
    # ---------------------------------------------------------

    def process_predictions(
        self,
        predictions,
    ):
        """
        Clean and post-process model predictions.

        Parameters
        ----------
        predictions : dict
            {
                h3_cell : predicted_demand
            }

        Returns
        -------
        dict
            {
                h3_cell : processed_demand
            }
        """

        processed = {}

        for h3_cell, demand in predictions.items():

            # Prevent negative demand
            demand = max(MIN_DEMAND, float(demand))

            # Demand represents number of orders
            demand = int(round(demand))

            processed[h3_cell] = demand

        return processed