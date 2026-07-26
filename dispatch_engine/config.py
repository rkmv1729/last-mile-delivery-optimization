"""
===========================================================================
Dispatch Engine Configuration
===========================================================================

Centralized configuration for the Dispatch Engine.

This module contains only configurable constants used across the complete
Dispatch Engine pipeline.

Pipeline
--------
1. Batch Formation Optimization (EPS-based)
2. Batch Utility Evaluation (BUS-based)
3. Resource Allocation
4. Dispatch Decision

No computation or business logic should be placed here.

Sections
--------
1. Vehicle Configuration
2. Dispatch Centre Configuration
3. Dispatch Policies
4. Batch Formation
5. Effective Product Score (EPS)
6. Batch Utility Score (BUS)
7. Resource Generation
8. Output Configuration
===========================================================================
"""

from pathlib import Path


# =============================================================================
# Vehicle Configuration
# =============================================================================

# Standardized carrying capacities (Normalized Cargo Units)

BIKE = "BIKE"
VAN = "VAN"

VAN_CAPACITY = 100
BIKE_CAPACITY = 20

# Minimum vehicle utilization before dispatch
# (May be overridden by high-priority batches)

MIN_VEHICLE_UTILIZATION = 0.80


# =============================================================================
# Dispatch Centre Configuration
# =============================================================================

# Maximum storage capacity (Normalized Cargo Units)

DISPATCH_CENTER_STORAGE_CAPACITY = 5000

# Storage thresholds

STORAGE_WARNING_THRESHOLD = 0.80
STORAGE_CRITICAL_THRESHOLD = 0.95


# =============================================================================
# Dispatch Policies
# =============================================================================

# Allow partially filled vehicles if priority is sufficiently high

ALLOW_PARTIAL_DISPATCH = False

# Priority override threshold

PRIORITY_OVERRIDE_THRESHOLD = 0.90

# Maximum dispatch cycles a batch/product may be retained

MAX_BATCH_RETENTION_CYCLES = 5

# Forecast horizon for opportunity estimation

FORECAST_LOOKAHEAD_SUBSHIFTS = 1


# =============================================================================
# Batch Formation
# =============================================================================

# Options:
# "zone"
# "capacity"
# "hybrid"

BATCH_FORMATION_STRATEGY = "hybrid"

# Capacity constraints

MAX_BATCH_SIZE = VAN_CAPACITY
MIN_BATCH_SIZE = BIKE_CAPACITY


# =============================================================================
# Effective Product Score (EPS)
# =============================================================================

# EPS =
# (Priority × EPS_PRIORITY_WEIGHT)
# +
# (Retention Penalty × EPS_RETENTION_WEIGHT)

EPS_PRIORITY_WEIGHT = 0.75

EPS_RETENTION_WEIGHT = 0.25

# Penalty added after every retained dispatch cycle

RETENTION_PENALTY_INCREMENT = 0.10

# Upper bound for carry-over influence

MAX_RETENTION_PENALTY = 0.40


# =============================================================================
# Batch Utility Score (BUS)
# =============================================================================

# Must sum approximately to 1.0

BUS_UTILITY_WEIGHTS = {

    "batch_priority": 0.35,

    "vehicle_utilization": 0.20,

    "storage_utilization": 0.15,

    "retention_penalty": -0.20,

    "forecast_opportunity": 0.10,

}

# =============================================================================
# Optimization Configuration
# =============================================================================



# =============================================================================
# Resource Generation
# =============================================================================

# Synthetic vehicle availability

MIN_AVAILABLE_VANS = 2
MAX_AVAILABLE_VANS = 8

MIN_AVAILABLE_BIKES = 5
MAX_AVAILABLE_BIKES = 20

# Synthetic driver availability

MIN_AVAILABLE_DRIVERS = 8
MAX_AVAILABLE_DRIVERS = 30


# =============================================================================
# Output Configuration
# =============================================================================

ROUND_METRICS = 4


# =============================================================================
# Dispatch Engine Logging
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

LOG_DIR = PROJECT_ROOT / "logs"
LOG_FILE = LOG_DIR / "dispatch.logs"


