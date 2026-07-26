"""
===============================================================
ZONE ASSIGNMENT CONFIGURATION
===============================================================

Configuration constants used by the Zone Assignment layer.

This module is responsible for assigning one available driver to
each operational zone (AHSI zone) for every dispatch batch.

Driver familiarity is computed on H3 Resolution 8 cells and then
aggregated to the operational zone using the AHSI cell mapping.

===============================================================
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

# ===============================================================
# INPUT FILES
# ===============================================================

PROCESSED_FOLDER = BASE_DIR / "data/processed/lade"
DRIVER_FAMILIARITY_FILE = "driver_cell_familiarity.parquet"
CELL_MAPPING_FILE = "cell_mapping.parquet"


# ===============================================================
# FAMILIARITY AGGREGATION
# ===============================================================

# Supported:
#   "mean"   -> Mean familiarity of all H3-8 cells in the zone
#   "median" -> Median familiarity
#   "max"    -> Maximum familiarity
#
# Current project decision:
# Mean familiarity.

FAMILIARITY_AGGREGATION = "mean"


# ===============================================================
# OPTIMIZATION
# ===============================================================

# One driver is assigned to one operational zone.
ONE_DRIVER_PER_ZONE = True

# Maximum-weight bipartite matching
OPTIMIZATION_METHOD = "hungarian"


# ===============================================================
# VALIDATION
# ===============================================================

# Warn if a driver's familiarity with an assigned zone falls below
# this threshold. Assignment is still allowed.
MIN_FAMILIARITY_THRESHOLD = 0.10


# ===============================================================
# OUTPUT
# ===============================================================

ZONE_ASSIGNMENT_FOLDER = "outputs"
ZONE_ASSIGNMENT_OUTPUT = "zone_assignment.parquet"


# ===============================================================
# LOGGING
# ===============================================================

MODULE_NAME = "Zone Assignment"