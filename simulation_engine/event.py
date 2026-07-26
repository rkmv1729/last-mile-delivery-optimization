"""
simulation_engine/event.py

Defines simulation events used by the event scheduler.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class EventType(str, Enum):
    """
    Supported simulation event types.
    """

    # Order lifecycle
    ORDER_CREATED = "order_created"
    ORDER_READY = "order_ready"
    ORDER_PICKUP = "order_pickup"
    ORDER_DELIVERED = "order_delivered"

    # Driver lifecycle
    DRIVER_AVAILABLE = "driver_available"
    DRIVER_RETURN_IDLE = "driver_return_idle"

    # Backend periodic events
    FORECAST = "forecast"
    DISPATCH = "dispatch"
    ASSIGNMENT = "assignment"

    # Simulation
    TICK = "tick"
    END_SIMULATION = "end_simulation"


@dataclass(order=True, slots=True)
class SimulationEvent:
    """
    Event stored inside the scheduler priority queue.

    Events are ordered by:
        1. scheduled_time
        2. priority
    """

    scheduled_time: datetime
    priority: int

    event_type: EventType = field(compare=False)
    payload: dict[str, Any] = field(default_factory=dict, compare=False)

    def __repr__(self) -> str:
        return (
            f"SimulationEvent("
            f"time={self.scheduled_time}, "
            f"type={self.event_type.value}, "
            f"priority={self.priority})"
        )