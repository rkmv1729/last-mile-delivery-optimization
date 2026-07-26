from simulation_engine.state import SimulationState
from simulation_engine.entities.driver import Driver, DriverStatus

from datetime import timedelta

from simulation_engine.event import (
    EventType,
    SimulationEvent,
)

from simulation_engine.config import (
    PICKUP_TIME,
    DELIVERY_TIME,
    RETURN_TIME,
)

class DriverManager:
    """
    Manages drivers throughout the simulation.
    """

    def __init__(
        self,
        scheduler,
        zone_assignment_engine=None,
    ):
        self.scheduler = scheduler
        self.zone_assignment_engine = zone_assignment_engine

    # ------------------------------------------------------------------
    # Driver Registration
    # ------------------------------------------------------------------

    def add_driver(
        self,
        state: SimulationState,
        driver: Driver,
    ):

        state.drivers[driver.driver_id] = driver

        state.log(
            f"Driver {driver.driver_id} registered."
        )

    # ------------------------------------------------------------------
    # Driver Lookup
    # ------------------------------------------------------------------

    def get_driver(
        self,
        state: SimulationState,
        driver_id: int,
    ):

        return state.drivers.get(driver_id)

    def get_all_drivers(
        self,
        state: SimulationState,
    ):

        return state.drivers.values()

    def get_available_drivers(
        self,
        state: SimulationState,
    ):

        return [
            driver
            for driver in state.drivers.values()
            if driver.available
        ]

    # ------------------------------------------------------------------
    # Driver Status
    # ------------------------------------------------------------------

    def assign_driver(
        self,
        state: SimulationState,
        driver_id: int,
        batch_id: int,
    ):

        # check if driver is available
        # change order status to "out for delivery"
        driver = state.drivers.get(driver_id)

        if driver is None:
            return

        driver.status = DriverStatus.ASSIGNED
        driver.available = False
        driver.current_batch = batch_id

        pickup_time = state.current_time + timedelta(
        minutes=PICKUP_TIME
        )

        self.scheduler.schedule_event(
            SimulationEvent(
                scheduled_time=pickup_time,
                priority=2,
                event_type=EventType.ORDER_PICKUP,
                payload={
                    "driver_id": driver_id,
                    "batch_id": batch_id,
                },
            )
        )

        state.log(
            f"Driver {driver_id} assigned to Batch {batch_id}."
        )

    # ------------------------------------------------------------------
    # Pickup
    # ------------------------------------------------------------------

    def pickup_order(
        self,
        state: SimulationState,
        driver_id: str,
        order_id: str,
    ) -> None:
        """
        Driver picks up an order.
        """

        driver = state.drivers[driver_id]

        if driver is None:
            return

        driver.status = DriverStatus.PICKING_UP

        delivery_time = state.current_time + timedelta(
            minutes=DELIVERY_TIME
        )

        self.scheduler.schedule_event(
            SimulationEvent(
                scheduled_time=delivery_time,
                priority=1,
                event_type=EventType.ORDER_DELIVERED,
                payload={
                    "driver_id": driver_id,
                    "order_id": order_id,
                },
            )
        )


    # ------------------------------------------------------------------
    # Delivery Complete
    # ------------------------------------------------------------------

    def complete_delivery(
        self,
        state: SimulationState,
        driver_id: str,
        order_id: str,
    ) -> None:
        """
        Complete delivery.
        """

        driver = state.drivers[driver_id]

        driver.completed_orders += 1

        driver.current_batch = None

        driver.status = DriverStatus.DELIVERY_COMPLETE

        idle_time = state.current_time + timedelta(
            minutes=RETURN_TIME
        )

        self.scheduler.schedule_event(
            SimulationEvent(
                scheduled_time=idle_time,
                priority=3,
                event_type=EventType.DRIVER_RETURN_IDLE,
                payload={
                    "driver_id": driver_id,
                },
            )
        )

    # ------------------------------------------------------------------
    # Return Idle
    # ------------------------------------------------------------------

    def return_idle(
        self,
        state: SimulationState,
        driver_id: str,
    ) -> None:
        """
        Return driver to idle state.
        """

        driver = state.drivers[driver_id]

        driver.status = DriverStatus.IDLE
        driver.available = True

        driver.current_order = None


    # ------------------------------------------------------------------
    # Availability
    # ------------------------------------------------------------------

    def update_availability(
        self,
        state: SimulationState,
        driver_id: str,
        available: bool,
    ) -> None:
        """
        Update driver availability.
        """

        driver = state.drivers[driver_id]

        driver.available = available


    def complete_delivery_batch(
        self,
        state: SimulationState,
        driver_id: int,
    ):
        driver = state.drivers.get(driver_id)

        if driver is None or driver.current_batch is None:
            return

        batch = state.batches.get(driver.current_batch)

        # Mark all orders in batch completed
        for order in batch.orders:
            # self.complete_delivery_order(state, order)
            # order manager delegation
            pass

        state.batches.pop(batch.batch_id, None)

        driver.current_batch = None
        driver.available = True
        driver.completed_orders += len(batch.orders)

        state.log(
            f"Driver {driver_id} completed Batch {batch.batch_id}."
        )

    def update(self, state):
        """
        Update driver states every simulation tick.
        """

        self.assign_zones(state)

    # ------------------------------------------------------------------
    # Familiarity
    # ------------------------------------------------------------------

    def load_familiarity_profile(
        self,
        state: SimulationState,
        driver_id: int,
        profile: dict,
    ):

        state.drivers[driver_id].familiarity_profile = profile

    # ------------------------------------------------------------------
    # Zone Assignment
    # ------------------------------------------------------------------

    def assign_zones(
        self,
        state: SimulationState,
    ):
        """
        Assign available drivers to the latest
        operational zones.
        """

        if self.zone_assignment_engine is None:
            return

        assignments = self.zone_assignment_engine.assign(
            zones=list(state.zones.values()),
            drivers=self.get_available_drivers(state),
        )

        state.zone_assignments = assignments

        # Update driver objects
        for assignment in assignments:

            driver = state.drivers.get(assignment.driver_id)

            if driver is None:
                continue

            driver.assigned_zone = assignment.zone_id

        state.log(
            f"Assigned {len(assignments)} drivers to operational zones."
        )

        return assignments
