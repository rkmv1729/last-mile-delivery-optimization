from pathlib import Path
import pandas as pd
from algorithms import *


INPUT_FILE = "inputs/sample_02_largest.parquet"
OUTPUT_DIR = Path("outputs")

NUM_ZONES = 35
SEED_SPACING = 2


def run_ahsi(
    h3_demand_df,
    num_zones,
    seed_spacing=2,
):
    """
    Execute the complete Adaptive H3 Spatial Indexing pipeline.

    Parameters
    ----------
    h3_demand_df : pd.DataFrame
        Columns:
            - h3_cell_8
            - orders

    num_zones : int
        Number of operational zones to create.

    seed_spacing : int, default=2
        Minimum H3 graph distance between seed cells.

    Returns
    -------
    pd.DataFrame
        Columns:
            - h3_cell_8
            - zone_id
    """

    seed_df = initialize_seeds(
        h3_demand_df=h3_demand_df,
        num_zones=num_zones,
        seed_spacing=seed_spacing,
    )

    zone_df = grow_regions(
        h3_demand_df=h3_demand_df,
        seed_df=seed_df,
    )

    zone_df = refine_boundaries(
        h3_demand_df=h3_demand_df,
        zone_df=zone_df,
    )

    return zone_df


def main():

    OUTPUT_DIR.mkdir(exist_ok=True)

    h3_demand_df = pd.read_parquet(INPUT_FILE)

    zone_df = run_ahsi(
        h3_demand_df=h3_demand_df,
        num_zones=NUM_ZONES,
        seed_spacing=SEED_SPACING,
    )

    zone_df.to_parquet(
        OUTPUT_DIR / "zone_mapping.parquet",
        index=False,
    )

    print("AHSI completed successfully.")
    print(f"Zones saved to {OUTPUT_DIR / 'zone_mapping.parquet'}")


if __name__ == "__main__":
    main()