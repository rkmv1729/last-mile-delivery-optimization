"""
config.py

Configuration constants for the Adaptive H3 Spatial Indexing (AHSI) layer.

Contains only algorithm-specific parameters used exclusively by AHSI.
Shared project configuration (paths, logging, data sources, etc.) is
maintained in the global configuration module.
"""

from pathlib import Path


# =============================================================================
# H3 Configuration
# =============================================================================

H3_RESOLUTION = 7
CHILD_RESOLUTION = 8


# =============================================================================
# Threshold Initialization
# (Initial values for the threshold optimizer.)
# =============================================================================

INITIAL_SPARSE_PERCENTILE = 25.0
INITIAL_HOTSPOT_PERCENTILE = 99.0


# =============================================================================
#  AHSI Engine Logging
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

LOG_DIR = PROJECT_ROOT / "logs"
LOG_FILE = LOG_DIR / "ahsi.log"




# =============================================================================
# Zone Optimization
# =============================================================================

# Add future optimization-specific constants here.
# Example:
# TARGET_ZONE_TOLERANCE = 0.10
# MAX_OPTIMIZATION_ITERATIONS = 50


# =============================================================================
# Validation
# =============================================================================

# Add AHSI-specific validation constants here.
# Example:
# MIN_ZONE_SIZE = 1
# MAX_ZONE_SIZE = 20