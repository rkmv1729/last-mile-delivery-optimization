from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

from simulation_engine.config import DriverStatus, VehicleType


@dataclass
class Driver:
    """
    Represents a delivery driver in the simulation.
    """

    # ------------------------------------------------------------------
    # Basic Information
    # ------------------------------------------------------------------

    driver_id: int

    name: Optional[str] = None

    vehicle_id: Optional[int] = None

    vehicle_type: VehicleType

    status: DriverStatus = DriverStatus.IDLE

    # ------------------------------------------------------------------
    # Current Location
    # ------------------------------------------------------------------

    # latitude: float = 0.0

    # longitude: float = 0.0

    # current_zone: Optional[str] = None

    # ------------------------------------------------------------------
    # Availability
    # ------------------------------------------------------------------

    current_batch: Optional[int] = None

    # assigned_time : Optional[int] = None

    assigned_zone: Optional[str] = None

    # ------------------------------------------------------------------
    # Simulation
    # ------------------------------------------------------------------

    remaining_service_time: float = 0.0

    completed_orders: int = 0

    # total_distance: float = 0.0

    # ------------------------------------------------------------------
    # Historical Information
    # ------------------------------------------------------------------

    familiarity_profile: dict = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    metadata: dict = field(default_factory=dict)

    def to_display_dict(self) -> dict:
        return {
            "Driver ID": self.driver_id,
            "Name": self.name or "-",
            "Status": self.status.name,
            "Vehicle ID": self.vehicle_id,
            "Vehicle type": self.vehicle_type,
            "Assigned Zone": self.assigned_zone or "-",
            "Current Batch": self.current_batch or "-",
            "Completed Orders": self.completed_orders,
        }

    # TODO : bring non-default fields before deafult fields