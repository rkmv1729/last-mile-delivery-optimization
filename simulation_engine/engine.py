"""
Simulation Engine
-----------------
Coordinates the complete event-driven simulation.

The engine orchestrates all simulation managers while
delegating business logic to the respective backend layers.
"""

from simulation_engine.state import SimulationState
from simulation_engine.scheduler import SimulationScheduler


class SimulationEngine:
    """
    Main simulation engine.
    """

    def __init__(self):

        self.state = SimulationState()

        self.scheduler = SimulationScheduler()

        # Managers
        self.order_manager = None
        self.driver_manager = None
        self.zone_manager = None
        self.forecast_manager = None
        self.dispatch_manager = None
        self.statistics_manager = None

    # ---------------------------------------------------------
    # Manager Registration
    # ---------------------------------------------------------

    def register_managers(
        self,
        order_manager=None,
        driver_manager=None,
        zone_manager=None,
        forecast_manager=None,
        dispatch_manager=None,
        statistics_manager=None,
    ):
        """
        Register simulation managers.
        """

        self.order_manager = order_manager
        self.driver_manager = driver_manager
        self.zone_manager = zone_manager
        self.forecast_manager = forecast_manager
        self.dispatch_manager = dispatch_manager
        self.statistics_manager = statistics_manager

    # ---------------------------------------------------------
    # Initialization
    # ---------------------------------------------------------

    def initialize(self):
        """
        Initialize all simulation managers.
        """

        managers = [
            self.zone_manager,
            self.driver_manager,
            self.dispatch_manager,
            self.forecast_manager,
            self.statistics_manager,
        ]

        for manager in managers:

            if manager and hasattr(manager, "initialize"):
                manager.initialize(self.state)

        self.state.log(
            "Simulation initialized."
        )

    # ---------------------------------------------------------
    # Simulation Controls
    # ---------------------------------------------------------

    # start simulation
    def start(self):
        """
        Start simulation.
        """

        self.initialize()

        self.state.running = True

        self.state.log(
            "Simulation started."
        )

    # pause simulation
    def pause(self):
        """
        Pause simulation.
        """

        self.state.running = False

        self.state.log(
            "Simulation paused."
        )

    # reset simulation
    def reset(self):
        """
        Reset simulation.
        """

        self.state.reset()

        self.state.log(
            "Simulation reset."
        )

    # change scheduler speed
    def set_speed(self, speed):
        """
        Set simulation speed.
        """

        self.scheduler.speed = speed

    # ---------------------------------------------------------
    # Internal Pipeline
    # ---------------------------------------------------------

    def _process_events(self):
        """
        Execute scheduled events.
        """

        self.scheduler.tick(self.state)

    def _process_orders(self):
        """
        Process orders and update operational zones.
        """

        if self.order_manager is None:
            return

        # Update order state (arrivals, expiries, etc.)
        self.order_manager.update(self.state)

        if self.zone_manager is None:
            return

        # Convert simulation orders to backend format
        orders_df = self.order_manager.to_dataframe(
            self.state,
        )

        if orders_df.empty:
            return

        # Run backend processing (H3 + Temporal + AHSI)
        order_zone_map = self.zone_manager.update(
            self.state,
            orders_df,
        )

        # Update simulation orders with backend outputs
        if order_zone_map is not None:
            self.order_manager.update_orders(
                self.state,
                order_zone_map,
            )

    def _process_forecast(self):
        """
        Process demand forecasting.
        """

        if self.forecast_manager is None:
            return

        orders_df = self.order_manager.to_dataframe(
            self.state,
        )

        if orders_df.empty:
            return

        forecast_results = self.forecast_manager.update(
            self.state,
            orders_df,
        )

        if forecast_results is not None:
            self.forecast_manager.update_zones(
                self.state,
                forecast_results,
            )

    def _process_dispatch(self):
        """
        Process dispatch decisions.
        """

        if self.dispatch_manager is None:
            return

        # Convert simulation orders to backend format
        orders_df = self.order_manager.to_dataframe(
            self.state,
        )

        if orders_df.empty:
            return

        # Run dispatch backend
        dispatch_results = self.dispatch_manager.update(
            self.state,
            orders_df,
        )

        # Update simulation dispatch centres
        if dispatch_results is not None:
            self.dispatch_manager.update_dispatch_centers(
                self.state,
                dispatch_results,
            )


    def _update_zones(self):

        orders_df = self.order_manager.to_dataframe(
            self.state,
        )

        order_zone_map = self.zone_manager.update(
            self.state,
            orders_df,
        )

        if order_zone_map is not None:

            self.order_manager.update_orders(
                self.state,
                order_zone_map,
            )

        

    def _run_forecast(self):

        if self.forecast_manager:
            self.forecast_manager.update(self.state)

    def _run_dispatch(self):

        if self.dispatch_manager:
            self.dispatch_manager.update(self.state)

    def _update_drivers(self):

        if self.driver_manager:
            self.driver_manager.update(self.state)

    def _update_statistics(self):

        if self.statistics_manager:
            self.statistics_manager.update(self.state)

    # ---------------------------------------------------------
    # Simulation Step
    # ---------------------------------------------------------

    def step(self):
        """
        Execute one simulation tick.
        """

        if not self.state.running:
            return

        # Execute scheduled events
        self._process_events()

        # Update simulation
        self._update_orders()

        self._update_zones()

        self._run_forecast()

        self._run_dispatch()

        self._update_drivers()

        self._update_statistics()

        self.state.event_history.append(
            f"Tick {self.state.tick} completed."
        )

    # ---------------------------------------------------------
    # Continuous Execution
    # ---------------------------------------------------------

    def run(self, max_steps=None):
        """
        Run continuously.
        """

        self.start()

        steps = 0

        while self.state.running:

            self.step()

            steps += 1

            if (
                max_steps is not None
                and steps >= max_steps
            ):
                self.stop()

    # ---------------------------------------------------------
    # Snapshot
    # ---------------------------------------------------------

    def snapshot(self):
        """
        Return current simulation state for UI.
        """

        return {
            "time": self.state.current_time,
            "tick": self.state.tick,
            "orders": self.state.orders,
            "drivers": self.state.drivers,
            "zones": self.state.zones,
            "vehicles": self.state.vehicles,
            "dispatch_centers": self.state.dispatch_centers,
            "statistics": self.statistics_manager.simulation_summary(self.state),
        }