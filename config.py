from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

DATA_DIR = PROJECT_ROOT / "data"

NUM_ZONES = 35
SEED_SPACING = 2


FEATURE_COLUMNS = [
    "demand",
    "rolling_mean_3",
    "rolling_std_3",
    "demand_diff",
    "growth_rate",
    "shift",
    "dow_sin",
    "dow_cos",
    "is_weekend",
    "day_index",
]

SHIFT_MAPPING = {
    "Morning": 0,
    "Afternoon": 1,
    "Evening": 2,
}

MAX_QTY_PER_ITEM = 20


VEHICLE_CAPACITY = 250

BUS_WEIGHTS = {
    "priority_score": 0.35,
    "vehicle_utilization": 0.20,
    "storage_pressure": 0.15,
    "retention_penalty": 0.20,
    "forecast_opportunity": 0.10,
}

EPS_ALPHA = 0.7
MAX_PENALTY = 0.4
RETENTION_PENALTY_INCREMENT = 0.1

DASHBOARD_TITLE = "Last Mile Delivery Operations"