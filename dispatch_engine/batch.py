"""
batch.py

Core batch entity used throughout the Dispatch Engine.

This module defines the Batch data structure, which encapsulates all
information associated with a dispatch batch. Optimization scores and
resource assignments are computed by other modules.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from simulation_engine.config import BatchStatus, Shift, VehicleType


@dataclass
class Batch:
    """
    Represents a dispatch batch.

    Attributes
    ----------
    batch_id : str
        Unique identifier for the batch.

    dispatch_center : str
        Dispatch center responsible for this batch.

    destination_zone : str
        Operational zone to which the batch will be delivered.

    order_ids : List[str]
        List of customer order IDs included in the batch.

    batch_size : int
        Total quantity/items in the batch.

    order_count : int
        Number of customer orders.

    creation_time : datetime
        Time when the batch was created.

    predicted_dispatch_shift : str
        Forecasted shift for dispatch.

    status : enum
        Current batch status.

    assigned_driver : Optional[str]
        Driver allocated to the batch.

    optimization_score : Optional[float]
        Final Batch Utility Score (BUS), assigned during optimization.

    metadata : Dict[str, Any]
        Additional extensible information.
    """

    batch_id: str
    dispatch_center: int
    zone_id: str
    order_ids: List[int]


    batch_size: int
    order_count: int

    creation_time: datetime
    scheduled_shift: Shift

    status: BatchStatus

    assigned_driver: Optional[int] = None

    assigned_vehicle: Optional[int] = None

    vehicle_type: Optional[VehicleType] = None


    optimization_score: Optional[float] = None

    metrics: Dict[str, float] = field(default_factory=dict)

    metadata: Dict[str, Any] = field(default_factory=dict)

    def remaining_capacity(self, vehicle_capacity: int) -> int:
        """Returns remaining capacity for a given vehicle."""
        return max(vehicle_capacity - self.batch_size, 0)

    def is_full(self, vehicle_capacity: int) -> bool:
        """Checks whether the batch has reached vehicle capacity."""
        return self.batch_size >= vehicle_capacity

    def to_dict(self) -> Dict[str, Any]:
        """Converts the Batch object into a dictionary."""
        return {
            "batch_id": self.batch_id,
            "dispatch_center": self.dispatch_center,
            "zone_id": self.zone_id,
            "order_ids": self.order_ids,
            "batch_size": self.batch_size,
            "order_count": self.order_count,
            "creation_time": self.creation_time,
            "scheduled_shift": self.scheduled_shift.name,
            "status": self.status.name,
            "assigned_driver": self.assigned_driver,
            "assigned_vehicle": self.assigned_vehicle,
            "optimization_score": self.optimization_score,
            "metrics" : self.metrics,
            "metadata": self.metadata,
        }

    def to_display_dict(self):
        return {
            "Batch": self.batch_id,
            "Status": self.status.value if hasattr(self.status, "value") else self.status,
            "Orders": self.order_count,
            "Size": self.batch_size,
            "Zone": self.zone_id,
            "Dispatch Centre": self.dispatch_center,
            "Driver": self.assigned_driver or "-",
            "Vehicle": self.assigned_vehicle or "-",
            "Score": (
                round(self.optimization_score, 2)
                if self.optimization_score is not None
                else "-"
            ),
        }