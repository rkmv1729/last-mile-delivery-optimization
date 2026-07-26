"""
merge.py

Sparse cell merging for the AHSI algorithm.
"""

import pandas as pd

from collections import defaultdict

# TODO : update the dostrings indide function

def merge_sparse_cells(
    h3_demand: pd.DataFrame,
    neighbor_graph,
    sparse_threshold : float
) -> dict[str, str]:
    """
    Merge sparse H3 cells with their highest-demand neighboring cell.

    Args:
        neighbor_graph (dict[str, list[str]]):
            Mapping of each H3 cell to its neighboring H3 cells.

        demand_lookup (dict[str, int]):
            Mapping of H3 cell IDs to their observed demand.

        sparse_threshold (int):
            Demand threshold below which a cell is considered sparse and
            eligible for merging.

    Returns
    -------
    dict
        Mapping of representative H3 cells to all H3 cells
        belonging to the merged operational zone.

        Example
        -------
        {
            representative_cell: [
                representative_cell,
                merged_cell_1,
                merged_cell_2,
                ...
            ]
        }
    """

    merged_groups = defaultdict(set)

    merged_cells = set()

    # ------------------------------------------------------------
    # Process sparse cells only
    # ------------------------------------------------------------

    demand_lookup = dict(
    zip(
        h3_demand["h3_cell_7"],
        h3_demand["orders_h3_7"],
        )
    )

    for cell, demand in demand_lookup.items():

        # Already merged
        if cell in merged_cells:
            continue

        # Not sparse
        if demand >= sparse_threshold:
            continue

        # Available neighbors
        candidates = []

        for neighbor in neighbor_graph.get(cell, []):

            if neighbor in merged_cells:
                continue

            candidates.append(neighbor)

        # No valid neighbor
        if not candidates:
            continue

        # --------------------------------------------------------
        # Version 1 heuristic:

        # Merge each sparse cell into the neighboring cell
        # with the highest observed demand. This preserves
        # existing demand hotspots while absorbing sparse regions.
        # --------------------------------------------------------

        # the get function ensures non-active neighbours do not cause errors
        target = max(
            candidates,
            key=lambda n: demand_lookup.get(n, 0),
        )

        # TODO: can return merged_groups directly
        merged_groups[target].add(target)
        merged_groups[target].add(cell)

        merged_cells.add(cell)
        merged_cells.add(target)

    merge_plan = {
        representative: sorted(cells)
        for representative, cells in merged_groups.items()
    }

    return merge_plan