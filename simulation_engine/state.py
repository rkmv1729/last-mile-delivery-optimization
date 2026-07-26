"""
Simulation State
----------------
Maintains the current state of the event-driven simulation.

Every manager reads from and updates this state object.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta

from typing import Dict, List, Optional

from simulation_engine.entities.order import Order
from simulation_engine.entities.driver import Driver
from simulation_engine.entities.zone import Zone
from simulation_engine.entities.vehicle import Vehicle
from dispatch_engine.batch import Batch
from simulation_engine.entities.dispatch_centre import DispatchCenter
from simulation_engine.event import SimulationEvent

from simulation_engine.config import (
    SIMULATION_START_TIME,
    Shift
)

from simulation_engine.entities.zone import Sh

@dataclass
class SimulationState:
    """
    Central state shared across the simulation engine.
    """

    # ==========================================================
    # Simulation Clock
    # ==========================================================

    current_time: datetime = field(
        default_factory=lambda: datetime.strptime(
            SIMULATION_START_TIME,
            "%Y-%m-%d %H:%M:%S",
        )
    )

    tick: int = 0
    running: bool = False
    current_shift: Shift = Shift.MORNING

    # ==========================================================
    # Dynamic Entities
    # ==========================================================

    orders: Dict[int, Order] = field(default_factory=dict)

    batches: Dict[int, Batch] = field(default_factory=dict)

    pending_orders: Dict[int, Order] = field(default_factory=dict)

    active_orders: Dict[int, Order] = field(default_factory=dict)

    completed_orders: Dict[int, Order] = field(default_factory=dict)

    cancelled_orders: Dict[int, Order] = field(default_factory=dict)

    drivers: Dict[int, Driver] = field(default_factory=dict)

    vehicles: Dict[int, Vehicle] = field(default_factory=dict)

    zones: Dict[str, Zone] = field(default_factory=dict)

    dispatch_centers: Dict[int, DispatchCenter] = field(default_factory=dict)

    event_history: List[SimulationEvent] = field(default_factory=list)

    # pending_events: List = field(default_factory=list)

    # ==========================================================
    # Backend Layer Outputs
    # ==========================================================

    demand_forecast: Optional[dict] = None

    dispatch_plan: Optional[dict] = None

    zone_assignments: Optional[dict] = None

    # ==========================================================
    # Simulation Statistics
    # ==========================================================

    statistics: dict = field(
        default_factory=lambda: {
            "orders_created": 0,
            "orders_completed": 0,
            "orders_cancelled": 0,
            "active_drivers": 0,
            "completed_deliveries": 0,
            "simulation_minutes": 0,
        }
    )

    # TODO : Add the registration function in respective managers


    # ==========================================================
    # Helper Methods
    # ==========================================================

    @property
    def status(self):
        return "Running" if self.running else "Stopped"

    def update_shift(self):
        """
        Update the current simulation shift based on the simulation time.
        """

        hour = self.current_time.hour

        if 6 <= hour < 14:
            self.current_shift = Shift.MORNING

        elif 14 <= hour < 18:
            self.current_shift = Shift.AFTERNOON

        else:
            self.current_shift = Shift.EVENING

    def advance_time(self, minutes=1):
        """
        Advance simulation clock.
        """
        self.current_time += timedelta(minutes=minutes)
        self.tick += 1
        self.statistics["simulation_minutes"] += minutes

        self.update_shift()

        
    def reset(self):
        """
        Reset simulation state.
        """

        self.orders.clear()
        self.pending_orders.clear()
        self.active_orders.clear()
        self.completed_orders.clear()
        self.cancelled_orders.clear()

        self.drivers.clear()
        self.vehicles.clear()
        self.dispatch_centers.clear()
        self.zones.clear()

        self.event_history.clear()

        self.demand_forecast = None
        self.dispatch_plan = None
        self.zone_assignments = None

        # Use a DEFAULT_STATISTICS constant to reset this
        self.statistics = {
            "orders_created": 0,
            "orders_completed": 0,
            "orders_cancelled": 0,
            "active_drivers": 0,
            "completed_deliveries": 0,
            "simulation_minutes": 0,
        }

        self.tick = 0
        self.running = False

        self.current_time = datetime.strptime(
            SIMULATION_START_TIME,
            "%Y-%m-%d %H:%M:%S",
        )

        self.update_shift()

    
    def log(self, message: str):
        """
        Add an entry to simulation history.
        """

        self.event_history.append(message)



