from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

from simulation_engine.config import OrderStatus


@dataclass
class Order:
    """
    Represents a customer order in the simulation.
    """

    # ------------------------------------------------------------------
    # Basic Information
    # ------------------------------------------------------------------

    order_id: int
    customer_id: int

    created_time: datetime

    # ------------------------------------------------------------------
    # Order Details
    # ------------------------------------------------------------------

    products: List[dict]

    priority_score: float = 0.0

    retention_cycles: int = 0

    # ------------------------------------------------------------------
    # Delivery Location
    # ------------------------------------------------------------------

    latitude: float
    longitude: float

    h3_cell_7: Optional[str] = None
    h3_cell_8: Optional[str] = None
    zone_id: Optional[str] = None
    dispatch_centre: Optional[int] = None

    # ------------------------------------------------------------------
    # Assignment
    # ------------------------------------------------------------------

    driver_id: Optional[int] = None

    batch_id: Optional[int] = None

    # ------------------------------------------------------------------
    # Simulation State
    # ------------------------------------------------------------------

    status: OrderStatus = OrderStatus.PLACED

    expected_delivery_time: Optional[datetime] = None

    service_time: Optional[float] = None

    delivered_time: Optional[datetime] = None

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """
        Convert the order into a dictionary for backend processing.
        """

        return {
            "order_id": self.order_id,
            "priority_score": self.priority_score,
            "retention_cycles": self.retention_cycles,
            "customer_id": self.customer_id,
            "timestamp": self.created_time,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "products": self.products,
            "status": self.status,
        }

    def to_display_dict(self) -> dict:
        """
        Convert the order into a dictionary for UI display.
        """

        return {
            "Order ID": self.order_id,
            "Customer": self.customer_id,
            "Priority Score": self.priority_score, 
            "Retention Cycles": self.retention_cycles,
            "Status": self.status.name, 
            "Zone": self.destination_zone or "-",
            "Dispatch Centre": self.dispatch_centre,
            "Driver": self.driver_id or "-",
            "Batch": self.batch_id or "-",
            "ETA": self.expected_delivery_time or "-",
            "Delivered": self.delivered_time or "-",
        }
    