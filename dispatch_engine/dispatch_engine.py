"""
Dispatch Engine

Coordinates batch optimization,
batch creation,
metric computation,
and resource allocation.
"""

from dispatch_engine.batch_optimizer import BatchOptimizer
from dispatch_engine.batch_builder import BatchBuilder
from dispatch_engine.metrics import BatchMetrics
from dispatch_engine.resource_allocator import ResourceAllocator
from dispatch_engine.validator import DispatchValidator

from dispatch_engine.config import VAN, BIKE

class DispatchEngine:

    def __init__(self):

        self.optimizer = BatchOptimizer()

        self.builder = BatchBuilder()

        self.metrics = BatchMetrics()

        self.allocator = ResourceAllocator()

        self.validator = DispatchValidator()

    def _update_retention_cycles(
        self,
        retained_batches,
    ):
        """
        Increment retention cycle for products
        belonging to retained batches.
        """

        for batch in retained_batches:

            for product in batch.products:

                product["retention_cycles"] += 1

    def dispatch(
        self,
        transfer_products,
        retained_products,
        dispatch_center_state,
        forecast,
        available_vehicles,
        available_drivers,
    ):
        """
        Execute complete dispatch pipeline.
        """


        self.validator.validate_forecast(
            forecast,
        )

        self.validator.validate_products(
            transfer_products,
        )

        self.validator.validate_resources(
            available_vehicles,
            available_drivers,
        )

        optimized_groups = (
            self.optimizer.optimize(
                transfer_products,
                retained_products,
            )
        )

        batches = self.builder.build_batches(
            optimized_groups,
        )

        self.validator.validate_batches(
            batches,
        )

        self.metrics.compute_bus(
            batches,
            dispatch_center_state,
            forecast,
        )


        (
            selected_batches,
            retained_batches,
        ) = self.allocator.allocate_resources(
            batches,
            available_vehicles,
            available_drivers,
        )

        self._update_retention_cycles(
            retained_batches,
        )

        self.validator.validate_output(
            selected_batches,
            retained_batches,
        )

        return (
            selected_batches,
            retained_batches,
        )