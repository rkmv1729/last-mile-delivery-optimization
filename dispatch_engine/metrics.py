"""
===========================================================================
Batch Metrics

Computes Batch Utility Score (BUS) for candidate batches.
===========================================================================

Responsibilities
----------------
1. Compute individual batch metrics.
2. Store computed metrics in batch.metrics.
3. Compute overall Batch Utility Score (BUS).
4. Store BUS in batch.optimization_score.
===========================================================================
"""

from dispatch_engine.config import (
    BUS_UTILITY_WEIGHTS,
    MAX_BATCH_SIZE,
    DISPATCH_CENTER_STORAGE_CAPACITY,
)

from dispatch_engine.batch import Batch


class BatchMetrics:
    """
    Computes Batch Utility Score (BUS).
    """

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def compute_bus(
        self,
        batches: list[Batch],
        dispatch_center_state: dict,
        forecast: dict | None = None,
    ) -> list[Batch]:
        """
        Compute BUS for every candidate batch.

        Parameters
        ----------
        batches : list[Batch]

        dispatch_center_state : dict

        forecast : dict | None

        Returns
        -------
        list[Batch]
        """

        for batch in batches:

            batch.metrics["batch_priority"] = (
                self._batch_priority(batch)
            )

            batch.metrics["vehicle_utilization"] = (
                self._vehicle_utilization(batch)
            )

            batch.metrics["storage_utilization"] = (
                self._storage_utilization(
                    batch,
                    dispatch_center_state,
                )
            )

            batch.metrics["retention_penalty"] = (
                self._retention_penalty(batch)
            )

            batch.metrics["forecast_opportunity"] = (
                self._forecast_opportunity(
                    batch,
                    forecast,
                )
            )

            batch.optimization_score = (
                self._batch_utility_score(batch)
            )

        return batches

    # ------------------------------------------------------------------ #
    # Individual Metrics
    # ------------------------------------------------------------------ #

    def _batch_priority(self, batch, orders_state):

        if not batch.order_ids:
            return 0.0

        priorities = []

        for order_id in batch.order_ids:

            order = orders_state.get(order_id)

            if order is None:
                continue

            priorities.append(order.priority_score)

        if not priorities:
            return 0.0

        return sum(priorities) / len(priorities)


    def _vehicle_utilization(self, batch):
        """
        Vehicle utilization ratio.
        """

        if MAX_BATCH_SIZE == 0:
            return 0.0
        
        return batch.batch_size / MAX_BATCH_SIZE
    

    def _storage_utilization(
        self,
        batch,
        dispatch_center_state,
    ):
        """
        Current storage utilization of the dispatch centre.
        """

        inventory = dispatch_center_state.get(
            batch.dispatch_center,
            0,
        )

        if DISPATCH_CENTER_STORAGE_CAPACITY == 0:
            return 0.0

        return (
            inventory
            / DISPATCH_CENTER_STORAGE_CAPACITY
        )


    def _retention_penalty(self, batch):
        """
        Average retention penalty across all products.
        """

        products = batch.products

        if not products:
            return 0.0

        penalties = [
            product.get(
                "retention_penalty",
                0.0,
            )
            for product in products
        ]

        return sum(penalties) / len(penalties)

    def _forecast_opportunity(
        self,
        batch,
        forecast,
    ):
        """
        Forecast opportunity score.
        """

        if forecast is None:
            return 0.0

        return forecast.get(
            batch.destination_zone,
            0.0
        )

    # ------------------------------------------------------------------ #
    # Final BUS
    # ------------------------------------------------------------------ #

    def _batch_utility_score(
        self,
        batch,
    ):
        """
        Compute Batch Utility Score (BUS).
        """

        metrics = batch.metrics

        return (

            BUS_UTILITY_WEIGHTS["batch_priority"]
            * metrics["batch_priority"]

            +

            BUS_UTILITY_WEIGHTS["vehicle_utilization"]
            * metrics["vehicle_utilization"]

            +

            BUS_UTILITY_WEIGHTS["storage_utilization"]
            * metrics["storage_utilization"]

            +

            BUS_UTILITY_WEIGHTS["retention_penalty"]
            * metrics["retention_penalty"]

            +

            BUS_UTILITY_WEIGHTS["forecast_opportunity"]
            * metrics["forecast_opportunity"]

        )