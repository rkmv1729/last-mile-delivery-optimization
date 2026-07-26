import h3
import pandas as pd

from config import CHILD_RESOLUTION

# TODO : make it consistent to use with parent and child resolution
# TODO : update the docstrings
# TODO : consider the zip of df to dict inside a helper func, or directly accept 
# dict from backend

def split_hotspot_cells(
    h3_demand: pd.DataFrame,
    hotspot_threshold,
    child_resolution=CHILD_RESOLUTION
) -> dict[str, list[str]]:
    """
    Identify hotspot H3 cells and generate their child H3 cells.

    Args:
        demand_lookup (dict[str, int]):
            Mapping of H3 cell IDs to their observed demand.

        hotspot_threshold (int):
            Demand threshold above which a cell is considered a hotspot and
            eligible for splitting.

        child_resolution (int):
            Target H3 resolution for generating child cells.

    Returns:
        dict[str, list[str]]:
            Mapping of hotspot H3 cell IDs to the list of generated child
            H3 cells.
    """

    split_plan = {}

    demand_lookup = dict(
        zip(
            h3_demand["h3_cell_7"],
            h3_demand["orders_h3_7"]
            )
    )

    for cell, demand in demand_lookup.items():

        if demand < hotspot_threshold:
            continue

        if child_resolution <= h3.get_resolution(cell):
            raise ValueError(
                "Child resolution must be greater than parent resolution."
            )
        
        # --------------------------------------------------------
        # Version 1 heuristic:

        # This function only computes the topology of the split.
        # It does not redistribute demand among child cells.
        # Demand allocation is handled elsewhere.
        # --------------------------------------------------------

        children = list(
            h3.cell_to_children(
                cell,
                child_resolution
            )
        )

        split_plan[cell] = children

    return split_plan