"""
zone_builder.py

Builds the final operational zone mapping for the
Adaptive H3 Spatial Indexing (AHSI) layer.
"""

from itertools import count

import pandas as pd

from .config import (
    H3_RESOLUTION,
    CHILD_RESOLUTION
)

# TODO : update the docstrings


def build_zone_mapping(
    h3_demand: pd.DataFrame,
    merge_plan: dict,
    split_plan: dict,
) -> pd.DataFrame:
    """
    Build the final operational zone mapping.

    Parameters
    ----------
    h3_demand : pd.DataFrame
        Input H3 demand table.

    merge_plan : dict
        Mapping of sparse H3-7 cells to their representative H3-7 cell.

        Example:
        {
            sparse_cell : representative_cell
        }

    split_plan : dict
        Mapping of hotspot H3-7 cells to their generated H3-8 children.

        Example:
        {
            hotspot_cell : [child1, child2, ...]
        }

    Returns
    -------
    pd.DataFrame

    Columns
    -------
    zone_id
        Operational zone identifier.

    cell_id
        H3 cell representing the operational unit.

    resolution
        H3 resolution of the operational cell.

    parent_cell
        Representative H3-7 cell for merged zones,
        original H3-7 parent for split zones,
        or itself for normal zones.
    """

    rows = []

    zone_counter = count(1)

    split_cells = set(split_plan.keys())


    # --------------------------------------------------
    # Merged zones
    # --------------------------------------------------

    processed = set()

    for representative, cells in merge_plan.items():

        zone_id = f"Z{next(zone_counter):03d}"

        for cell in cells:

            rows.append({
                "zone_id": zone_id,
                "cell_id": cell,
                "resolution": H3_RESOLUTION,
                "parent_cell": representative
            })

            processed.add(cell)

    # --------------------------------------------------
    # Normal zones
    # --------------------------------------------------

    for cell in h3_demand["h3_cell_7"].unique():

        if cell in processed:
            continue

        if cell in split_cells:
            continue

        zone_id = f"Z{next(zone_counter):03d}"

        rows.append({
            "zone_id": zone_id,
            "cell_id": cell,
            "resolution": H3_RESOLUTION,
            "parent_cell": cell
        })

    # --------------------------------------------------
    # Split zones
    # --------------------------------------------------

    for parent, children in split_plan.items():

        for child in children:

            zone_id = f"Z{next(zone_counter):03d}"

            rows.append({
                "zone_id": zone_id,
                "cell_id": child,
                "resolution": CHILD_RESOLUTION,
                "parent_cell": parent
            })

    zone_mapping = pd.DataFrame(rows)

    zone_mapping = zone_mapping.sort_values(
        ["zone_id", "resolution", "cell_id"]
    ).reset_index(drop=True)

    return zone_mapping