"""
Demand Forecast Configuration
-----------------------------
Configuration constants for the runtime demand forecasting layer.
"""

from pathlib import Path
import torch

# ==========================================================
# Paths
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

MODEL_DIR = PROJECT_ROOT / "demand_forecast" / "models"

MODEL_PATH = MODEL_DIR / "best_demand_model.pth"
SCALER_PATH = MODEL_DIR / "demand_scaler.pkl"


# =============================================================================
#  Demand Forecast Engine Logging
# =============================================================================

LOG_DIR = PROJECT_ROOT / "logs"
LOG_FILE = LOG_DIR / "demand_forecast.log"

# ==========================================================
# Model Configuration
# ==========================================================

LOOKBACK = 12

INPUT_SIZE = 6
HIDDEN_SIZE = 64
NUM_LAYERS = 2
DROPOUT = 0.2
OUTPUT_SIZE = 1

# ==========================================================
# Runtime Device
# ==========================================================

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

# ==========================================================
# Feature Configuration
# ==========================================================

FEATURE_COLUMNS = [
    "demand",
    "shift_sin",
    "shift_cos",
    "dow_sin",
    "dow_cos",
    "day_index",
]

SCALE_COLUMNS = [
    "demand",
    "day_index",
]

# ==========================================================
# Shift Encoding
# ==========================================================

SHIFT_MAPPING = {
    "Morning": 0,
    "Afternoon": 1,
    "Evening": 2,
}

# ==========================================================
# Required Input Columns
# ==========================================================

REQUIRED_COLUMNS = [
    "date",
    "shift",
    "h3_cell_8",
    "demand",
]

# ==========================================================
# Forecast Metadata
# ==========================================================

MODEL_NAME = "DemandLSTM"
MODEL_VERSION = "1.0"


# ==========================================================
# Zone Forecast Configuration
# ==========================================================

# Number of historical days used to compute aggregation weights
WEIGHT_HISTORY_DAYS = 30

# ==========================================================
# Demand Thresholds
# ==========================================================

# Minimum predicted demand considered for zone aggregation
MIN_DEMAND = 1