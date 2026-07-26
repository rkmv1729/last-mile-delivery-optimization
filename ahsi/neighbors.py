"""
neighbors.py

Constructs the neighboring H3 graph required by the
Adaptive H3 Spatial Indexing (AHSI) algorithm.
"""

import h3
import pandas as pd


def build_neighbor_graph(
    h3_demand: pd.DataFrame
    ) -> dict[str, list[str]]:
    """
    Build adjacency graph for occupied H3 cells.

    Parameters
    ----------
    h3_demand : pandas.DataFrame

        Required columns:
            h3_cell_7

    Returns
    -------
    dict[str, list[str]]
        Mapping of each occupied H3 cell to the list of its
        occupied neighboring H3 cells.
    """

    required_columns = {"h3_cell_7"}

    missing = required_columns - set(h3_demand.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    occupied_cells = set(h3_demand["h3_cell_7"])

    neighbor_graph = {}

    for cell in occupied_cells:

        # k = 1 gives immediate neighboring hexagons
        neighbors = set(h3.grid_disk(cell, 1))

        # Remove itself
        neighbors.discard(cell)

        # Additional check: exclusion of non-active cells 
        # already done by get function in merge.py

        # Keep only occupied neighbors
        occupied_neighbors = [
            n
            for n in neighbors
            if n in occupied_cells
        ]

        neighbor_graph[cell] = occupied_neighbors

    return neighbor_graph