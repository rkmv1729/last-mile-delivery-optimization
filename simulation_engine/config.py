"""
Simulation Engine Configuration
-------------------------------
Contains constants governing the behaviour of the
event-driven simulation engine.

This configuration is independent of backend layer
implementations.
"""

from pathlib import Path

# ============================================================
# Simulation Clock
# ============================================================

SIMULATION_START_TIME = "2024-01-01 08:00:00"
SIMULATION_TIME_STEP_MINUTES = 1
SIMULATION_SPEED = 1.0  # 1x real-time equivalent


# ============================================================
# Scheduler Intervals (Minutes)
# ============================================================

ORDER_PROCESS_INTERVAL = 1
ZONE_UPDATE_INTERVAL = 5
DISPATCH_INTERVAL = 5
FORECAST_INTERVAL = 60
STATISTICS_UPDATE_INTERVAL = 1


# ============================================================
# Driver Configuration
# ============================================================

INITIAL_DRIVER_COUNT = 12
DRIVER_SHIFT_DURATION_HOURS = 8
DRIVER_REST_DURATION_MINUTES = 30

DEFAULT_DRIVER_SPEED_KMPH = 25.0


# ============================================================
# Dispatch Centre Configuration
# ============================================================

INITIAL_DISPATCH_CENTERS = 1
INITIAL_DISPATCH_STORAGE = 500


# ============================================================
# Order Configuration
# ============================================================

ORDER_EXPIRY_MINUTES = 45
MAX_PENDING_ORDERS = 10000


# ============================================================
# Delivery Simulation
# ============================================================

DEFAULT_SERVICE_TIME_MINUTES = 8
PICKUP_BUFFER_MINUTES = 2
DELIVERY_TIME_BIAS_MINUTES = 3


# ============================================================
# UI Refresh
# ============================================================

DASHBOARD_REFRESH_INTERVAL = 1
MAP_REFRESH_INTERVAL = 1


# ============================================================
# Randomness
# ============================================================

RANDOM_SEED = 42


# ============================================================
# Order status
# ============================================================

PENDING = "Pending"
ACTIVE = "Active"
COMPLETED = "Completed"


# ============================================================
# Logging
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = PROJECT_ROOT / "simulation_engine" / "logs"
LOG_FILE = LOG_DIR / "simulation_engine.log"


PICKUP_TIME = 5

DELIVERY_TIME = 18

RETURN_TIME = 6


# Enumerations
from enum import Enum


class BatchStatus(str, Enum):
    RETAINED = "retained"
    DISPATCHED = "dispatched"


class Shift(str, Enum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"

class VehicleType(str, Enum):
    BIKE = "bike"
    VAN = "van"


class DriverStatus(str, Enum):
    """
    Driver operational states.
    """

    IDLE = "idle"

    ASSIGNED = "assigned"

    # TRAVELLING_TO_PICKUP = "travelling_to_pickup"

    # PICKING_UP = "picking_up"

    DELIVERING = "delivering"

    DELIVERY_COMPLETE = "delivery_complete"

    RETURNING = "returning"

    # OFFLINE = "offline"

class OrderStatus(str, Enum):
    """
    Order lifecycle within the simulation.
    """

    PLACED = "placed"

    BATCHED = "batched"

    OUT_FOR_DELIVERY = "out_for_delivery"

    DELIVERED = "delivered"