"""
===========================================================================
Resource Allocator
===========================================================================

Performs Stage-2 Dispatch Optimization.

Responsibilities
----------------
1. Assign required vehicle type to each candidate batch.
2. Solve Binary ILP for dispatch selection.
3. Respect vehicle and driver availability.
4. Return selected and retained batches.
===========================================================================
"""

from pulp import (
    LpProblem,
    LpVariable,
    LpBinary,
    LpMaximize,
    lpSum,
    PULP_CBC_CMD,
    LpStatus,
)

from dispatch_engine.config import (
    BIKE_CAPACITY,
    VAN_CAPACITY,
)
from dispatch_engine.batch import Batch

from simulation_engine.config import VehicleType
from simulation_engine.config import BatchStatus


class ResourceAllocator:
    """
    Stage-2 Resource Allocator.
    """

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def allocate_resources(
        self,
        batches: list[Batch],
        available_vehicles,
        available_drivers,
    ):
        """
        Allocate resources using Binary ILP.
        """

        if not batches:
            return [], []

        self._assign_vehicle_types(batches)

        problem = LpProblem(
            "Dispatch_Optimization",
            LpMaximize,
        )

        variables = {

            batch.batch_id:

            LpVariable(
                f"x_{batch.batch_id}",
                cat=LpBinary,
            )

            for batch in batches

        }

        # Objective
        problem += lpSum(

            batch.optimization_score
            * variables[batch.batch_id]

            for batch in batches

        )

        # Vehicle constraints
        for vehicle_type, available in available_vehicles.items():

            problem += (

                lpSum(

                    variables[batch.batch_id]

                    for batch in batches

                    if batch.vehicle_type == vehicle_type

                )

                <= available

            )

        # Driver constraint
        problem += (

            lpSum(

                variables[batch.batch_id]

                for batch in batches

            )

            <= available_drivers

        )

        problem.solve(
            PULP_CBC_CMD(msg=False)
        )

        if LpStatus[problem.status] != "Optimal":
            raise RuntimeError(
                f"Optimization failed: {LpStatus[problem.status]}"
            )

        selected_batches = []
        retained_batches = []

        for batch in batches:

            if variables[
                batch.batch_id
            ].varValue == 1:

                batch.status = BatchStatus.DISPATCHED

                selected_batches.append(batch)

            else:

                batch.status = BatchStatus.RETAINED

                retained_batches.append(batch)

        return (
            selected_batches,
            retained_batches,
        )

    # ------------------------------------------------------------------ #
    # Vehicle Assignment
    # ------------------------------------------------------------------ #

    def _assign_vehicle_types(
        self,
        batches,
    ):
        """
        Assign the smallest feasible vehicle type.
        """

        for batch in batches:

            if batch.batch_size <= BIKE_CAPACITY:

                batch.vehicle_type = VehicleType.BIKE

            elif batch.batch_size <= VAN_CAPACITY:

                batch.vehicle_type = VehicleType.VAN

            else:
                raise ValueError(
                    f"Batch {batch.batch_id} exceeds maximum vehicle capacity."
                )