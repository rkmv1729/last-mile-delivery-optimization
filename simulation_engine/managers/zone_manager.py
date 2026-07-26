from simulation_engine.state import SimulationState
from simulation_engine.entities.zone import Zone

import pandas as pd

from simulation_engine.config import ZONE_UPDATE_INTERVAL

class ZoneManager:
    """
    Manages operational zones within the simulation.
    """

    def __init__(self, 
        order_manager=None, 
        backend=None
    ):
        """
        Parameters
        ----------
        ahsi_engine
            Adaptive H3 Spatial Indexing engine.
        """

        self.backend = backend
        self.order_manager = order_manager

    # ------------------------------------------------------------------
    # Zone Generation
    # ------------------------------------------------------------------

    def update_zones(
        self,
        state: SimulationState,
        zone_mapping: pd.DataFrame,
    ):
        """
        Update operational zones from the backend zone mapping.
        """

        # TODO:
        # Preserve existing Zone objects across AHSI updates.
        # Currently this recreates zones and does not handle:
        # - retaining runtime state
        # - removed zones
        # - merged/split zone transitions

        state.zones = {}

        for zone_id, group in zone_mapping.groupby("zone_id"):

            h3_cells = [
                {
                    "cell_id": row["cell_id"],
                    "resolution": row["resolution"],
                }
                for _, row in group.iterrows()
            ]

            state.zones[zone_id] = Zone(
                zone_id=zone_id,
                h3_cells=h3_cells,
            )

    def update(
        self,
        state: SimulationState,
        orders_df: pd.DataFrame,
    ):
        """
        Periodically update operational zones using the backend AHSI pipeline.
        """
        if state.current_tick % ZONE_UPDATE_INTERVAL != 0:
            return

        if orders_df.empty:
            return

        zone_mapping, order_zone_map = self.backend.process_orders(
            orders_df,
        )

        if zone_mapping is None:
            return

        self.update_zones(
            state,
            zone_mapping,
        )

        return order_zone_map

    # ------------------------------------------------------------------
    # Batch Assignment
    # ------------------------------------------------------------------

    def assign_batch_to_zone(
        self,
        state: SimulationState,
        batch_id: int,
        zone_id: str,
    ):

        batch = state.batches.get(batch_id)
        zone = state.zones.get(zone_id)

        if batch is None or zone is None:
            return

        batch.operational_zone = zone_id

        # Assign every order in the batch
        for order in batch.orders:

            order.operational_zone = zone_id
            zone.active_orders[order.order_id] = order

        # Register batch in zone
        zone.active_batches[batch_id] = batch

        state.log(
            f"Batch {batch_id} assigned to Zone {zone_id}."
    )

    # ------------------------------------------------------------------
    # Zone Lookup
    # ------------------------------------------------------------------

    def get_zone(
        self,
        state: SimulationState,
        zone_id: str,
    ):

        return state.zones.get(zone_id)

    def get_all_zones(
        self,
        state: SimulationState,
    ):

        return state.zones.values()

    # ------------------------------------------------------------------
    # Zone Statistics
    # ------------------------------------------------------------------

    def active_order_count(
        self,
        state: SimulationState,
        zone_id: str,
    ):

        return len(state.zones[zone_id].active_orders)
