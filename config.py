from pathlib import Path




# --------------------------------------------------
# Raw Datasets
# --------------------------------------------------

# LADE_FILE = RAW_DIR / "delivery_hz.csv"
# FAVORITA_FILE = RAW_DIR / "favorita.parquet" # fix this, we have two files


# # --------------------------------------------------
# # Processed Datasets
# # --------------------------------------------------

# MASTER_H3_FILE = PROCESSED_DIR / "lade_hz_df.parquet"


# # --------------------------------------------------
# # Input Files
# # --------------------------------------------------

# H3_DEMAND_FILE = INPUT_DIR / "h3_demand.parquet"







# started here

# =============================================================================
# Layer Interfaces
# =============================================================================

AHSI_COLUMNS = [
    "h3_cell_7",
    "h3_cell_8",
    "order_id",
]

DEMAND_FORECAST_COLUMNS = [
    "order_id",
    "date",
    "weekday",
    "shift",
    "h3_cell_8",
]

ZONE_ASSIGNMENT_COLUMNS = [
    ...
]

DISPATCH_COLUMNS = [
    ...
]

# =============================================================================
# H3 cells resolution
# =============================================================================

H3_RESOLUTION = 7
CHILD_RESOLUTION = 8


# =============================================================================
# Project paths
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent

DATA_DIR = PROJECT_ROOT / "data"

RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "master"
INPUT_DIR = DATA_DIR / "inputs"
OUTPUT_DIR = DATA_DIR / "outputs"


# =============================================================================
# Output files
# =============================================================================

ZONE_MAPPING_FILE = OUTPUT_DIR / "zone_mapping.parquet"

