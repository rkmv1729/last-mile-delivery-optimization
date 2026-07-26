from simulation_engine.state import SimulationState

from simulation_engine.entities.dispatch_centre import DispatchCenter
from simulation_engine.entities.vehicle import Vehicle
from simulation_engine.config import DISPATCH_INTERVAL

import pandas as pd


class DispatchManager:
    """
    Manages dispatch decisions within the simulation.
    """

    def __init__(
        self,
        backend,
    ):
        self.backend = backend

    # ------------------------------------------------------------------
    # Dispatch Center Management
    # ------------------------------------------------------------------

    def add_dispatch_center(
        self,
        state: SimulationState,
        dispatch_center: DispatchCenter,
        max_storage: int
    ):
        """
        Register a dispatch center in the simulation.
        """

        dispatch_center.storage_capacity = max_storage

        state.dispatch_centers[
            dispatch_center.center_id
        ] = dispatch_center

    def get_dispatch_center(
        self,
        state: SimulationState,
        dispatch_center_id: int,
    ):

        return state.dispatch_centers.get(
            dispatch_center_id
        )

    def get_all_dispatch_centers(
        self,
        state: SimulationState,
    ):

        return state.dispatch_centers.values()


    # ------------------------------------------------------------------
    # Vehicle Management
    # ------------------------------------------------------------------

    def add_vehicle(
        self,
        state: SimulationState,
        dispatch_center_id: int,
        vehicle: Vehicle,
    ):
        """
        Register a vehicle with a dispatch center.
        """

        dispatch_center = state.dispatch_centers.get(
            dispatch_center_id
        )

        if dispatch_center is None:
            return

        state.vehicles[vehicle.vehicle_id] = vehicle

        dispatch_center.available_vehicles[
            vehicle.vehicle_id
        ] = vehicle

    def get_available_vehicles(
        self,
        state: SimulationState,
        dispatch_center_id: int,
    ):

        dispatch_center = state.dispatch_centers.get(
            dispatch_center_id
        )

        if dispatch_center is None:
            return []

        return dispatch_center.available_vehicles.values()

    # ------------------------------------------------------------------
    # Storage Management
    # ------------------------------------------------------------------

    def initialize_storage(
        self,
        state: SimulationState,
        dispatch_center_id: int,
        initial_storage: int = 0,
    ):
        """
        Initialize the storage level of a dispatch center.
        """

        dispatch_center = state.dispatch_centers.get(
            dispatch_center_id
        )

        if dispatch_center is None:
            return

        dispatch_center.current_storage = initial_storage

    # ------------------------------------------------------------------
    # Dispatch Optimization
    # ------------------------------------------------------------------

    def update(
        self,
        orders_df: pd.DataFrame,
    ) -> pd.DataFrame | None:
        """
        Run the dispatch pipeline.
        """

        return self.backend.process_dispatch(orders_df)
    

    '''   def update_dispatch_centers(
        self,
        state: SimulationState,
        dispatch_results: pd.DataFrame,
    ):
        """
        Update simulation dispatch centres with
        dispatch decisions.
        """

        for _, row in dispatch_results.iterrows():

            dispatch_center = state.dispatch_centers.get(
                row["dispatch_center_id"],
            )

            if dispatch_center is None:
                continue

            dispatch_center.dispatch_status = row["dispatch_status"]
            dispatch_center.retained_orders = row["retained_orders"]
            dispatch_center.dispatched_orders = row["dispatched_orders"]
            dispatch_center.vehicle_type = row["vehicle_type"]
            dispatch_center.dispatch_score = row["dispatch_score"] '''

    # ------------------------------------------------------------------
    # Decision Application
    # ------------------------------------------------------------------

    def _apply_dispatch_results(
        self,
        state,
        decisions
    ):
        for batch, decision in decisions.items():

            dispatch_center = state.dispatch_centers.get(
                batch.dispatch_center
            )

            if dispatch_center is None:
                continue

            if decision == 1:
                dispatch_center.active_batches[batch.batch_id] = batch
                state.batches[batch.batch_id] = batch

            else:
                # Update retention history for each retained order
                for order_id in batch.order_ids:

                    order = state.orders.get(order_id)

                    if order is not None:
                        order.retention_cycles += 1

                dispatch_center.retained_batches[batch.batch_id] = batch

            dispatched = sum(decision == 1 for decision in decisions.values())
            retained = len(decisions) - dispatched

            state.log(
                f"Dispatch completed: {dispatched} dispatched, {retained} retained."
            )

    # ------------------------------------------------------------------
    # Batch Lookup
    # ------------------------------------------------------------------

    def get_dispatch_center_batches(
        self,
        state: SimulationState,
        dispatch_center_id: int,
    ):

        dispatch_center = state.dispatch_centers.get(
            dispatch_center_id
        )

        if dispatch_center is None:
            return []

        return dispatch_center.active_batches.values()

    def get_all_batches(
        self,
        state: SimulationState,
    ):

        batches = []

        for dispatch_center in state.dispatch_centers.values():
            batches.extend(
                dispatch_center.active_batches.values()
            )

        return batches

    def retained_batches_to_dataframe(self) -> pd.DataFrame:
        """
        Convert all retained batches across dispatch centres into
        an order-level DataFrame for the dispatch backend.
        """

        rows = []

        for dispatch_center in self.backend.state.dispatch_centers.values():

            for batch in dispatch_center.retained_batches:

                for order_id in batch.order_ids:

                    order = self.backend.state.orders.get(order_id)

                    if order is None:
                        continue

                    row = order.to_dict()

                    rows.append(row)

        return pd.DataFrame(rows)