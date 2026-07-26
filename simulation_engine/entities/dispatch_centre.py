from dataclasses import dataclass, field
from typing import Optional, List, Dict

from simulation_engine.entities.driver import Driver
from simulation_engine.entities.vehicle import Vehicle
from simulation_engine.entities.zone import Zone

from dispatch_engine.batch import Batch

from simulation_engine.config import INITIAL_DISPATCH_STORAGE



@dataclass
class DispatchCenter:
    """
    Represents a dispatch center in the simulation.
    """

    # ------------------------------------------------------------------
    # Basic Information
    # ------------------------------------------------------------------

    center_id: int

    name: str

    latitude: float

    longitude: float

    # ------------------------------------------------------------------
    # Current Resources
    # ------------------------------------------------------------------

    available_drivers: Dict[int, Driver] = field(default_factory=dict)

    available_vehicles: Dict[int, Vehicle] = field(default_factory=dict)

    active_batches: Dict[int, Batch] = field(default_factory=dict)

    retained_batches: Dict[int, Batch] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Storage State
    # ------------------------------------------------------------------

    current_storage: int = 0

    storage_capacity: int = INITIAL_DISPATCH_STORAGE

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    dispatched_batches: int = 0

    dispatched_orders: int = 0

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    metadata: dict = field(default_factory=dict)

    def to_display_dict(self) -> dict:
        return {
            "Centre": self.name,
            "Drivers": len(self.available_drivers),
            "Vehicles": len(self.available_vehicles),
            "Active Batches": len(self.active_batches),
            "Retained Batches": len(self.retained_batches),
            "Storage": f"{self.current_storage}/{self.storage_capacity}",
        }

    