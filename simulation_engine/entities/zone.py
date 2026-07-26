from dataclasses import dataclass, field
from typing import List, Optional, Dict 

from simulation_engine.entities.order import Order
from dispatch_engine.batch import Batch


@dataclass
class Zone:
    """
    Represents an operational zone.
    """

    # ------------------------------------------------------------------
    # Basic Information
    # ------------------------------------------------------------------

    zone_id: str

    shift: str

    # ------------------------------------------------------------------
    # Spatial Information
    # ------------------------------------------------------------------

    h3_cells: List[dict] = field(default_factory=list)

    centroid_latitude: float = 0.0

    centroid_longitude: float = 0.0

    # ------------------------------------------------------------------
    # Demand
    # ------------------------------------------------------------------

    predicted_demand: float = 0.0

    # ------------------------------------------------------------------
    # Dispatch
    # ------------------------------------------------------------------

    active_batches: Dict[int, Batch] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    completed_orders: int = 0

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    metadata: dict = field(default_factory=dict)

    def to_display_dict(self) -> dict:
        return {
            "Zone": self.zone_id,
            "Shift": self.shift.value,
            "Predicted Demand": round(self.predicted_demand, 2),
            "Active Batches": len(self.active_batches),
            "Completed Orders": self.completed_orders,
        }