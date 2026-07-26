"""
Generate H3 demand input for the AHSI layer.
"""

from pathlib import Path

import pandas as pd


from config import (
    MASTER_H3_FILE,
    H3_DEMAND_FILE
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = MASTER_H3_FILE
OUTPUT_FILE = H3_DEMAND_FILE


def main():

    df = pd.read_parquet(INPUT_FILE)

    h3_demand = (
        df.groupby("h3_cell_7")
          .size()
          .reset_index(name="orders")
    )

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    h3_demand.to_parquet(OUTPUT_FILE, index=False)

    print(f"Saved {len(h3_demand)} H3 cells.")


if __name__ == "__main__":
    main()