from dataclasses import dataclass
from typing import Optional

from simulation_engine.entities.driver import VehicleType


@dataclass
class Vehicle:
    """
    Represents a delivery vehicle in the simulation.
    """

    # ------------------------------------------------------------------
    # Basic Information
    # ------------------------------------------------------------------

    vehicle_id: int

    vehicle_type: VehicleType

    capacity: int

    # ------------------------------------------------------------------
    # Current Status
    # ------------------------------------------------------------------

    available: bool = True

    current_load: int = 0


    # ------------------------------------------------------------------
    # Simulation Statistics
    # ------------------------------------------------------------------

    # total_trips: int = 0

    # total_distance: float = 0.0