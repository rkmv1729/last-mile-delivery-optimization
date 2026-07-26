from simulation_engine.state import SimulationState
from simulation_engine.config import STATISTICS_UPDATE_INTERVAL

class StatisticsManager:
    """
    Tracks simulation statistics and performance metrics.
    """

    # ------------------------------------------------------------------
    # Order Statistics
    # ------------------------------------------------------------------

    def total_orders(
        self,
        state: SimulationState,
    ):

        return len(state.orders)

    def pending_orders(
        self,
        state: SimulationState,
    ):

        return len(state.pending_orders)

    def active_orders(
        self,
        state: SimulationState,
    ):

        return len(state.active_orders)

    def completed_orders(
        self,
        state: SimulationState,
    ):

        return len(state.completed_orders)

    def cancelled_orders(
        self,
        state: SimulationState,
    ):

        return len(state.cancelled_orders)

    # ------------------------------------------------------------------
    # Driver Statistics
    # ------------------------------------------------------------------

    def total_drivers(
        self,
        state: SimulationState,
    ):

        return len(state.drivers)

    def available_drivers(
        self,
        state: SimulationState,
    ):

        return sum(
            driver.available
            for driver in state.drivers.values()
        )

    def busy_drivers(
        self,
        state: SimulationState,
    ):

        return self.total_drivers(state) - self.available_drivers(state)

    # ------------------------------------------------------------------
    # Zone Statistics
    # ------------------------------------------------------------------

    def total_zones(
        self,
        state: SimulationState,
    ):

        return len(state.zones)

    # ------------------------------------------------------------------
    # Dispatch Statistics
    # ------------------------------------------------------------------

    def active_batches(
        self,
        state: SimulationState,
    ):

        total = 0

        for dispatch_center in state.dispatch_centers.values():
            total += len(dispatch_center.active_batches)

        return total

    def retained_batches(
        self,
        state: SimulationState,
    ):
        total = 0

        for dispatch_center in state.dispatch_centers.values():
            total += len(dispatch_center.retained_batches)

        return total

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def simulation_summary(
        self,
        state: SimulationState,
    ):

        return {
            "simulation_time": state.current_time,
            "tick": state.tick,
            "orders": self.total_orders(state),
            "pending_orders": self.pending_orders(state),
            "active_orders": self.active_orders(state),
            "completed_orders": self.completed_orders(state),
            "cancelled_orders": self.cancelled_orders(state),
            "drivers": self.total_drivers(state),
            "available_drivers": self.available_drivers(state),
            "busy_drivers": self.busy_drivers(state),
            "zones": self.total_zones(state),
            "active_batches": self.active_batches(state),
            "retained_batches": self.retained_batches(state),
        }

    def update(
        self,
        state: SimulationState,
    ):
        """
        Refresh simulation statistics.
        """
        if state.tick % STATISTICS_UPDATE_INTERVAL == 0: 
            state.statistics = self.simulation_summary(state)